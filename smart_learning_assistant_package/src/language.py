# 语言学习专项模块
import json
import re
from typing import Dict, List, Any

from .config import VOCAB_DATA_PATH, VOCAB_REVIEW_INTERVALS
from .utils import read_csv, write_csv, get_db_connection, get_current_date, calculate_next_review_date


class LanguageSystem:
    """
    语言学习系统
    """
    
    def __init__(self):
        """
        初始化语言学习系统
        """
        self.vocab_data = self.load_vocab_data()
    
    def load_vocab_data(self) -> List[Dict[str, Any]]:
        """
        加载词汇数据
        
        Returns:
            词汇数据
        """
        return read_csv(VOCAB_DATA_PATH)
    
    def save_vocab_data(self) -> None:
        """
        保存词汇数据
        """
        fieldnames = ['word', 'meaning', 'example', 'phonetic']
        write_csv(VOCAB_DATA_PATH, self.vocab_data, fieldnames)
    
    def vocab_train(self, word_list: List[str], mode: str = 'review') -> Dict[str, Any]:
        """
        单词记忆训练
        
        Args:
            word_list: 单词列表
            mode: 训练模式 (review, learn)
        
        Returns:
            训练结果
        """
        # 检查模式
        if mode not in ['review', 'learn']:
            mode = 'review'
        
        # 加载词汇学习数据
        vocab_learning = self.load_vocab_learning()
        
        # 处理单词列表
        results = []
        for word in word_list:
            # 查找单词信息
            word_info = self.find_word_info(word)
            
            if word_info:
                # 检查是否在学习列表中
                existing = next((v for v in vocab_learning if v['word'] == word), None)
                
                if existing:
                    # 更新复习信息
                    review_count = existing['review_count'] + 1
                    interval_index = min(review_count - 1, len(VOCAB_REVIEW_INTERVALS) - 1)
                    next_review = calculate_next_review_date(get_current_date(), VOCAB_REVIEW_INTERVALS[interval_index])
                    
                    # 更新数据库
                    self.update_vocab_learning(word, next_review, review_count)
                    
                    results.append({
                        'word': word,
                        'meaning': word_info['meaning'],
                        'example': word_info.get('example', ''),
                        'phonetic': word_info.get('phonetic', ''),
                        'review_count': review_count,
                        'next_review': next_review,
                        'status': 'reviewed'
                    })
                else:
                    # 新单词，添加到学习列表
                    next_review = calculate_next_review_date(get_current_date(), VOCAB_REVIEW_INTERVALS[0])
                    self.add_vocab_learning(word, word_info['meaning'], word_info.get('example', ''))
                    
                    results.append({
                        'word': word,
                        'meaning': word_info['meaning'],
                        'example': word_info.get('example', ''),
                        'phonetic': word_info.get('phonetic', ''),
                        'review_count': 1,
                        'next_review': next_review,
                        'status': 'added'
                    })
            else:
                results.append({
                    'word': word,
                    'status': 'not_found'
                })
        
        return {
            'mode': mode,
            'results': results,
            'total': len(word_list),
            'found': len([r for r in results if r['status'] != 'not_found'])
        }
    
    def find_word_info(self, word: str) -> Dict[str, Any]:
        """
        查找单词信息
        
        Args:
            word: 单词
        
        Returns:
            单词信息
        """
        # 先在本地数据中查找
        for item in self.vocab_data:
            if item['word'] == word:
                return item
        
        # 内置单词库
        builtin_words = {
            'apple': {
                'meaning': '苹果',
                'example': 'I have an apple every day.',
                'phonetic': '/ˈæpl/'
            },
            'banana': {
                'meaning': '香蕉',
                'example': 'Bananas are rich in potassium.',
                'phonetic': '/bəˈnɑːnə/'
            },
            'cat': {
                'meaning': '猫',
                'example': 'The cat is sleeping on the sofa.',
                'phonetic': '/kæt/'
            },
            'dog': {
                'meaning': '狗',
                'example': 'Dogs are loyal animals.',
                'phonetic': '/dɒɡ/'
            },
            'book': {
                'meaning': '书',
                'example': 'I love reading books.',
                'phonetic': '/bʊk/'
            },
            'computer': {
                'meaning': '电脑',
                'example': 'I use a computer for work.',
                'phonetic': '/kəmˈpjuːtə/'
            },
            'student': {
                'meaning': '学生',
                'example': 'She is a hardworking student.',
                'phonetic': '/ˈstjuːdnt/'
            },
            'teacher': {
                'meaning': '老师',
                'example': 'My teacher is very kind.',
                'phonetic': '/ˈtiːtʃə/'
            },
            'friend': {
                'meaning': '朋友',
                'example': 'He is my best friend.',
                'phonetic': '/frend/'
            },
            'family': {
                'meaning': '家庭',
                'example': 'I have a happy family.',
                'phonetic': '/ˈfæməli/'
            }
        }
        
        return builtin_words.get(word, None)
    
    def load_vocab_learning(self) -> List[Dict[str, Any]]:
        """
        加载词汇学习数据
        
        Returns:
            词汇学习数据
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM vocab_learning')
        vocab_learning = []
        
        for row in cursor.fetchall():
            vocab_learning.append({
                'id': row['id'],
                'word': row['word'],
                'meaning': row['meaning'],
                'example': row['example'],
                'last_review': row['last_review'],
                'next_review': row['next_review'],
                'review_count': row['review_count'],
                'difficulty': row['difficulty']
            })
        
        conn.close()
        return vocab_learning
    
    def add_vocab_learning(self, word: str, meaning: str, example: str) -> None:
        """
        添加词汇到学习列表
        
        Args:
            word: 单词
            meaning: 含义
            example: 例句
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO vocab_learning (word, meaning, example, last_review, next_review, review_count, difficulty)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (word, meaning, example, get_current_date(), calculate_next_review_date(get_current_date(), VOCAB_REVIEW_INTERVALS[0]), 1, 0))
        
        conn.commit()
        conn.close()
    
    def update_vocab_learning(self, word: str, next_review: str, review_count: int) -> None:
        """
        更新词汇学习信息
        
        Args:
            word: 单词
            next_review: 下次复习日期
            review_count: 复习次数
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE vocab_learning
        SET last_review = ?, next_review = ?, review_count = ?
        WHERE word = ?
        ''', (get_current_date(), next_review, review_count, word))
        
        conn.commit()
        conn.close()
    
    def correct_essay(self, text: str) -> Dict[str, Any]:
        """
        作文批改
        
        Args:
            text: 作文文本
        
        Returns:
            批改结果
        """
        # 简单的语法纠错
        errors = self.detect_grammar_errors(text)
        
        # 计算评分
        score = self.calculate_essay_score(text, errors)
        
        # 生成改进建议
        suggestions = self.generate_improvement_suggestions(text, errors)
        
        # 润色文本
        polished_text = self.polish_text(text, errors)
        
        return {
            'original_text': text,
            'polished_text': polished_text,
            'errors': errors,
            'score': score,
            'suggestions': suggestions
        }
    
    def detect_grammar_errors(self, text: str) -> List[Dict[str, Any]]:
        """
        检测语法错误
        
        Args:
            text: 文本
        
        Returns:
            错误列表
        """
        errors = []
        
        # 简单的语法检查规则
        # 1. 检查主谓一致
        if re.search(r'He have|She have|It have', text):
            errors.append({
                'type': 'subject_verb_agreement',
                'message': '主谓不一致，第三人称单数应该使用 has',
                'example': 'He have → He has'
            })
        
        # 2. 检查时态
        if re.search(r'I went to school yesterday and study', text):
            errors.append({
                'type': 'tense_error',
                'message': '时态不一致，yesterday 应该使用过去时',
                'example': 'study → studied'
            })
        
        # 3. 检查冠词
        if re.search(r'go to school|go to university', text):
            errors.append({
                'type': 'article_error',
                'message': '缺少冠词',
                'example': 'go to school → go to the school'
            })
        
        # 4. 检查拼写
        common_misspellings = {
            'recieve': 'receive',
            'seperate': 'separate',
            'definately': 'definitely',
            'occured': 'occurred',
            'untill': 'until'
        }
        
        for misspelled, correct in common_misspellings.items():
            if misspelled in text:
                errors.append({
                    'type': 'spelling_error',
                    'message': f'拼写错误: {misspelled}',
                    'example': f'{misspelled} → {correct}'
                })
        
        return errors
    
    def calculate_essay_score(self, text: str, errors: List[Dict[str, Any]]) -> int:
        """
        计算作文评分
        
        Args:
            text: 文本
            errors: 错误列表
        
        Returns:
            评分
        """
        # 基础分数
        base_score = 80
        
        # 根据错误数量扣分
        error_penalty = min(len(errors) * 5, 30)
        
        # 根据文本长度加分
        length_bonus = min(len(text.split()) // 10, 10)
        
        # 计算最终分数
        score = base_score - error_penalty + length_bonus
        
        # 确保分数在0-100之间
        return max(0, min(100, score))
    
    def generate_improvement_suggestions(self, text: str, errors: List[Dict[str, Any]]) -> List[str]:
        """
        生成改进建议
        
        Args:
            text: 文本
            errors: 错误列表
        
        Returns:
            建议列表
        """
        suggestions = []
        
        if errors:
            suggestions.append('请检查并修正语法错误')
        
        # 检查文本长度
        word_count = len(text.split())
        if word_count < 50:
            suggestions.append('建议增加文本长度，提供更多细节和例子')
        
        # 检查句子多样性
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) < 5:
            suggestions.append('建议使用更多句子，提高文本的流畅度')
        
        # 检查词汇多样性
        unique_words = len(set(text.lower().split()))
        if unique_words < word_count * 0.5:
            suggestions.append('建议使用更多同义词，丰富词汇表达')
        
        return suggestions
    
    def polish_text(self, text: str, errors: List[Dict[str, Any]]) -> str:
        """
        润色文本
        
        Args:
            text: 原始文本
            errors: 错误列表
        
        Returns:
            润色后的文本
        """
        polished = text
        
        # 修正常见错误
        corrections = {
            'He have': 'He has',
            'She have': 'She has',
            'It have': 'It has',
            'recieve': 'receive',
            'seperate': 'separate',
            'definately': 'definitely',
            'occured': 'occurred',
            'untill': 'until'
        }
        
        for error, correction in corrections.items():
            polished = polished.replace(error, correction)
        
        return polished
    
    def translate_text(self, text: str, src: str, tgt: str) -> str:
        """
        中英互译
        
        Args:
            text: 文本
            src: 源语言 (zh, en)
            tgt: 目标语言 (zh, en)
        
        Returns:
            翻译结果
        """
        # 简单的翻译实现
        translations = {
            'hello': '你好',
            'world': '世界',
            'apple': '苹果',
            'banana': '香蕉',
            'cat': '猫',
            'dog': '狗',
            'book': '书',
            'computer': '电脑',
            'student': '学生',
            'teacher': '老师',
            '你好': 'hello',
            '世界': 'world',
            '苹果': 'apple',
            '香蕉': 'banana',
            '猫': 'cat',
            '狗': 'dog',
            '书': 'book',
            '电脑': 'computer',
            '学生': 'student',
            '老师': 'teacher'
        }
        
        # 简单的单词翻译
        words = text.split()
        translated_words = []
        
        for word in words:
            # 移除标点符号
            clean_word = re.sub(r'[.,?!]', '', word)
            if clean_word in translations:
                translated = translations[clean_word]
                # 保留标点符号
                if word.endswith(tuple('.,?!')):
                    translated += word[-1]
                translated_words.append(translated)
            else:
                translated_words.append(word)
        
        return ' '.join(translated_words)


# 模块接口
def vocab_train(word_list: List[str], mode: str = 'review') -> Dict[str, Any]:
    """
    单词记忆训练
    
    Args:
        word_list: 单词列表
        mode: 训练模式 (review, learn)
    
    Returns:
        训练结果
    """
    language_system = LanguageSystem()
    return language_system.vocab_train(word_list, mode)


def correct_essay(text: str) -> Dict[str, Any]:
    """
    作文批改
    
    Args:
        text: 作文文本
    
    Returns:
        批改结果
    """
    language_system = LanguageSystem()
    return language_system.correct_essay(text)


def translate_text(text: str, src: str, tgt: str) -> str:
    """
    中英互译
    
    Args:
        text: 文本
        src: 源语言 (zh, en)
        tgt: 目标语言 (zh, en)
    
    Returns:
        翻译结果
    """
    language_system = LanguageSystem()
    return language_system.translate_text(text, src, tgt)
