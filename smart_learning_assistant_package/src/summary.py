# 资料整理与总结模块
import re
from typing import Dict, List, Any

from .config import MAX_SUMMARY_LENGTH, MAX_MINDMAP_DEPTH
from .utils import clean_text, split_text_into_chunks


class SummarySystem:
    """
    资料整理与总结系统
    """
    
    def __init__(self):
        """
        初始化总结系统
        """
        pass
    
    def summarize_text(self, text: str, max_length: int = MAX_SUMMARY_LENGTH) -> str:
        """
        文本摘要
        
        Args:
            text: 原始文本
            max_length: 摘要最大长度
        
        Returns:
            文本摘要
        """
        # 清理文本
        text = clean_text(text)
        
        # 如果文本长度小于最大长度，直接返回
        if len(text) <= max_length:
            return text
        
        # 分割文本为句子
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 计算每个句子的重要性（简单实现：基于句子长度和位置）
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            # 位置权重：开头和结尾的句子更重要
            position_score = 1.0
            if i == 0 or i == len(sentences) - 1:
                position_score = 1.5
            elif i < len(sentences) * 0.2 or i > len(sentences) * 0.8:
                position_score = 1.2
            
            # 长度权重：中等长度的句子更重要
            length = len(sentence)
            length_score = 1.0
            if 20 <= length <= 100:
                length_score = 1.2
            elif length < 10:
                length_score = 0.5
            
            # 总分数
            score = position_score * length_score
            sentence_scores.append((sentence, score))
        
        # 按分数排序，选择前N个句子
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 构建摘要
        summary = []
        current_length = 0
        
        for sentence, _ in sentence_scores:
            if current_length + len(sentence) + 1 <= max_length:  # +1 for punctuation
                summary.append(sentence)
                current_length += len(sentence) + 1
            else:
                break
        
        # 按原顺序排序
        summary = [s for s, _ in sorted(zip([s for s, _ in sentence_scores[:len(summary)]], 
                                           [sentences.index(s) for s, _ in sentence_scores[:len(summary)]]), 
                                       key=lambda x: x[1])]
        
        # 添加标点符号
        summary_text = '。'.join(summary) + '。'
        
        return summary_text
    
    def generate_mindmap(self, topic: str, content: str) -> str:
        """
        生成结构化思维导图（Markdown格式）
        
        Args:
            topic: 主题
            content: 内容
        
        Returns:
            Markdown格式的思维导图
        """
        # 清理内容
        content = clean_text(content)
        
        # 提取关键信息
        key_points = self.extract_key_points(content)
        
        # 构建思维导图
        mindmap = []
        mindmap.append(f"# {topic}")
        mindmap.append("")
        
        # 生成一级节点
        for i, point in enumerate(key_points, 1):
            mindmap.append(f"## {i}. {point['title']}")
            
            # 生成二级节点
            if 'subpoints' in point and point['subpoints']:
                for j, subpoint in enumerate(point['subpoints'], 1):
                    mindmap.append(f"### {i}.{j}. {subpoint}")
            
            mindmap.append("")
        
        return '\n'.join(mindmap)
    
    def outline_chapter(self, chapter: str, content: str) -> str:
        """
        章节知识点归纳、复习提纲
        
        Args:
            chapter: 章节名称
            content: 章节内容
        
        Returns:
            章节大纲
        """
        # 清理内容
        content = clean_text(content)
        
        # 提取章节结构
        sections = self.extract_sections(content)
        
        # 构建大纲
        outline = []
        outline.append(f"# {chapter}")
        outline.append("")
        outline.append("## 章节知识点归纳")
        outline.append("")
        
        # 生成大纲内容
        for i, section in enumerate(sections, 1):
            outline.append(f"### {i}. {section['title']}")
            
            if 'content' in section and section['content']:
                # 提取重点
                key_points = self.extract_key_points(section['content'])
                for j, point in enumerate(key_points, 1):
                    outline.append(f"#### {i}.{j}. {point['title']}")
            
            outline.append("")
        
        # 添加复习重点
        outline.append("## 复习重点")
        outline.append("")
        
        # 提取复习重点
        review_points = self.extract_review_points(content)
        for i, point in enumerate(review_points, 1):
            outline.append(f"- {point}")
        
        return '\n'.join(outline)
    
    def extract_key_points(self, text: str) -> List[Dict[str, Any]]:
        """
        提取关键信息
        
        Args:
            text: 文本内容
        
        Returns:
            关键信息列表
        """
        # 简单实现：基于句子长度和关键词
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        key_points = []
        
        # 关键词列表
        keywords = ['重要', '关键', '核心', '重点', '注意', '必须', '需要', '应该', '建议']
        
        for sentence in sentences:
            # 检查是否包含关键词
            has_keyword = any(keyword in sentence for keyword in keywords)
            
            # 检查句子长度
            if len(sentence) > 10 and (has_keyword or len(sentence) > 50):
                # 提取子点（简单实现）
                subpoints = []
                if '：' in sentence:
                    parts = sentence.split('：')
                    if len(parts) > 1:
                        title = parts[0].strip()
                        content = parts[1].strip()
                        # 提取分点
                        if '，' in content:
                            subpoints = [p.strip() for p in content.split('，') if p.strip()]
                        elif '；' in content:
                            subpoints = [p.strip() for p in content.split('；') if p.strip()]
                        key_points.append({'title': title, 'subpoints': subpoints})
                else:
                    key_points.append({'title': sentence, 'subpoints': []})
        
        # 限制数量
        return key_points[:5]  # 最多返回5个关键点
    
    def extract_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        提取章节结构
        
        Args:
            text: 文本内容
        
        Returns:
            章节结构列表
        """
        # 简单实现：基于段落和标题
        paragraphs = text.split('\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        sections = []
        current_section = None
        
        for paragraph in paragraphs:
            # 检查是否为标题（简单实现：以数字或特定符号开头）
            if re.match(r'^[0-9]+\.|^[一二三四五六七八九十]+、|^[A-Za-z]\.|^#', paragraph):
                # 新章节
                if current_section:
                    sections.append(current_section)
                current_section = {'title': paragraph, 'content': ''}
            else:
                # 章节内容
                if current_section:
                    current_section['content'] += paragraph + '。'
        
        # 添加最后一个章节
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def extract_review_points(self, text: str) -> List[str]:
        """
        提取复习重点
        
        Args:
            text: 文本内容
        
        Returns:
            复习重点列表
        """
        # 简单实现：基于关键词和句子重要性
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        review_points = []
        
        # 关键词列表
        review_keywords = ['重要', '关键', '核心', '重点', '注意', '必须', '需要', '应该', '建议', '掌握', '理解', '记住']
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in review_keywords):
                review_points.append(sentence)
        
        # 限制数量
        return review_points[:10]  # 最多返回10个复习重点


# 模块接口
def summarize_text(text: str, max_length: int = MAX_SUMMARY_LENGTH) -> str:
    """
    文本摘要
    
    Args:
        text: 原始文本
        max_length: 摘要最大长度
    
    Returns:
        文本摘要
    """
    summary_system = SummarySystem()
    return summary_system.summarize_text(text, max_length)


def generate_mindmap(topic: str, content: str) -> str:
    """
    生成结构化思维导图（Markdown格式）
    
    Args:
        topic: 主题
        content: 内容
    
    Returns:
        Markdown格式的思维导图
    """
    summary_system = SummarySystem()
    return summary_system.generate_mindmap(topic, content)


def outline_chapter(chapter: str, content: str) -> str:
    """
    章节知识点归纳、复习提纲
    
    Args:
        chapter: 章节名称
        content: 章节内容
    
    Returns:
        章节大纲
    """
    summary_system = SummarySystem()
    return summary_system.outline_chapter(chapter, content)
