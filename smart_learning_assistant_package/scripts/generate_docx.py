from __future__ import annotations

import os
import zipfile
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "智能学习助手_项目介绍.docx"


PARAGRAPHS = [
    ("title", "智能学习助手项目介绍"),
    ("heading1", "一、项目概述"),
    ("body", "智能学习助手是一个基于 Python 开发的本地化学习辅助系统，面向学生日常学习中的常见需求，提供知识问答、题目练习与批改、学习计划制定、资料总结、语言学习以及学习工具箱等功能。"),
    ("body", "项目的核心目标是将多个学习场景整合到一个轻量、可离线运行的系统中，帮助用户在同一平台内完成提问、练习、复习、规划和记录。"),
    ("heading1", "二、项目背景"),
    ("body", "在实际学习过程中，学生往往需要同时使用多个工具，例如查知识点、刷题、做计划、记错题、整理笔记和进行语言练习。这种工具分散会增加学习成本，也不利于形成连续的学习流程。"),
    ("body", "因此，我们设计了这个项目，希望通过一个本地命令行系统，把常见学习功能集中起来，形成一个简单、清晰、易扩展的学习助手原型。"),
    ("heading1", "三、项目目标"),
    ("bullet", "整合常见学习功能，减少工具切换成本"),
    ("bullet", "支持本地离线运行，不依赖外部网络接口"),
    ("bullet", "通过命令行菜单提供清晰的交互方式"),
    ("bullet", "使用本地文件和 SQLite 数据库存储学习记录"),
    ("heading1", "四、系统整体结构"),
    ("body", "项目采用模块化结构设计，不同功能分别放在独立的 Python 模块中，主程序负责统一调度。"),
    ("bullet", "main.py：项目主入口，负责显示菜单和调用各个模块"),
    ("bullet", "src/qa.py：知识问答模块"),
    ("bullet", "src/practice.py：题目练习与批改模块"),
    ("bullet", "src/plan.py：学习规划与进度跟踪模块"),
    ("bullet", "src/summary.py：资料整理与摘要生成模块"),
    ("bullet", "src/language.py：语言学习模块"),
    ("bullet", "src/tools.py：学习工具箱模块"),
    ("bullet", "src/utils.py：数据库初始化和通用工具函数"),
    ("heading1", "五、核心功能介绍"),
    ("heading2", "1. 知识问答"),
    ("body", "知识问答模块主要用于回答数学、英语、物理、编程等学科中的基础问题。系统通过内置知识库与本地数据文件进行关键词匹配，输出通俗解释、解题步骤以及常见易错点。"),
    ("heading2", "2. 题目练习与批改"),
    ("body", "练习模块支持按学科和难度生成题目，题型包括选择题、填空题和简答题。客观题采用直接比对的方式进行批改，简答题则通过文本相似度进行基础评分。答错的题目会自动写入数据库，形成错题本。"),
    ("heading2", "3. 学习计划与进度管理"),
    ("body", "学习计划模块可根据用户输入的学习目标、学习天数和学科列表，自动生成每日学习任务，并将任务保存到数据库中。用户还可以更新任务状态，系统会进一步生成学习进度报告。"),
    ("heading2", "4. 资料总结"),
    ("body", "资料整理模块支持文本摘要、章节提纲整理以及 Markdown 形式的思维导图生成，帮助用户快速提取学习资料中的重点内容。"),
    ("heading2", "5. 语言学习"),
    ("body", "语言学习模块包含单词训练、作文纠错和中英互译。单词训练支持基础复习逻辑，作文纠错支持简单语法规则检查，翻译功能则基于本地词汇映射进行实现。"),
    ("heading2", "6. 学习工具箱"),
    ("body", "工具箱模块包含公式速查、计算器、单位换算、进制转换、待办事项、课程表和倒计时等功能，补充了用户在学习过程中的常用辅助需求。"),
    ("heading1", "六、数据存储设计"),
    ("body", "项目的数据存储主要分为两部分：本地文件存储和 SQLite 数据库存储。"),
    ("bullet", "data/qa_data.jsonl：存储问答数据"),
    ("bullet", "data/questions.csv：存储题库数据"),
    ("bullet", "data/vocab.csv：存储词汇数据"),
    ("bullet", "data/learning_assistant.db：存储学习计划、任务、错题和词汇学习记录"),
    ("body", "这种设计方式保证了系统可以在无网络环境下独立运行，同时方便演示和后期扩展。"),
    ("heading1", "七、项目运行流程"),
    ("body", "用户运行 main.py 后，系统会显示主菜单。用户可以根据需要选择知识问答、练习、学习计划、资料总结、语言学习或工具箱模块。每个模块都会根据输入执行对应逻辑，并在需要时将结果保存到本地数据库。"),
    ("heading1", "八、项目亮点"),
    ("bullet", "功能覆盖面较广，贴近真实学习场景"),
    ("bullet", "结构清晰，模块之间职责分明"),
    ("bullet", "无需外部依赖，便于本地部署和课堂展示"),
    ("bullet", "支持错题、任务和词汇记录的本地持久化"),
    ("bullet", "具备继续扩展为图形界面或 Web 系统的基础"),
    ("heading1", "九、当前不足"),
    ("bullet", "问答能力主要依赖规则和内置知识库，智能程度有限"),
    ("bullet", "翻译和作文批改功能仍然较为基础"),
    ("bullet", "题库规模较小，覆盖面仍可继续扩大"),
    ("bullet", "部分工具状态没有完整持久化"),
    ("bullet", "项目中存在一些编码和测试一致性问题需要优化"),
    ("heading1", "十、后续优化方向"),
    ("bullet", "扩充知识库、题库和词汇数据"),
    ("bullet", "优化文本匹配、评分和摘要生成逻辑"),
    ("bullet", "增加图形界面或 Web 界面，提高易用性"),
    ("bullet", "引入更强的自然语言处理能力"),
    ("bullet", "完善测试和文档，提升工程稳定性"),
    ("heading1", "十一、总结"),
    ("body", "总体来看，智能学习助手是一个面向学习场景的本地化综合系统。它不仅演示了知识问答、练习批改、计划管理和资料整理等核心能力，也体现了模块化开发、数据持久化和功能整合的项目设计思路。"),
    ("body", "该项目适合作为课程设计、课堂答辩或学习型软件原型展示，并且具备较明确的后续扩展空间。"),
]


