# 解析几何题目生成系统

> 基于数学参数的动态解析几何题目生成系统，支持 TUI 交互界面、精确配图渲染和 LaTeX 输出。

## 功能特性

- **动态生成**：用户指定知识点、参数、题型，自动生成题目
- **自然语言输入**：TUI 中直接输入「椭圆 a=5 b=3 竞赛」即可
- **难度自动路由**：说"竞赛"/"压轴"/"难"自动选高难度题型
- **精确配图**：Matplotlib 渲染，1000 采样点，参数严格一致
- **LaTeX 渲染**：终端中 Unicode 符号显示分数、根号、上下标
- **可拖动分栏**：TUI 侧边栏和对话区可自由拖动调整大小
- **时间戳输出**：每次生成自动创建 `Question_YYYYMMDD_HHMMSS/` 目录

## 支持的知识点与题型

| 知识点 | 基础题 | 进阶题 | 竞赛/压轴题 |
|--------|--------|--------|-------------|
| 椭圆 | 标准方程、焦点 | 焦点弦 | 定点证明、面积最值、离心率范围、切线/极点极线、第三定义 |
| 双曲线 | 标准方程、渐近线 | 焦点弦 | 渐近线平行弦、焦点三角形面积 |
| 抛物线 | 标准方程、焦点 | 焦点弦 | 阿基米德三角形、定点证明 |
| 极坐标 | 坐标互化 | 直线与圆 | 圆锥曲线极坐标方程 |

**共 13 种题型**，覆盖高考压轴和数学竞赛难度。

## 快速开始

### 环境要求

- Python 3.10+

### 安装依赖

```bash
pip install numpy matplotlib textual rich python-pptx
```

### 启动 TUI

```bash
python3 run.py
# 或直接
python3 tui_app.py
```

### 命令行模式

```bash
# 指定参数生成
python3 run.py --cli --topic ellipse --a 5 --b 3 --type chord --k 1

# 交互式模式
python3 run.py --interactive
```

### 输入示例

在 TUI 中直接输入：

```
椭圆 a=5 b=3              # 椭圆基础题（指定参数）
椭圆 竞赛                  # 椭圆高难度题（自动随机参数）
双曲线 a=3 b=4 基础        # 双曲线基础题
抛物线 p=4 弦长 k=1        # 抛物线焦点弦
极坐标 r=3                 # 极坐标基础题
random                     # 随机生成
```

**参数和题型均可省略**，省略后自动随机生成。

## 项目结构

```
analytic_geometry_generator/
├── run.py                     # 统一入口 (TUI/CLI)
├── tui_app.py                 # Textual TUI 交互界面
├── interactive_generator.py   # 动态题目生成 (用户指定参数)
├── problem_generator.py       # 核心题目生成引擎
├── diagram_renderer.py        # Matplotlib 配图渲染引擎
├── latex_render.py            # LaTeX → Unicode 终端渲染
├── main.py                    # 全量生成演示
├── build_exe.py               # PyInstaller .exe 构建
├── create_ppt.py              # PPT 演示文稿生成
├── create_defense_ppt.py      # 答辩 PPT 生成
├── README.md                  # 项目说明
├── LICENSE                    # MIT 开源协议
├── DESIGN.md                  # Anthropic 设计规范参考
├── 技术原理说明文档.md          # 技术原理文档
└── output/                    # 输出目录 (运行时生成)
    └── Question_YYYYMMDD_HHMMSS/
        ├── diagram.png        # 精确配图
        ├── problem.tex        # LaTeX 题干
        ├── solution.tex       # LaTeX 解答
        └── problem.txt        # 纯文本版
```

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.12 |
| 数值计算 | NumPy |
| 绘图 | Matplotlib |
| TUI 框架 | Textual + Rich |
| 数学渲染 | LaTeX → Unicode |
| 打包 | PyInstaller (.exe) |

## 构建 .exe

```bash
pip install pyinstaller
python3 build_exe.py
```

## 许可证

MIT License
