# 主入口模块
import sys
from typing import Optional

from src.qa import ask_question
from src.practice import generate_questions, grade_answer, get_wrong_questions
from src.plan import make_study_plan, log_progress, get_progress_report
from src.summary import summarize_text, generate_mindmap, outline_chapter
from src.language import vocab_train, correct_essay, translate_text
from src.tools import tool_query
from src.utils import init_database


def print_menu():
    """
    打印主菜单
    """
    print("=" * 60)
    print("智能学习助手")
    print("=" * 60)
    print("1. 知识问答")
    print("2. 题目练习与批改")
    print("3. 学习规划与进度")
    print("4. 资料整理与总结")
    print("5. 语言学习专项")
    print("6. 工具集")
    print("0. 退出")
    print("=" * 60)


def handle_qa():
    """
    处理知识问答
    """
    print("\n知识问答模块")
    print("-" * 40)
    
    while True:
        question = input("请输入问题（输入 'q' 退出）: ")
        if question.lower() == 'q':
            break
        
        try:
            answer = ask_question(question)
            print("\n回答:")
            print(answer)
            print("-" * 40)
        except Exception as e:
            print(f"错误: {str(e)}")


def handle_practice():
    """
    处理题目练习与批改
    """
    print("\n题目练习与批改模块")
    print("-" * 40)
    
    while True:
        print("1. 生成题目")
        print("2. 批改答案")
        print("3. 查看错题本")
        print("0. 返回主菜单")
        choice = input("请选择: ")
        
        if choice == '0':
            break
        elif choice == '1':
            # 生成题目
            subject = input("请输入学科（数学/英语/物理/编程）: ")
            difficulty = input("请输入难度（简单/中等/困难）: ")
            count = input("请输入题目数量: ")
            
            try:
                count = int(count)
                questions = generate_questions(subject, difficulty, count)
                
                if questions:
                    print("\n生成的题目:")
                    for i, q in enumerate(questions, 1):
                        print(f"\n{i}. {q['question']}")
                        if 'options' in q:
                            for j, option in enumerate(q['options'], 1):
                                print(f"   {j}. {option}")
                else:
                    print("无法生成题目，请检查输入参数")
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '2':
            # 批改答案
            question = input("请输入题目: ")
            user_answer = input("请输入答案: ")
            
            try:
                result = grade_answer({'question': question, 'correct_answer': '正确答案', 'type': '简答题'}, user_answer)
                print("\n批改结果:")
                print(f"得分: {result['score']}")
                print(f"是否正确: {'是' if result['is_correct'] else '否'}")
                if result['explanation']:
                    print(f"解析: {result['explanation']}")
                if result['improvement']:
                    print(f"改进建议: {result['improvement']}")
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '3':
            # 查看错题本
            try:
                wrong_questions = get_wrong_questions()
                if wrong_questions:
                    print("\n错题本:")
                    for i, q in enumerate(wrong_questions, 1):
                        print(f"\n{i}. {q['question']}")
                        print(f"   你的答案: {q['user_answer']}")
                        print(f"   正确答案: {q['correct_answer']}")
                        print(f"   学科: {q['subject']}")
                        print(f"   难度: {q['difficulty']}")
                        print(f"   类型: {q['question_type']}")
                        print(f"   时间: {q['timestamp']}")
                else:
                    print("错题本为空")
            except Exception as e:
                print(f"错误: {str(e)}")
        else:
            print("无效选择")
        print("-" * 40)


def handle_plan():
    """
    处理学习规划与进度
    """
    print("\n学习规划与进度模块")
    print("-" * 40)
    
    while True:
        print("1. 制定学习计划")
        print("2. 记录进度")
        print("3. 获取进度报表")
        print("0. 返回主菜单")
        choice = input("请选择: ")
        
        if choice == '0':
            break
        elif choice == '1':
            # 制定学习计划
            goal = input("请输入学习目标: ")
            days = input("请输入计划天数: ")
            subjects = input("请输入学习科目（用逗号分隔）: ")
            
            try:
                days = int(days)
                subjects = [s.strip() for s in subjects.split(',')]
                plan = make_study_plan(goal, days, subjects)
                
                print("\n学习计划已生成:")
                print(f"计划ID: {plan['plan_id']}")
                print(f"目标: {plan['goal']}")
                print(f"时间范围: {plan['start_date']} 至 {plan['end_date']}")
                print(f"总天数: {plan['total_days']}")
                print(f"总学习时间: {plan['total_hours']} 小时")
                print("\n科目时间分配:")
                for subject, hours in plan['subject_hours'].items():
                    print(f"- {subject}: {hours} 小时")
                print("\n每日计划:")
                for daily in plan['daily_plans']:
                    print(f"- {daily['date']}: 学习{daily['subjects']} ({daily['hours']}小时)")
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '2':
            # 记录进度
            task_id = input("请输入任务ID: ")
            status = input("请输入状态（completed/pending/in_progress）: ")
            
            try:
                task_id = int(task_id)
                success = log_progress(task_id, status)
                if success:
                    print("进度记录成功")
                else:
                    print("进度记录失败，任务ID无效")
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '3':
            # 获取进度报表
            try:
                report = get_progress_report()
                print("\n学习进度报表:")
                print(report)
            except Exception as e:
                print(f"错误: {str(e)}")
        else:
            print("无效选择")
        print("-" * 40)