def content_types() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""


def root_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


def document_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>
"""


def app_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Office Word</Application>
</Properties>
"""


def core_xml() -> str:
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>智能学习助手项目介绍</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>
"""


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="等线"/>
        <w:sz w:val="24"/>
        <w:szCs w:val="24"/>
      </w:rPr>
    </w:rPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="等线"/>
      <w:sz w:val="24"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:jc w:val="center"/>
      <w:spacing w:after="240"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:eastAsia="等线" w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:b/>
      <w:sz w:val="36"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:spacing w:before="240" w:after="120"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:sz w:val="30"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:spacing w:before="160" w:after="80"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:sz w:val="26"/>
    </w:rPr>
  </w:style>
</w:styles>
"""


def paragraph_xml(style: str, text: str, bullet: bool = False) -> str:
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if bullet:
        ppr.append(
            '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
        )
        ppr.append('<w:ind w:left="720" w:hanging="360"/>')
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else ""
    return (
        f"<w:p>{ppr_xml}<w:r><w:t xml:space=\"preserve\">{escape(text)}</w:t></w:r></w:p>"
    )


def numbering_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="0">
    <w:nsid w:val="12345678"/>
    <w:multiLevelType w:val="hybridMultilevel"/>
    <w:tmpl w:val="12345678"/>
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/>
      <w:numFmt w:val="bullet"/>
      <w:lvlText w:val="•"/>
      <w:lvlJc w:val="left"/>
      <w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>
      <w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol" w:hint="default"/></w:rPr>
    </w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>
"""


def document_xml() -> str:
    body = []
    for kind, text in PARAGRAPHS:
        if kind == "title":
            body.append(paragraph_xml("Title", text))
        elif kind == "heading1":
            body.append(paragraph_xml("Heading1", text))
        elif kind == "heading2":
            body.append(paragraph_xml("Heading2", text))
        elif kind == "bullet":
            body.append(paragraph_xml("", text, bullet=True))
        else:
            body.append(paragraph_xml("", text))

    sect = """
<w:sectPr>
  <w:pgSz w:w="11906" w:h="16838"/>
  <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>
</w:sectPr>
"""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'xmlns:o="urn:schemas-microsoft-com:office:office" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
        'xmlns:v="urn:schemas-microsoft-com:vml" '
        'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:w10="urn:schemas-microsoft-com:office:word" '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
        'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
        'xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" '
        'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
        'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
        'mc:Ignorable="w14 wp14">'
        '<w:body>'
        + "".join(body)
        + sect
        + "</w:body></w:document>"
    )


def make_docx() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types())
        zf.writestr("_rels/.rels", root_rels())
        zf.writestr("docProps/app.xml", app_xml())
        zf.writestr("docProps/core.xml", core_xml())
        zf.writestr("word/document.xml", document_xml())
        zf.writestr("word/styles.xml", styles_xml())
        zf.writestr("word/numbering.xml", numbering_xml())
        zf.writestr("word/_rels/document.xml.rels", document_rels())


if __name__ == "__main__":
    make_docx()
    print(os.fspath(OUTPUT))
