"""
解析几何题目生成引擎
Analytic Geometry Problem Generator Engine

支持的知识点：
- 椭圆 (Ellipse)
- 双曲线 (Hyperbola)
- 抛物线 (Parabola)
- 极坐标 (Polar Coordinates)

难度等级：
- 1: 基础 (Basic) - 标准方程、焦点、顶点
- 2: 进阶 (Intermediate) - 弦长、面积、位置关系
- 3: 竞赛 (Competition) - 综合证明、最值问题
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Any
import random
import json


@dataclass
class ConicParams:
    """圆锥曲线参数"""
    center: Tuple[float, float] = (0, 0)  # 中心点
    a: float = 1.0  # 半长轴 / 半实轴
    b: float = 1.0  # 半短轴 / 半虚轴
    c: float = 0.0  # 半焦距
    e: float = 0.0  # 离心率
    rotation: float = 0.0  # 旋转角度(弧度)

    def __post_init__(self):
        if abs(self.c) < 1e-10:
            self.c = np.sqrt(abs(self.a**2 - self.b**2))
        if abs(self.e) < 1e-10 and self.c > 1e-10:
            self.e = self.c / self.a


@dataclass
class Point:
    """二维点"""
    x: float
    y: float
    label: str = ""

    def coords(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def distance_to(self, other: 'Point') -> float:
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class Line:
    """直线: ax + by + c = 0"""
    a: float
    b: float
    c: float
    label: str = ""

    def slope(self) -> float:
        if self.b == 0:
            return float('inf')
        return -self.a / self.b

    def y_intercept(self) -> float:
        if self.b == 0:
            return float('inf')
        return -self.c / self.b

    def point_on_line(self, x: float) -> float:
        """给定x坐标，求y坐标"""
        if self.b == 0:
            return float('inf')
        return (-self.a * x - self.c) / self.b

    def distance_to_point(self, p: Point) -> float:
        """点到直线距离"""
        return abs(self.a * p.x + self.b * p.y + self.c) / np.sqrt(self.a**2 + self.b**2)


@dataclass
class Problem:
    """解析几何题目"""
    title: str
    topic: str  # 知识点
    difficulty: int  # 难度等级
    problem_latex: str  # 题干LaTeX
    solution_latex: str  # 解答LaTeX
    conic_params: ConicParams  # 圆锥曲线参数
    points: List[Point] = field(default_factory=list)  # 关键点
    lines: List[Line] = field(default_factory=list)  # 关键直线
    conic_type: str = ""  # 曲线类型
    answer: str = ""  # 最终答案


class ProblemGenerator:
    """解析几何题目生成器"""

    def __init__(self, seed: int = None):
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

    # ==================== 椭圆题目 ====================

    def generate_ellipse_basic(self) -> Problem:
        """难度1: 椭圆基础题 - 求椭圆方程、焦点、顶点"""
        # 随机生成椭圆参数
        a = np.random.choice([2, 3, 4, 5, 6])
        b_choices = [x for x in [1, 2, 3, 4, 5] if x < a]
        b = np.random.choice(b_choices)
        c = np.sqrt(a**2 - b**2)
        e = c / a

        params = ConicParams(a=a, b=b, c=c, e=e)

        # 焦点
        F1 = Point(-c, 0, "F_1")
        F2 = Point(c, 0, "F_2")

        # 顶点
        A1 = Point(-a, 0, "A_1")
        A2 = Point(a, 0, "A_2")
        B1 = Point(0, -b, "B_1")
        B2 = Point(0, b, "B_2")

        points = [F1, F2, A1, A2, B1, B2]

        # 生成题干
        problem_latex = (
            f"已知椭圆 $C$ 的中心在原点，焦点在 $x$ 轴上，"
            f"长轴长为 ${2*a}$，短轴长为 ${2*b}$。\n\n"
            f"(1) 求椭圆 $C$ 的标准方程；\n\n"
            f"(2) 求椭圆 $C$ 的焦点坐标和离心率。"
        )

        # 生成解答
        solution_latex = (
            f"**解：**\n\n"
            f"(1) 由题意知 $a = {a}$，$b = {b}$，"
            f"$c = \\sqrt{{a^2 - b^2}} = \\sqrt{{{a**2} - {b**2}}} = {c:.4g}$。\n\n"
            f"椭圆的标准方程为：\n"
            f"$$\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$$\n\n"
            f"(2) 焦点坐标为 $F_1({-c:.4g}, 0)$，$F_2({c:.4g}, 0)$。\n\n"
            f"离心率 $e = \\frac{{c}}{{a}} = \\frac{{{c:.4g}}}{{{a}}} = {e:.4g}$。"
        )

        return Problem(
            title="椭圆基础题",
            topic="椭圆",
            difficulty=1,
            problem_latex=problem_latex,
            solution_latex=solution_latex,
            conic_params=params,
            points=points,
            conic_type="ellipse",
            answer=f"\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1"
        )

    def generate_ellipse_intermediate(self) -> Problem:
        """难度2: 椭圆进阶题 - 过焦点的弦长问题"""
        a = np.random.choice([3, 4, 5])
        b = np.random.choice([2, 3, 4])
        if b >= a:
            b = a - 1
        c = np.sqrt(a**2 - b**2)
        e = c / a

        params = ConicParams(a=a, b=b, c=c, e=e)

        F1 = Point(-c, 0, "F_1")
        F2 = Point(c, 0, "F_2")

        # 选择一个过F1的弦的斜率
        k = np.random.choice([0.5, 1, 1.5, 2])

        # 计算弦与椭圆的交点
        # 直线: y = k(x + c)
        # 代入椭圆方程: x²/a² + k²(x+c)²/b² = 1
        # (b² + a²k²)x² + 2a²ck²x + a²c²k² - a²b² = 0
        A_coeff = b**2 + a**2 * k**2
        B_coeff = 2 * a**2 * c * k**2
        C_coeff = a**2 * c**2 * k**2 - a**2 * b**2

        discriminant = B_coeff**2 - 4 * A_coeff * C_coeff
        if discriminant < 0:
            # 如果无实根，调整参数
            k = 0.5
            A_coeff = b**2 + a**2 * k**2
            B_coeff = 2 * a**2 * c * k**2
            C_coeff = a**2 * c**2 * k**2 - a**2 * b**2
            discriminant = B_coeff**2 - 4 * A_coeff * C_coeff

        x1 = (-B_coeff + np.sqrt(discriminant)) / (2 * A_coeff)
        x2 = (-B_coeff - np.sqrt(discriminant)) / (2 * A_coeff)
        y1 = k * (x1 + c)
        y2 = k * (x2 + c)

        P = Point(x1, y1, "P")
        Q = Point(x2, y2, "Q")

        # 弦长
        chord_length = P.distance_to(Q)

        # 直线PQ
        line_pq = Line(k, -1, k * c, "PQ")

        points = [F1, F2, P, Q]
        lines = [line_pq]

        problem_latex = (
            f"已知椭圆 $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
            f"的左焦点为 $F_1$，过 $F_1$ 且斜率为 ${k}$ 的直线 $l$ 与椭圆交于 $P$、$Q$ 两点。\n\n"
            f"(1) 求弦 $PQ$ 的长；\n\n"
            f"(2) 求 $\\triangle PF_1Q$ 的面积。"
        )

        # 计算三角形面积 (F1到直线PQ的距离 × PQ / 2)
        dist_F1_to_PQ = line_pq.distance_to_point(F1)
        triangle_area = 0.5 * chord_length * dist_F1_to_PQ

        solution_latex = (
            f"**解：**\n\n"
            f"椭圆方程为 $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$，"
            f"$c = \\sqrt{{{a**2} - {b**2}}} = {c:.4g}$。\n\n"
            f"左焦点 $F_1({-c:.4g}, 0)$。\n\n"
            f"(1) 直线 $l$ 的方程为 $y = {k}(x + {c:.4g})$。\n\n"
            f"联立椭圆方程，整理得：\n"
            f"$({b**2} + {a**2} \\cdot {k**2})x^2 + 2 \\cdot {a**2} \\cdot {c:.4g} \\cdot {k**2} x + {a**2} \\cdot {c:.4g}^2 \\cdot {k**2} - {a**2} \\cdot {b**2} = 0$\n\n"
            f"即 ${A_coeff}x^2 + {B_coeff:.4g}x + {C_coeff:.4g} = 0$\n\n"
            f"由韦达定理：$x_1 + x_2 = \\frac{{{-B_coeff:.4g}}}{{{A_coeff}}}$，"
            f"$x_1 x_2 = \\frac{{{C_coeff:.4g}}}{{{A_coeff}}}$\n\n"
            f"$|PQ| = \\sqrt{{1 + {k**2}}} \\cdot |x_1 - x_2| = \\sqrt{{1 + {k**2}}} \\cdot \\sqrt{{(x_1+x_2)^2 - 4x_1x_2}}$\n\n"
            f"$= \\sqrt{{{1 + k**2}}} \\cdot \\sqrt{{\\frac{{{B_coeff**2:.4g} - 4 \\cdot {A_coeff} \\cdot {C_coeff:.4g}}}{{{A_coeff**2}}}}}$\n\n"
            f"$= {chord_length:.4g}$\n\n"
            f"(2) 点 $F_1$ 到直线 $l$ 的距离 $d = \\frac{{|{k} \\cdot ({-c:.4g}) - 0 + {k * c:.4g}|}}{{\\sqrt{{{k**2} + 1}}}} = {dist_F1_to_PQ:.4g}$\n\n"
            f"$S_{{\\triangle PF_1Q}} = \\frac{{1}}{{2}} \\cdot |PQ| \\cdot d = \\frac{{1}}{{2}} \\cdot {chord_length:.4g} \\cdot {dist_F1_to_PQ:.4g} = {triangle_area:.4g}$"
        )

        return Problem(
            title="椭圆弦长问题",
            topic="椭圆",
            difficulty=2,
            problem_latex=problem_latex,
            solution_latex=solution_latex,
            conic_params=params,
            points=points,
            lines=lines,
            conic_type="ellipse",
            answer=f"|PQ| = {chord_length:.4g}"
        )

    def generate_ellipse_competition(self) -> Problem:
        """难度3: 椭圆竞赛题 - 焦点三角形与离心率"""
        a = 5
        b = 3
        c = 4
        e = c / a

        params = ConicParams(a=a, b=b, c=c, e=e)

        F1 = Point(-c, 0, "F_1")
        F2 = Point(c, 0, "F_2")

        # 在椭圆上取一点P，使得∠F1PF2 = 90°
        # PF1² + PF2² = F1F2² = (2c)²
        # PF1 + PF2 = 2a
        # 设PF1 = m, PF2 = n，则 m + n = 2a, m² + n² = 4c²
        # (m+n)² = m² + n² + 2mn → 4a² = 4c² + 2mn
        # mn = 2(a² - c²) = 2b²
        # S = mn/2 = b²

        mn = 2 * b**2
        triangle_area = mn / 2

        # 求P的坐标
        # PF1² + PF2² = 4c²
        # (x+c)² + y² + (x-c)² + y² = 4c²
        # 2x² + 2c² + 2y² = 4c²
        # x² + y² = c² ... (1)
        # x²/a² + y²/b² = 1 ... (2)
        # 由(1): y² = c² - x²
        # 代入(2): x²/a² + (c²-x²)/b² = 1
        # b²x² + a²c² - a²x² = a²b²
        # (b²-a²)x² = a²b² - a²c² = -a²(a²-b²) = -a²c²
        # -c²x² = -a²c² → x² = a²

        # 这个情况P在顶点，不太合适。换个角度。
        # 让∠F1PF2 = 60°
        angle_deg = 60
        angle_rad = np.radians(angle_deg)

        # 余弦定理: F1F2² = PF1² + PF2² - 2·PF1·PF2·cos60°
        # 4c² = (PF1+PF2)² - 2PF1·PF2 - PF1·PF2
        # 4c² = 4a² - 3PF1·PF2
        # PF1·PF2 = (4a² - 4c²)/3 = 4b²/3
        pf1_pf2 = 4 * b**2 / 3
        triangle_area_60 = 0.5 * pf1_pf2 * np.sin(angle_rad)

        problem_latex = (
            f"已知椭圆 $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
            f"的左、右焦点分别为 $F_1$、$F_2$，点 $P$ 在椭圆上，且 $\\angle F_1PF_2 = {angle_deg}°$。\n\n"
            f"(1) 求 $\\triangle F_1PF_2$ 的面积；\n\n"
            f"(2) 求 $|PF_1| \\cdot |PF_2|$ 的值。"
        )

        solution_latex = (
            f"**解：**\n\n"
            f"由椭圆方程知 $a = {a}$，$b = {b}$，$c = \\sqrt{{{a**2} - {b**2}}} = {c}$，离心率 $e = \\frac{{{c}}}{{{a}}} = {e}$。\n\n"
            f"(1) 由椭圆定义知 $|PF_1| + |PF_2| = 2a = {2*a}$。\n\n"
            f"在 $\\triangle F_1PF_2$ 中，由余弦定理：\n"
            f"$|F_1F_2|^2 = |PF_1|^2 + |PF_2|^2 - 2|PF_1||PF_2|\\cos{angle_deg}°$\n\n"
            f"即 $(2c)^2 = (|PF_1| + |PF_2|)^2 - 2|PF_1||PF_2| - 2|PF_1||PF_2| \\cdot \\frac{{1}}{{2}}$\n\n"
            f"${4*c**2} = {4*a**2} - 3|PF_1||PF_2|$\n\n"
            f"$|PF_1||PF_2| = \\frac{{{4*a**2} - {4*c**2}}}{{3}} = \\frac{{{4*(a**2-c**2)}}}{{3}} = \\frac{{{4*b**2}}}{{3}} = {pf1_pf2:.4g}$\n\n"
            f"$S_{{\\triangle F_1PF_2}} = \\frac{{1}}{{2}} |PF_1||PF_2| \\sin{angle_deg}° = \\frac{{1}}{{2}} \\cdot {pf1_pf2:.4g} \\cdot \\frac{{\\sqrt{{3}}}}{{2}} = {triangle_area_60:.4g}$\n\n"
            f"(2) 由(1)知 $|PF_1| \\cdot |PF_2| = {pf1_pf2:.4g}$。"
        )

        P = Point(0, 0, "P")  # 占位，实际计算较复杂

        return Problem(
            title="椭圆焦点三角形",
            topic="椭圆",
            difficulty=3,
            problem_latex=problem_latex,
            solution_latex=solution_latex,
            conic_params=params,
            points=[F1, F2, P],
            conic_type="ellipse",
            answer=f"S = {triangle_area_60:.4g}"
        )

    # ==================== 双曲线题目 ====================

    def generate_hyperbola_basic(self) -> Problem:
        """难度1: 双曲线基础题"""
        a = np.random.choice([2, 3, 4])
        b = np.random.choice([1, 2, 3, 4, 5])
        c = np.sqrt(a**2 + b**2)
        e = c / a

        params = ConicParams(a=a, b=b, c=c, e=e)

        F1 = Point(-c, 0, "F_1")
        F2 = Point(c, 0, "F_2")
        V1 = Point(-a, 0, "V_1")
        V2 = Point(a, 0, "V_2")

        # 渐近线
        # y = ±(b/a)x
        asymptote1 = Line(b, -a, 0, "y = \\frac{b}{a}x")
        asymptote2 = Line(b, a, 0, "y = -\\frac{b}{a}x")

        points = [F1, F2, V1, V2]
        lines = [asymptote1, asymptote2]

        problem_latex = (
            f"已知双曲线 $C$ 的中心在原点，焦点在 $x$ 轴上，"
            f"实轴长为 ${2*a}$，虚轴长为 ${2*b}$。\n\n"
            f"(1) 求双曲线 $C$ 的标准方程；\n\n"
            f"(2) 求双曲线 $C$ 的焦点坐标、离心率和渐近线方程。"
        )

        solution_latex = (
            f"**解：**\n\n"
            f"(1) 由题意知 $a = {a}$，$b = {b}$，"
            f"$c = \\sqrt{{a^2 + b^2}} = \\sqrt{{{a**2} + {b**2}}} = {c:.4g}$。\n\n"
            f"双曲线的标准方程为：\n"
            f"$$\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$$\n\n"
            f"(2) 焦点坐标为 $F_1({-c:.4g}, 0)$，$F_2({c:.4g}, 0)$。\n\n"
            f"离心率 $e = \\frac{{c}}{{a}} = \\frac{{{c:.4g}}}{{{a}}} = {e:.4g}$。\n\n"
            f"渐近线方程为 $y = \\pm \\frac{{{b}}}{{{a}}}x = \\pm {b/a:.4g}x$。"
        )

        return Problem(
            title="双曲线基础题",
            topic="双曲线",
            difficulty=1,
            problem_latex=problem_latex,
            solution_latex=solution_latex,
            conic_params=params,
            points=points,
            lines=lines,
            conic_type="hyperbola",
            answer=f"\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1"
        )

    def generate_hyperbola_intermediate(self) -> Problem:
        """难度2: 双曲线进阶题 - 焦点弦"""
        a = 3
        b = 4
        c = 5
        e = c / a

        params = ConicParams(a=a, b=b, c=c, e=e)

        F1 = Point(-c, 0, "F_1")
        F2 = Point(c, 0, "F_2")

        # 过右焦点的弦，斜率为1
        k = 1.0
        # 直线: y = k(x - c)
        # 代入双曲线: x²/a² - k²(x-c)²/b² = 1
        # b²x² - a²k²(x-c)² = a²b²
        # (b² - a²k²)x² + 2a²ck²x - a²c²k² - a²b² = 0
        A_coeff = b**2 - a**2 * k**2
        B_coeff = 2 * a**2 * c * k**2
        C_coeff = -(a**2 * c**2 * k**2 + a**2 * b**2)

        discriminant = B_coeff**2 - 4 * A_coeff * C_coeff
        x1 = (-B_coeff + np.sqrt(discriminant)) / (2 * A_coeff)
        x2 = (-B_coeff - np.sqrt(discriminant)) / (2 * A_coeff)
        y1 = k * (x1 - c)
        y2 = k * (x2 - c)

        P = Point(x1, y1, "P")
        Q = Point(x2, y2, "Q")

        chord_length = P.distance_to(Q)

        points = [F1, F2, P, Q]

        problem_latex = (
            f"已知双曲线 $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$，"
            f"$F_2$ 为其右焦点。过 $F_2$ 且斜率为 ${k}$ 的直线 $l$ 与双曲线交于 $P$、$Q$ 两点。\n\n"
            f"(1) 求弦 $|PQ|$ 的长；\n\n"
            f"(2) 若 $P$ 在第一象限，求 $P$ 点坐标。"
        )

        solution_latex = (
            f"**解：**\n\n"
            f"双曲线 $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$，$c = {c}$，右焦点 $F_2({c}, 0)$。\n\n"
            f"(1) 直线 $l: y = {k}(x - {c})$。\n\n"
            f"代入双曲线方程：$\\frac{{x^2}}{{{a**2}}} - \\frac{{{k**2}(x - {c})^2}}{{{b**2}}} = 1$\n\n"
            f"整理得：${A_coeff}x^2 + {B_coeff:.4g}x + {C_coeff:.4g} = 0$\n\n"
            f"$|PQ| = \\sqrt{{1 + {k**2}}} \\cdot |x_1 - x_2| = \\sqrt{{2}} \\cdot \\sqrt{{\\frac{{\\Delta}}{{{A_coeff}^2}}}} = {chord_length:.4g}$\n\n"
            f"(2) $P({x1:.4g}, {y1:.4g})$"
        )

        return Problem(
            title="双曲线焦点弦",
            topic="双曲线",
            difficulty=2,
            problem_latex=problem_latex,
            solution_latex=solution_latex,
            conic_params=params,
            points=points,
            conic_type="hyperbola",
            answer=f"|PQ| = {chord_length:.4g}"
        )

    def generate_hyperbola_competition(self) -> Problem:
        """难度3: 双曲线竞赛题 - 焦点三角形面积"""
        a = 3
        b = 4
        c = 5
        e = c / a

        params = ConicParams(a=a, b=b, c=c, e=e)

        F1 = Point(-c, 0, "F_1")
        F2 = Point(c, 0, "F_2")

        # 设∠F1PF2 = θ
        # |PF1 - PF2| = 2a
        # 余弦定理: 4c² = PF1² + PF2² - 2PF1·PF2·cosθ
        # (PF1-PF2)² = PF1² + PF2² - 2PF1·PF2
        # 4a² = 4c² + 2PF1·PF2·cosθ - 2PF1·PF2
        # 4a² = 4c² - 2PF1·PF2(1-cosθ)
        # PF1·PF2 = 2(c²-a²)/(1-cosθ) = 2b²/(1-cosθ)

        angle_deg = 60
        angle_rad = np.radians(angle_deg)
        pf1_pf2 = 2 * b**2 / (1 - np.cos(angle_rad))
        triangle_area = 0.5 * pf1_pf2 * np.sin(angle_rad)

        problem_latex = (
            f"已知双曲线 $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$，"
            f"$F_1$、$F_2$ 分别为左、右焦点，点 $P$ 在双曲线上，$\\angle F_1PF_2 = {angle_deg}°$。\n\n"
            f"(1) 求 $|PF_1| \\cdot |PF_2|$ 的值；\n\n"
            f"(2) 求 $\\triangle F_1PF_2$ 的面积。"
        )

        solution_latex = (
            f"**解：**\n\n"
            f"由双曲线方程知 $a = {a}$，$b = {b}$，$c = {c}$。\n\n"
            f"(1) 由双曲线定义：$||PF_1| - |PF_2|| = 2a = {2*a}$。\n\n"
            f"在 $\\triangle F_1PF_2$ 中，由余弦定理：\n"
            f"$|F_1F_2|^2 = |PF_1|^2 + |PF_2|^2 - 2|PF_1||PF_2|\\cos{angle_deg}°$\n\n"
            f"又 $(|PF_1| - |PF_2|)^2 = |PF_1|^2 + |PF_2|^2 - 2|PF_1||PF_2|$\n\n"
            f"两式相减：$(2c)^2 - (2a)^2 = 2|PF_1||PF_2|(1 - \\cos{angle_deg}°)$\n\n"
            f"$4({c**2} - {a**2}) = 2|PF_1||PF_2| \\cdot (1 - \\frac{{1}}{{2}})$\n\n"
            f"$|PF_1||PF_2| = \\frac{{2 \\cdot {b**2}}}{{1 - \\frac{{1}}{{2}}}} = {pf1_pf2:.4g}$\n\n"
            f"(2) $S_{{\\triangle F_1PF_2}} = \\frac{{1}}{{2}} |PF_1||PF_2| \\sin{angle_deg}° = \\frac{{1}}{{2}} \\cdot {pf1_pf2:.4g} \\cdot \\frac{{\\sqrt{{3}}}}{{2}} = {triangle_area:.4g}$"
        )

        P = Point(0, 0, "P")  # 占位

        return Problem(
            title="双曲线焦点三角形",
            topic="双曲线",
            difficulty=3,
            problem_latex=problem_latex,
            solution_latex=solution_latex,
            conic_params=params,
            points=[F1, F2, P],
            conic_type="hyperbola",
            answer=f"|PF_1||PF_2| = {pf1_pf2:.4g}"
        )

    # ==================== 抛物线题目 ====================

    def generate_parabola_basic(self) -> Problem:
        """难度1: 抛物线基础题"""
        p = np.random.choice([2, 4, 6, 8])

        params = ConicParams(a=p / 2, b=0, c=p / 2)

        F = Point(p / 2, 0, "F")
        V = Point(0, 0, "O")

        # 准线
        directrix = Line(1, 0, p / 2, "x = -\\frac{p}{2}")

        points = [F, V]
        lines = [directrix]

        problem_latex = (
            f"已知抛物线 $C$ 的顶点在原点，焦点在 $x$ 轴正半轴上，"
            f"焦点到准线的距离为 ${p}$。\n\n"
            f"(1) 求抛物线 $C$ 的标准方程；\n\n"
            f"(2) 求焦点坐标和准线方程。"
        )

        solution_latex = (
            f"**解：**\n\n"
            f"(1) 由题意知 $p = {p}$，抛物线开口向右。\n\n"
            f"抛物线的标准方程为：\n"
            f"$$y^2 = {2*p}x$$\n\n"
            f"(2) 焦点坐标为 $F(\\frac{{{p}}}{{2}}, 0) = F({p/2}, 0)$。\n\n"
            f"准线方程为 $x = -\\frac{{{p}}}{{2}} = -{p/2}$。"
        )

        return Problem(
            title="抛物线基础题",
            topic="抛物线",
            difficulty=1,
            problem_latex=problem_latex,
            solution_latex=solution_latex,
            conic_params=params,
            points=points,
            lines=lines,
            conic_type="parabola",
            answer=f"y^2 = {2*p}x"
        )

    def generate_parabola_intermediate(self) -> Problem:
        """难度2: 抛物线进阶题 - 焦点弦"""
        p = 4

        params = ConicParams(a=p / 2, b=0, c=p / 2)

        F = Point(p / 2, 0, "F")

        # 过焦点的弦，斜率k
        k = 1.0
        # 直线: y = k(x - p/2)
        # 代入抛物线: k²(x-p/2)² = 2px
        # k²x² - k²px + k²p²/4 = 2px
        # k²x² - (k²p + 2p)x + k²p²/4 = 0
        A_coeff = k**2
        B_coeff = -(k**2 * p + 2 * p)
        C_coeff = k**2 * p**2 / 4

        discriminant = B_coeff**2 - 4 * A_coeff * C_coeff
        x1 = (-B_coeff + np.sqrt(discriminant)) / (2 * A_coeff)
        x2 = (-B_coeff - np.sqrt(discriminant)) / (2 * A_coeff)
        y1 = k * (x1 - p / 2)
        y2 = k * (x2 - p / 2)

        P = Point(x1, y1, "P")
        Q = Point(x2, y2, "Q")

        # 焦点弦长公式: |PQ| = 2p/sin²θ，θ为弦与x轴夹角
        theta = np.arctan(k)
        chord_length_formula = 2 * p / np.sin(theta)**2
        chord_length_actual = P.distance_to(Q)

        points = [F, P, Q]

        problem_latex = (
            f"已知抛物线 $y^2 = {2*p}x$ 的焦点为 $F$，过 $F$ 且斜率为 ${k}$ 的直线 $l$ "
            f"与抛物线交于 $P$、$Q$ 两点。\n\n"
            f"(1) 求弦 $|PQ|$ 的长；\n\n"
            f"(2) 求 $\\triangle OPQ$ 的面积（$O$ 为原点）。"
        )

        # 原点到直线距离
        line_pq = Line(k, -1, -k * p / 2, "PQ")
        dist_O_to_PQ = line_pq.distance_to_point(Point(0, 0, "O"))
        triangle_area = 0.5 * chord_length_actual * dist_O_to_PQ

        solution_latex = (
            f"**解：**\n\n"
            f"抛物线 $y^2 = {2*p}x$，焦点 $F({p/2}, 0)$。\n\n"
            f"(1) 直线 $l: y = {k}(x - {p/2})$。\n\n"
            f"代入抛物线方程：${k**2}(x - {p/2})^2 = {2*p}x$\n\n"
            f"整理得：${A_coeff}x^2 + {B_coeff:.4g}x + {C_coeff:.4g} = 0$\n\n"
            f"由焦点弦公式：$|PQ| = \\frac{{2p}}{{\\sin^2\\theta}} = \\frac{{2 \\cdot {p}}}{{\\sin^2 45°}} = {chord_length_formula:.4g}$\n\n"
            f"(2) 原点 $O$ 到直线 $l$ 的距离 $d = \\frac{{|{k} \\cdot 0 - 0 - {k * p / 2}|}}{{\\sqrt{{{k**2} + 1}}}} = {dist_O_to_PQ:.4g}$\n\n"
            f"$S_{{\\triangle OPQ}} = \\frac{{1}}{{2}} \\cdot |PQ| \\cdot d = {triangle_area:.4g}$"
        )

        return Problem(
            title="抛物线焦点弦",
            topic="抛物线",
            difficulty=2,
            problem_latex=problem_latex,
            solution_latex=solution_latex,
            conic_params=params,
            points=points,
            lines=[line_pq],
            conic_type="parabola",
            answer=f"|PQ| = {chord_length_actual:.4g}"
        )

    def generate_parabola_competition(self) -> Problem:
        """难度3: 抛物线竞赛题 - 焦点弦性质"""
        p = 4

        params = ConicParams(a=p / 2, b=0, c=p / 2)

        F = Point(p / 2, 0, "F")

        # 设过焦点的弦PQ，证明1/|PF| + 1/|QF|为定值
        # 设P(x1,y1), Q(x2,y2)，则|PF| = x1 + p/2, |QF| = x2 + p/2
        # 1/|PF| + 1/|QF| = (x1+x2+p) / ((x1+p/2)(x2+p/2))
        # = (x1+x2+p) / (x1x2 + p(x1+x2)/2 + p²/4)
        # 对于焦点弦: x1x2 = p²/4
        # 所以 = (x1+x2+p) / (p²/4 + p(x1+x2)/2 + p²/4)
        # = (x1+x2+p) / (p(x1+x2+p)/2) = 2/p

        problem_latex = (
            f"已知抛物线 $y^2 = {2*p}x$ 的焦点为 $F$，过 $F$ 的直线 $l$ 与抛物线交于 $P$、$Q$ 两点。\n\n"
            f"证明：$\\frac{{1}}{{|PF|}} + \\frac{{1}}{{|QF|}}$ 为定值，并求此定值。"
        )

        solution_latex = (
            f"**证明：**\n\n"
            f"抛物线 $y^2 = {2*p}x$，焦点 $F({p/2}, 0)$。\n\n"
            f"设直线 $l$ 的参数方程为：\n"
            f"$\\begin{{cases}} x = {p/2} + t\\cos\\theta \\\\ y = t\\sin\\theta \\end{{cases}}$\n\n"
            f"代入抛物线方程：$t^2\\sin^2\\theta = {2*p}({p/2} + t\\cos\\theta)$\n\n"
            f"即 $t^2\\sin^2\\theta - {2*p}t\\cos\\theta - {p**2} = 0$\n\n"
            f"设 $t_1$、$t_2$ 为两根，则 $|PF| = |t_1|$，$|QF| = |t_2|$。\n\n"
            f"由韦达定理：$t_1 + t_2 = \\frac{{{2*p}\\cos\\theta}}{{\\sin^2\\theta}}$，"
            f"$t_1 t_2 = \\frac{{-{p**2}}}{{\\sin^2\\theta}}$\n\n"
            f"由于 $P$、$Q$ 在焦点两侧，$t_1 t_2 < 0$，故 $|PF| = t_1$，$|QF| = -t_2$（或反之）。\n\n"
            f"$\\frac{{1}}{{|PF|}} + \\frac{{1}}{{|QF|}} = \\frac{{1}}{{t_1}} - \\frac{{1}}{{t_2}} = \\frac{{t_2 - t_1}}{{t_1 t_2}}$\n\n"
            f"$(t_2 - t_1)^2 = (t_1 + t_2)^2 - 4t_1 t_2 = \\frac{{{4*p**2}\\cos^2\\theta}}{{\\sin^4\\theta}} + \\frac{{{4*p**2}}}{{\\sin^2\\theta}} = \\frac{{{4*p**2}}}{{\\sin^4\\theta}}$\n\n"
            f"$|t_2 - t_1| = \\frac{{{2*p}}}{{\\sin^2\\theta}}$\n\n"
            f"$\\frac{{1}}{{|PF|}} + \\frac{{1}}{{|QF|}} = \\frac{{\\frac{{{2*p}}}{{\\sin^2\\theta}}}}{{\\frac{{{p**2}}}{{\\sin^2\\theta}}}} = \\frac{{{2*p}}}{{{p**2}}} = \\frac{{2}}{{{p}}} = \\frac{{1}}{{{p/2}}}$\n\n"
            f"此为定值，与直线 $l$ 的倾斜角 $\\theta$ 无关。"
        )

        P = Point(0, 0, "P")
        Q = Point(0, 0, "Q")

        return Problem(
            title="抛物线焦点弦性质",
            topic="抛物线",
            difficulty=3,
            problem_latex=problem_latex,
            solution_latex=solution_latex,
            conic_params=params,
            points=[F, P, Q],
            conic_type="parabola",
            answer=f"\\frac{{1}}{{|PF|}} + \\frac{{1}}{{|QF|}} = \\frac{{2}}{{p}}"
        )

    # ==================== 极坐标题目 ====================

    def generate_polar_basic(self) -> Problem:
        """难度1: 极坐标基础题 - 直角坐标与极坐标互化"""
        # 圆的极坐标方程
        r = np.random.choice([2, 3, 4, 5])
        a = r  # 圆心在极轴上，到极点距离为a

        params = ConicParams(a=a, b=a)

        O = Point(0, 0, "O")
        A = Point(2 * a, 0, "A")

        problem_latex = (
            f"在极坐标系中，已知圆 $C$ 的极坐标方程为 $\\rho = {2*a}\\cos\\theta$。\n\n"
            f"(1) 将圆 $C$ 的极坐标方程化为直角坐标方程；\n\n"
            f"(2) 求圆 $C$ 的圆心坐标和半径。"
        )

        solution_latex = (
            f"**解：**\n\n"
            f"(1) 由 $\\rho = {2*a}\\cos\\theta$，两边乘以 $\\rho$：\n\n"
            f"$\\rho^2 = {2*a}\\rho\\cos\\theta$\n\n"
            f"由 $\\rho^2 = x^2 + y^2$，$\\rho\\cos\\theta = x$，代入得：\n\n"
            f"$x^2 + y^2 = {2*a}x$\n\n"
            f"即 $(x - {a})^2 + y^2 = {a**2}$\n\n"
            f"(2) 圆心坐标为 $({a}, 0)$，半径 $r = {a}$。"
        )

        return Problem(
            title="极坐标基础题",
            topic="极坐标",
            difficulty=1,
            problem_latex=problem_latex,
            solution_latex=solution_latex,
            conic_params=params,
            points=[O, A],
            conic_type="polar",
            answer=f"(x-{a})^2 + y^2 = {a**2}"
        )

    def generate_polar_intermediate(self) -> Problem:
        """难度2: 极坐标进阶题 - 直线与圆的位置关系"""
        r = 3
        a = r

        params = ConicParams(a=a, b=a)

        O = Point(0, 0, "O")
        C = Point(a, 0, "C")

        # 圆: ρ = 2a·cosθ = 6cosθ
        # 直线: θ = π/3 (过原点，倾角60°)
        # 交点: ρ = 6cos(π/3) = 3
        # 所以交点极坐标为(3, π/3)

        angle = np.pi / 3
        rho = 2 * a * np.cos(angle)
        P = Point(rho * np.cos(angle), rho * np.sin(angle), "P")

        # 另一个交点是原点O
        chord_length = rho

        problem_latex = (
            f"在极坐标系中，圆 $C$ 的方程为 $\\rho = {2*a}\\cos\\theta$，"
            f"直线 $l$ 的方程为 $\\theta = \\frac{{\\pi}}{{3}}$。\n\n"
            f"(1) 求直线 $l$ 与圆 $C$ 的交点坐标；\n\n"
            f"(2) 求弦长 $|OP|$（$O$ 为极点）。"
        )

        solution_latex = (
            f"**解：**\n\n"
            f"(1) 将 $\\theta = \\frac{{\\pi}}{{3}}$ 代入圆的方程：\n\n"
            f"$\\rho = {2*a}\\cos\\frac{{\\pi}}{{3}} = {2*a} \\cdot \\frac{{1}}{{2}} = {rho}$\n\n"
            f"交点 $P$ 的极坐标为 $({rho}, \\frac{{\\pi}}{{3}})$。\n\n"
            f"化为直角坐标：$P({rho}\\cos\\frac{{\\pi}}{{3}}, {rho}\\sin\\frac{{\\pi}}{{3}}) = P(\\frac{{{rho}}}{{2}}, \\frac{{{rho}\\sqrt{{3}}}}{{2}}) = P({P.x:.4g}, {P.y:.4g})$\n\n"
            f"另一个交点为极点 $O(0, 0)$。\n\n"
            f"(2) $|OP| = \\rho = {rho}$。"
        )

        return Problem(
            title="极坐标直线与圆",
            topic="极坐标",
            difficulty=2,
            problem_latex=problem_latex,
            solution_latex=solution_latex,
            conic_params=params,
            points=[O, C, P],
            conic_type="polar",
            answer=f"|OP| = {rho}"
        )

    def generate_polar_competition(self) -> Problem:
        """难度3: 极坐标竞赛题 - 圆锥曲线的极坐标方程"""
        # 以焦点为极点的椭圆极坐标方程: ρ = ep/(1 - e·cosθ)
        # 设 e = 1/2, p = 3
        e = 0.5
        p_val = 3
        ep = e * p_val

        # 直角坐标参数
        # e = c/a, p = a²/c - c = b²/c
        # 由 e = 1/2: c = a/2
        # p = b²/c = b²/(a/2) = 2b²/a
        # 3 = 2b²/a → b² = 3a/2
        # 又 c² = a² - b² → a²/4 = a² - 3a/2 → 3a²/4 = 3a/2 → a = 2
        a = 2
        c = a * e  # = 1
        b = np.sqrt(a**2 - c**2)  # = √3

        params = ConicParams(a=a, b=b, c=c, e=e)

        F = Point(0, 0, "F")  # 极点即焦点

        problem_latex = (
            f"在极坐标系中，以椭圆的左焦点 $F$ 为极点，$x$ 轴正方向为极轴建立极坐标系。"
            f"已知椭圆的离心率 $e = \\frac{{1}}{{2}}$，焦点到相应准线的距离 $p = 3$。\n\n"
            f"(1) 求椭圆的极坐标方程；\n\n"
            f"(2) 求椭圆的直角坐标标准方程。"
        )

        solution_latex = (
            f"**解：**\n\n"
            f"(1) 以焦点为极点的椭圆极坐标方程为：\n\n"
            f"$\\rho = \\frac{{ep}}{{1 - e\\cos\\theta}} = \\frac{{\\frac{{1}}{{2}} \\cdot 3}}{{1 - \\frac{{1}}{{2}}\\cos\\theta}} = \\frac{{3}}{{2 - \\cos\\theta}}$\n\n"
            f"(2) 由 $e = \\frac{{c}}{{a}} = \\frac{{1}}{{2}}$，$p = \\frac{{b^2}}{{c}} = 3$。\n\n"
            f"设 $c = t$，则 $a = 2t$，$b^2 = 3t$。\n\n"
            f"又 $c^2 = a^2 - b^2$，即 $t^2 = 4t^2 - 3t$，解得 $t = 1$。\n\n"
            f"故 $a = 2$，$b = \\sqrt{{3}}$，$c = 1$。\n\n"
            f"椭圆的直角坐标标准方程为：\n"
            f"$$\\frac{{x^2}}{{4}} + \\frac{{y^2}}{{3}} = 1$$"
        )

        return Problem(
            title="极坐标与椭圆",
            topic="极坐标",
            difficulty=3,
            problem_latex=problem_latex,
            solution_latex=solution_latex,
            conic_params=params,
            points=[F],
            conic_type="polar",
            answer=f"\\rho = \\frac{{3}}{{2 - \\cos\\theta}}"
        )

    # ==================== 生成入口 ====================

    def generate(self, topic: str, difficulty: int) -> Problem:
        """
        生成解析几何题目

        Args:
            topic: 知识点 (ellipse/hyperbola/parabola/polar)
            difficulty: 难度等级 (1/2/3)

        Returns:
            Problem 对象
        """
        generators = {
            "ellipse": {
                1: self.generate_ellipse_basic,
                2: self.generate_ellipse_intermediate,
                3: self.generate_ellipse_competition,
            },
            "hyperbola": {
                1: self.generate_hyperbola_basic,
                2: self.generate_hyperbola_intermediate,
                3: self.generate_hyperbola_competition,
            },
            "parabola": {
                1: self.generate_parabola_basic,
                2: self.generate_parabola_intermediate,
                3: self.generate_parabola_competition,
            },
            "polar": {
                1: self.generate_polar_basic,
                2: self.generate_polar_intermediate,
                3: self.generate_polar_competition,
            },
        }

        if topic not in generators:
            raise ValueError(f"不支持的知识点: {topic}，可选: {list(generators.keys())}")
        if difficulty not in generators[topic]:
            raise ValueError(f"不支持的难度: {difficulty}，可选: {list(generators[topic].keys())}")

        return generators[topic][difficulty]()


def main():
    """测试生成器"""
    generator = ProblemGenerator(seed=42)

    topics = ["ellipse", "hyperbola", "parabola", "polar"]
    difficulties = [1, 2, 3]

    for topic in topics:
        for diff in difficulties:
            problem = generator.generate(topic, diff)
            print(f"\n{'='*60}")
            print(f"【{problem.title}】难度: {'★' * problem.difficulty}")
            print(f"知识点: {problem.topic}")
            print(f"{'='*60}")
            print(problem.problem_latex)
            print(f"\n{'-'*40}")
            print("解答:")
            print(problem.solution_latex)


if __name__ == "__main__":
    main()
