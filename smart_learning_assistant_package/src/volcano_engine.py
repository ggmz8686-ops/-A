import os
import re
from typing import Dict, List, Any, Optional, Callable

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from .config import QA_DATA_PATH
from .utils import read_jsonl


class VolcanoEngineAPI:
    """
    火山引擎API接入模块
    支持大模型语义分析，降级到本地语义分析
    """

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None, model: str = "doubao-pro"):
        """
        初始化火山引擎API

        Args:
            api_key: 火山引擎API密钥，如果为None则使用环境变量 VOLCANO_API_KEY
            endpoint: API端点，如果为None则使用默认端点
            model: 使用的模型名称
        """
        self.api_key = api_key or os.environ.get("VOLCANO_API_KEY")
        self.endpoint = endpoint or os.environ.get("VOLCANO_ENDPOINT", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
        self.model = model
        self.available = bool(self.api_key and REQUESTS_AVAILABLE)
        self._local_analyzer = LocalSemanticAnalyzer()

        if not self.api_key:
            print("[警告] 未配置火山引擎API密钥 (VOLCANO_API_KEY)，将使用本地语义分析")
        elif not REQUESTS_AVAILABLE:
            print("[警告] requests库未安装，将使用本地语义分析")

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        发送对话请求

        Args:
            messages: 对话消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            API响应结果
        """
        if not self.available:
            return self._fallback_to_local(messages)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                print(f"[错误] 火山引擎API返回错误: {result['error']}")
                return self._fallback_to_local(messages)

            return {
                "success": True,
                "data": result,
                "fallback": False
            }

        except requests.exceptions.Timeout:
            print("[错误] 火山引擎API请求超时")
            return self._fallback_to_local(messages)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 401 or status_code == 403:
                print(f"[错误] 火山引擎API认证失败 (状态码: {status_code})，可能是token无效或过期")
            elif status_code == 429:
                print("[错误] 火山引擎API请求频率超限")
            else:
                print(f"[错误] 火山引擎API HTTP错误: {status_code}")
            return self._fallback_to_local(messages)
        except requests.exceptions.RequestException as e:
            print(f"[错误] 火山引擎API请求失败: {str(e)}")
            return self._fallback_to_local(messages)
        except Exception as e:
            print(f"[错误] 未知错误: {str(e)}")
            return self._fallback_to_local(messages)

    def _fallback_to_local(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        降级到本地语义分析

        Args:
            messages: 对话消息列表

        Returns:
            本地分析结果
        """
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        local_result = self._local_analyzer.analyze(user_message)

        return {
            "success": False,
            "error": "API调用失败",
            "fallback": True,
            "message": "火山引擎API暂时不可用，已自动切换到本地语义分析",
            "local_result": local_result,
            "data": {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": local_result["response"]
                    }
                }]
            }
        }

    def analyze_semantic(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        语义分析接口

        Args:
            text: 待分析文本
            context: 上下文信息

        Returns:
            语义分析结果
        """
        messages = [
            {"role": "system", "content": "你是一个智能学习助手，擅长回答各种学科问题。"},
            {"role": "user", "content": text}
        ]

        result = self.chat(messages)

        if result.get("fallback"):
            return result

        try:
            content = result["data"]["choices"][0]["message"]["content"]
            return {
                "success": True,
                "content": content,
                "fallback": False
            }
        except (KeyError, IndexError, TypeError) as e:
            print(f"[错误] 解析API响应失败: {str(e)}")
            return self._fallback_to_local(messages)


class LocalSemanticAnalyzer:
    """
    本地语义分析器
    当API不可用时作为降级方案
    """

    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.subject_keywords = {
            "数学": ["数学", "几何", "代数", "方程", "函数", "概率", "统计", "微积分", "三角函数", "勾股定理", "质数", "导数", "积分", "向量", "矩阵"],
            "英语": ["英语", "语法", "词汇", "阅读", "写作", "听力", "口语", "时态", "语态", "单词", "句子", "从句", "被动语态"],
            "物理": ["物理", "力学", "热学", "光学", "电磁学", "声学", "牛顿", "能量", "功率", "速度", "加速度", "力", "质量"],
            "编程": ["编程", "代码", "程序", "算法", "数据结构", "变量", "函数", "循环", "条件", "Python", "Java", "C++", "数组", "链表"]
        }
        self.concept_responses = self._init_concept_responses()

    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """加载知识库"""
        return read_jsonl(QA_DATA_PATH)

    def _init_concept_responses(self) -> Dict[str, Dict[str, Any]]:
        """初始化概念响应模板"""
        return {
            "质数": {
                "subject": "数学",
                "explanation": "质数是指大于1的自然数，除了1和它本身之外没有其他因数的数。",
                "steps": ["判断一个数是否大于1", "检查它是否能被2到其平方根之间的任何数整除", "如果都不能整除，则是质数"],
                "common_mistakes": ["将1误认为是质数", "检查时遗漏因数", "平方根计算错误"]
            },
            "勾股定理": {
                "subject": "数学",
                "explanation": "勾股定理是一个基本的几何定理，指直角三角形的两条直角边的平方和等于斜边的平方。",
                "steps": ["确定直角三角形的两条直角边长度a和b", "计算a² + b²", "开平方得到斜边c的长度"],
                "common_mistakes": ["混淆直角边和斜边", "计算时忘记平方", "单位不统一"]
            },
            "牛顿运动定律": {
                "subject": "物理",
                "explanation": "牛顿运动定律是经典力学的基础，包括惯性定律、加速度定律和作用力与反作用力定律。",
                "steps": ["理解惯性概念", "掌握F=ma公式", "应用作用力与反作用力原理"],
                "common_mistakes": ["惯性与力的关系理解错误", "单位换算错误", "作用力与反作用力混淆"]
            },
            "能量守恒": {
                "subject": "物理",
                "explanation": "能量守恒定律指在一个封闭系统中，能量既不会凭空产生，也不会凭空消失，只会从一种形式转化为另一种形式。",
                "steps": ["确定系统范围", "分析能量形式", "计算能量变化"],
                "common_mistakes": ["系统边界确定错误", "能量形式识别错误", "计算时单位不统一"]
            },
            "英语时态": {
                "subject": "英语",
                "explanation": "英语时态是表示动作发生时间的语法形式，包括现在时、过去时、将来时等。",
                "steps": ["确定动作发生的时间", "选择正确的时态", "注意动词的变化形式"],
                "common_mistakes": ["时态混用", "不规则动词变化错误", "时间状语与时态不匹配"]
            },
            "Python函数": {
                "subject": "编程",
                "explanation": "函数是一段可重复使用的代码块，接受输入参数并返回结果。",
                "steps": ["定义函数", "调用函数", "处理返回值"],
                "common_mistakes": ["参数传递方式理解错误", "返回值处理错误", "函数命名不规范"]
            }
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        本地语义分析

        Args:
            text: 输入文本

        Returns:
            分析结果
        """
        text = text.strip()

        matched_subject = None
        for subject, keywords in self.subject_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    matched_subject = subject
                    break
            if matched_subject:
                break

        for concept, details in self.concept_responses.items():
            if concept in text:
                return self._format_response(details, concept)

        if matched_subject:
            return {
                "subject": matched_subject,
                "response": f"这是一个关于{matched_subject}的问题。我目前运行在本地模式，完整的语义分析需要配置火山引擎API。\n\n如果您能提供更具体的问题描述，我可以尝试基于内置知识库回答。",
                "matched_subject": matched_subject
            }

        return {
            "response": "您好！我目前运行在本地模式，完整的智能语义分析需要配置火山引擎API。\n\n请尝试：\n1. 设置环境变量 VOLCANO_API_KEY\n2. 或者配置有效的API端点 VOLCANO_ENDPOINT\n\n配置完成后，我将能够提供更智能的问题解答服务。",
            "fallback": True
        }

    def _format_response(self, details: Dict[str, Any], concept: str) -> Dict[str, Any]:
        """格式化响应"""
        response_parts = []
        response_parts.append(f"【{details.get('subject', '未知学科')} - {concept}】")
        response_parts.append(f"\n通俗讲解：{details.get('explanation', '')}")

        if details.get('steps'):
            response_parts.append("\n步骤拆解：")
            for i, step in enumerate(details['steps'], 1):
                response_parts.append(f"{i}. {step}")

        if details.get('common_mistakes'):
            response_parts.append("\n易错点提示：")
            for mistake in details['common_mistakes']:
                response_parts.append(f"- {mistake}")

        response_parts.append("\n\n[提示：当前运行在本地模式，如需更精准的分析请配置火山引擎API]")

        return {
            "subject": details.get('subject'),
            "concept": concept,
            "response": "".join(response_parts),
            "fallback": True
        }


_volcano_api_instance: Optional[VolcanoEngineAPI] = None


def get_volcano_api() -> VolcanoEngineAPI:
    """
    获取火山引擎API单例

    Returns:
        VolcanoEngineAPI实例
    """
    global _volcano_api_instance
    if _volcano_api_instance is None:
        _volcano_api_instance = VolcanoEngineAPI()
    return _volcano_api_instance


def semantic_analysis(text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    语义分析便捷接口

    Args:
        text: 待分析文本
        context: 上下文信息

    Returns:
        语义分析结果
    """
    api = get_volcano_api()
    return api.analyze_semantic(text, context)


def chat(prompt: str, system_prompt: str = "你是一个智能学习助手。") -> Dict[str, Any]:
    """
    对话便捷接口

    Args:
        prompt: 用户输入
        system_prompt: 系统提示

    Returns:
        对话结果
    """
    api = get_volcano_api()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    return api.chat(messages)
