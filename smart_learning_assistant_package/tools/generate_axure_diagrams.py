from __future__ import annotations

from pathlib import Path


DESKTOP = Path.home() / "Desktop"


TITLE_FONT = "'Microsoft YaHei', 'PingFang SC', sans-serif"


def svg_text(x: int, y: int, text: str, cls: str) -> str:
    return f'<text x="{x}" y="{y}" class="{cls}">{text}</text>'


def svg_multiline_text(x: int, y: int, lines: list[str], cls: str, line_gap: int = 20) -> str:
    return "".join(svg_text(x, y + i * line_gap, line, cls) for i, line in enumerate(lines))


def card(
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    lines: list[str],
    accent: str = "#2F6BFF",
    fill: str = "#FFFFFF",
    title_fill: str = "#1F2A37",
) -> str:
    header_h = 34
    body = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="#C9D2E3" stroke-width="1.5"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{header_h}" rx="8" fill="#F7F9FC" stroke="#C9D2E3" stroke-width="1.5"/>',
        f'<rect x="{x}" y="{y}" width="6" height="{header_h}" rx="8" fill="{accent}"/>',
        svg_text(x + 16, y + 22, title, "card-title" if title_fill == "#1F2A37" else "card-title-soft"),
        svg_multiline_text(x + 16, y + 58, lines, "card-text"),
    ]
    return "".join(body)


def lane(x: int, y: int, w: int, h: int, title: str) -> str:
    return "".join(
        [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#FCFDFF" stroke="#D7DEEA" stroke-width="1.5"/>',
            f'<rect x="{x}" y="{y}" width="{w}" height="44" rx="10" fill="#EEF3FB" stroke="#D7DEEA" stroke-width="1.5"/>',
            svg_text(x + 18, y + 28, title, "lane-title"),
        ]
    )


def connector(x1: int, y1: int, x2: int, y2: int, dashed: bool = False) -> str:
    dash = ' stroke-dasharray="7 6"' if dashed else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="#7B8798" stroke-width="2.2" marker-end="url(#arrow)"{dash}/>'
    )


def vertical_step_marker(x: int, y: int, label: str) -> str:
    return "".join(
        [
            f'<circle cx="{x}" cy="{y}" r="16" fill="#2F6BFF"/>',
            f'<text x="{x - 5}" y="{y + 6}" class="step-id">{label}</text>',
        ]
    )


def annotation(x: int, y: int, w: int, title: str, lines: list[str]) -> str:
    return "".join(
        [
            f'<rect x="{x}" y="{y}" width="{w}" height="{88 + max(0, len(lines) - 2) * 18}" rx="8" fill="#FFF9E8" stroke="#E8D28B" stroke-width="1.2"/>',
            svg_text(x + 14, y + 24, title, "note-title"),
            svg_multiline_text(x + 14, y + 50, lines, "note-text", 18),
        ]
    )


