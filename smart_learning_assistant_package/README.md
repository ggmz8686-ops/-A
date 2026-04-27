# 智能学习助手 (Smart Learning Assistant)

一个功能强大的Python智能学习助手，支持知识问答、题目练习与批改、学习规划与进度追踪、资料整理与总结、语言学习专项以及工具集等功能。

## 项目结构

```
smart_learning_assistant/
├── main.py                # 主入口
├── src/
│   ├── qa.py               # 知识问答
│   ├── practice.py         # 练习批改
│   ├── plan.py             # 学习规划
│   ├── summary.py          # 资料整理
│   ├── language.py         # 语言学习
│   ├── tools.py            # 工具集
│   ├── config.py           # 配置（路径、参数）
│   └── utils.py            # 通用工具函数
├── data/                   # 示例数据（JSONL/CSV）
│   ├── qa_data.jsonl
│   ├── questions.csv
│   └── vocab.csv
├── tests/                  # 单元测试
├── requirements.txt        # 依赖清单
└── README.md               # 安装/运行/使用说明
```

## 功能模块

### 1. 知识问答模块 (qa.py)
- 支持自然语言提问（知识点、概念、公式、原理）
- 内置基础学科知识库（数学/英语/物理/编程）
- 输出：通俗讲解、步骤拆解、易错点提示
- 接口：`ask_question(question: str) -> str`

### 2. 题目练习与批改 (practice.py)
- 按学科/难度/题型生成选择题、填空题、简答题
- 自动批改：客观题判分，主观题给评分与改进建议
- 错题本：自动收录、错题重练、薄弱点统计
- 接口：
  - `generate_questions(subject, difficulty, count) -> list`
  - `grade_answer(question, user_answer) -> dict`
  - `get_wrong_questions() -> list`

### 3. 学习规划与进度 (plan.py)
- 制定日/周/月学习计划（目标、时长、科目分配）
- 打卡与进度追踪，生成进度报表
- 考前冲刺计划与重点清单
- 接口：
  - `make_study_plan(goal, days, subjects) -> dict`
  - `log_progress(task_id, status) -> bool`
  - `get_progress_report() -> str`

### 4. 资料整理与总结 (summary.py)
- 文本摘要、重点提炼
- 生成结构化思维导图（Markdown格式）
- 章节知识点归纳、复习提纲
- 接口：
  - `summarize_text(text, max_length) -> str`
  - `generate_mindmap(topic, content) -> str`
  - `outline_chapter(chapter, content) -> str`

### 5. 语言学习专项 (language.py)
- 单词记忆（艾宾浩斯）、例句、发音提示
- 作文批改：语法纠错、润色、评分
- 中英互译
- 接口：
  - `vocab_train(word_list, mode) -> dict`
  - `correct_essay(text) -> dict`
  - `translate_text(text, src, tgt) -> str`

### 6. 工具集 (tools.py)
- 公式/定理速查
- 计算器、单位换算、进制转换
- 课程表、待办、倒计时
- 接口：`tool_query(tool_name, params) -> any`

## 安装与运行

### 环境要求
- Python 3.10+

### 安装步骤
1. 克隆或下载项目到本地
2. 进入项目目录

### 运行方式
在项目根目录下执行：

```bash
python main.py
```

然后按照命令行菜单的提示选择相应功能。

## 使用示例

### 1. 知识问答
```python
from src.qa import ask_question

question = "什么是质数？"
answer = ask_question(question)
print(answer)
```

### 2. 题目练习
```python
from src.practice import generate_questions, grade_answer

# 生成5道中等难度的数学题
questions = generate_questions("数学", "中等", 5)

# 批改答案
result = grade_answer(questions[0], "正确答案")
print(result)
```

### 3. 学习规划
```python
from src.plan import make_study_plan, log_progress, get_progress_report

# 制定学习计划
plan = make_study_plan("期末考试", 30, ["数学", "英语", "物理"])

# 记录进度
log_progress(1, "完成")

# 获取进度报告
report = get_progress_report()
print(report)
```

### 4. 资料整理
```python
from src.summary import summarize_text, generate_mindmap, outline_chapter

# 文本摘要
text = "这里是一段长文本..."
summary = summarize_text(text, 100)
print(summary)

# 生成思维导图
mindmap = generate_mindmap("Python编程", text)
print(mindmap)
```

### 5. 语言学习
```python
from src.language import vocab_train, correct_essay, translate_text

# 单词记忆
words = ["apple", "banana", "cat"]
training = vocab_train(words, "daily")
print(training)

# 作文批改
essay = "I is a student."
correction = correct_essay(essay)
print(correction)

# 中英互译
translation = translate_text("Hello, world!", "en", "zh")
print(translation)
```

### 6. 工具集
```python
from src.tools import tool_query

# 计算
result = tool_query("calculator", {"expression": "2 + 3 * 4"})
print(result)

# 单位换算
result = tool_query("unit_conversion", {"value": 100, "from_unit": "cm", "to_unit": "m"})
print(result)
```

## 数据说明

项目包含以下示例数据：
- `data/qa_data.jsonl`：知识问答数据，包含270+条Q&A对
- `data/questions.csv`：题目数据，包含数学、英语、物理、编程四个学科的题目
- `data/vocab.csv`：词汇数据，包含120+个常用单词

## 注意事项

1. 本项目为纯Python实现，无外部依赖
2. 所有功能均在本地运行，不依赖网络
3. 数据存储使用SQLite和本地文件
4. 代码符合Python规范，包含完整的类型提示和中文注释

## 扩展建议

1. 可以通过添加更多数据来扩展知识库和题目库
2. 可以实现网络接口，支持远程访问
3. 可以添加机器学习模型，提高问答和批改的准确性
4. 可以开发GUI界面，提升用户体验
