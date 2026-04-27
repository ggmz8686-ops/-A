import os
from typing import Any


PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

QA_DATA_PATH = os.path.join(DATA_DIR, "qa_data.jsonl")
QUESTIONS_DATA_PATH = os.path.join(DATA_DIR, "questions.csv")
VOCAB_DATA_PATH = os.path.join(DATA_DIR, "vocab.csv")
DB_PATH = os.path.join(DATA_DIR, "learning_assistant.db")

DEFAULT_STUDY_HOURS_PER_DAY = 2
DEFAULT_SUBJECTS = ["语文", "数学", "英语", "科学"]

VOCAB_REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]
MAX_CALCULATOR_INPUT_LENGTH = 100
MAX_SUMMARY_LENGTH = 500
MAX_MINDMAP_DEPTH = 3

QUESTION_TYPES = ["单选", "多选", "判断", "简答"]
DIFFICULTY_LEVELS = ["简单", "中等", "困难"]

GRADE_LEVELS = [
    "小学一年级",
    "小学二年级",
    "小学三年级",
    "小学四年级",
    "小学五年级",
    "小学六年级",
    "初一",
    "初二",
    "初三",
    "高一",
    "高二",
    "高三",
    "大学",
]

GRADE_GROUPS = {
    "小学一年级": "小学低年级",
    "小学二年级": "小学低年级",
    "小学三年级": "小学中年级",
    "小学四年级": "小学中年级",
    "小学五年级": "小学高年级",
    "小学六年级": "小学高年级",
    "初一": "初中",
    "初二": "初中",
    "初三": "初中",
    "高一": "高中",
    "高二": "高中",
    "高三": "高中",
    "大学": "大学",
}

LEGACY_DIFFICULTY_TO_GRADE_GROUP = {
    "简单": "小学高年级",
    "中等": "初中",
    "困难": "高中",
}

SUBJECTS_BY_GRADE_GROUP = {
    "小学低年级": ["语文", "数学"],
    "小学中年级": ["语文", "数学", "英语", "科学"],
    "小学高年级": ["语文", "数学", "英语", "科学"],
    "初中": ["语文", "数学", "英语", "物理", "化学", "生物", "历史", "地理", "政治"],
    "高中": ["语文", "数学", "英语", "物理", "化学", "生物", "历史", "地理", "政治", "Python"],
    "大学": ["高等数学", "大学英语", "计算机基础", "程序设计", "Python", "经济学"],
}

CONFIG: dict[str, Any] = {
    "project_root": PROJECT_ROOT,
    "data_dir": DATA_DIR,
    "qa_data_path": QA_DATA_PATH,
    "questions_data_path": QUESTIONS_DATA_PATH,
    "vocab_data_path": VOCAB_DATA_PATH,
    "db_path": DB_PATH,
    "default_study_hours_per_day": DEFAULT_STUDY_HOURS_PER_DAY,
    "default_subjects": DEFAULT_SUBJECTS,
    "vocab_review_intervals": VOCAB_REVIEW_INTERVALS,
    "max_calculator_input_length": MAX_CALCULATOR_INPUT_LENGTH,
    "max_summary_length": MAX_SUMMARY_LENGTH,
    "max_mindmap_depth": MAX_MINDMAP_DEPTH,
    "question_types": QUESTION_TYPES,
    "difficulty_levels": DIFFICULTY_LEVELS,
    "grade_levels": GRADE_LEVELS,
    "grade_groups": GRADE_GROUPS,
    "subjects_by_grade_group": SUBJECTS_BY_GRADE_GROUP,
}