def handle_summary():
    """
    处理资料整理与总结
    """
    print("\n资料整理与总结模块")
    print("-" * 40)
    
    while True:
        print("1. 文本摘要")
        print("2. 生成思维导图")
        print("3. 章节大纲")
        print("0. 返回主菜单")
        choice = input("请选择: ")
        
        if choice == '0':
            break
        elif choice == '1':
            # 文本摘要
            text = input("请输入文本: ")
            max_length = input("请输入摘要最大长度（默认500）: ")
            
            try:
                max_length = int(max_length) if max_length else 500
                summary = summarize_text(text, max_length)
                print("\n文本摘要:")
                print(summary)
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '2':
            # 生成思维导图
            topic = input("请输入主题: ")
            content = input("请输入内容: ")
            
            try:
                mindmap = generate_mindmap(topic, content)
                print("\n思维导图:")
                print(mindmap)
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '3':
            # 章节大纲
            chapter = input("请输入章节名称: ")
            content = input("请输入章节内容: ")
            
            try:
                outline = outline_chapter(chapter, content)
                print("\n章节大纲:")
                print(outline)
            except Exception as e:
                print(f"错误: {str(e)}")
        else:
            print("无效选择")
        print("-" * 40)


def handle_language():
    """
    处理语言学习专项
    """
    print("\n语言学习专项模块")
    print("-" * 40)
    
    while True:
        print("1. 单词记忆训练")
        print("2. 作文批改")
        print("3. 中英互译")
        print("0. 返回主菜单")
        choice = input("请选择: ")
        
        if choice == '0':
            break
        elif choice == '1':
            # 单词记忆训练
            words = input("请输入单词（用逗号分隔）: ")
            mode = input("请输入训练模式（review/learn，默认review）: ")
            
            try:
                word_list = [w.strip() for w in words.split(',')]
                result = vocab_train(word_list, mode)
                print("\n训练结果:")
                print(f"模式: {result['mode']}")
                print(f"总单词数: {result['total']}")
                print(f"找到单词数: {result['found']}")
                print("\n详细结果:")
                for item in result['results']:
                    if item['status'] != 'not_found':
                        print(f"- {item['word']}: {item['meaning']}")
                        if item.get('example'):
                            print(f"  例句: {item['example']}")
                        if item.get('phonetic'):
                            print(f"  音标: {item['phonetic']}")
                        print(f"  状态: {item['status']}")
                    else:
                        print(f"- {item['word']}: 未找到")
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '2':
            # 作文批改
            text = input("请输入作文文本: ")
            
            try:
                result = correct_essay(text)
                print("\n批改结果:")
                print(f"评分: {result['score']}")
                print("\n原始文本:")
                print(result['original_text'])
                print("\n润色后文本:")
                print(result['polished_text'])
                if result['errors']:
                    print("\n错误:")
                    for error in result['errors']:
                        print(f"- {error['message']}: {error['example']}")
                if result['suggestions']:
                    print("\n改进建议:")
                    for suggestion in result['suggestions']:
                        print(f"- {suggestion}")
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '3':
            # 中英互译
            text = input("请输入文本: ")
            src = input("请输入源语言（zh/en）: ")
            tgt = input("请输入目标语言（zh/en）: ")
            
            try:
                translation = translate_text(text, src, tgt)
                print("\n翻译结果:")
                print(translation)
            except Exception as e:
                print(f"错误: {str(e)}")
        else:
            print("无效选择")
        print("-" * 40)


