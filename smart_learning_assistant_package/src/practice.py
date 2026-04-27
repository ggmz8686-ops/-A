from __future__ import annotations

import copy
import random
import re
from typing import Any

from .config import (
    GRADE_GROUPS,
    GRADE_LEVELS,
    LEGACY_DIFFICULTY_TO_GRADE_GROUP,
    QUESTIONS_DATA_PATH,
    QUESTION_TYPES,
    SUBJECTS_BY_GRADE_GROUP,
)
from .utils import calculate_similarity, get_current_datetime, get_db_connection, normalize_text, read_csv


Question = dict[str, Any]

TYPE_ALIASES = {
    "选择题": "单选",
    "单选题": "单选",
    "多选题": "多选",
    "判断题": "判断",
    "简答题": "简答",
    "填空题": "简答",
}

TRUE_VALUES = {"对", "正确", "是", "true", "yes", "y", "t", "1"}
FALSE_VALUES = {"错", "错误", "否", "false", "no", "n", "f", "0"}


class PracticeSystem:
    def __init__(self) -> None:
        self.builtin_questions = [self._prepare_question_record(item) for item in self._build_builtin_questions()]
        self.questions_data = self.load_questions_data()
        self._repair_wrong_question_records()

    def _build_builtin_questions(self) -> list[Question]:
        return [
            {
                "grade_group": "小学低年级",
                "subject": "语文",
                "type": "单选",
                "question": "下列词语中，哪个最适合用来形容春天？",
                "options": ["寒冷", "温暖", "干燥", "刺骨"],
                "correct_answer": "温暖",
                "explanation": "春天通常给人温暖、生机勃勃的感觉。",
            },
            {
                "grade_group": "小学低年级",
                "subject": "数学",
                "type": "单选",
                "question": "36 + 24 的结果是？",
                "options": ["58", "60", "62", "64"],
                "correct_answer": "60",
                "explanation": "36 和 24 相加等于 60。",
            },
            {
                "grade_group": "小学低年级",
                "subject": "数学",
                "type": "判断",
                "question": "正方形的四条边都相等。",
                "correct_answer": "对",
                "explanation": "正方形既有四个直角，也有四条相等的边。",
            },
            {
                "grade_group": "小学低年级",
                "subject": "数学",
                "type": "简答",
                "question": "什么是长方形？",
                "correct_answer": "长方形是四边形，对边相等，四个角都是直角。",
                "key_points": [["四边形"], ["对边相等"], ["四个角", "直角"]],
                "explanation": "回答到形状特征和角的特征，就说明掌握得比较好了。",
            },
            {
                "grade_group": "小学中年级",
                "subject": "语文",
                "type": "简答",
                "question": "什么是比喻句？",
                "correct_answer": "比喻句是把一种事物比作另一种事物，让表达更生动形象的句子。",
                "key_points": [["一种事物比作另一种事物", "把事物比作"], ["生动", "形象"]],
                "explanation": "说清“把什么比作什么”和“让表达更形象”就可以。",
            },
            {
                "grade_group": "小学中年级",
                "subject": "英语",
                "type": "单选",
                "question": "I ___ a student.",
                "options": ["am", "is", "are", "be"],
                "correct_answer": "am",
                "explanation": "主语是 I 时，be 动词用 am。",
            },
            {
                "grade_group": "小学中年级",
                "subject": "科学",
                "type": "简答",
                "question": "植物进行光合作用需要哪些条件？",
                "correct_answer": "植物进行光合作用通常需要阳光、水、二氧化碳，并且依靠叶绿体。",
                "key_points": [["阳光"], ["水"], ["二氧化碳"], ["叶绿体", "叶子"]],
                "explanation": "答出主要条件即可，不要求字字一致。",
            },
            {
                "grade_group": "小学高年级",
                "subject": "数学",
                "type": "简答",
                "question": "什么是分数？",
                "correct_answer": "分数表示把单位“1”平均分成若干份，取其中一份或几份的数。",
                "key_points": [["单位1", "单位“1”"], ["平均分"], ["几份", "其中一份", "其中几份"]],
                "explanation": "把“平均分”和“取其中几份”说明白就算掌握住了。",
            },
            {
                "grade_group": "小学高年级",
                "subject": "数学",
                "type": "判断",
                "question": "1 是质数。",
                "correct_answer": "错",
                "explanation": "质数必须大于 1，并且只有 1 和它本身两个正因数。",
                "concept_tags": ["质数"],
            },
            {
                "grade_group": "小学高年级",
                "subject": "数学",
                "type": "判断",
                "question": "2 是最小的质数。",
                "correct_answer": "对",
                "explanation": "2 大于 1，并且只有 1 和 2 两个正因数，所以它是最小的质数。",
                "concept_tags": ["质数"],
            },
            {
                "grade_group": "小学高年级",
                "subject": "数学",
                "type": "判断",
                "question": "9 是质数。",
                "correct_answer": "错",
                "explanation": "9 除了 1 和 9，还能被 3 整除，所以不是质数。",
                "concept_tags": ["质数"],
            },
            {
                "grade_group": "小学高年级",
                "subject": "数学",
                "type": "判断",
                "question": "11 只有 1 和 11 两个正因数，所以它是质数。",
                "correct_answer": "对",
                "explanation": "11 只能被 1 和 11 整除，符合质数定义。",
                "concept_tags": ["质数"],
            },
            {
                "grade_group": "小学高年级",
                "subject": "英语",
                "type": "判断",
                "question": "there is 通常用于单数名词或不可数名词。",
                "correct_answer": "对",
                "explanation": "there is 对应单数名词或不可数名词，there are 对应复数名词。",
            },
            {
                "grade_group": "小学高年级",
                "subject": "科学",
                "type": "简答",
                "question": "为什么会出现月亮的圆缺变化？",
                "correct_answer": "因为月亮绕地球运动，太阳照亮月球的一半，而我们从地球看到的被照亮部分不断变化，所以会有月相变化。",
                "key_points": [["绕地球运动"], ["太阳照亮月球"], ["看到的部分变化", "被照亮部分变化", "月相变化"]],
                "explanation": "把“运动”和“看到的亮面变化”说出来就可以。",
            },
            {
                "grade_group": "初中",
                "subject": "语文",
                "type": "简答",
                "question": "概括文章中心时要注意什么？",
                "correct_answer": "概括文章中心要抓住主要内容、作者情感和文章主旨，语言尽量准确简洁。",
                "key_points": [["主要内容"], ["作者情感", "思想感情"], ["主旨"], ["准确", "简洁"]],
                "explanation": "只要覆盖文章写了什么、表达了什么、怎么概括就够了。",
            },
            {
                "grade_group": "初中",
                "subject": "数学",
                "type": "简答",
                "question": "什么是一次函数？",
                "correct_answer": "一次函数通常写成 y = kx + b，其中 k 不等于 0，图像是一条直线。",
                "key_points": [["y=kx+b", "kx+b"], ["k不等于0", "k≠0"], ["直线"]],
                "explanation": "公式和图像特征都说到，就算回答到位。",
            },
            {
                "grade_group": "初中",
                "subject": "英语",
                "type": "简答",
                "question": "什么是被动语态？",
                "correct_answer": "被动语态表示主语是动作的承受者，常见结构是 be 动词加过去分词。",
                "key_points": [["主语", "承受者"], ["be动词", "be"], ["过去分词"]],
                "explanation": "说出“谁承受动作”和基本结构就可以。",
            },
            {
                "grade_group": "初中",
                "subject": "物理",
                "type": "简答",
                "question": "什么是惯性？",
                "correct_answer": "惯性是物体保持原来静止状态或匀速直线运动状态不变的性质。",
                "key_points": [["保持原来状态", "保持原有状态"], ["静止"], ["匀速直线运动"]],
                "explanation": "核心是“保持原来运动状态不变”。",
            },
            {
                "grade_group": "初中",
                "subject": "化学",
                "type": "判断",
                "question": "化学变化的判断关键之一是有没有生成新物质。",
                "correct_answer": "对",
                "explanation": "抓住“是否生成新物质”就是判断关键。",
            },
            {
                "grade_group": "初中",
                "subject": "生物",
                "type": "简答",
                "question": "光合作用有什么意义？",
                "correct_answer": "光合作用能制造有机物、储存能量，并释放氧气，是地球生命的重要基础。",
                "key_points": [["有机物"], ["储存能量", "能量"], ["氧气"]],
                "explanation": "讲到“制造有机物”和“释放氧气”基本就答对了。",
            },
            {
                "grade_group": "初中",
                "subject": "历史",
                "type": "单选",
                "question": "辛亥革命推翻了哪个朝代的统治？",
                "options": ["唐朝", "元朝", "清朝", "明朝"],
                "correct_answer": "清朝",
                "explanation": "辛亥革命结束了清朝统治，推动了中国近代社会转型。",
            },
            {
                "grade_group": "初中",
                "subject": "地理",
                "type": "简答",
                "question": "为什么赤道附近气温普遍较高？",
                "correct_answer": "因为赤道附近太阳高度角大，单位面积获得的太阳辐射更多，所以气温更高。",
                "key_points": [["太阳高度角大"], ["太阳辐射更多", "获得热量更多"], ["气温高"]],
                "explanation": "只要抓住“太阳直射更强、得到热量更多”即可。",
            },
            {
                "grade_group": "初中",
                "subject": "政治",
                "type": "简答",
                "question": "为什么说权利和义务是统一的？",
                "correct_answer": "因为公民既依法享有权利，也必须履行义务，权利和义务相互依存、不可分割。",
                "key_points": [["享有权利"], ["履行义务"], ["相互依存", "统一", "不可分割"]],
                "explanation": "答出“既有权利又有义务，而且二者统一”就可以。",
            },
            {
                "grade_group": "高中",
                "subject": "语文",
                "type": "简答",
                "question": "议论文三要素是什么？",
                "correct_answer": "议论文三要素通常是论点、论据和论证。",
                "key_points": [["论点"], ["论据"], ["论证"]],
                "explanation": "三要素齐全即可。",
            },
            {
                "grade_group": "高中",
                "subject": "数学",
                "type": "简答",
                "question": "什么是函数的单调性？",
                "correct_answer": "函数单调性是指函数值随着自变量增大而持续增大或持续减小的性质。",
                "key_points": [["自变量增大"], ["函数值"], ["增大", "减小", "持续变化"]],
                "explanation": "把“自变量变化”和“函数值变化趋势”说清楚就好。",
            },
            {
                "grade_group": "高中",
                "subject": "英语",
                "type": "简答",
                "question": "定语从句有什么作用？",
                "correct_answer": "定语从句用来修饰名词或代词，对先行词进行补充说明，使表达更准确。",
                "key_points": [["修饰名词", "修饰代词"], ["先行词"], ["补充说明", "更准确"]],
                "explanation": "关键是“修饰先行词”。",
            },
            {
                "grade_group": "高中",
                "subject": "物理",
                "type": "简答",
                "question": "牛顿第二定律的内容是什么？",
                "correct_answer": "牛顿第二定律指出，物体的加速度跟所受合外力成正比，跟质量成反比，方向与合外力方向相同，可表示为 F=ma。",
                "key_points": [["加速度"], ["合外力成正比", "与合外力成正比"], ["质量成反比", "与质量成反比"], ["F=ma"]],
                "explanation": "说到比例关系和公式，就已经很接近标准答案了。",
            },
            {
                "grade_group": "高中",
                "subject": "化学",
                "type": "简答",
                "question": "什么是氧化还原反应？",
                "correct_answer": "氧化还原反应是反应中元素化合价发生变化，伴随电子得失或偏移的反应。",
                "key_points": [["化合价变化"], ["电子得失", "电子偏移"]],
                "explanation": "抓住化合价和电子变化即可。",
            },
            {
                "grade_group": "高中",
                "subject": "生物",
                "type": "简答",
                "question": "有丝分裂有什么意义？",
                "correct_answer": "有丝分裂能保持亲子细胞遗传物质相对稳定，实现细胞增殖、个体生长和组织修复。",
                "key_points": [["遗传物质稳定"], ["细胞增殖"], ["生长", "发育", "组织修复"]],
                "explanation": "讲清稳定遗传和细胞增殖作用就可以。",
            },
            {
                "grade_group": "高中",
                "subject": "历史",
                "type": "简答",
                "question": "工业革命带来了哪些主要影响？",
                "correct_answer": "工业革命提高了生产力，推动城市化和资本主义发展，也带来了社会结构变化和环境问题。",
                "key_points": [["生产力提高"], ["城市化", "资本主义发展"], ["社会结构变化", "环境问题"]],
                "explanation": "正反两面各讲到一点就不错。",
            },
            {
                "grade_group": "高中",
                "subject": "地理",
                "type": "简答",
                "question": "季风气候有什么特点？",
                "correct_answer": "季风气候通常降水季节分配不均，夏季高温多雨，冬季相对干燥寒冷，风向随季节变化明显。",
                "key_points": [["降水季节不均"], ["夏季多雨"], ["冬季干燥", "冬季寒冷"], ["风向变化"]],
                "explanation": "气温、降水和风向三点答到两点以上就比较完整了。",
            },
            {
                "grade_group": "高中",
                "subject": "政治",
                "type": "简答",
                "question": "市场在资源配置中起什么作用？",
                "correct_answer": "市场通过价格、供求和竞争机制引导资源流向效率更高的领域，在资源配置中起决定性作用。",
                "key_points": [["价格"], ["供求"], ["竞争"], ["资源配置", "决定性作用"]],
                "explanation": "把三种机制和资源配置联系起来即可。",
            },
            {
                "grade_group": "高中",
                "subject": "Python",
                "type": "单选",
                "question": "在 Python 中，`len([1, 2, 3])` 的结果是什么？",
                "options": ["2", "3", "4", "报错"],
                "correct_answer": "3",
                "explanation": "len 用来返回序列中元素的个数。",
            },
            {
                "grade_group": "高中",
                "subject": "Python",
                "type": "多选",
                "question": "下面哪些是 Python 的常见内置数据类型？",
                "options": ["list", "dict", "classroom", "tuple"],
                "correct_answer": ["list", "dict", "tuple"],
                "explanation": "list、dict、tuple 都是常见内置类型，classroom 不是类型名。",
            },
            {
                "grade_group": "高中",
                "subject": "Python",
                "type": "判断",
                "question": "Python 中的缩进会影响代码块结构。",
                "correct_answer": "对",
                "explanation": "Python 用缩进表示代码层级，缩进错误往往会直接导致语法或逻辑问题。",
            },
            {
                "grade_group": "高中",
                "subject": "Python",
                "type": "简答",
                "question": "什么是 Python 里的 for 循环？",
                "correct_answer": "for 循环用于按顺序遍历可迭代对象中的元素，并对每个元素重复执行一段代码。",
                "key_points": [["遍历", "循环处理"], ["可迭代对象", "序列", "列表"], ["重复执行", "逐个处理"]],
                "explanation": "说到“遍历对象中的元素并重复执行代码”就比较完整了。",
            },
            {
                "grade_group": "高中",
                "subject": "Python",
                "type": "单选",
                "question": "下面哪一个是 Python 中用于定义函数的关键字？",
                "options": ["func", "define", "def", "lambda"],
                "correct_answer": "def",
                "explanation": "普通函数使用 def 定义，lambda 用于匿名函数表达式。",
            },
            {
                "grade_group": "大学",
                "subject": "高等数学",
                "type": "简答",
                "question": "导数的几何意义是什么？",
                "correct_answer": "导数的几何意义是函数图像在某一点处切线的斜率。",
                "key_points": [["切线"], ["斜率"], ["某一点"]],
                "explanation": "回答到“切线斜率”就基本正确。",
            },
            {
                "grade_group": "大学",
                "subject": "大学英语",
                "type": "简答",
                "question": "What is a thesis statement?",
                "correct_answer": "A thesis statement is the main claim or central idea of an essay, usually showing what the writer will argue.",
                "key_points": [["main claim", "central idea"], ["essay"], ["argue", "writer will discuss"]],
                "explanation": "As long as the answer explains that it is the essay's central claim, it is acceptable.",
            },
            {
                "grade_group": "大学",
                "subject": "计算机基础",
                "type": "简答",
                "question": "操作系统的主要作用是什么？",
                "correct_answer": "操作系统负责管理硬件和软件资源，为应用程序和用户提供运行环境与基础服务。",
                "key_points": [["管理硬件"], ["管理软件资源", "软件资源"], ["运行环境", "基础服务", "用户"]],
                "explanation": "说出资源管理和运行支撑就算答到点上了。",
            },
            {
                "grade_group": "大学",
                "subject": "程序设计",
                "type": "简答",
                "question": "什么是面向对象编程？",
                "correct_answer": "面向对象编程是一种以对象为核心组织程序的思想，强调封装、继承和多态。",
                "key_points": [["对象"], ["封装"], ["继承"], ["多态"]],
                "explanation": "答出对象思想，再说出三大特征中的两到三个就可以。",
            },
            {
                "grade_group": "大学",
                "subject": "Python",
                "type": "单选",
                "question": "Python 列表的 `append()` 方法执行成功后会返回什么？",
                "options": ["新增后的列表", "True", "None", "新增元素"],
                "correct_answer": "None",
                "explanation": "append 会原地修改列表，返回值是 None。",
            },
            {
                "grade_group": "大学",
                "subject": "Python",
                "type": "多选",
                "question": "关于 Python 函数，下面哪些说法是正确的？",
                "options": [
                    "可以设置默认参数",
                    "可以返回多个值",
                    "定义函数必须写 class",
                    "函数内部不能再定义函数",
                ],
                "correct_answer": ["可以设置默认参数", "可以返回多个值"],
                "explanation": "Python 函数支持默认参数，也常通过元组打包返回多个值。",
            },
            {
                "grade_group": "大学",
                "subject": "Python",
                "type": "判断",
                "question": "在 Python 中，`def` 用于定义函数。",
                "correct_answer": "对",
                "explanation": "def 是定义普通函数的关键字。",
            },
            {
                "grade_group": "大学",
                "subject": "Python",
                "type": "简答",
                "question": "什么是 Python 中的列表推导式？",
                "correct_answer": "列表推导式是一种用简洁语法根据已有可迭代对象快速生成新列表的写法，还可以带条件筛选。",
                "key_points": [["简洁语法", "快速生成"], ["新列表"], ["可迭代对象"], ["条件筛选", "过滤"]],
                "explanation": "说到“用更简洁的方式生成列表”就抓住重点了。",
            },
            {
                "grade_group": "大学",
                "subject": "Python",
                "type": "单选",
                "question": "读取字典 `student = {'name': 'Tom'}` 中 name 对应的值，下面哪个写法正确？",
                "options": ["student.name", "student['name']", "student(name)", "student->name"],
                "correct_answer": "student['name']",
                "explanation": "Python 字典通过方括号和键访问对应值。",
            },
            {
                "grade_group": "大学",
                "subject": "经济学",
                "type": "简答",
                "question": "供求关系如何影响价格？",
                "correct_answer": "一般来说，需求增加或供给减少会推动价格上升；需求减少或供给增加会促使价格下降。",
                "key_points": [["需求增加", "供给减少"], ["价格上升"], ["需求减少", "供给增加"], ["价格下降"]],
                "explanation": "把供求变化和价格方向对应起来即可。",
            },
        ]

    def _normalize_question_type(self, question_type: str | None) -> str:
        normalized = (question_type or "").strip()
        return TYPE_ALIASES.get(normalized, normalized or "简答")

    def _normalize_boolean_answer(self, value: Any) -> str:
        normalized = normalize_text(str(value))
        if normalized in {normalize_text(item) for item in TRUE_VALUES}:
            return "对"
        if normalized in {normalize_text(item) for item in FALSE_VALUES}:
            return "错"
        return "对" if str(value).strip() == "对" else "错"

    def _normalize_option_value(self, question: Question, value: Any) -> str:
        options = [str(item).strip() for item in question.get("options", []) if str(item).strip()]
        token = str(value).strip()
        if not token:
            return ""

        upper_token = token.upper()
        if options and len(token) == 1 and "A" <= upper_token <= chr(ord("A") + len(options) - 1):
            return options[ord(upper_token) - ord("A")]

        if options and token.isdigit():
            index = int(token) - 1
            if 0 <= index < len(options):
                return options[index]

        return token

    def _split_answer_tokens(self, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return [item.strip() for item in re.split(r"[、,，|/;；\n]+", str(value)) if item.strip()]

    def _parse_key_points(self, value: Any) -> list[str | list[str]]:
        raw_value = str(value or "").strip()
        if not raw_value:
            return []

        key_points: list[str | list[str]] = []
        for group in re.split(r"[;；]+", raw_value):
            candidates = [item.strip() for item in re.split(r"[/|｜]+", group) if item.strip()]
            if not candidates:
                continue
            key_points.append(candidates if len(candidates) > 1 else candidates[0])
        return key_points

    def _normalize_multi_answer(self, question: Question, answer: Any) -> list[str]:
        resolved: list[str] = []
        seen: set[str] = set()
        for token in self._split_answer_tokens(answer):
            option_value = self._normalize_option_value(question, token)
            normalized_key = self._normalize_option(option_value)
            if option_value and normalized_key not in seen:
                seen.add(normalized_key)
                resolved.append(option_value)
        return resolved

    def _prepare_question_record(self, question: Question) -> Question:
        prepared = copy.deepcopy(question)
        question_type = self._normalize_question_type(prepared.get("type"))
        prepared["type"] = question_type
        prepared["concept_tags"] = [str(item).strip() for item in prepared.get("concept_tags", []) if str(item).strip()]

        options = [str(item).strip() for item in prepared.get("options", []) if str(item).strip()]
        if question_type == "判断" and not options:
            options = ["对", "错"]
        prepared["options"] = options

        if question_type == "多选":
            prepared["correct_answer"] = self._normalize_multi_answer(prepared, prepared.get("correct_answer", []))
        elif question_type == "判断":
            prepared["correct_answer"] = self._normalize_boolean_answer(prepared.get("correct_answer", "错"))
        else:
            prepared["correct_answer"] = self._normalize_option_value(prepared, prepared.get("correct_answer", ""))

        if question_type == "判断":
            prepared["options"] = ["对", "错"]
        elif question_type == "多选":
            missing_options = [
                answer
                for answer in prepared.get("correct_answer", [])
                if answer and answer not in prepared["options"]
            ]
            prepared["options"].extend(missing_options)
        elif question_type == "单选":
            correct_answer = str(prepared.get("correct_answer") or "").strip()
            if correct_answer and correct_answer not in prepared["options"]:
                prepared["options"].append(correct_answer)

        return prepared

    def load_questions_data(self) -> list[Question]:
        raw_rows = read_csv(QUESTIONS_DATA_PATH)
        external_questions: list[Question] = []

        for row in raw_rows:
            subject = (row.get("subject") or "").strip()
            grade_value = (row.get("grade") or "").strip()
            grade_group_value = (row.get("grade_group") or "").strip()
            question = (row.get("question") or "").strip()
            question_type = self._normalize_question_type(row.get("type"))
            correct_answer = row.get("correct_answer")

            if not subject or not question or question_type not in QUESTION_TYPES or correct_answer in {None, ""}:
                continue

            grade_group = grade_group_value or self.resolve_grade_group(grade_value)
            if not grade_group or grade_group not in SUBJECTS_BY_GRADE_GROUP:
                continue

            options: list[str] = []
            for key in ("options", "option_a", "option_b", "option_c", "option_d", "option_e", "option_f"):
                value = (row.get(key) or "").strip()
                if not value:
                    continue
                if key == "options":
                    options.extend([item.strip() for item in value.split("|") if item.strip()])
                else:
                    options.append(value)

            question_record = self._prepare_question_record(
                {
                    "grade_group": grade_group,
                    "subject": subject,
                    "type": question_type,
                    "question": question,
                    "options": options,
                    "correct_answer": correct_answer,
                    "explanation": (row.get("explanation") or "").strip(),
                    "key_points": self._parse_key_points(row.get("key_points")),
                    "concept_tags": self._split_answer_tokens(row.get("concept_tags")),
                }
            )
            external_questions.append(question_record)

        return external_questions

    def save_questions_data(self) -> None:
        return

    def get_practice_catalog(self) -> dict[str, Any]:
        subjects_by_grade = {
            grade: SUBJECTS_BY_GRADE_GROUP[GRADE_GROUPS[grade]]
            for grade in GRADE_LEVELS
        }
        return {
            "grades": GRADE_LEVELS,
            "subjects_by_grade": subjects_by_grade,
            "question_types": QUESTION_TYPES,
        }

    def resolve_grade_group(self, level: str | None) -> str | None:
        if not level:
            return None
        if level in GRADE_GROUPS:
            return GRADE_GROUPS[level]
        if level in LEGACY_DIFFICULTY_TO_GRADE_GROUP:
            return LEGACY_DIFFICULTY_TO_GRADE_GROUP[level]
        return None

    def _question_pool(
        self,
        subject: str,
        grade: str | None,
        question_types: list[str] | None = None,
        concept: str | None = None,
    ) -> list[Question]:
        grade_group = self.resolve_grade_group(grade)
        normalized_types = {self._normalize_question_type(item) for item in question_types or [] if item}
        normalized_concept = normalize_text(concept or "")
        question_bank = self.builtin_questions + self.questions_data

        pool = [
            question
            for question in question_bank
            if question["subject"] == subject and (not grade_group or question["grade_group"] == grade_group)
        ]
        if normalized_types:
            pool = [question for question in pool if question["type"] in normalized_types]
        if normalized_concept:
            pool = [question for question in pool if self._question_matches_concept(question, normalized_concept)]
        return pool

    def _question_matches_concept(self, question: Question, normalized_concept: str) -> bool:
        if not normalized_concept:
            return True

        for tag in question.get("concept_tags", []):
            normalized_tag = normalize_text(str(tag))
            if normalized_tag and (normalized_tag in normalized_concept or normalized_concept in normalized_tag):
                return True

        haystacks = [
            str(question.get("question", "")),
            str(question.get("explanation", "")),
            str(question.get("correct_answer", "")),
        ]
        return any(normalized_concept in normalize_text(text) for text in haystacks if text)

    def _infer_question_metadata(self, question_text: str) -> tuple[str, str]:
        for question in self.builtin_questions + self.questions_data:
            if question.get("question") == question_text:
                inferred_subject = question.get("subject", "未知")
                inferred_grade_group = question.get("grade_group")
                inferred_grade = next(
                    (grade for grade, group in GRADE_GROUPS.items() if group == inferred_grade_group),
                    "未知",
                )
                return inferred_subject, inferred_grade
        if "勾股定理" in question_text:
            return "数学", "初一"
        if "牛顿第一定律" in question_text:
            return "物理", "初二"
        if "Python" in question_text or "列表推导式" in question_text:
            return "Python", "大学"
        return "未知", "未知"

    def _suggest_wrong_question_repair(self, row: Any) -> dict[str, str] | None:
        question = str(row["question"] or "")
        correct_answer = str(row["correct_answer"] or "")
        subject = str(row["subject"] or "")
        grade = str(row["grade"] or "")
        question_type = str(row["question_type"] or "")

        if subject == "Python" and "list" in correct_answer and "dict" in correct_answer and "tuple" in correct_answer:
            repaired_grade = grade if grade and "?" not in grade else "高一"
            return {
                "question": "下面哪些是 Python 的常见内置数据类型？",
                "correct_answer": "list、dict、tuple",
                "subject": "Python",
                "grade": repaired_grade,
                "question_type": "多选",
            }

        needs_repair = any("?" in value for value in (question, grade, question_type))
        if not needs_repair:
            return None

        inferred_subject, inferred_grade = self._infer_question_metadata(question)
        repaired_subject = subject if subject and "?" not in subject else inferred_subject
        repaired_grade = grade if grade and "?" not in grade else inferred_grade
        repaired_type = question_type if question_type and "?" not in question_type else "简答"

        if repaired_subject == "未知" and repaired_grade == "未知" and repaired_type == "简答":
            return None

        return {
            "question": question,
            "correct_answer": correct_answer,
            "subject": repaired_subject,
            "grade": repaired_grade,
            "question_type": repaired_type,
        }

    def _repair_wrong_question_records(self) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        rows = cursor.execute(
            """
            SELECT id, question, correct_answer, subject, grade, question_type
            FROM wrong_questions
            WHERE question LIKE '%?%' OR COALESCE(subject, '') LIKE '%?%' OR COALESCE(grade, '') LIKE '%?%' OR COALESCE(question_type, '') LIKE '%?%'
            """
        ).fetchall()

        updated = False
        for row in rows:
            repaired = self._suggest_wrong_question_repair(row)
            if not repaired:
                continue
            cursor.execute(
                """
                UPDATE wrong_questions
                SET question = ?, correct_answer = ?, subject = ?, grade = ?, question_type = ?, difficulty = COALESCE(NULLIF(difficulty, ''), ?)
                WHERE id = ?
                """,
                (
                    repaired["question"],
                    repaired["correct_answer"],
                    repaired["subject"],
                    repaired["grade"],
                    repaired["question_type"],
                    repaired["grade"],
                    row["id"],
                ),
            )
            updated = True

        if updated:
            conn.commit()
        conn.close()

    def _find_question_record(
        self,
        question_text: str,
        subject: str | None = None,
        grade: str | None = None,
        question_type: str | None = None,
        correct_answer: str | None = None,
    ) -> Question | None:
        normalized_type = self._normalize_question_type(question_type)
        grade_group = self.resolve_grade_group(grade)
        best_match: Question | None = None
        best_score = -1

        for question in self.builtin_questions + self.questions_data:
            if question.get("question") != question_text:
                continue

            score = 0
            if subject and question.get("subject") == subject:
                score += 3
            if grade_group and question.get("grade_group") == grade_group:
                score += 3
            if normalized_type and question.get("type") == normalized_type:
                score += 2
            if correct_answer and self._serialize_user_answer(question.get("correct_answer")) == self._serialize_user_answer(correct_answer):
                score += 3

            if score > best_score:
                best_score = score
                best_match = question

        return copy.deepcopy(best_match) if best_match else None

    def _rehydrate_wrong_question(self, row: Any) -> Question:
        inferred_subject, inferred_grade = self._infer_question_metadata(row["question"])
        subject = inferred_subject if row["subject"] in {None, "", "未知"} else row["subject"]
        grade = inferred_grade if (row["grade"] or row["difficulty"] or "未知") in {"", "未知"} else (row["grade"] or row["difficulty"])
        question_type = self._normalize_question_type(row["question_type"] or "简答")

        matched = self._find_question_record(
            question_text=str(row["question"] or ""),
            subject=subject,
            grade=grade,
            question_type=question_type,
            correct_answer=str(row["correct_answer"] or ""),
        )
        if matched:
            matched["subject"] = subject
            matched["grade"] = grade
            matched["difficulty"] = grade
            return matched

        fallback = {
            "question": str(row["question"] or ""),
            "subject": subject,
            "grade": grade,
            "difficulty": grade,
            "type": question_type,
            "correct_answer": str(row["correct_answer"] or ""),
            "explanation": "",
            "options": ["对", "错"] if question_type == "判断" else [],
        }
        return self._prepare_question_record(fallback)

    def _shuffle_question_options(self, question: Question) -> None:
        if question.get("type") not in {"单选", "多选", "判断"}:
            return
        options = question.get("options", [])
        if len(options) <= 1:
            return
        random.shuffle(options)
        question["options"] = options

    def _build_question_batch(self, pool: list[Question], count: int) -> list[Question]:
        questions: list[Question] = []
        round_number = 0

        while len(questions) < count:
            round_number += 1
            batch = copy.deepcopy(pool)
            random.shuffle(batch)
            for question in batch:
                question["practice_round"] = round_number
                self._shuffle_question_options(question)
                questions.append(question)
                if len(questions) >= count:
                    break

        return questions

    def generate_questions(
        self,
        subject: str,
        grade: str,
        count: int,
        question_types: list[str] | None = None,
        concept: str | None = None,
    ) -> list[Question]:
        pool = self._question_pool(subject, grade, question_types, concept=concept)
        used_fallback = False
        if not pool and question_types:
            pool = self._question_pool(subject, grade, None, concept=concept)
            used_fallback = bool(pool)
        if not pool or count <= 0:
            return []

        questions = self._build_question_batch(pool, count)
        for index, question in enumerate(questions, start=1):
            question["id"] = index
            question["subject"] = subject
            question["grade"] = grade
            question["difficulty"] = grade
            question["used_type_fallback"] = used_fallback
            question["concept"] = concept or ""

        return questions

    def _normalize_option(self, value: str) -> str:
        return re.sub(r"[\s,.!?;:()（）【】\[\]\"'“”‘’`]", "", normalize_text(value))

    def _is_numeric(self, value: str) -> bool:
        return bool(re.fullmatch(r"-?\d+(\.\d+)?", value.strip()))

    def _grade_objective_answer(self, question: Question, user_answer: Any) -> tuple[bool, int, str]:
        question_type = question.get("type", "简答")

        if question_type == "多选":
            expected_answers = self._normalize_multi_answer(question, question["correct_answer"])
            actual_answers = self._normalize_multi_answer(question, user_answer)
            expected_set = {self._normalize_option(item) for item in expected_answers}
            actual_set = {self._normalize_option(item) for item in actual_answers}

            if actual_set == expected_set:
                return True, 100, ""

            matched = len(expected_set & actual_set)
            score = int(round((matched / max(len(expected_set), 1)) * 100))
            missing = [item for item in expected_answers if self._normalize_option(item) not in actual_set]
            extra = [item for item in actual_answers if self._normalize_option(item) not in expected_set]

            feedback_parts: list[str] = []
            if missing:
                feedback_parts.append(f"漏选：{'、'.join(missing)}")
            if extra:
                feedback_parts.append(f"多选：{'、'.join(extra)}")

            return False, min(score, 99), "；".join(feedback_parts)

        expected = question["correct_answer"]
        if question_type == "判断":
            expected_text = self._normalize_boolean_answer(expected)
            actual_text = self._normalize_boolean_answer(user_answer)
        else:
            expected_text = str(self._normalize_option_value(question, expected)).strip()
            actual_text = str(self._normalize_option_value(question, user_answer)).strip()

        if self._normalize_option(actual_text) == self._normalize_option(expected_text):
            return True, 100, ""

        if self._is_numeric(actual_text) and self._is_numeric(expected_text):
            if abs(float(actual_text) - float(expected_text)) < 1e-6:
                return True, 100, ""

        return False, 0, ""

    def _match_keyword_group(self, answer: str, keyword_group: Any) -> bool:
        candidates = keyword_group if isinstance(keyword_group, list) else [keyword_group]
        normalized_answer = normalize_text(answer)
        return any(normalize_text(candidate) in normalized_answer for candidate in candidates)

    def _grade_short_answer(self, question: Question, user_answer: str) -> tuple[bool, int, list[str]]:
        key_points = question.get("key_points") or []
        similarity = calculate_similarity(user_answer, str(question["correct_answer"]))

        matched_points = 0
        missing_points: list[str] = []
        for point in key_points:
            if self._match_keyword_group(user_answer, point):
                matched_points += 1
            else:
                if isinstance(point, list):
                    missing_points.append(str(point[0]))
                else:
                    missing_points.append(str(point))

        keyword_coverage = (matched_points / len(key_points)) if key_points else 0.0
        normalized_user = normalize_text(user_answer)
        normalized_correct = normalize_text(str(question["correct_answer"]))
        length_ratio = min(len(normalized_user), len(normalized_correct)) / max(len(normalized_correct), 1)
        score = int(round((keyword_coverage * 0.65 + similarity * 0.25 + length_ratio * 0.10) * 100))

        is_correct = False
        if key_points:
            if keyword_coverage >= 0.75:
                is_correct = True
            elif keyword_coverage >= 0.6 and similarity >= 0.25:
                is_correct = True
            elif keyword_coverage >= 0.5 and similarity >= 0.18 and len(normalized_user) >= 12:
                is_correct = True
            elif keyword_coverage >= 0.5 and len(normalized_user) >= 18:
                is_correct = True
        elif similarity >= 0.72:
            is_correct = True

        if is_correct and score < 65:
            score = 65
        return is_correct, min(score, 100), missing_points

    def _serialize_user_answer(self, user_answer: Any) -> str:
        if isinstance(user_answer, list):
            return "、".join(str(item).strip() for item in user_answer if str(item).strip())
        return str(user_answer).strip()

    def grade_answer(self, question: Question, user_answer: Any) -> dict[str, Any]:
        question_payload = self._prepare_question_record(question)
        user_answer_text = self._serialize_user_answer(user_answer)
        result = {
            "question": question_payload["question"],
            "user_answer": user_answer_text,
            "correct_answer": self._serialize_user_answer(question_payload["correct_answer"]),
            "is_correct": False,
            "score": 0,
            "explanation": question_payload.get("explanation", ""),
            "improvement": "",
        }

        question_type = question_payload.get("type", "简答")
        if question_type in {"单选", "多选", "判断"}:
            is_correct, score, feedback = self._grade_objective_answer(question_payload, user_answer)
            result["is_correct"] = is_correct
            result["score"] = score
            if not is_correct:
                result["improvement"] = feedback or "这道题适合再对照选项和知识点复习一遍。"
                self.record_wrong_question(question_payload, user_answer_text)
            return result

        is_correct, score, missing_points = self._grade_short_answer(question_payload, user_answer_text)
        result["is_correct"] = is_correct
        result["score"] = score

        if not is_correct:
            if missing_points:
                result["improvement"] = f"答案已经接近了，再补上这些关键点会更完整：{'、'.join(missing_points[:3])}。"
            else:
                result["improvement"] = "答案方向基本对，但还可以再把关键概念说完整一些。"
            self.record_wrong_question(question_payload, user_answer_text)
        elif score < 90:
            result["improvement"] = "核心意思已经答到了，如果想拿更高分，可以把关键词写得更完整。"

        return result

    def record_wrong_question(self, question: Question, user_answer: str) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        question_type = self._normalize_question_type(question.get("type"))

        cursor.execute(
            """
            SELECT id
            FROM wrong_questions
            WHERE question = ? AND correct_answer = ? AND subject = ? AND COALESCE(grade, '') = ? AND notebook_status = 'active'
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                question["question"],
                self._serialize_user_answer(question["correct_answer"]),
                question.get("subject", "未知"),
                question.get("grade", question.get("difficulty", "未知")),
            ),
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE wrong_questions
                SET user_answer = ?, difficulty = ?, grade = ?, question_type = ?, timestamp = ?
                WHERE id = ?
                """,
                (
                    user_answer,
                    question.get("difficulty", question.get("grade", "未知")),
                    question.get("grade", question.get("difficulty", "未知")),
                    question_type,
                    get_current_datetime(),
                    existing["id"],
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO wrong_questions (
                    question, user_answer, correct_answer, subject, difficulty, grade,
                    question_type, timestamp, notebook_status, review_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', 0)
                """,
                (
                    question["question"],
                    user_answer,
                    self._serialize_user_answer(question["correct_answer"]),
                    question.get("subject", "未知"),
                    question.get("difficulty", question.get("grade", "未知")),
                    question.get("grade", question.get("difficulty", "未知")),
                    question_type,
                    get_current_datetime(),
                ),
            )

        conn.commit()
        conn.close()

    def get_wrong_questions(self, status: str | None = None) -> list[Question]:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM wrong_questions"
        params: list[Any] = []
        if status:
            query += " WHERE notebook_status = ?"
            params.append(status)
        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        wrong_questions: list[Question] = []
        for row in rows:
            payload = self._rehydrate_wrong_question(row)
            wrong_questions.append(
                {
                    "id": row["id"],
                    "question": row["question"],
                    "user_answer": row["user_answer"],
                    "correct_answer": row["correct_answer"],
                    "subject": payload.get("subject", "未知"),
                    "difficulty": row["difficulty"],
                    "grade": payload.get("grade", row["grade"] or row["difficulty"] or "未知"),
                    "question_type": payload.get("type", self._normalize_question_type(row["question_type"] or "简答")),
                    "type": payload.get("type", self._normalize_question_type(row["question_type"] or "简答")),
                    "options": payload.get("options", []),
                    "explanation": payload.get("explanation", ""),
                    "timestamp": row["timestamp"],
                    "notebook_status": row["notebook_status"] or "active",
                    "review_count": row["review_count"] or 0,
                    "last_reviewed_at": row["last_reviewed_at"],
                    "mastered_at": row["mastered_at"],
                }
            )
        return wrong_questions

    def retry_wrong_question(self, question_id: int, user_answer: Any) -> dict[str, Any] | None:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wrong_questions WHERE id = ?", (question_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        question_payload = self._rehydrate_wrong_question(row)
        result = self.grade_answer(question_payload, user_answer)
        now = get_current_datetime()
        serialized_answer = self._serialize_user_answer(user_answer)

        if result["is_correct"]:
            cursor.execute(
                """
                UPDATE wrong_questions
                SET user_answer = ?, review_count = COALESCE(review_count, 0) + 1,
                    notebook_status = 'mastered', mastered_at = ?, last_reviewed_at = ?, timestamp = ?
                WHERE id = ?
                """,
                (serialized_answer, now, now, now, question_id),
            )
        else:
            cursor.execute(
                """
                UPDATE wrong_questions
                SET user_answer = ?, last_reviewed_at = ?, timestamp = ?
                WHERE id = ?
                """,
                (serialized_answer, now, now, question_id),
            )

        conn.commit()
        conn.close()
        result["auto_mastered"] = result["is_correct"]
        return result

    def update_wrong_question(self, question_id: int, action: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = get_current_datetime()

        if action == "mastered":
            cursor.execute(
                """
                UPDATE wrong_questions
                SET notebook_status = 'mastered', mastered_at = ?, last_reviewed_at = ?
                WHERE id = ?
                """,
                (now, now, question_id),
            )
        elif action == "reactivate":
            cursor.execute(
                """
                UPDATE wrong_questions
                SET notebook_status = 'active', mastered_at = NULL, last_reviewed_at = ?
                WHERE id = ?
                """,
                (now, question_id),
            )
        elif action == "review":
            cursor.execute(
                """
                UPDATE wrong_questions
                SET review_count = COALESCE(review_count, 0) + 1, last_reviewed_at = ?
                WHERE id = ?
                """,
                (now, question_id),
            )
        elif action == "delete":
            cursor.execute("DELETE FROM wrong_questions WHERE id = ?", (question_id,))
        else:
            conn.close()
            return False

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def get_wrong_book_summary(self) -> dict[str, Any]:
        wrong_questions = self.get_wrong_questions()
        active = [item for item in wrong_questions if item["notebook_status"] == "active"]
        mastered = [item for item in wrong_questions if item["notebook_status"] == "mastered"]

        subject_counts: dict[str, int] = {}
        for item in active:
            subject_counts[item["subject"]] = subject_counts.get(item["subject"], 0) + 1

        return {
            "total": len(wrong_questions),
            "active": len(active),
            "mastered": len(mastered),
            "total_reviews": sum(item.get("review_count", 0) for item in wrong_questions),
            "top_subjects": sorted(
                [{"subject": subject, "count": count} for subject, count in subject_counts.items()],
                key=lambda item: item["count"],
                reverse=True,
            )[:5],
        }

    def get_weak_points(self) -> dict[str, int]:
        summary: dict[str, int] = {}
        for item in self.get_wrong_questions(status="active"):
            summary[item["subject"]] = summary.get(item["subject"], 0) + 1
        return summary


def generate_questions(
    subject: str,
    difficulty: str,
    count: int,
    question_types: list[str] | None = None,
    concept: str | None = None,
) -> list[Question]:
    practice_system = PracticeSystem()
    return practice_system.generate_questions(subject, difficulty, count, question_types=question_types, concept=concept)


def grade_answer(question: Question, user_answer: Any) -> dict[str, Any]:
    practice_system = PracticeSystem()
    return practice_system.grade_answer(question, user_answer)


def get_wrong_questions(status: str | None = None) -> list[Question]:
    practice_system = PracticeSystem()
    return practice_system.get_wrong_questions(status=status)


def update_wrong_question(question_id: int, action: str) -> bool:
    practice_system = PracticeSystem()
    return practice_system.update_wrong_question(question_id, action)


def retry_wrong_question(question_id: int, user_answer: Any) -> dict[str, Any] | None:
    practice_system = PracticeSystem()
    return practice_system.retry_wrong_question(question_id, user_answer)


def get_wrong_book_summary() -> dict[str, Any]:
    practice_system = PracticeSystem()
    return practice_system.get_wrong_book_summary()


def get_practice_catalog() -> dict[str, Any]:
    practice_system = PracticeSystem()
    return practice_system.get_practice_catalog()