def build_flowchart_svg() -> str:
    title = "智能学习助手 功能流程图（Axure 线框风格）"
    subtitle = "角度：用户任务流 + 页面跳转 + 系统处理 + 数据结果"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1080" viewBox="0 0 1600 1080">
  <defs>
    <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
      <path d="M0,0 L12,6 L0,12 z" fill="#7B8798"/>
    </marker>
    <style>
      .page-title {{ font: 700 30px {TITLE_FONT}; fill: #16202A; }}
      .page-subtitle {{ font: 400 14px {TITLE_FONT}; fill: #66758A; }}
      .lane-title {{ font: 700 18px {TITLE_FONT}; fill: #304156; }}
      .card-title {{ font: 700 16px {TITLE_FONT}; fill: #1F2A37; }}
      .card-title-soft {{ font: 700 16px {TITLE_FONT}; fill: #415166; }}
      .card-text {{ font: 400 13px {TITLE_FONT}; fill: #4A5A70; }}
      .step-id {{ font: 700 14px {TITLE_FONT}; fill: #FFFFFF; }}
      .note-title {{ font: 700 15px {TITLE_FONT}; fill: #6A4A00; }}
      .note-text {{ font: 400 12px {TITLE_FONT}; fill: #6D5A1D; }}
      .footer-text {{ font: 400 13px {TITLE_FONT}; fill: #66758A; }}
    </style>
  </defs>

  <rect width="100%" height="100%" fill="#F5F7FA"/>
  {svg_text(40, 54, title, "page-title")}
  {svg_text(40, 80, subtitle, "page-subtitle")}

  {lane(40, 110, 300, 840, "泳道 A：用户操作")}
  {lane(370, 110, 360, 840, "泳道 B：页面与交互")}
  {lane(760, 110, 390, 840, "泳道 C：业务逻辑与系统处理")}
  {lane(1180, 110, 380, 840, "泳道 D：数据沉淀与输出")}

  {vertical_step_marker(24, 206, "1")}
  {card(66, 160, 248, 98, "打开首页", ["进入 Web 端", "查看今日学习概况"])}
  {card(396, 160, 310, 98, "首页 Dashboard", ["展示导航入口", "学习数据摘要与快捷入口"], accent="#8B5CF6")}
  {card(786, 160, 338, 98, "初始化首页数据", ["加载计划、错题、练习概况", "构建入口导航状态"], accent="#0EA5E9")}
  {card(1206, 160, 328, 98, "首页概览输出", ["近期任务", "学习状态摘要", "模块跳转路径"], accent="#10B981")}

  {connector(314, 209, 396, 209)}
  {connector(706, 209, 786, 209)}
  {connector(1124, 209, 1206, 209)}

  {vertical_step_marker(24, 356, "2")}
  {card(66, 310, 248, 116, "提出知识问题", ["例：“什么是质数？”", "或“什么是 Python？”"])}
  {card(396, 310, 310, 116, "知识问答页", ["输入问题并触发问答", "页面预留“去练习”入口"], accent="#8B5CF6")}
  {card(786, 310, 338, 116, "知识匹配与识别", ["抽取关键概念", "判断学科、年级、推荐题型"], accent="#0EA5E9")}
  {card(1206, 310, 328, 116, "结构化问答结果", ["answer", "subject / grade / concept", "practice recommendation"], accent="#10B981")}

  {connector(314, 369, 396, 369)}
  {connector(706, 369, 786, 369)}
  {connector(1124, 369, 1206, 369)}
  {annotation(1210, 438, 324, "交付说明", ["这一层对应 Axure 中的“问答结果状态面板”", "为后续练习跳转提供预置参数"])}

  {vertical_step_marker(24, 548, "3")}
  {card(66, 500, 248, 116, "点击“去练习”", ["使用问答的推荐参数", "无需再手动重新选项"])}
  {card(396, 500, 310, 116, "练习中心预置表单", ["自动带入学科、年级、题型、题量", "页面打开后可直接生成题目"], accent="#8B5CF6")}
  {card(786, 500, 338, 116, "生成练习题", ["按知识点过滤题库", "不足时执行可用题型回退"], accent="#0EA5E9")}
  {card(1206, 500, 328, 116, "练习列表输出", ["支持单选 / 多选 / 判断 / 简答", "记录本次练习任务"], accent="#10B981")}

  {connector(314, 559, 396, 559)}
  {connector(706, 559, 786, 559)}
  {connector(1124, 559, 1206, 559)}

  {vertical_step_marker(24, 720, "4")}
  {card(66, 660, 248, 140, "提交作答", ["用户完成客观题或简答题", "期待获得详细反馈"])}
  {card(396, 660, 310, 140, "结果反馈与错题本", ["展示分数、解析、你的答案", "错题本采用分页摘要 + 展开详情"], accent="#8B5CF6")}
  {card(786, 660, 338, 140, "智能判题与错题流转", ["客观题校验正确答案是否在选项中", "简答题按关键点覆盖度 + 表达接近度判定", "答错后进入错题本，答对后更新掌握状态"], accent="#0EA5E9")}
  {card(1206, 660, 328, 140, "学习记录沉淀", ["练习记录", "错题条目", "掌握次数与复习次数"], accent="#10B981")}

  {connector(314, 730, 396, 730)}
  {connector(706, 730, 786, 730)}
  {connector(1124, 730, 1206, 730)}

  {annotation(786, 820, 338, "错题本规则", ["不允许用户手动点击“复习一次”", "必须重新作答且答对后才计入掌握"])}

  {vertical_step_marker(24, 906, "5")}
  {card(66, 860, 248, 98, "新建学习计划", ["填写目标、周期、每日学习时间"])}
  {card(396, 860, 310, 98, "学习计划页", ["支持 0.5h 为单位", "展示进度报告、任务时间线"], accent="#8B5CF6")}
  {card(786, 860, 338, 98, "计划生成与标准化", ["后端规范学习时长", "生成每日任务与节奏建议"], accent="#0EA5E9")}
  {card(1206, 860, 328, 98, "进度报告", ["完成率", "任务分布", "时间投入与学习节奏"], accent="#10B981")}

  {connector(314, 909, 396, 909)}
  {connector(706, 909, 786, 909)}
  {connector(1124, 909, 1206, 909)}

  <rect x="40" y="974" width="1520" height="66" rx="10" fill="#FFFFFF" stroke="#D7DEEA" stroke-width="1.2"/>
  {svg_text(58, 1002, "闭环总结：知识问答解决“知道什么”，练习中心解决“会不会用”，错题本解决“错在哪里”，学习计划解决“怎么持续推进”。", "footer-text")}
  {svg_text(58, 1024, "这张图采用 Axure 常见的泳道 + 线框交付逻辑，适合直接放入产品文档或答辩 PPT。", "footer-text")}
</svg>
"""


def build_ia_svg() -> str:
    title = "智能学习助手 信息结构图（Axure Sitemap 风格）"
    subtitle = "角度：产品导航结构 + 页面层级 + 主要模块 + 跨页联动关系"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1120" viewBox="0 0 1600 1120">
  <defs>
    <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
      <path d="M0,0 L12,6 L0,12 z" fill="#7B8798"/>
    </marker>
    <style>
      .page-title {{ font: 700 30px {TITLE_FONT}; fill: #16202A; }}
      .page-subtitle {{ font: 400 14px {TITLE_FONT}; fill: #66758A; }}
      .card-title {{ font: 700 16px {TITLE_FONT}; fill: #1F2A37; }}
      .card-text {{ font: 400 13px {TITLE_FONT}; fill: #4A5A70; }}
      .section-title {{ font: 700 18px {TITLE_FONT}; fill: #304156; }}
      .tag-text {{ font: 700 12px {TITLE_FONT}; fill: #32507A; }}
      .footer-text {{ font: 400 13px {TITLE_FONT}; fill: #66758A; }}
    </style>
  </defs>

  <rect width="100%" height="100%" fill="#F5F7FA"/>
  {svg_text(40, 54, title, "page-title")}
  {svg_text(40, 80, subtitle, "page-subtitle")}

  <rect x="600" y="108" width="400" height="86" rx="10" fill="#FFFFFF" stroke="#BFD0EA" stroke-width="1.8"/>
  <rect x="600" y="108" width="400" height="34" rx="10" fill="#EAF1FF" stroke="#BFD0EA" stroke-width="1.8"/>
  {svg_text(620, 130, "产品根节点", "tag-text")}
  {svg_text(620, 164, "智能学习助手 Web 端", "card-title")}
  {svg_text(620, 186, "学习问答、计划生成、专题练习、错题复盘一体化", "card-text")}

  <rect x="90" y="240" width="1420" height="250" rx="10" fill="#FCFDFF" stroke="#D7DEEA" stroke-width="1.3"/>
  {svg_text(110, 270, "一级信息架构", "section-title")}
  {svg_text(110, 292, "对应 Axure 的 Sitemap 第一层：全局导航 + 核心业务页", "page-subtitle")}

  {card(124, 320, 220, 130, "首页 / Dashboard", ["项目入口", "学习概览", "快捷跳转"], accent="#2F6BFF")}
  {card(388, 320, 220, 130, "知识问答", ["输入问题", "展示答案", "推荐去练习"], accent="#8B5CF6")}
  {card(652, 320, 220, 130, "学习计划", ["新建计划", "进度报告", "任务时间线"], accent="#F59E0B")}
  {card(916, 320, 220, 130, "练习中心", ["选年级 / 学科", "选题型 / 题量", "生成题目"], accent="#0EA5E9")}
  {card(1180, 320, 220, 130, "错题本", ["分页摘要", "重新作答", "答对后掌握"], accent="#10B981")}

  {connector(800, 194, 234, 320, True)}
  {connector(800, 194, 498, 320, True)}
  {connector(800, 194, 762, 320, True)}
  {connector(800, 194, 1026, 320, True)}
  {connector(800, 194, 1290, 320, True)}

  <rect x="90" y="520" width="1420" height="320" rx="10" fill="#FCFDFF" stroke="#D7DEEA" stroke-width="1.3"/>
  {svg_text(110, 550, "二级模块拆解", "section-title")}
  {svg_text(110, 572, "对应每个页面内的主要信息分区与功能面板", "page-subtitle")}

  {card(110, 604, 260, 186, "首页模块", ["1. 学习概况卡片", "2. 快速入口导航", "3. 近期任务 / 提醒", "4. 学习数据简报"], accent="#2F6BFF")}
  {card(420, 604, 260, 186, "知识问答模块", ["1. 问题输入区", "2. 答案展示区", "3. 知识点识别结果", "4. 去练习联动按钮"], accent="#8B5CF6")}
  {card(730, 604, 260, 186, "学习计划模块", ["1. 计划表单", "2. 每日学习时长", "3. 进度报告大屏", "4. 任务时间线"], accent="#F59E0B")}
  {card(1040, 604, 260, 186, "练习中心模块", ["1. 条件筛选区", "2. 题目列表区", "3. 提交与判题", "4. 解析与反馈"], accent="#0EA5E9")}
  {card(1330, 604, 150, 186, "错题本模块", ["1. 摘要列表", "2. 展开详情", "3. 重答入口", "4. 掌握状态"], accent="#10B981")}

  {connector(234, 450, 240, 604)}
  {connector(498, 450, 550, 604)}
  {connector(762, 450, 860, 604)}
  {connector(1026, 450, 1170, 604)}
  {connector(1290, 450, 1405, 604)}

  <rect x="90" y="870" width="930" height="190" rx="10" fill="#FFFFFF" stroke="#D7DEEA" stroke-width="1.3"/>
  {svg_text(110, 900, "跨页联动关系", "section-title")}
  {svg_text(110, 922, "这部分建议在 Axure 中作为交互备注区域单独标注", "page-subtitle")}
  {card(118, 948, 200, 82, "知识问答 → 练习中心", ["携带 concept / subject / grade", "直接生成相关练习"], accent="#8B5CF6")}
  {card(346, 948, 200, 82, "练习中心 → 错题本", ["答错自动入库", "保存用户作答记录"], accent="#0EA5E9")}
  {card(574, 948, 200, 82, "错题本 → 掌握状态", ["重新作答", "答对后再标记已掌握"], accent="#10B981")}
  {card(802, 948, 190, 82, "学习计划 → 进度报告", ["任务拆分", "节奏和投入可视化"], accent="#F59E0B")}

  <rect x="1050" y="870" width="460" height="190" rx="10" fill="#FFFFFF" stroke="#D7DEEA" stroke-width="1.3"/>
  {svg_text(1070, 900, "支撑层（可在答辩时作为技术说明）", "section-title")}
  {card(1074, 926, 196, 104, "内容资源", ["本地知识库", "本地题库 questions.csv", "Python / 数学 / 英语等学科"], accent="#6366F1")}
  {card(1290, 926, 196, 104, "数据与服务", ["SQLite 记录计划、练习、错题", "Flask API 连接前后端", "简答题宽松判分"], accent="#14B8A6")}

  <rect x="40" y="1074" width="1520" height="26" rx="8" fill="#FFFFFF" stroke="#D7DEEA" stroke-width="1.2"/>
  {svg_text(58, 1092, "图示说明：蓝线重点为用户可见页面，右侧支撑层用于说明系统是如何支撑这些交互的。", "footer-text")}
</svg>
"""


def main() -> None:
    flow_path = DESKTOP / "product_function_flowchart.svg"
    ia_path = DESKTOP / "product_information_architecture.svg"
    flow_path.write_text(build_flowchart_svg(), encoding="utf-8")
    ia_path.write_text(build_ia_svg(), encoding="utf-8")
    print(flow_path)
    print(ia_path)


if __name__ == "__main__":
    main()