def handle_tools():
    """
    处理工具集
    """
    print("\n工具集模块")
    print("-" * 40)
    
    while True:
        print("1. 公式速查")
        print("2. 计算器")
        print("3. 单位换算")
        print("4. 进制转换")
        print("5. 待办事项")
        print("6. 课程表")
        print("7. 倒计时")
        print("0. 返回主菜单")
        choice = input("请选择: ")
        
        if choice == '0':
            break
        elif choice == '1':
            # 公式速查
            subject = input("请输入学科（数学/物理/化学）: ")
            formula_name = input("请输入公式名称: ")
            
            try:
                result = tool_query('formula', {'subject': subject, 'name': formula_name})
                print("\n公式:")
                print(result)
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '2':
            # 计算器
            expression = input("请输入表达式: ")
            
            try:
                result = tool_query('calculator', {'expression': expression})
                print("\n计算结果:")
                print(result)
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '3':
            # 单位换算
            value = input("请输入数值: ")
            from_unit = input("请输入原单位: ")
            to_unit = input("请输入目标单位: ")
            unit_type = input("请输入单位类型（长度/质量/时间/温度）: ")
            
            try:
                result = tool_query('unit_conversion', {
                    'value': value,
                    'from_unit': from_unit,
                    'to_unit': to_unit,
                    'unit_type': unit_type
                })
                print("\n换算结果:")
                print(result)
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '4':
            # 进制转换
            number = input("请输入数字: ")
            from_base = input("请输入原进制: ")
            to_base = input("请输入目标进制: ")
            
            try:
                from_base = int(from_base)
                to_base = int(to_base)
                result = tool_query('base_conversion', {
                    'number': number,
                    'from_base': from_base,
                    'to_base': to_base
                })
                print("\n转换结果:")
                print(result)
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '5':
            # 待办事项
            todo_action = input("请选择操作（add/list/complete/remove）: ")
            
            try:
                if todo_action == 'add':
                    task = input("请输入任务内容: ")
                    deadline = input("请输入截止日期（可选）: ")
                    result = tool_query('todo', {'action': 'add', 'task': task, 'deadline': deadline})
                elif todo_action == 'list':
                    result = tool_query('todo', {'action': 'list'})
                elif todo_action == 'complete':
                    index = input("请输入待办事项索引: ")
                    result = tool_query('todo', {'action': 'complete', 'index': int(index)})
                elif todo_action == 'remove':
                    index = input("请输入待办事项索引: ")
                    result = tool_query('todo', {'action': 'remove', 'index': int(index)})
                else:
                    print("无效操作")
                    continue
                
                print("\n操作结果:")
                if isinstance(result, list):
                    for i, item in enumerate(result, 1):
                        status = '✓' if item['completed'] else '○'
                        print(f"{i}. {status} {item['task']}")
                        if item['deadline']:
                            print(f"   截止日期: {item['deadline']}")
                        print(f"   创建时间: {item['created_at']}")
                else:
                    print(result)
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '6':
            # 课程表
            schedule_action = input("请选择操作（add/list）: ")
            
            try:
                if schedule_action == 'add':
                    day = input("请输入星期: ")
                    course = input("请输入课程名称: ")
                    time = input("请输入时间: ")
                    result = tool_query('schedule', {'action': 'add', 'day': day, 'course': course, 'time': time})
                elif schedule_action == 'list':
                    day = input("请输入星期（可选，留空查看全部）: ")
                    result = tool_query('schedule', {'action': 'list', 'day': day if day else None})
                else:
                    print("无效操作")
                    continue
                
                print("\n操作结果:")
                if isinstance(result, dict):
                    for day, courses in result.items():
                        print(f"\n{day}:")
                        if courses:
                            for course in courses:
                                print(f"- {course['time']}: {course['course']}")
                        else:
                            print("  无课程")
                else:
                    print(result)
            except Exception as e:
                print(f"错误: {str(e)}")
        elif choice == '7':
            # 倒计时
            target_date = input("请输入目标日期（格式: YYYY-MM-DD HH:MM:SS）: ")
            
            try:
                result = tool_query('countdown', {'target_date': target_date})
                print("\n倒计时结果:")
                print(result)
            except Exception as e:
                print(f"错误: {str(e)}")
        else:
            print("无效选择")
        print("-" * 40)


def main():
    """
    主函数
    """
    # 初始化数据库
    try:
        init_database()
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
    
    while True:
        print_menu()
        choice = input("请选择功能: ")
        
        try:
            if choice == '0':
                print("谢谢使用智能学习助手！")
                break
            elif choice == '1':
                handle_qa()
            elif choice == '2':
                handle_practice()
            elif choice == '3':
                handle_plan()
            elif choice == '4':
                handle_summary()
            elif choice == '5':
                handle_language()
            elif choice == '6':
                handle_tools()
            else:
                print("无效选择，请重新输入")
        except KeyboardInterrupt:
            print("\n操作被用户中断")
        except Exception as e:
            print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    main()
