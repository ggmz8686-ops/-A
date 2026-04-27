#!/usr/bin/env python3
# 测试火山引擎API功能

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.volcano_engine import semantic_analysis, chat

def test_semantic_analysis():
    """测试语义分析功能"""
    print("=== 测试语义分析功能 ===")
    
    test_questions = [
        "什么是勾股定理",
        "牛顿运动定律是什么",
        "Python函数如何定义",
        "英语时态有哪些",
        "质数的定义是什么"
    ]
    
    for question in test_questions:
        print(f"\n测试问题: {question}")
        result = semantic_analysis(question)
        
        print(f"成功: {result.get('success', False)}")
        print(f"降级: {result.get('fallback', False)}")
        
        if result.get('fallback'):
            print(f"本地分析结果: {result.get('local_result', {}).get('response', '无结果')}")
        else:
            print(f"API返回: {result.get('content', '无内容')}")
        
        print("-" * 50)

def test_chat():
    """测试对话功能"""
    print("\n=== 测试对话功能 ===")
    
    test_prompts = [
        "请解释什么是质数",
        "如何学习Python编程",
        "物理中的能量守恒定律"
    ]
    
    for prompt in test_prompts:
        print(f"\n测试对话: {prompt}")
        result = chat(prompt)
        
        print(f"成功: {result.get('success', False)}")
        print(f"降级: {result.get('fallback', False)}")
        
        if result.get('fallback'):
            print(f"本地分析结果: {result.get('local_result', {}).get('response', '无结果')}")
        else:
            if result.get('data'):
                content = result['data']['choices'][0]['message']['content']
                print(f"API返回: {content}")
        
        print("-" * 50)

def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    # 测试网络错误（模拟）
    print("测试网络错误情况...")
    # 这里会触发降级机制
    result = semantic_analysis("这是一个测试问题")
    print(f"降级: {result.get('fallback', False)}")
    print(f"消息: {result.get('message', '无消息')}")
    print("-" * 50)

def main():
    """主测试函数"""
    print("开始测试火山引擎API功能...")
    print(f"当前环境变量 VOLCANO_API_KEY: {'已设置' if os.environ.get('VOLCANO_API_KEY') else '未设置'}")
    print(f"当前环境变量 VOLCANO_ENDPOINT: {os.environ.get('VOLCANO_ENDPOINT', '未设置')}")
    print("=" * 60)
    
    test_semantic_analysis()
    test_chat()
    test_error_handling()
    
    print("\n测试完成！")
    print("注意：由于未配置API密钥，所有测试都会降级到本地语义分析模式。")
    print("要测试完整API功能，请设置 VOLCANO_API_KEY 环境变量。")

if __name__ == "__main__":
    main()
