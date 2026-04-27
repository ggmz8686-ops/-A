import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.qa import ask_question
from src.practice import generate_questions, grade_answer, get_wrong_questions
from src.plan import make_study_plan, log_progress, get_progress_report
from src.summary import summarize_text, generate_mindmap, outline_chapter
from src.language import vocab_train, correct_essay, translate_text
from src.tools import tool_query
from src.utils import init_database

def test_qa():
    """测试知识问答模块"""
    print("\n=== 测试知识问答模块 ===")
    test_questions = [
        "什么是质数？",
        "如何学习Python？",
        "什么是牛顿第一定律？"
    ]
    
    for question in test_questions:
        print(f"问题: {question}")
        answer = ask_question(question)
        print(f"回答: {answer[:100]}...")  # 只打印前100个字符
        print()

def test_practice():
    """测试题目练习与批改模块"""
    print("\n=== 测试题目练习与批改模块 ===")
    
    # 生成题目
    print("生成数学题目:")
    questions = generate_questions("数学", "简单", 2)
    for i, q in enumerate(questions):
        print(f"题目 {i+1}: {q['question']}")
    
    # 批改答案
    if questions:
        print("\n批改答案:")
        result = grade_answer(questions[0], "7")  # 假设第一个题目是关于质数的
        print(f"批改结果: {result}")
    
    # 获取错题
    wrong_questions = get_wrong_questions()
    print(f"\n错题数量: {len(wrong_questions)}")

def test_plan():
    """测试学习规划与进度模块"""
    print("\n=== 测试学习规划与进度模块 ===")
    
    # 制定学习计划
    plan = make_study_plan("期末考试", 7, ["数学", "英语", "物理"])
    print(f"学习计划: {plan['plan_id']}")
    print(f"目标: {plan['goal']}")
    print(f"天数: {plan['days']}")
    print(f"科目: {plan['subjects']}")
    
    # 记录进度
    task_id = plan['tasks'][0]['task_id'] if plan['tasks'] else 1
    success = log_progress(task_id, "完成")
    print(f"\n记录进度: {'成功' if success else '失败'}")
    
    # 获取进度报告
    report = get_progress_report()
    print("\n进度报告:")
    print(report[:200] + "...")  # 只打印前200个字符

def test_summary():
    """测试资料整理与总结模块"""
    print("\n=== 测试资料整理与总结模块 ===")
    
    test_text = "Python是一种广泛使用的高级编程语言，它具有简单易学的语法，强大的库支持，以及广泛的应用场景。Python可以用于Web开发、数据分析、人工智能、自动化测试等多个领域。学习Python可以帮助你快速开发各种应用程序，提高工作效率。"
    
    # 文本摘要
    summary = summarize_text(test_text, 50)
    print(f"文本摘要: {summary}")
    
    # 生成思维导图
    mindmap = generate_mindmap("Python编程", test_text)
    print("\n思维导图:")
    print(mindmap)
    
    # 章节大纲
    outline = outline_chapter("Python基础", test_text)
    print("\n章节大纲:")
    print(outline)

def test_language():
    """测试语言学习专项模块"""
    print("\n=== 测试语言学习专项模块 ===")
    
    # 单词记忆
    words = ["apple", "banana", "cat"]
    training = vocab_train(words, "daily")
    print(f"单词记忆: {training}")
    
    # 作文批改
    essay = "I is a student. I like play football."
    correction = correct_essay(essay)
    print("\n作文批改:")
    print(f"原文: {essay}")
    print(f"修改: {correction['corrected_text']}")
    print(f"错误: {correction['errors']}")
    
    # 中英互译
    translation = translate_text("Hello, world!", "en", "zh")
    print(f"\n中英互译: {translation}")

def test_tools():
    """测试工具集模块"""
    print("\n=== 测试工具集模块 ===")
    
    # 计算器
    calc_result = tool_query("calculator", {"expression": "2 + 3 * 4"})
    print(f"计算结果: 2 + 3 * 4 = {calc_result}")
    
    # 单位换算
    unit_result = tool_query("unit_conversion", {"value": 100, "from_unit": "cm", "to_unit": "m"})
    print(f"单位换算: 100 cm = {unit_result} m")
    
    # 进制转换
    base_result = tool_query("base_conversion", {"number": 10, "from_base": 10, "to_base": 2})
    print(f"进制转换: 10 (十进制) = {base_result} (二进制)")

if __name__ == "__main__":
    print("开始测试智能学习助手项目...")
    
    # 初始化数据库
    try:
        init_database()
        print("数据库初始化成功")
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
    
    test_qa()
    test_practice()
    test_plan()
    test_summary()
    test_language()
    test_tools()
    
    print("\n测试完成！")
