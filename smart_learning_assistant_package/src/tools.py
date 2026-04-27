# 工具集模块
import math
from typing import Dict, List, Any, Union
from datetime import datetime, timedelta

from .config import MAX_CALCULATOR_INPUT_LENGTH


class ToolsSystem:
    """
    工具集系统
    """
    
    def __init__(self):
        """
        初始化工具集系统
        """
        # 内置公式库
        self.formulas = {
            # 数学公式
            '数学': {
                '勾股定理': 'a² + b² = c²，其中a和b是直角边，c是斜边',
                '二次方程求根公式': 'x = [-b ± √(b² - 4ac)] / (2a)',
                '圆的面积': 'S = πr²',
                '圆的周长': 'C = 2πr',
                '三角形面积': 'S = 1/2 × 底 × 高',
                '矩形面积': 'S = 长 × 宽',
                '正方形面积': 'S = 边长²',
                '立方体体积': 'V = 边长³',
                '长方体体积': 'V = 长 × 宽 × 高',
                '圆柱体体积': 'V = πr²h',
                '圆锥体体积': 'V = 1/3 × πr²h'
            },
            # 物理公式
            '物理': {
                '牛顿第二定律': 'F = ma',
                '动能公式': 'Eₖ = 1/2 mv²',
                '势能公式': 'Eₚ = mgh',
                '功率公式': 'P = W/t',
                '欧姆定律': 'V = IR',
                '电阻定律': 'R = ρL/S',
                '电功率公式': 'P = VI',
                '速度公式': 'v = s/t',
                '加速度公式': 'a = (v - u)/t',
                '力的做功公式': 'W = Fs'
            },
            # 化学公式
            '化学': {
                '物质的量': 'n = m/M',
                '摩尔质量': 'M = m/n',
                '气体摩尔体积': 'Vₘ = V/n',
                '物质的量浓度': 'c = n/V',
                '质量分数': 'ω = m(溶质)/m(溶液) × 100%',
                '化学平衡常数': 'K = [产物]/[反应物]',
                'pH值计算公式': 'pH = -log[H⁺]',
                '中和反应': '酸 + 碱 → 盐 + 水',
                '氧化还原反应': '氧化剂 + 还原剂 → 还原产物 + 氧化产物',
                '酯化反应': '酸 + 醇 → 酯 + 水'
            }
        }
        
        # 单位换算系数
        self.unit_conversions = {
            '长度': {
                '米': 1.0,
                '厘米': 0.01,
                '毫米': 0.001,
                '千米': 1000.0,
                '英寸': 0.0254,
                '英尺': 0.3048,
                '码': 0.9144,
                '英里': 1609.34
            },
            '质量': {
                '千克': 1.0,
                '克': 0.001,
                '毫克': 0.000001,
                '吨': 1000.0,
                '磅': 0.453592,
                '盎司': 0.0283495
            },
            '时间': {
                '秒': 1.0,
                '分钟': 60.0,
                '小时': 3600.0,
                '天': 86400.0,
                '周': 604800.0,
                '月': 2592000.0,
                '年': 31536000.0
            },
            '温度': {
                '摄氏度': lambda x: x,
                '华氏度': lambda x: (x - 32) * 5/9,
                '开尔文': lambda x: x - 273.15
            }
        }
        
        # 待办事项
        self.todos = []
        
        # 课程表
        self.schedule = {
            '周一': [],
            '周二': [],
            '周三': [],
            '周四': [],
            '周五': [],
            '周六': [],
            '周日': []
        }
    
    def tool_query(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        工具查询
        
        Args:
            tool_name: 工具名称
            params: 工具参数
        
        Returns:
            工具执行结果
        """
        if tool_name == 'formula':
            return self.get_formula(params.get('subject'), params.get('name'))
        elif tool_name == 'calculator':
            return self.calculate(params.get('expression'))
        elif tool_name == 'unit_conversion':
            return self.convert_unit(params.get('value'), params.get('from_unit'), params.get('to_unit'), params.get('unit_type'))
        elif tool_name == 'base_conversion':
            return self.convert_base(params.get('number'), params.get('from_base'), params.get('to_base'))
        elif tool_name == 'todo':
            action = params.get('action', 'list')
            if action == 'add':
                return self.add_todo(params.get('task'), params.get('deadline'))
            elif action == 'list':
                return self.list_todos()
            elif action == 'complete':
                return self.complete_todo(params.get('index'))
            elif action == 'remove':
                return self.remove_todo(params.get('index'))
        elif tool_name == 'schedule':
            action = params.get('action', 'list')
            if action == 'add':
                return self.add_schedule(params.get('day'), params.get('course'), params.get('time'))
            elif action == 'list':
                return self.list_schedule(params.get('day'))
        elif tool_name == 'countdown':
            return self.countdown(params.get('target_date'))
        else:
            return f"未知工具: {tool_name}"
    
    def get_formula(self, subject: str, formula_name: str) -> str:
        """
        获取公式
        
        Args:
            subject: 学科
            formula_name: 公式名称
        
        Returns:
            公式
        """
        if subject in self.formulas:
            if formula_name in self.formulas[subject]:
                return f"{subject} - {formula_name}: {self.formulas[subject][formula_name]}"
            else:
                return f"未找到 {subject} 中的公式: {formula_name}"
        else:
            return f"未找到学科: {subject}"
    
    def calculate(self, expression: str) -> str:
        """
        计算器
        
        Args:
            expression: 表达式
        
        Returns:
            计算结果
        """
        if not expression:
            return "请输入表达式"
        
        if len(expression) > MAX_CALCULATOR_INPUT_LENGTH:
            return "表达式过长"
        
        try:
            # 安全计算
            result = eval(expression, {'__builtins__': None}, {'math': math})
            return f"{expression} = {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"
    
    def convert_unit(self, value: float, from_unit: str, to_unit: str, unit_type: str) -> str:
        """
        单位换算
        
        Args:
            value: 数值
            from_unit: 原单位
            to_unit: 目标单位
            unit_type: 单位类型
        
        Returns:
            换算结果
        """
        if unit_type not in self.unit_conversions:
            return f"未支持的单位类型: {unit_type}"
        
        if from_unit not in self.unit_conversions[unit_type]:
            return f"未支持的原单位: {from_unit}"
        
        if to_unit not in self.unit_conversions[unit_type]:
            return f"未支持的目标单位: {to_unit}"
        
        try:
            value = float(value)
            
            # 温度换算特殊处理
            if unit_type == '温度':
                # 先转换为摄氏度
                if from_unit != '摄氏度':
                    value = self.unit_conversions[unit_type][from_unit](value)
                # 再转换为目标单位
                if to_unit == '华氏度':
                    result = value * 9/5 + 32
                elif to_unit == '开尔文':
                    result = value + 273.15
                else:
                    result = value
            else:
                # 其他单位换算
                value_in_base = value * self.unit_conversions[unit_type][from_unit]
                result = value_in_base / self.unit_conversions[unit_type][to_unit]
            
            return f"{value} {from_unit} = {result:.4f} {to_unit}"
        except Exception as e:
            return f"换算错误: {str(e)}"
    
    def convert_base(self, number: str, from_base: int, to_base: int) -> str:
        """
        进制转换
        
        Args:
            number: 数字
            from_base: 原进制
            to_base: 目标进制
        
        Returns:
            转换结果
        """
        try:
            # 转换为十进制
            decimal = int(number, from_base)
            
            # 转换为目标进制
            if to_base == 2:
                return bin(decimal)[2:]
            elif to_base == 8:
                return oct(decimal)[2:]
            elif to_base == 10:
                return str(decimal)
            elif to_base == 16:
                return hex(decimal)[2:].upper()
            else:
                return f"未支持的目标进制: {to_base}"
        except Exception as e:
            return f"转换错误: {str(e)}"
    
    def add_todo(self, task: str, deadline: str = None) -> str:
        """
        添加待办事项
        
        Args:
            task: 任务内容
            deadline: 截止日期
        
        Returns:
            添加结果
        """
        if not task:
            return "请输入任务内容"
        
        self.todos.append({
            'task': task,
            'deadline': deadline,
            'completed': False,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        return f"已添加待办事项: {task}"
    
    def list_todos(self) -> List[Dict[str, Any]]:
        """
        列出待办事项
        
        Returns:
            待办事项列表
        """
        return self.todos
    
    def complete_todo(self, index: int) -> str:
        """
        完成待办事项
        
        Args:
            index: 待办事项索引
        
        Returns:
            完成结果
        """
        if 0 <= index < len(self.todos):
            self.todos[index]['completed'] = True
            return f"已完成待办事项: {self.todos[index]['task']}"
        else:
            return "待办事项索引无效"
    
    def remove_todo(self, index: int) -> str:
        """
        删除待办事项
        
        Args:
            index: 待办事项索引
        
        Returns:
            删除结果
        """
        if 0 <= index < len(self.todos):
            task = self.todos[index]['task']
            self.todos.pop(index)
            return f"已删除待办事项: {task}"
        else:
            return "待办事项索引无效"
    
    def add_schedule(self, day: str, course: str, time: str) -> str:
        """
        添加课程
        
        Args:
            day: 星期
            course: 课程名称
            time: 时间
        
        Returns:
            添加结果
        """
        if day not in self.schedule:
            return f"无效的星期: {day}"
        
        if not course or not time:
            return "请输入课程名称和时间"
        
        self.schedule[day].append({
            'course': course,
            'time': time
        })
        
        return f"已添加课程: {day} {time} {course}"
    
    def list_schedule(self, day: str = None) -> Dict[str, List[Dict[str, str]]]:
        """
        列出课程表
        
        Args:
            day: 星期
        
        Returns:
            课程表
        """
        if day:
            if day in self.schedule:
                return {day: self.schedule[day]}
            else:
                return {day: []}
        else:
            return self.schedule
    
    def countdown(self, target_date: str) -> str:
        """
        倒计时
        
        Args:
            target_date: 目标日期，格式为 YYYY-MM-DD HH:MM:SS
        
        Returns:
            倒计时结果
        """
        try:
            target = datetime.strptime(target_date, '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            
            if target < now:
                return "目标日期已过"
            
            delta = target - now
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return f"距离 {target_date} 还有 {days} 天 {hours} 小时 {minutes} 分钟 {seconds} 秒"
        except Exception as e:
            return f"倒计时错误: {str(e)}"


# 模块接口
def tool_query(tool_name: str, params: Dict[str, Any]) -> Any:
    """
    工具查询
    
    Args:
        tool_name: 工具名称
        params: 工具参数
    
    Returns:
        工具执行结果
    """
    tools_system = ToolsSystem()
    return tools_system.tool_query(tool_name, params)
