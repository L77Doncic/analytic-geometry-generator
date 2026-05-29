"""
解析几何题目生成器 — TUI 交互界面
Analytic Geometry Problem Generator — Terminal UI

参考 DeepSeek TUI / Claude Code 的交互形式
设计规范参考 Anthropic DESIGN.md (cream + coral)
"""

import os
import re
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Input, RichLog, Button,
    Label, DataTable, Markdown
)

# Divider replacement for older textual versions
class Divider(Static):
    def __init__(self):
        super().__init__("─" * 40, classes="divider")
from textual.reactive import reactive
from textual.message import Message
from textual import work

# Import our problem generators
from interactive_generator import (
    generate_ellipse_dynamic,
    generate_hyperbola_dynamic,
    generate_parabola_dynamic,
    generate_polar_dynamic,
)
from diagram_renderer import DiagramRenderer
from latex_render import latex_to_unicode, render_problem_text

# ==================== DESIGN TOKENS (DESIGN.md) ====================
# Warm cream + coral palette

CANVAS = "#faf9f5"
SURFACE_CARD = "#efe9de"
SURFACE_DARK = "#181715"
PRIMARY = "#cc785c"
PRIMARY_ACTIVE = "#a9583e"
INK = "#141413"
BODY = "#3d3d3a"
MUTED = "#6c6a64"
MUTED_SOFT = "#8e8b82"
HAIRLINE = "#e6dfd8"
ACCENT_TEAL = "#5db8a6"
ACCENT_AMBER = "#e8a55a"

OUTPUT_DIR = "/root/analytic_geometry_generator/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==================== PARSER ====================

def parse_user_input(text: str) -> dict:
    """
    解析用户自然语言输入，提取知识点、参数、题型。

    支持的输入格式：
    - "椭圆 a=5 b=3"
    - "双曲线 基础题"
    - "抛物线 p=4 弦长题 k=1"
    - "极坐标 r=3 直线与圆"
    - "ellipse a=5 b=3 chord"
    - "hyperbola basic"
    """
    text = text.strip().lower()
    result = {
        "topic": None,
        "problem_type": "basic",
        "params": {},
        "slope": None,
    }

    # ---- 识别知识点 ----
    topic_map = {
        "椭圆": "ellipse", "ellipse": "ellipse", "ell": "ellipse",
        "双曲线": "hyperbola", "双": "hyperbola", "hyperbola": "hyperbola", "hyp": "hyperbola",
        "抛物线": "parabola", "抛物": "parabola", "parabola": "parabola", "par": "parabola",
        "极坐标": "polar", "极": "polar", "polar": "polar",
    }
    for keyword, topic in topic_map.items():
        if keyword in text:
            result["topic"] = topic
            break

    # ---- 识别题型 ----
    type_map = {
        "基础": "basic", "基本": "basic", "标准方程": "basic", "basic": "basic",
        "弦长": "chord", "焦点弦": "chord", "弦": "chord", "chord": "chord",
        "焦点三角形": "focus_triangle", "三角形": "focus_triangle", "focus_triangle": "focus_triangle",
        "直线与圆": "line_circle", "line_circle": "line_circle",
        "性质": "property", "证明": "property", "property": "property",
        "极坐标方程": "conic", "conic": "conic",
        # 高考压轴 / 竞赛题型
        "定点": "fixed_point", "定值": "fixed_point", "fixed_point": "fixed_point",
        "面积最值": "area_opt", "最值": "area_opt", "area_opt": "area_opt",
        "离心率": "ecc_range", "范围": "ecc_range", "ecc_range": "ecc_range",
        "切线": "tangent", "极点极线": "tangent", "tangent": "tangent",
        "第三定义": "third_def", "斜率积": "third_def", "third_def": "third_def",
        "阿基米德": "archimedes", "archimedes": "archimedes",
        "渐近线": "asymptote_angle", "asymptote_angle": "asymptote_angle",
    }
    for keyword, ptype in type_map.items():
        if keyword in text:
            result["problem_type"] = ptype
            break

    # ---- 识别参数 ----
    # a=5, b=3, p=4, r=3, k=1.5
    param_patterns = {
        "a": r"a\s*[=＝]\s*([\d.]+)",
        "b": r"b\s*[=＝]\s*([\d.]+)",
        "p": r"p\s*[=＝]\s*([\d.]+)",
        "r": r"r\s*[=＝]\s*([\d.]+)",
        "k": r"k\s*[=＝]\s*([\d.]+)",
        "斜率": r"斜率\s*[=＝]?\s*([\d.]+)",
    }
    for key, pattern in param_patterns.items():
        match = re.search(pattern, text)
        if match:
            val = float(match.group(1))
            if key in ("k", "斜率"):
                result["slope"] = val
            else:
                result["params"][key] = val

    # ---- 识别难度 ----
    if "竞赛" in text or "难" in text or "高级" in text or "压轴" in text:
        # 自动从高难度题型中随机选择
        import random as _rand
        hard_types = {
            "ellipse": ["fixed_point", "area_opt", "ecc_range", "tangent", "third_def"],
            "hyperbola": ["asymptote_angle", "area_opt", "focus_triangle"],
            "parabola": ["archimedes", "fixed_point", "property"],
            "polar": ["conic"],
        }
        if result["topic"] in hard_types:
            result["problem_type"] = _rand.choice(hard_types[result["topic"]])
    elif "进阶" in text or "中等" in text:
        if result["topic"] == "ellipse":
            result["problem_type"] = "chord"
        elif result["topic"] == "hyperbola":
            result["problem_type"] = "chord"
        elif result["topic"] == "parabola":
            result["problem_type"] = "chord"
        elif result["topic"] == "polar":
            result["problem_type"] = "line_circle"

    # ---- 自动推断题型 ----
    if result["topic"] and result["problem_type"] == "basic":
        if result["slope"] is not None:
            result["problem_type"] = "chord"

    return result


