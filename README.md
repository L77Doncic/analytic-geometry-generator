# 解析几何题目生成系统

## 项目简介

这是一个基于数学参数的动态解析几何题目生成系统，能够根据用户指定的知识点与难度等级，自动生成格式严谨的解析几何题目，并配以精确的几何图形。

## 功能特性

### 支持的知识点

| 知识点 | 基础 (Level 1) | 进阶 (Level 2) | 竞赛 (Level 3) |
|--------|---------------|---------------|---------------|
| 椭圆 | 标准方程、焦点、顶点 | 焦点弦长、三角形面积 | 焦点三角形、离心率 |
| 双曲线 | 标准方程、渐近线 | 焦点弦 | 焦点三角形面积 |
| 抛物线 | 标准方程、焦点、准线 | 焦点弦 | 焦点弦性质证明 |
| 极坐标 | 坐标互化 | 直线与圆 | 圆锥曲线极坐标方程 |

### 核心特性

- **数学严谨性**：所有生成的题目都有明确的解析解，保证可解性
- **精确配图**：Matplotlib渲染，所有关键点、直线、曲线位置与数学参数严格一致
- **LaTeX输出**：标准数学排版格式，便于教学使用
- **自动生成**：无需人工干预，一键生成完整题目

## 项目结构

```
analytic_geometry_generator/
├── main.py                 # 主程序入口
├── problem_generator.py    # 题目生成引擎
├── diagram_renderer.py     # 配图渲染器
├── create_ppt.py          # PPT演示文稿创建
├── README.md              # 项目说明文档
└── output/                # 输出目录
    ├── 椭圆_difficulty1.png
    ├── 椭圆_difficulty2.png
    ├── 椭圆_difficulty3.png
    ├── 双曲线_difficulty1.png
    ├── ...
    └── 解析几何题目生成系统.pptx
```

## 快速开始

### 环境要求

- Python 3.8+
- matplotlib
- numpy
- python-pptx

### 安装依赖

```bash
pip install matplotlib numpy python-pptx
```

### 运行程序

```bash
cd /root/analytic_geometry_generator
python3 main.py
```

### 使用示例

```python
from problem_generator import ProblemGenerator
from diagram_renderer import DiagramRenderer

# 初始化
generator = ProblemGenerator(seed=42)
renderer = DiagramRenderer()

# 生成椭圆基础题
problem = generator.generate("ellipse", 1)

# 打印题干
print(problem.problem_latex)

# 渲染配图
renderer.render(problem, "output/ellipse.png")
```

## 系统架构

### 模块划分

1. **ProblemGenerator（题目生成器）**
   - 椭圆题目生成（3个难度）
   - 双曲线题目生成（3个难度）
   - 抛物线题目生成（3个难度）
   - 极坐标题目生成（3个难度）

2. **DiagramRenderer（配图渲染器）**
   - 坐标系建立（网格、刻度、箭头）
   - 圆锥曲线绘制（椭圆、双曲线、抛物线）
   - 关键点/线标注
   - 图形导出（PNG格式）

### 数据结构

#### ConicParams（圆锥曲线参数）

```python
@dataclass
class ConicParams:
    center: Tuple[float, float]  # 中心点坐标
    a: float                      # 半长轴/半实轴
    b: float                      # 半短轴/半虚轴
    c: float                      # 半焦距
    e: float                      # 离心率
```

#### Problem（题目对象）

```python
@dataclass
class Problem:
    title: str                    # 题目标题
    topic: str                    # 知识点
    difficulty: int               # 难度等级 (1-3)
    problem_latex: str            # LaTeX格式题干
    solution_latex: str           # LaTeX格式解答
    conic_params: ConicParams     # 圆锥曲线参数
    points: List[Point]           # 关键点列表
    lines: List[Line]             # 关键直线列表
    conic_type: str               # 曲线类型
    answer: str                   # 最终答案
```

## 核心算法

### 题目生成流程

1. **参数采样**：在合理范围内随机生成几何参数
2. **参数推导**：计算 c = √(a²±b²), e = c/a 等派生参数
3. **几何对象构造**：生成焦点、顶点、渐近线等
4. **交点计算**：联立方程求解弦与曲线的交点
5. **题干生成**：将参数代入LaTeX模板
6. **解答推导**：自动计算并生成完整解答过程

### 配图渲染流程

1. **坐标系建立**：设置坐标轴范围、网格、刻度、箭头
2. **曲线绘制**：根据参数方程精确绘制椭圆/双曲线/抛物线
3. **直线绘制**：根据直线方程 ax+by+c=0 绘制
4. **点标注**：在计算得到的精确位置绘制关键点
5. **标签渲染**：添加 LaTeX 格式的点标签
6. **图形导出**：保存为高分辨率 PNG

## 输出示例

### 题干示例（椭圆基础题）

```
已知椭圆 $C$ 的中心在原点，焦点在 $x$ 轴上，长轴长为 $10$，短轴长为 $2$。

(1) 求椭圆 $C$ 的标准方程；
(2) 求椭圆 $C$ 的焦点坐标和离心率。
```

### 配图说明

- **蓝色曲线**：圆锥曲线
- **红色直线**：关键直线（弦、切线等）
- **紫色虚线**：渐近线（双曲线）
- **绿色点划线**：准线（抛物线）
- **金色点**：关键点（焦点、顶点等）

## 扩展方向

- 添加更多知识点：圆、参数方程、直线方程等
- 支持自定义难度：更细粒度的难度控制
- 题目数据库：将生成的题目存储到数据库
- Web界面：开发在线题目生成平台
- TikZ输出：支持LaTeX TikZ绘图代码导出
- 智能组卷：根据知识点覆盖率自动组卷

## 许可证

MIT License
