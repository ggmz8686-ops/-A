from __future__ import annotations

import os
import zipfile
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Smart_Learning_Assistant_Presentation.pptx"


SLIDES = [
    (
        "Smart Learning Assistant",
        [
            "A local Python-based intelligent learning assistant",
            "Covers Q&A, practice, study planning, summarization, language learning, and study tools",
            "Suitable for classroom demos, course projects, and prototype presentations",
        ],
    ),
    (
        "Project Background",
        [
            "Students often switch between many separate tools while studying",
            "Common needs include asking questions, doing exercises, making plans, and reviewing materials",
            "We wanted one lightweight local system to connect these tasks",
        ],
    ),
    (
        "Project Goal",
        [
            "Integrate multiple study functions into one system",
            "Run fully offline without external APIs",
            "Provide a simple command-line interface",
            "Store learning records locally for later review",
        ],
    ),
    (
        "Overall Architecture",
        [
            "main.py: program entry and menu interaction",
            "qa.py: knowledge Q&A",
            "practice.py: question generation and grading",
            "plan.py: study plan and progress tracking",
            "summary.py / language.py / tools.py: support modules",
            "utils.py: shared utilities and database setup",
        ],
    ),
    (
        "Core Function 1: Knowledge Q&A",
        [
            "Supports common questions in math, English, physics, and programming",
            "Combines built-in knowledge with local data files",
            "Uses keyword matching to identify subject and concept",
            "Returns explanation, solving steps, and common mistakes",
        ],
    ),
    (
        "Core Function 2: Practice and Wrong-Question Book",
        [
            "Generates questions by subject and difficulty",
            "Supports multiple-choice, fill-in-the-blank, and short-answer questions",
            "Grades objective questions directly",
            "Uses text similarity for short-answer grading",
            "Stores wrong answers in SQLite",
        ],
    ),
    (
        "Core Function 3: Study Planning",
        [
            "Creates study plans based on goal, days, and subjects",
            "Automatically splits study hours across subjects",
            "Generates daily tasks",
            "Tracks task status: pending / in_progress / completed",
            "Produces a progress report from database records",
        ],
    ),
    (
        "Other Modules",
        [
            "Summary: text summarization, outline generation, Markdown mind map",
            "Language: vocabulary review, essay correction, Chinese-English translation",
            "Tools: formula lookup, calculator, unit conversion, base conversion",
            "Also includes todo list, schedule, and countdown",
        ],
    ),
    (
        "Data Storage and Local Design",
        [
            "qa_data.jsonl stores local Q&A data",
            "questions.csv stores question bank data",
            "vocab.csv stores vocabulary data",
            "learning_assistant.db stores plans, tasks, wrong questions, and vocab records",
            "All data stays on the local machine",
        ],
    ),
    (
        "Typical User Flow",
        [
            "Start the program from the command line",
            "Choose a module from the main menu",
            "Ask a question, practice exercises, or create a plan",
            "Save progress and wrong answers automatically",
            "Return later to review reports and continue learning",
        ],
    ),
    (
        "Project Highlights",
        [
            "Clear modular structure",
            "Fully local and easy to deploy",
            "Covers multiple learning scenarios",
            "Includes persistent storage with SQLite",
            "Suitable as a teaching demo or prototype system",
        ],
    ),
    (
        "Current Limitations",
        [
            "Rule-based Q&A is limited compared with real AI systems",
            "Translation and essay correction are relatively simple",
            "Question bank size is still small",
            "Some tool state is not fully persistent",
            "There are encoding and test consistency issues to clean up",
        ],
    ),
    (
        "Future Work",
        [
            "Expand the local knowledge base and question bank",
            "Improve answer matching and grading logic",
            "Add a GUI or web interface",
            "Introduce smarter NLP or model-based capabilities",
            "Optimize persistence, tests, and text encoding",
        ],
    ),
    (
        "Thank You",
        [
            "Our project builds a local intelligent learning assistant",
            "It supports questioning, practicing, planning, reviewing, and utility tools",
            "It demonstrates both educational value and software modularity",
        ],
    ),
]


def emu(inches: float) -> int:
    return int(inches * 914400)


