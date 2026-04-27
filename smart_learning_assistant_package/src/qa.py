from __future__ import annotations

import re
from typing import Any

from .config import QA_DATA_PATH
from .utils import calculate_similarity, clean_text, normalize_text, read_jsonl, write_jsonl


class QASystem:
    def __init__(self) -> None:
        self.knowledge_base = self.load_knowledge_base()
        self.builtin_knowledge = self._build_builtin_knowledge()

    def _build_builtin_knowledge(self) -> dict[str, dict[str, dict[str, Any]]]:
        return {
            "数学": {
                "质数": {
                    "keywords": ["质数", "素数"],
                    "explanation": "质数是大于 1 且只有 1 和它本身两个正因数的自然数。",
                    "steps": ["先判断这个数是否大于 1。", "再看它是否还能被 1 和自身以外的整数整除。", "如果不能，就可以判定它是质数。"],
                    "common_mistakes": ["把 1 当成质数。", "漏掉平方根以内的因数检查。"],
                    "recommended_grade": "小学五年级",
                    "practice_subject": "数学",
                    "practice_types": ["判断"],
                    "practice_count": 3,
                    "concept_tags": ["质数"],
                },
                "勾股定理": {
                    "keywords": ["勾股定理", "直角三角形", "a2+b2=c2", "a^2+b^2=c^2"],
                    "explanation": "勾股定理说明直角三角形两条直角边平方和，等于斜边平方。",
                    "steps": ["确认这是直角三角形。", "把两条直角边分别平方后相加。", "结果等于斜边的平方。"],
                    "common_mistakes": ["把斜边和直角边弄反。", "忘记先平方再相加。"],
                    "recommended_grade": "初一",
                    "practice_subject": "数学",
                    "practice_types": ["单选", "判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["勾股定理"],
                },
                "一次函数": {
                    "keywords": ["一次函数", "y=kx+b", "kx+b"],
                    "explanation": "一次函数通常写成 y = kx + b，其中 k 不等于 0，图像是一条直线。",
                    "steps": ["先认出它的标准形式。", "再判断 k 和 b 的含义。", "最后联系图像是一条直线。"],
                    "common_mistakes": ["忘记 k 不能等于 0。", "把一次函数和正比例函数混淆。"],
                    "recommended_grade": "初一",
                    "practice_subject": "数学",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["一次函数"],
                },
                "导数": {
                    "keywords": ["导数", "切线斜率", "瞬时变化率"],
                    "explanation": "导数描述函数在某一点附近变化有多快，几何意义是该点切线的斜率。",
                    "steps": ["先理解平均变化率。", "再让自变量的变化量趋近于 0。", "得到的极限就是导数。"],
                    "common_mistakes": ["把平均变化率和瞬时变化率混淆。", "忽略极限存在的条件。"],
                    "recommended_grade": "大学",
                    "practice_subject": "高等数学",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["导数"],
                },
                "常数": {
                    "keywords": ["常数", "固定的数", "不变的数"],
                    "explanation": "常数是数值固定不变的量，比如 3、-5、1/2 都可以看作常数。",
                    "steps": ["先看这个量的值会不会变化。", "如果在当前问题里它始终不变，就可以把它看成常数。", "再区分它和会变化的变量。"],
                    "common_mistakes": ["把字母一定都当成变量。", "忽略“在当前情境下是否变化”这个前提。"],
                    "recommended_grade": "小学六年级",
                    "practice_subject": "数学",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["常数"],
                },
                "变量": {
                    "keywords": ["变量", "会变化的量", "未知数"],
                    "explanation": "变量是值可能发生变化的量，常用字母来表示，比如 x、y。",
                    "steps": ["先看这个量是不是可能取不同的值。", "如果会变化，就把它看成变量。", "再根据题意判断它的取值范围。"],
                    "common_mistakes": ["把所有字母都当成未知数。", "分不清变量和常数的区别。"],
                    "recommended_grade": "小学六年级",
                    "practice_subject": "数学",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["变量"],
                },
                "分数": {
                    "keywords": ["分数", "真分数", "假分数"],
                    "explanation": "分数表示把单位“1”平均分成若干份，取其中一份或几份得到的数。",
                    "steps": ["先确定单位“1”。", "再看它被平均分成了多少份。", "最后看取了其中几份。"],
                    "common_mistakes": ["没有强调平均分。", "分不清分子和分母表示什么。"],
                    "recommended_grade": "小学五年级",
                    "practice_subject": "数学",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["分数"],
                },
            },
            "语文": {
                "比喻句": {
                    "keywords": ["比喻句", "比喻"],
                    "explanation": "比喻句是把一种事物比作另一种事物，让表达更生动形象。",
                    "steps": ["找出本体。", "找出喻体。", "理解作者想突出什么特点。"],
                    "common_mistakes": ["把普通比较误认为比喻。", "只看到相似词，却没有理解表达效果。"],
                    "recommended_grade": "小学四年级",
                    "practice_subject": "语文",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["比喻句"],
                },
                "中心思想": {
                    "keywords": ["中心思想", "文章主旨", "概括中心"],
                    "explanation": "中心思想是文章最想表达的核心内容、态度和情感。",
                    "steps": ["先概括文章主要写了什么。", "再判断作者表达了什么态度或情感。", "最后用简洁语言合并成一句话。"],
                    "common_mistakes": ["只复述情节，不概括主旨。", "概括太空泛，没有落到文章内容上。"],
                    "recommended_grade": "初一",
                    "practice_subject": "语文",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["中心思想", "主旨"],
                },
                "主语": {
                    "keywords": ["主语", "句子成分", "谁怎么样"],
                    "explanation": "主语是句子里说明‘谁’或‘什么’的成分，通常是动作的发出者或陈述对象。",
                    "steps": ["先看句子在说谁或什么。", "再看后面的动作或状态是围绕谁展开的。", "把这个核心对象找出来，就是主语。"],
                    "common_mistakes": ["把第一个词直接当主语。", "把宾语或状语误判成主语。"],
                    "recommended_grade": "小学六年级",
                    "practice_subject": "语文",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["主语"],
                },
            },
            "英语": {
                "时态": {
                    "keywords": ["时态", "一般现在时", "一般过去时", "完成时"],
                    "explanation": "英语时态用来表示动作发生的时间和状态，比如现在、过去、将来以及是否完成。",
                    "steps": ["先判断动作发生的时间。", "再看动作是正在发生、已经完成还是经常发生。", "最后选择对应的动词形式。"],
                    "common_mistakes": ["时间状语和时态不匹配。", "第三人称单数变化遗漏。"],
                    "recommended_grade": "初一",
                    "practice_subject": "英语",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["时态"],
                },
                "被动语态": {
                    "keywords": ["被动语态", "passive voice"],
                    "explanation": "被动语态强调动作的承受者，常见结构是 be 动词加过去分词。",
                    "steps": ["先找出谁是动作承受者。", "把承受者放到主语位置。", "再用 be + 过去分词构成句子。"],
                    "common_mistakes": ["过去分词形式写错。", "时态转换后 be 动词没有跟着变。"],
                    "recommended_grade": "初二",
                    "practice_subject": "英语",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["被动语态"],
                },
            },
            "物理": {
                "牛顿第一定律": {
                    "keywords": ["牛顿第一定律", "惯性定律", "第一定律", "惯性"],
                    "explanation": "牛顿第一定律指出，物体在不受外力或所受合外力为零时，会保持静止或匀速直线运动状态。",
                    "steps": ["先看物体是否受到了合外力。", "如果没有，就分析它会保持原来的运动状态。", "这种保持原状的性质叫惯性。"],
                    "common_mistakes": ["把惯性理解成力。", "把静止和速度为零时的受力情况混为一谈。"],
                    "recommended_grade": "初二",
                    "practice_subject": "物理",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["牛顿第一定律", "惯性"],
                },
                "牛顿第二定律": {
                    "keywords": ["牛顿第二定律", "f=ma", "F=ma", "加速度"],
                    "explanation": "牛顿第二定律说明加速度与合外力成正比、与质量成反比，方向与合外力方向相同。",
                    "steps": ["先分析受力，求合外力。", "再用 F=ma 建立关系。", "最后结合方向判断加速度方向。"],
                    "common_mistakes": ["把多个力直接相加却没有考虑方向。", "质量和重量混淆。"],
                    "recommended_grade": "高一",
                    "practice_subject": "物理",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["牛顿第二定律", "F=ma"],
                },
            },
            "化学": {
                "化学变化": {
                    "keywords": ["化学变化", "新物质"],
                    "explanation": "化学变化的核心特征是生成了新物质。",
                    "steps": ["先观察是否有颜色、气味、沉淀等变化。", "再判断本质上是否生成了新物质。", "如果有，就是化学变化。"],
                    "common_mistakes": ["把状态变化当成化学变化。", "只看现象，不看本质。"],
                    "recommended_grade": "初三",
                    "practice_subject": "化学",
                    "practice_types": ["判断"],
                    "practice_count": 3,
                    "concept_tags": ["化学变化"],
                },
                "氧化还原反应": {
                    "keywords": ["氧化还原", "化合价", "电子得失"],
                    "explanation": "氧化还原反应中元素化合价发生变化，本质上伴随电子得失或偏移。",
                    "steps": ["先找出反应前后的元素化合价。", "看哪些元素升高、哪些降低。", "再判断氧化和还原分别发生在哪里。"],
                    "common_mistakes": ["不会判断化合价。", "把氧化剂和还原剂记反。"],
                    "recommended_grade": "高一",
                    "practice_subject": "化学",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["氧化还原反应"],
                },
            },
            "生物": {
                "光合作用": {
                    "keywords": ["光合作用", "叶绿体", "二氧化碳", "氧气"],
                    "explanation": "光合作用是绿色植物利用光能，把二氧化碳和水转化为有机物并释放氧气的过程。",
                    "steps": ["记住原料是水和二氧化碳。", "场所主要是叶绿体。", "产物是有机物和氧气。"],
                    "common_mistakes": ["把呼吸作用和光合作用混淆。", "忘记光能和叶绿体条件。"],
                    "recommended_grade": "初一",
                    "practice_subject": "生物",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["光合作用"],
                },
                "有丝分裂": {
                    "keywords": ["有丝分裂", "细胞分裂", "染色体"],
                    "explanation": "有丝分裂让一个细胞分成两个遗传物质基本相同的子细胞，是生长、发育和修复的重要基础。",
                    "steps": ["先复制遗传物质。", "再让染色体平均分配到两端。", "最后形成两个子细胞。"],
                    "common_mistakes": ["把减数分裂和有丝分裂混淆。", "搞不清染色体和 DNA 的关系。"],
                    "recommended_grade": "高一",
                    "practice_subject": "生物",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["有丝分裂"],
                },
            },
            "历史": {
                "辛亥革命": {
                    "keywords": ["辛亥革命", "武昌起义", "清朝"],
                    "explanation": "辛亥革命推翻了清朝统治，结束了两千多年的君主专制制度，推动中国近代化进程。",
                    "steps": ["先明确它发生在 1911 年。", "再记住它推翻了清朝。", "理解它在政治制度上的重要意义。"],
                    "common_mistakes": ["把辛亥革命和戊戌变法混淆。", "只记结论，不理解历史影响。"],
                    "recommended_grade": "初三",
                    "practice_subject": "历史",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["辛亥革命"],
                },
                "工业革命": {
                    "keywords": ["工业革命", "蒸汽机", "城市化"],
                    "explanation": "工业革命大幅提升生产力，推动工厂制度、城市化和资本主义经济的发展。",
                    "steps": ["记住核心技术突破，如蒸汽机。", "再看生产方式和社会结构的变化。", "最后分析它带来的长期影响。"],
                    "common_mistakes": ["只记发明家，不理解时代变化。", "忽略负面影响，如环境问题。"],
                    "recommended_grade": "高一",
                    "practice_subject": "历史",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["工业革命"],
                },
            },
            "地理": {
                "季风气候": {
                    "keywords": ["季风气候", "夏季多雨", "冬季干燥", "风向变化"],
                    "explanation": "季风气候的典型特点是风向随季节明显变化，降水主要集中在夏季。",
                    "steps": ["先看海陆热力差异。", "再分析夏季和冬季风向变化。", "最后联系降水和气温特点。"],
                    "common_mistakes": ["只记降水，不理解风向成因。", "把季风气候和温带海洋性气候混淆。"],
                    "recommended_grade": "高一",
                    "practice_subject": "地理",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["季风气候"],
                },
                "赤道气候": {
                    "keywords": ["赤道", "太阳高度角", "热量"],
                    "explanation": "赤道附近太阳高度角大，全年获得太阳辐射较多，所以气温普遍较高。",
                    "steps": ["先看纬度位置。", "再联系太阳直射和入射角。", "最后得出热量丰富、气温高的结论。"],
                    "common_mistakes": ["只说离太阳近。", "忽略纬度和太阳高度角的关系。"],
                    "recommended_grade": "初一",
                    "practice_subject": "地理",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["赤道", "气温"],
                },
            },
            "政治": {
                "权利与义务": {
                    "keywords": ["权利", "义务", "统一"],
                    "explanation": "公民依法享有权利，也必须履行义务，二者相互依存、不可分割。",
                    "steps": ["先理解权利是什么。", "再理解义务是什么。", "最后把二者放在社会生活中一起看。"],
                    "common_mistakes": ["只强调权利，不谈义务。", "把道德要求和法定义务完全混在一起。"],
                    "recommended_grade": "初二",
                    "practice_subject": "政治",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["权利", "义务"],
                },
                "市场配置资源": {
                    "keywords": ["市场", "资源配置", "价格", "供求", "竞争"],
                    "explanation": "市场主要通过价格、供求和竞争机制引导资源流向效率更高的领域。",
                    "steps": ["先看价格如何传递稀缺信息。", "再看供求变化如何影响生产。", "最后理解竞争如何促进效率提升。"],
                    "common_mistakes": ["只记结论，不理解机制。", "把政府调控和市场作用完全对立起来。"],
                    "recommended_grade": "高一",
                    "practice_subject": "政治",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["市场配置资源"],
                },
            },
            "计算机": {
                "数据结构": {
                    "keywords": ["数据结构", "数组", "链表", "栈", "队列"],
                    "explanation": "数据结构是组织和存储数据的方式，会影响数据访问和算法效率。",
                    "steps": ["先看数据的存储方式。", "再看支持哪些操作。", "最后比较时间和空间效率。"],
                    "common_mistakes": ["只背名字，不理解适用场景。", "忽略操作复杂度。"],
                    "recommended_grade": "大学",
                    "practice_subject": "程序设计",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["数据结构"],
                },
                "操作系统": {
                    "keywords": ["操作系统", "硬件", "软件资源", "进程"],
                    "explanation": "操作系统负责管理硬件和软件资源，并为应用程序提供统一的运行环境。",
                    "steps": ["先理解它夹在硬件和应用之间。", "再看资源管理、进程调度和文件管理。", "最后理解它为什么是基础软件。"],
                    "common_mistakes": ["把应用软件当成操作系统。", "只记界面，不理解底层作用。"],
                    "recommended_grade": "大学",
                    "practice_subject": "计算机基础",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["操作系统"],
                },
            },
            "Python": {
                "Python": {
                    "keywords": ["python", "Python", "python语言", "编程语言 python", "python编程"],
                    "explanation": "Python 是一种语法简洁、可读性强的通用编程语言，常用于入门编程、数据分析、自动化和人工智能等方向。",
                    "steps": ["先把它理解成一种和计算机交流的语言。", "再认识变量、条件、循环、函数这些基础语法。", "最后通过小项目把语法真正用起来。"],
                    "common_mistakes": ["只背语法，不写代码。", "一开始就追很复杂的框架，反而没打稳基础。"],
                    "recommended_grade": "高一",
                    "practice_subject": "Python",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["Python", "变量"],
                },
                "列表推导式": {
                    "keywords": ["列表推导式", "list comprehension"],
                    "explanation": "列表推导式是一种用简洁语法根据已有可迭代对象快速生成新列表的写法，还可以带条件筛选。",
                    "steps": ["先确定要遍历哪个可迭代对象。", "再写出生成的新元素表达式。", "如果需要，再补上筛选条件。"],
                    "common_mistakes": ["把表达式和循环顺序写反。", "只会照抄，不知道它本质上是在生成新列表。"],
                    "recommended_grade": "大学",
                    "practice_subject": "Python",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["列表推导式"],
                },
                "变量": {
                    "keywords": ["变量", "赋值", "variable"],
                    "explanation": "变量是程序中用来保存数据的名字，赋值后可以在后续代码中继续使用。",
                    "steps": ["先给变量起一个合法的名字。", "再把值赋给它。", "之后通过变量名读取或更新这个值。"],
                    "common_mistakes": ["变量名以数字开头。", "把等号当成数学里的相等而不是赋值。"],
                    "recommended_grade": "高一",
                    "practice_subject": "Python",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["变量"],
                },
            },
            "经济学": {
                "供求关系": {
                    "keywords": ["供求", "价格", "需求", "供给"],
                    "explanation": "一般情况下，需求增加或供给减少会推高价格；需求减少或供给增加会压低价格。",
                    "steps": ["先判断需求还是供给在变化。", "再看变化方向。", "最后推断价格的上升或下降。"],
                    "common_mistakes": ["把需求量和需求概念混淆。", "只记价格结果，不理解原因。"],
                    "recommended_grade": "大学",
                    "practice_subject": "经济学",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["供求关系"],
                },
                "机会成本": {
                    "keywords": ["机会成本", "选择", "放弃"],
                    "explanation": "机会成本是为了得到某种选择而放弃的次优选择中的最大价值。",
                    "steps": ["先明确你做了什么选择。", "再看放弃了哪些可选项。", "找出其中价值最高的放弃项。"],
                    "common_mistakes": ["把花出去的钱全都当成机会成本。", "没有比较被放弃选项的价值。"],
                    "recommended_grade": "大学",
                    "practice_subject": "经济学",
                    "practice_types": ["判断", "简答"],
                    "practice_count": 3,
                    "concept_tags": ["机会成本"],
                },
            },
        }

    def load_knowledge_base(self) -> list[dict[str, Any]]:
        return read_jsonl(QA_DATA_PATH)

    def save_knowledge_base(self) -> None:
        write_jsonl(QA_DATA_PATH, self.knowledge_base)

    def add_knowledge(self, question: str, answer: str) -> None:
        self.knowledge_base.append({"question": question, "answer": answer})
        self.save_knowledge_base()

    def _build_practice_recommendation(self, match_result: dict[str, Any]) -> dict[str, Any] | None:
        practice_subject = match_result.get("practice_subject")
        recommended_grade = match_result.get("recommended_grade")
        if not practice_subject or not recommended_grade:
            return None

        practice_types = match_result.get("practice_types") or ["判断"]
        concept_tags = match_result.get("concept_tags") or [match_result.get("concept", "")]
        return {
            "subject": practice_subject,
            "grade": recommended_grade,
            "concept": match_result.get("concept", ""),
            "concept_tags": [item for item in concept_tags if item],
            "question_types": practice_types,
            "count": int(match_result.get("practice_count") or 3),
        }

    def _extract_focus_terms(self, question: str) -> list[str]:
        patterns = [
            r"什么是(.+?)[？?]?$",
            r"什么叫(.+?)[？?]?$",
            r"(.+?)是什么意思[？?]?$",
            r"解释一下(.+?)[？?]?$",
            r"请解释(.+?)[？?]?$",
            r"(.+?)是什么[？?]?$",
        ]

        focus_terms: list[str] = []
        cleaned_question = clean_text(question)
        for pattern in patterns:
            match = re.match(pattern, cleaned_question)
            if not match:
                continue
            term = match.group(1).strip("：:，,。.!！？? ")
            if term and term not in focus_terms:
                focus_terms.append(term)

        return focus_terms

    def _match_builtin_knowledge(self, question: str) -> dict[str, Any] | None:
        normalized_question = normalize_text(question)
        focus_terms = self._extract_focus_terms(question)
        normalized_focus_terms = [normalize_text(item) for item in focus_terms if item]
        best_match: dict[str, Any] | None = None
        best_score = 0.0

        for subject, concepts in self.builtin_knowledge.items():
            for concept, details in concepts.items():
                score = 0.0
                normalized_concept = normalize_text(concept)
                for keyword in details["keywords"]:
                    normalized_keyword = normalize_text(keyword)
                    if normalized_keyword in normalized_question:
                        score += 2
                    if any(normalized_keyword == focus_term for focus_term in normalized_focus_terms):
                        score += 2

                if normalized_concept in normalized_question:
                    score += 2
                if any(normalized_concept == focus_term for focus_term in normalized_focus_terms):
                    score += 3

                for focus_term in normalized_focus_terms:
                    similarity = calculate_similarity(focus_term, normalized_concept)
                    if similarity >= 0.72:
                        score += similarity * 3
                    for keyword in details["keywords"]:
                        keyword_similarity = calculate_similarity(focus_term, normalize_text(keyword))
                        if keyword_similarity >= 0.76:
                            score += keyword_similarity * 2

                if score > best_score:
                    best_score = score
                    best_match = {
                        "subject": subject,
                        "concept": concept,
                        "explanation": details["explanation"],
                        "steps": details["steps"],
                        "common_mistakes": details["common_mistakes"],
                        "recommended_grade": details.get("recommended_grade"),
                        "practice_subject": details.get("practice_subject", subject),
                        "practice_types": details.get("practice_types", ["判断"]),
                        "practice_count": details.get("practice_count", 3),
                        "concept_tags": details.get("concept_tags", [concept]),
                    }

        return best_match if best_score >= 1.8 else None

    def _match_user_knowledge(self, question: str) -> dict[str, Any] | None:
        best_item: dict[str, Any] | None = None
        best_score = 0.0
        for item in self.knowledge_base:
            candidate_question = item.get("question") or ""
            if not candidate_question:
                continue

            score = calculate_similarity(question, candidate_question)
            if normalize_text(candidate_question) in normalize_text(question):
                score += 0.2

            if score > best_score:
                best_score = score
                best_item = item

        if best_item and best_score >= 0.38:
            return {"answer": best_item.get("answer", "")}
        return None

    def match_question(self, question: str) -> dict[str, Any] | None:
        cleaned_question = clean_text(question)
        builtin_match = self._match_builtin_knowledge(cleaned_question)
        if builtin_match:
            return builtin_match
        return self._match_user_knowledge(cleaned_question)

    def format_answer(self, match_result: dict[str, Any]) -> str:
        if "answer" in match_result:
            return match_result["answer"]

        answer_parts = [
            f"【{match_result['subject']} · {match_result['concept']}】",
            "",
            f"通俗讲解：{match_result['explanation']}",
        ]

        steps = match_result.get("steps") or []
        if steps:
            answer_parts.append("")
            answer_parts.append("理解步骤：")
            answer_parts.extend([f"{index}. {step}" for index, step in enumerate(steps, start=1)])

        common_mistakes = match_result.get("common_mistakes") or []
        if common_mistakes:
            answer_parts.append("")
            answer_parts.append("容易出错的地方：")
            answer_parts.extend([f"- {item}" for item in common_mistakes])

        return "\n".join(answer_parts)

    def answer_question(self, question: str) -> dict[str, Any]:
        match_result = self.match_question(question)
        if not match_result:
            return {
                "answer": "抱歉，我暂时还没有在本地知识库里找到这个问题的稳定答案。你可以换个问法，或者把学科和关键词说得更具体一些。",
                "matched": False,
                "practice_recommendation": None,
            }

        response = {
            "answer": self.format_answer(match_result),
            "matched": True,
            "subject": match_result.get("subject"),
            "concept": match_result.get("concept"),
            "practice_recommendation": self._build_practice_recommendation(match_result),
        }
        return response

    def ask_question(self, question: str) -> str:
        return self.answer_question(question)["answer"]


def answer_question(question: str) -> dict[str, Any]:
    qa_system = QASystem()
    return qa_system.answer_question(question)


def ask_question(question: str) -> str:
    qa_system = QASystem()
    return qa_system.ask_question(question)
