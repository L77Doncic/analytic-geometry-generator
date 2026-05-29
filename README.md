<h1 align="center">📐 解析几何题目生成系统</h1>

<p align="center">
  <em>基于数学参数的动态解析几何题目生成 · TUI 交互 · 精确配图 · LaTeX 输出</em>
</p>

<p align="center">
  <a href="https://github.com/L77Doncic/analytic-geometry-generator/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
  <a href="https://github.com/L77Doncic/analytic-geometry-generator">
    <img src="https://img.shields.io/badge/python-3.10+-green.svg" alt="Python">
  </a>
  <a href="https://github.com/L77Doncic/analytic-geometry-generator">
    <img src="https://img.shields.io/badge/TUI-Textual-orange.svg" alt="TUI">
  </a>
</p>

---

根据用户指定的知识点、参数和难度等级，自动生成可解的解析几何题目，配以精确的 Matplotlib 渲染配图，并通过 TUI 交互界面实时展示。

## Quick Start

```bash
# 安装依赖
pip install numpy matplotlib textual rich python-pptx

# 启动 TUI
python3 run.py
```

在 TUI 中输入：

```
椭圆 a=5 b=3           # 指定参数
椭圆 竞赛              # 自动选高难度
抛物线 p=4 弦长 k=1    # 焦点弦题
random                 # 随机生成
```

## Key Features

**1. 动态题目生成**：用户可指定椭圆/双曲线/抛物线/极坐标的任意参数，系统自动计算交点、韦达定理推导，生成完整可解题目。

**2. 13 种题型覆盖**：从基础标准方程到高考压轴（定点证明、面积最值、离心率范围）和竞赛难度（阿基米德三角形、极点极线、第三定义）。

**3. 精确配图渲染**：Matplotlib 参数方程绘制，1000 采样点，焦点/渐近线/准线精确标注，坐标轴等比例显示。

**4. LaTeX → Unicode 终端渲染**：分数 `x²/25`、根号 `√(a²−b²)`、希腊字母 `α β π θ`、上下标 `F₁ F₂` 直接在终端显示。

**5. TUI 交互界面**：Chat-style 输入，可拖动分栏，侧边栏显示所有快捷命令和题型说明。

**6. 时间戳输出**：每次生成自动创建 `output/Question_YYYYMMDD_HHMMSS/` 目录，包含 `diagram.png`、`problem.tex`、`solution.tex`、`problem.txt`。

**7. 难度自动路由**：说"竞赛"/"压轴"/"难"自动从高难度题型中随机选择，无需记忆具体题型名。

## Supported Topics & Problem Types

| Topic | Basic | Intermediate | Competition / 压轴 |
|-------|-------|-------------|-------------------|
| **Ellipse** 椭圆 | 标准方程、焦点 | 焦点弦 | 定点证明、面积最值、离心率范围、切线/极点极线、第三定义 |
| **Hyperbola** 双曲线 | 标准方程、渐近线 | 焦点弦 | 渐近线平行弦、焦点三角形面积 |
| **Parabola** 抛物线 | 标准方程、焦点 | 焦点弦 | 阿基米德三角形、定点证明 |
| **Polar** 极坐标 | 坐标互化 | 直线与圆 | 圆锥曲线极坐标方程 |

## Input Format

```
[知识点] [参数] [题型]
```

| Component | Required | Default | Example |
|-----------|----------|---------|---------|
| 知识点 | ✅ | — | `椭圆` / `ellipse` |
| 参数 | ❌ | 随机 | `a=5 b=3` / `p=4` |
| 题型 | ❌ | `basic` | `chord` / `竞赛` |

**难度快捷方式**：`基础` → basic，`进阶` → chord，`竞赛/压轴/难` → 自动选高难度

## Project Structure

```
analytic_geometry_generator/
├── run.py                     # Entry point (TUI / CLI)
├── tui_app.py                 # Textual TUI with draggable split pane
├── interactive_generator.py   # Dynamic problem generation
├── problem_generator.py       # Core engine (12 problem templates)
├── diagram_renderer.py        # Matplotlib precise rendering
├── latex_render.py            # LaTeX → Unicode for terminal
├── build_exe.py               # PyInstaller .exe build
├── main.py                    # Batch generation demo
├── LICENSE                    # MIT
└── output/
    └── Question_YYYYMMDD_HHMMSS/
        ├── diagram.png
        ├── problem.tex
        ├── solution.tex
        └── problem.txt
```

## Architecture

```
User Input (natural language)
       │
       ▼
  TUI Parser ──── 识别知识点 / 题型 / 参数 / 难度
       │
       ▼
  ProblemGenerator ──── 参数推导 → 几何构造 → 交点计算 → LaTeX 生成
       │
       ├──► DiagramRenderer ──── 坐标系 → 曲线绘制 → 点标注 → PNG 导出
       │
       └──► LatexRender ──── LaTeX → Unicode → 终端 Chat 显示
                                    │
                                    ▼
                          output/Question_timestamp/
```

## Build .exe

```bash
pip install pyinstaller
python3 build_exe.py
# Output: dist/geometry-generator/geometry-generator
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Numerical | NumPy |
| Plotting | Matplotlib |
| TUI | Textual + Rich |
| Math rendering | LaTeX → Unicode |
| Packaging | PyInstaller |

## License

[MIT](LICENSE) © L77Doncic