def slide_xml(title: str, bullets: list[str]) -> str:
    title_runs = (
        '<a:p><a:r><a:rPr lang="en-US" sz="2800" b="1"/>'
        f"<a:t>{escape(title)}</a:t></a:r><a:endParaRPr lang=\"en-US\" sz=\"2800\"/></a:p>"
    )

    body_parts = []
    for bullet in bullets:
        body_parts.append(
            '<a:p marL="342900" indent="-285750">'
            '<a:pPr lvl="0"><a:buChar char="•"/></a:pPr>'
            '<a:r><a:rPr lang="en-US" sz="2000"/>'
            f"<a:t>{escape(bullet)}</a:t></a:r>"
            '<a:endParaRPr lang="en-US" sz="2000"/>'
            "</a:p>"
        )
    body_xml = "".join(body_parts)

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
 <p:cSld>
  <p:spTree>
   <p:nvGrpSpPr>
    <p:cNvPr id="1" name=""/>
    <p:cNvGrpSpPr/>
    <p:nvPr/>
   </p:nvGrpSpPr>
   <p:grpSpPr>
    <a:xfrm>
     <a:off x="0" y="0"/>
     <a:ext cx="0" cy="0"/>
     <a:chOff x="0" y="0"/>
     <a:chExt cx="0" cy="0"/>
    </a:xfrm>
   </p:grpSpPr>
   <p:sp>
    <p:nvSpPr>
     <p:cNvPr id="2" name="Title 1"/>
     <p:cNvSpPr/>
     <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
     <a:xfrm>
      <a:off x="{emu(0.7)}" y="{emu(0.5)}"/>
      <a:ext cx="{emu(11.0)}" cy="{emu(1.0)}"/>
     </a:xfrm>
    </p:spPr>
    <p:txBody>
     <a:bodyPr/>
     <a:lstStyle/>
     {title_runs}
    </p:txBody>
   </p:sp>
   <p:sp>
    <p:nvSpPr>
     <p:cNvPr id="3" name="Content Placeholder 2"/>
     <p:cNvSpPr/>
     <p:nvPr/>
    </p:nvSpPr>
    <p:spPr>
     <a:xfrm>
      <a:off x="{emu(0.95)}" y="{emu(1.7)}"/>
      <a:ext cx="{emu(10.4)}" cy="{emu(4.9)}"/>
     </a:xfrm>
    </p:spPr>
    <p:txBody>
     <a:bodyPr wrap="square"/>
     <a:lstStyle/>
     {body_xml}
    </p:txBody>
   </p:sp>
  </p:spTree>
 </p:cSld>
 <p:clrMapOvr>
  <a:masterClrMapping/>
 </p:clrMapOvr>
</p:sld>
"""


def presentation_xml() -> str:
    slide_ids = []
    base = 256
    for i in range(len(SLIDES)):
        slide_ids.append(f'<p:sldId id="{base + i}" r:id="rId{i + 1}"/>')
    ids_xml = "".join(slide_ids)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
 saveSubsetFonts="1" autoCompressPictures="0">
 <p:sldMasterIdLst>
  <p:sldMasterId id="2147483648" r:id="rId{len(SLIDES) + 1}"/>
 </p:sldMasterIdLst>
 <p:sldIdLst>{ids_xml}</p:sldIdLst>
 <p:sldSz cx="12192000" cy="6858000"/>
 <p:notesSz cx="6858000" cy="9144000"/>
 <p:defaultTextStyle>
  <a:defPPr>
   <a:defRPr lang="en-US"/>
  </a:defPPr>
 </p:defaultTextStyle>
</p:presentation>
"""


def presentation_rels_xml() -> str:
    rels = []
    for i in range(len(SLIDES)):
        rels.append(
            f'<Relationship Id="rId{i + 1}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" '
            f'Target="slides/slide{i + 1}.xml"/>'
        )
    rels.append(
        f'<Relationship Id="rId{len(SLIDES) + 1}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" '
        'Target="slideMasters/slideMaster1.xml"/>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(rels)
        + "</Relationships>"
    )


def content_types_xml() -> str:
    overrides = [
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]
    for i in range(len(SLIDES)):
        overrides.append(
            f'<Override PartName="/ppt/slides/slide{i + 1}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        + "".join(overrides)
        + "</Types>"
    )


def root_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
 <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
 <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


def app_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
 <Application>Microsoft Office PowerPoint</Application>
 <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
 <Slides>{len(SLIDES)}</Slides>
 <Notes>0</Notes>
 <HiddenSlides>0</HiddenSlides>
 <MMClips>0</MMClips>
 <ScaleCrop>false</ScaleCrop>
 <HeadingPairs>
  <vt:vector size="2" baseType="variant">
   <vt:variant><vt:lpstr>Slides</vt:lpstr></vt:variant>
   <vt:variant><vt:i4>{len(SLIDES)}</vt:i4></vt:variant>
  </vt:vector>
 </HeadingPairs>
 <TitlesOfParts>
  <vt:vector size="{len(SLIDES)}" baseType="lpstr">
   {''.join(f'<vt:lpstr>{escape(title)}</vt:lpstr>' for title, _ in SLIDES)}
  </vt:vector>
 </TitlesOfParts>
 <Company></Company>
 <LinksUpToDate>false</LinksUpToDate>
 <SharedDoc>false</SharedDoc>
 <HyperlinksChanged>false</HyperlinksChanged>
 <AppVersion>16.0000</AppVersion>
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
 <dc:title>Smart Learning Assistant Presentation</dc:title>
 <dc:creator>Codex</dc:creator>
 <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
 <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
 <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>