# ==================== TUI APP ====================

class GeometryTUI(App):
    """解析几何题目生成器 TUI"""

    TITLE = "解析几何题目生成器"
    SUB_TITLE = "Interactive Analytic Geometry Generator"

    CSS = f"""
    Screen {{
        background: {CANVAS};
    }}

    #sidebar {{
        width: 28%;
        min-width: 28;
        background: {SURFACE_CARD};
        border-right: solid {HAIRLINE};
        padding: 1 2;
    }}

    #sidebar-title {{
        color: {PRIMARY};
        text-style: bold;
        content-align: center top;
        height: 3;
        padding-top: 1;
    }}

    #main {{
        width: 72%;
    }}

    #chat {{
        height: 1fr;
        padding: 1 2;
    }}

    #input-bar {{
        height: 5;
        padding: 0 2;
        background: {SURFACE_CARD};
        border-top: solid {HAIRLINE};
    }}

    .user-msg {{
        color: {PRIMARY};
        text-style: bold;
        margin: 0 0 1 0;
    }}

    .bot-msg {{
        color: {INK};
        margin: 0 0 1 0;
    }}

    .code-block {{
        background: {SURFACE_DARK};
        color: #faf9f5;
        padding: 1 2;
        margin: 0 0 1 0;
    }}

    .highlight {{
        color: {ACCENT_TEAL};
        text-style: bold;
    }}

    .muted {{
        color: {MUTED};
    }}

    .success {{
        color: {ACCENT_TEAL};
    }}

    .warning {{
        color: {ACCENT_AMBER};
    }}

    .help-item {{
        color: {BODY};
        margin: 0 0 0 2;
    }}

    .help-cmd {{
        color: {PRIMARY};
        text-style: bold;
    }}

    Button {{
        background: {PRIMARY};
        color: #ffffff;
        height: 3;
        min-width: 16;
    }}

    Button:hover {{
        background: {PRIMARY_ACTIVE};
    }}

    Input {{
        background: {CANVAS};
        border: solid {HAIRLINE};
        height: 3;
        color: {INK};
    }}

    Input:focus {{
        border: solid {PRIMARY};
    }}
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "退出"),
        Binding("ctrl+l", "clear", "清空对话"),
        Binding("ctrl+h", "help", "帮助"),
        Binding("ctrl+s", "save", "保存当前题目"),
    ]

    # ---- 响应式状态 ----
    current_problem = reactive(None)
    chat_history = reactive([])

    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Header(show_clock=True, name="解析几何题目生成器")

        with Horizontal():
            # 左侧边栏
            with Vertical(id="sidebar"):
                yield Static("📐 解析几何生成器", id="sidebar-title")
                yield Divider()
                yield Static("快捷命令", classes="muted")
                yield Static("  椭圆 a=5 b=3", classes="help-item")
                yield Static("  双曲线 a=3 b=4 基础", classes="help-item")
                yield Static("  抛物线 p=4 弦长", classes="help-item")
                yield Static("  极坐标 r=3 直线与圆", classes="help-item")
                yield Divider()
                yield Static("参数说明", classes="muted")
                yield Static("  a — 半长轴/半实轴", classes="help-item")
                yield Static("  b — 半短轴/半虚轴", classes="help-item")
                yield Static("  p — 抛物线焦距参数", classes="help-item")
                yield Static("  r — 极坐标圆半径", classes="help-item")
                yield Static("  k — 弦斜率", classes="help-item")
                yield Divider()
                yield Static("题型", classes="muted")
                yield Static("  basic — 基础题", classes="help-item")
                yield Static("  chord — 焦点弦", classes="help-item")
                yield Static("  focus_triangle — 焦点三角形", classes="help-item")
                yield Static("  line_circle — 直线与圆", classes="help-item")
                yield Static("  property — 性质证明", classes="help-item")
                yield Divider()
                yield Static("快捷键", classes="muted")
                yield Static("  Ctrl+Q 退出", classes="help-item")
                yield Static("  Ctrl+L 清空", classes="help-item")
                yield Static("  Ctrl+S 保存", classes="help-item")
                yield Static("  Ctrl+H 帮助", classes="help-item")

            # 右侧主区域
            with Vertical(id="main"):
                with ScrollableContainer(id="chat"):
                    yield Static("欢迎使用解析几何题目生成器！", classes="bot-msg")
                    yield Static("输入题目需求，例如：「椭圆 a=5 b=3」", classes="muted")
                    yield Static("系统将自动生成 LaTeX 题干、解答和精确配图。", classes="muted")

                with Horizontal(id="input-bar"):
                    yield Input(placeholder="输入题目需求，例如：椭圆 a=5 b=3 ...",
                                id="user-input")
                    yield Button("生成", id="generate-btn", variant="primary")

        yield Footer()

    def on_mount(self):
        """启动时聚焦输入框"""
        self.query_one("#user-input").focus()

    # ---- 事件处理 ----

    def on_input_submitted(self, event: Input.Submitted):
        """回车提交"""
        self._process_input(event.value)

    def on_button_pressed(self, event: Button.Pressed):
        """按钮点击"""
        if event.button.id == "generate-btn":
            input_widget = self.query_one("#user-input")
            self._process_input(input_widget.value)

    def _process_input(self, text: str):
        """处理用户输入"""
        if not text.strip():
            return

        # 显示用户消息
        chat = self.query_one("#chat")
        chat.mount(Static(f"  You: {text}", classes="user-msg"))

        # 清空输入框
        self.query_one("#user-input").value = ""

        # 特殊命令
        if text.strip() in ("help", "帮助", "?", "h"):
            self._show_help()
            return
        if text.strip() in ("clear", "清空", "cls"):
            self.action_clear()
            return
        if text.strip() in ("random", "随机", "rand"):
            self._generate_random()
            return

        # 解析并生成
        self._work_generate(text)

    @work(exclusive=True, thread=True)
    def _work_generate(self, text: str):
        """异步生成题目（在后台线程运行，通过 call_from_thread 更新 UI）"""
        # 解析输入
        parsed = parse_user_input(text)

        if not parsed["topic"]:
            self.call_from_thread(self._append_chat,
                Static("  ⚠ 无法识别知识点。请输入：椭圆/双曲线/抛物线/极坐标\n"
                       "  例如：椭圆 a=5 b=3", classes="warning"))
            return

        try:
            # 生成题目（纯计算，可在后台线程运行）
            problem = self._generate_problem(parsed)
            self.current_problem = problem

            # 创建时间戳目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            question_dir = os.path.join(OUTPUT_DIR, f"Question_{timestamp}")
            os.makedirs(question_dir, exist_ok=True)

            # 渲染配图
            renderer = DiagramRenderer(figsize=(10, 8), dpi=150)
            img_path = os.path.join(question_dir, "diagram.png")
            renderer.render(problem, img_path)

            # 保存 LaTeX 题干
            latex_path = os.path.join(question_dir, "problem.tex")
            with open(latex_path, "w", encoding="utf-8") as f:
                f.write(f"% {problem.title}\n\n")
                f.write(problem.problem_latex)

            # 保存 LaTeX 解答
            sol_path = os.path.join(question_dir, "solution.tex")
            with open(sol_path, "w", encoding="utf-8") as f:
                f.write(f"% {problem.title} — 解答\n\n")
                f.write(problem.solution_latex)

            # 保存纯文本版本（Unicode 渲染后的）
            txt_path = os.path.join(question_dir, "problem.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"{'='*50}\n")
                f.write(f"{problem.title}\n")
                f.write(f"{'='*50}\n\n")
                f.write(render_problem_text(problem.problem_latex))
                f.write(f"\n\n{'─'*50}\n\n")
                f.write(render_problem_text(problem.solution_latex))

            # 构建消息列表（纯数据，不涉及 UI）
            # 将 LaTeX 渲染为 Unicode 用于终端显示
            problem_text = render_problem_text(problem.problem_latex)
            solution_text = render_problem_text(problem.solution_latex)

            messages = []
            messages.append(Static(f"  ━━━ {problem.title} ━━━", classes="highlight"))
            messages.append(Static(f"\n  【题干】", classes="highlight"))
            for line in problem_text.split("\n"):
                if line.strip():
                    messages.append(Static(f"  {line}", classes="bot-msg"))
            messages.append(Static(f"\n  【解答】", classes="highlight"))
            for line in solution_text.split("\n"):
                if line.strip():
                    messages.append(Static(f"  {line}", classes="bot-msg"))
            messages.append(Static(
                f"\n  ✓ 已保存到: {question_dir}/"
                f"\n    ├── diagram.png   (配图)"
                f"\n    ├── problem.tex   (LaTeX 题干)"
                f"\n    ├── solution.tex  (LaTeX 解答)"
                f"\n    └── problem.txt   (纯文本版)",
                classes="success"))

            # 回到主线程更新 UI
            self.call_from_thread(self._append_chat_list, messages)

        except Exception as e:
            self.call_from_thread(self._append_chat,
                Static(f"  ✗ 生成失败: {str(e)}", classes="warning"))

    def _append_chat(self, widget):
        """在主线程中向 chat 追加单个 widget"""
        chat = self.query_one("#chat")
        chat.mount(widget)
        chat.scroll_end(animate=False)

    def _append_chat_list(self, widgets):
        """在主线程中向 chat 追加多个 widget"""
        chat = self.query_one("#chat")
        for w in widgets:
            chat.mount(w)
        chat.scroll_end(animate=False)

    def _generate_problem(self, parsed: dict):
        """根据解析结果生成题目"""
        topic = parsed["topic"]
        ptype = parsed["problem_type"]
        params = parsed["params"]
        slope = parsed["slope"]

        if topic == "ellipse":
            return generate_ellipse_dynamic(
                a=params.get("a"), b=params.get("b"),
                problem_type=ptype, slope=slope)
        elif topic == "hyperbola":
            return generate_hyperbola_dynamic(
                a=params.get("a"), b=params.get("b"),
                problem_type=ptype, slope=slope)
        elif topic == "parabola":
            return generate_parabola_dynamic(
                p=params.get("p"), problem_type=ptype, slope=slope)
        elif topic == "polar":
            return generate_polar_dynamic(
                r=params.get("r"), problem_type=ptype)

    def _generate_random(self):
        """随机生成一道题"""
        import random
        topics = ["ellipse", "hyperbola", "parabola", "polar"]
        topic = random.choice(topics)
        ptype = random.choice(["basic", "chord"])

        fake_input = f"{topic} {ptype}"
        self._work_generate(fake_input)

    def _show_help(self):
        """显示帮助"""
        chat = self.query_one("#chat")
        help_text = """
  ━━━ 使用帮助 ━━━

  输入格式：[知识点] [参数] [题型]

  知识点：
    椭圆 / ellipse        双曲线 / hyperbola
    抛物线 / parabola     极坐标 / polar

  参数：
    a=数值   半长轴/半实轴
    b=数值   半短轴/半虚轴
    p=数值   抛物线焦距参数
    r=数值   极坐标圆半径
    k=数值   弦斜率

  题型：
    basic         基础题（标准方程）
    chord         焦点弦问题
    focus_triangle 焦点三角形（竞赛）
    line_circle   直线与圆（极坐标）
    property      性质证明（抛物线）

  示例：
    椭圆 a=5 b=3
    双曲线 a=3 b=4 基础
    抛物线 p=4 弦长 k=1
    极坐标 r=3 直线与圆
    ellipse a=5 b=3 chord
    hyperbola basic
    random （随机生成）

  快捷键：
    Ctrl+Q  退出
    Ctrl+L  清空对话
    Ctrl+S  保存当前题目
    Ctrl+H  帮助
"""
        chat.mount(Static(help_text, classes="bot-msg"))
        chat.scroll_end(animate=False)

    # ---- 快捷键动作 ----

    def action_clear(self):
        """清空对话"""
        chat = self.query_one("#chat")
        chat.remove_children()
        chat.mount(Static("对话已清空。输入题目需求开始生成。", classes="muted"))
        self.current_problem = None

    def action_help(self):
        """显示帮助"""
        self._show_help()

    def action_save(self):
        """保存当前题目"""
        if self.current_problem is None:
            chat = self.query_one("#chat")
            chat.mount(Static("  ⚠ 没有可保存的题目", classes="warning"))
            return

        problem = self.current_problem
        # 保存 LaTeX
        tex_path = os.path.join(OUTPUT_DIR, f"{problem.topic}_saved.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(f"% {problem.title}\n\n")
            f.write(problem.problem_latex)
            f.write("\n\n% ===== 解答 =====\n\n")
            f.write(problem.solution_latex)

        chat = self.query_one("#chat")
        chat.mount(Static(f"  ✓ 已保存 LaTeX: {tex_path}", classes="success"))
        chat.scroll_end(animate=False)


# ==================== MAIN ====================

def main():
    """启动 TUI 应用"""
    app = GeometryTUI()
    app.run()


if __name__ == "__main__":
    main()