"""


def slide_master_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
 <p:cSld name="Office Theme">
  <p:bg>
   <p:bgRef idx="1001">
    <a:schemeClr val="bg1"/>
   </p:bgRef>
  </p:bg>
  <p:spTree>
   <p:nvGrpSpPr>
    <p:cNvPr id="1" name=""/>
    <p:cNvGrpSpPr/>
    <p:nvPr/>
   </p:nvGrpSpPr>
   <p:grpSpPr>
    <a:xfrm>
     <a:off x="0" y="0"/>
     <a:ext cx="0" cy="0"/>
     <a:chOff x="0" y="0"/>
     <a:chExt cx="0" cy="0"/>
    </a:xfrm>
   </p:grpSpPr>
  </p:spTree>
 </p:cSld>
 <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
 <p:sldLayoutIdLst>
  <p:sldLayoutId id="2147483649" r:id="rId1"/>
 </p:sldLayoutIdLst>
 <p:txStyles>
  <p:titleStyle/>
  <p:bodyStyle/>
  <p:otherStyle/>
 </p:txStyles>
</p:sldMaster>
"""


def slide_master_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
 <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>
"""


def slide_layout_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="tx" preserve="1">
 <p:cSld name="Title and Content">
  <p:spTree>
   <p:nvGrpSpPr>
    <p:cNvPr id="1" name=""/>
    <p:cNvGrpSpPr/>
    <p:nvPr/>
   </p:nvGrpSpPr>
   <p:grpSpPr>
    <a:xfrm>
     <a:off x="0" y="0"/>
     <a:ext cx="0" cy="0"/>
     <a:chOff x="0" y="0"/>
     <a:chExt cx="0" cy="0"/>
    </a:xfrm>
   </p:grpSpPr>
  </p:spTree>
 </p:cSld>
 <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>
"""


def slide_layout_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>
"""


def theme_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
 <a:themeElements>
  <a:clrScheme name="Office">
   <a:dk1><a:srgbClr val="1F1F1F"/></a:dk1>
   <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
   <a:dk2><a:srgbClr val="44546A"/></a:dk2>
   <a:lt2><a:srgbClr val="E7E6E6"/></a:lt2>
   <a:accent1><a:srgbClr val="5B9BD5"/></a:accent1>
   <a:accent2><a:srgbClr val="ED7D31"/></a:accent2>
   <a:accent3><a:srgbClr val="A5A5A5"/></a:accent3>
   <a:accent4><a:srgbClr val="FFC000"/></a:accent4>
   <a:accent5><a:srgbClr val="4472C4"/></a:accent5>
   <a:accent6><a:srgbClr val="70AD47"/></a:accent6>
   <a:hlink><a:srgbClr val="0563C1"/></a:hlink>
   <a:folHlink><a:srgbClr val="954F72"/></a:folHlink>
  </a:clrScheme>
  <a:fontScheme name="Office">
   <a:majorFont>
    <a:latin typeface="Aptos Display"/>
    <a:ea typeface=""/>
    <a:cs typeface=""/>
   </a:majorFont>
   <a:minorFont>
    <a:latin typeface="Aptos"/>
    <a:ea typeface=""/>
    <a:cs typeface=""/>
   </a:minorFont>
  </a:fontScheme>
  <a:fmtScheme name="Office">
   <a:fillStyleLst>
    <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
   </a:fillStyleLst>
   <a:lnStyleLst>
    <a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
   </a:lnStyleLst>
   <a:effectStyleLst>
    <a:effectStyle><a:effectLst/></a:effectStyle>
   </a:effectStyleLst>
   <a:bgFillStyleLst>
    <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
   </a:bgFillStyleLst>
  </a:fmtScheme>
 </a:themeElements>
 <a:objectDefaults/>
 <a:extraClrSchemeLst/>
</a:theme>
"""


def make_pptx() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml())
        zf.writestr("_rels/.rels", root_rels_xml())
        zf.writestr("docProps/app.xml", app_xml())
        zf.writestr("docProps/core.xml", core_xml())
        zf.writestr("ppt/presentation.xml", presentation_xml())
        zf.writestr("ppt/_rels/presentation.xml.rels", presentation_rels_xml())
        zf.writestr("ppt/slideMasters/slideMaster1.xml", slide_master_xml())
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels_xml())
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout_xml())
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels_xml())
        zf.writestr("ppt/theme/theme1.xml", theme_xml())
        for i, (title, bullets) in enumerate(SLIDES, start=1):
            zf.writestr(f"ppt/slides/slide{i}.xml", slide_xml(title, bullets))


if __name__ == "__main__":
    make_pptx()
    print(os.fspath(OUTPUT))
