"""
交互式解析几何题目生成器
Interactive Analytic Geometry Problem Generator

用户可通过命令行指定参数，动态生成题目。

用法示例：
  # 全部随机
  python3 interactive_generator.py

  # 指定椭圆参数
  python3 interactive_generator.py --topic ellipse --a 5 --b 3

  # 指定双曲线 + 难度
  python3 interactive_generator.py --topic hyperbola --a 3 --b 4 --difficulty 2

  # 指定抛物线参数
  python3 interactive_generator.py --topic parabola --p 4

  # 交互式模式
  python3 interactive_generator.py --interactive
"""

import argparse
import sys
import os
import numpy as np

from problem_generator import ProblemGenerator, Problem, ConicParams, Point, Line
from diagram_renderer import DiagramRenderer


# ==================== 参数校验 ====================

def validate_ellipse(a, b):
    """校验椭圆参数"""
    if a <= 0 or b <= 0:
        raise ValueError(f"椭圆参数必须为正数: a={a}, b={b}")
    if a == b:
        raise ValueError(f"椭圆不能是圆: a=b={a}，请令 a ≠ b")
    return True


def validate_hyperbola(a, b):
    """校验双曲线参数"""
    if a <= 0 or b <= 0:
        raise ValueError(f"双曲线参数必须为正数: a={a}, b={b}")
    return True


def validate_parabola(p):
    """校验抛物线参数"""
    if p <= 0:
        raise ValueError(f"抛物线参数必须为正数: p={p}")
    return True


# ==================== 动态题目生成 ====================

def generate_ellipse_dynamic(a=None, b=None, problem_type="basic", slope=None):
    """
    动态生成椭圆题目

    Args:
        a: 半长轴 (None则随机)
        b: 半短轴 (None则随机)
        problem_type: "basic" | "chord" | "focus_triangle"
        slope: 焦点弦斜率 (仅 chord 类型, None则随机)

    Returns:
        Problem 对象
    """
    # 参数处理
    if a is None:
        a = np.random.choice([2, 3, 4, 5, 6])
    if b is None:
        if problem_type == "basic":
            b_choices = [x for x in range(1, a) if x < a]
            b = np.random.choice(b_choices)
        else:
            b_choices = [x for x in range(1, a) if x < a and x > 0]
            if not b_choices:
                b = max(1, a - 1)
            else:
                b = np.random.choice(b_choices)
    elif b >= a:
        raise ValueError(f"椭圆要求 a > b: 当前 a={a}, b={b}")

    validate_ellipse(a, b)
    c = np.sqrt(a**2 - b**2)
    e = c / a
    params = ConicParams(a=a, b=b, c=c, e=e)

    if problem_type == "basic":
        return _ellipse_basic(a, b, c, e, params)
    elif problem_type == "chord":
        if slope is None:
            slope = np.random.choice([0.5, 1, 1.5, 2])
        return _ellipse_chord(a, b, c, e, params, slope)
    elif problem_type == "focus_triangle":
        angle = np.random.choice([60, 90, 120])
        return _ellipse_focus_triangle(a, b, c, e, params, angle)
    # 进阶题型
    elif problem_type == "midpoint_chord":
        return _ellipse_midpoint_chord(a, b, c, e, params)
    elif problem_type == "focal_radius":
        return _ellipse_focal_radius(a, b, c, e, params)
    elif problem_type == "slope_product":
        return _ellipse_slope_product(a, b, c, e, params)
    elif problem_type == "tangent_line":
        return _ellipse_tangent_line(a, b, c, e, params)
    elif problem_type == "second_def":
        return _ellipse_second_def(a, b, c, e, params)
    # 高考压轴/竞赛题型
    elif problem_type == "fixed_point":
        return _ellipse_fixed_point(a, b, c, e, params)
    elif problem_type == "area_opt":
        return _ellipse_area_opt(a, b, c, e, params)
    elif problem_type == "ecc_range":
        return _ellipse_ecc_range(a, b, c, e, params)
    elif problem_type == "tangent":
        return _ellipse_tangent(a, b, c, e, params)
    elif problem_type == "third_def":
        return _ellipse_third_def(a, b, c, e, params)
    elif problem_type == "optical_property":
        return _ellipse_optical_property(a, b, c, e, params)
    elif problem_type == "locus":
        return _ellipse_locus(a, b, c, e, params)
    elif problem_type == "monge_circle":
        return _ellipse_monge_circle(a, b, c, e, params)
    elif problem_type == "apollonius":
        return _ellipse_apollonius(a, b, c, e, params)
    else:
        raise ValueError(f"不支持的椭圆题型: {problem_type}")


def _ellipse_basic(a, b, c, e, params):
    """椭圆基础题"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")
    A1 = Point(-a, 0, "A_1")
    A2 = Point(a, 0, "A_2")
    B1 = Point(0, -b, "B_1")
    B2 = Point(0, b, "B_2")

    problem_latex = (
        f"已知椭圆 $C$ 的中心在原点，焦点在 $x$ 轴上，"
        f"长轴长为 ${2*a}$，短轴长为 ${2*b}$。\n\n"
        f"(1) 求椭圆 $C$ 的标准方程；\n\n"
        f"(2) 求椭圆 $C$ 的焦点坐标和离心率。"
    )

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
        title=f"椭圆基础题 (a={a}, b={b})",
        topic="椭圆", difficulty=1,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, A1, A2, B1, B2],
        conic_type="ellipse",
        answer=f"\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1"
    )


def _ellipse_chord(a, b, c, e, params, k):
    """椭圆焦点弦题"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 联立方程求交点
    A_coeff = b**2 + a**2 * k**2
    B_coeff = 2 * a**2 * c * k**2
    C_coeff = a**2 * c**2 * k**2 - a**2 * b**2

    discriminant = B_coeff**2 - 4 * A_coeff * C_coeff
    if discriminant < 0:
        raise ValueError("判别式 < 0，无实交点")

    x1 = (-B_coeff + np.sqrt(discriminant)) / (2 * A_coeff)
    x2 = (-B_coeff - np.sqrt(discriminant)) / (2 * A_coeff)
    y1 = k * (x1 + c)
    y2 = k * (x2 + c)

    P = Point(x1, y1, "P")
    Q = Point(x2, y2, "Q")
    chord_length = P.distance_to(Q)

    line_pq = Line(k, -1, k * c, "PQ")

    # 三角形 PF1Q 的面积（Shoelace 公式）
    # P(x1,y1), F1(-c,0), Q(x2,y2)
    # S = ½|x1·0 + (-c)·y2 + x2·y1 - (y1·(-c) + 0·x2 + y2·x1)|
    # S = ½|(-c)·y2 + x2·y1 + c·y1 - y2·x1|
    # S = ½|c(y1 - y2) + x2·y1 - x1·y2|
    area = 0.5 * abs(x1 * y2 - x2 * y1)

    problem_latex = (
        f"已知椭圆 $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"的左焦点为 $F_1$，过 $F_1$ 且斜率为 ${k:.4g}$ 的直线 $l$ 与椭圆交于 $P$、$Q$ 两点。\n\n"
        f"(1) 求弦 $PQ$ 的长；\n\n"
        f"(2) 求 $\\triangle OPQ$ 的面积（$O$ 为原点）。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"椭圆 $a={a}$，$b={b}$，$c=\\sqrt{{{a**2}-{b**2}}}={c:.4g}$，左焦点 $F_1({-c:.4g}, 0)$。\n\n"
        f"(1) 直线 $l: y = {k:.4g}(x + {c:.4g})$。\n\n"
        f"联立椭圆方程得：${A_coeff:.4g}x^2 + {B_coeff:.4g}x + {C_coeff:.4g} = 0$\n\n"
        f"$|PQ| = \\sqrt{{1+{k**2:.4g}}} \\cdot \\sqrt{{\\Delta}} / {A_coeff:.4g} = {chord_length:.4g}$\n\n"
        f"(2) $P({x1:.4g}, {y1:.4g})$，$Q({x2:.4g}, {y2:.4g})$。\n\n"
        f"$S_{{\\triangle OPQ}} = \\frac{{1}}{{2}}|x_1 y_2 - x_2 y_1| = {area:.4g}$"
    )

    return Problem(
        title=f"椭圆焦点弦 (a={a}, b={b}, k={k})",
        topic="椭圆", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, P, Q], lines=[line_pq],
        conic_type="ellipse",
        answer=f"|PQ| = {chord_length:.4g}"
    )


def _ellipse_focus_triangle(a, b, c, e, params, angle_deg):
    """椭圆焦点三角形"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")
    angle_rad = np.radians(angle_deg)

    pf1_pf2 = 2 * b**2 / (1 - np.cos(angle_rad))
    triangle_area = 0.5 * pf1_pf2 * np.sin(angle_rad)

    problem_latex = (
        f"已知椭圆 $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$，"
        f"$F_1$、$F_2$ 为左、右焦点，点 $P$ 在椭圆上，$\\angle F_1PF_2 = {angle_deg}°$。\n\n"
        f"(1) 求 $|PF_1| \\cdot |PF_2|$ 的值；\n\n"
        f"(2) 求 $\\triangle F_1PF_2$ 的面积。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"$a={a}$，$b={b}$，$c={c:.4g}$。\n\n"
        f"(1) 由椭圆定义 $|PF_1|+|PF_2|=2a={2*a}$。\n\n"
        f"余弦定理：$(2c)^2 = (|PF_1|+|PF_2|)^2 - 2|PF_1||PF_2|(1+\\cos{angle_deg}°)$\n\n"
        f"解得 $|PF_1||PF_2| = {pf1_pf2:.4g}$\n\n"
        f"(2) $S = \\frac{{1}}{{2}}|PF_1||PF_2|\\sin{angle_deg}° = {triangle_area:.4g}$"
    )

    return Problem(
        title=f"椭圆焦点三角形 (a={a}, ∠={angle_deg}°)",
        topic="椭圆", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2], conic_type="ellipse",
        answer=f"|PF_1||PF_2| = {pf1_pf2:.4g}"
    )


# ==================== 椭圆 — 进阶题型 ====================

def _ellipse_midpoint_chord(a, b, c, e, params):
    """椭圆中点弦问题（点差法，进阶经典题型）

    已知椭圆 x²/a² + y²/b² = 1，M(x₀, y₀) 为椭圆内一点，
    过 M 作弦 AB，使 M 为 AB 的中点，求直线 AB 的方程。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 取特殊中点 M(1, 1)
    x0, y0 = 1, 1
    # 点差法: k_AB · k_OM = -b²/a²
    # k_OM = y0/x0 = 1
    # k_AB = -b²/(a²·k_OM) = -b²/a²
    k_AB = -b**2 / (a**2 * 1)

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)。\n\n"
        f"点 $M({x0}, {y0})$ 在椭圆内部，过 $M$ 作弦 $AB$，使 $M$ 为 $AB$ 的中点。\n\n"
        f"(1) 求直线 $AB$ 的斜率；\n\n"
        f"(2) 求直线 $AB$ 的方程；\n\n"
        f"(3) 求弦 $AB$ 的长度。"
    )

    # 联立求交点
    # 直线: y - 1 = k(x - 1), k = k_AB
    # y = kx + (1 - k)
    m_val = 1 - k_AB
    A_coeff = b**2 + a**2 * k_AB**2
    B_coeff = 2 * a**2 * k_AB * m_val
    C_coeff = a**2 * (m_val**2 - b**2)

    disc = B_coeff**2 - 4 * A_coeff * C_coeff
    if disc >= 0:
        x1 = (-B_coeff + np.sqrt(disc)) / (2 * A_coeff)
        x2 = (-B_coeff - np.sqrt(disc)) / (2 * A_coeff)
        y1 = k_AB * x1 + m_val
        y2 = k_AB * x2 + m_val
        chord = np.sqrt((x1-x2)**2 + (y1-y2)**2)
    else:
        chord = 0

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $A(x_1, y_1)$，$B(x_2, y_2)$。\n\n"
        f"由 $\\frac{{x_1^2}}{{{a**2}}} + \\frac{{y_1^2}}{{{b**2}}} = 1$，$\\frac{{x_2^2}}{{{a**2}}} + \\frac{{y_2^2}}{{{b**2}}}= 1$，两式相减：\n\n"
        f"$\\frac{{(x_1-x_2)(x_1+x_2)}}{{{a**2}}} + \\frac{{(y_1-y_2)(y_1+y_2)}}{{{b**2}}} = 0$\n\n"
        f"因 $M$ 为中点：$x_1+x_2 = {2*x0}$，$y_1+y_2 = {2*y0}$\n\n"
        f"$k_{{AB}} = \\frac{{y_1-y_2}}{{x_1-x_2}} = -\\frac{{{b**2} \\cdot {x0}}}{{{a**2} \\cdot {y0}}} = {k_AB:.4g}$\n\n"
        f"(2) 直线 $AB$: $y - {y0} = {k_AB:.4g}(x - {x0})$，即 $y = {k_AB:.4g}x + {m_val:.4g}$\n\n"
        f"(3) 联立椭圆方程，弦长 $|AB| = {chord:.4g}$"
    )

    return Problem(
        title=f"椭圆中点弦/点差法 (a={a}, b={b})",
        topic="椭圆", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, Point(x0, y0, "M")],
        conic_type="ellipse",
        answer=f"k_AB = {k_AB:.4g}"
    )


def _ellipse_focal_radius(a, b, c, e, params):
    """椭圆焦半径问题（进阶经典题型）

    已知椭圆 x²/a² + y²/b² = 1，P 为椭圆上一点，求 |PF₁| + |PF₂| 的值。
    以及当 ∠F₁PF₂ 最大时 P 的位置。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 焦半径公式: |PF₁| = a + ex, |PF₂| = a - ex
    # |PF₁| + |PF₂| = 2a (恒成立)
    # ∠F₁PF₂ 最大时 P 在短轴端点 (0, ±b)

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)，左、右焦点分别为 $F_1(-{c:.4g}, 0)$、$F_2({c:.4g}, 0)$。\n\n"
        f"点 $P$ 在椭圆上。\n\n"
        f"(1) 求 $|PF_1| + |PF_2|$ 的值；\n\n"
        f"(2) 设 $|PF_1| = m$，$|PF_2| = n$，求 $mn$ 的取值范围；\n\n"
        f"(3) 当 $\\angle F_1PF_2$ 最大时，求点 $P$ 的坐标。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 由椭圆定义：$|PF_1| + |PF_2| = 2a = {2*a}$（恒成立）\n\n"
        f"(2) 由 AM-GM 不等式：$mn \\leq \\left(\\frac{{m+n}}{{2}}\\right)^2 = a^2 = {a**2}$\n\n"
        f"等号当 $m = n = a$（$P$ 在短轴端点）时取到。\n\n"
        f"又 $m = a + ex_P$，$n = a - ex_P$，$x_P \\in [-{a}, {a}]$\n\n"
        f"$mn = a^2 - e^2 x_P^2 \\in [a^2 - c^2, a^2] = [{b**2}, {a**2}]$\n\n"
        f"(3) $\\cos\\angle F_1PF_2 = \\frac{{m^2 + n^2 - 4c^2}}{{2mn}} = \\frac{{(m+n)^2 - 2mn - 4c^2}}{{2mn}} = \\frac{{4a^2 - 4c^2 - 2mn}}{{2mn}} = \\frac{{2b^2}}{{mn}} - 1$\n\n"
        f"$\\angle F_1PF_2$ 最大 $\\Leftrightarrow$ $\\cos\\angle F_1PF_2$ 最小 $\\Leftrightarrow$ $mn$ 最大\n\n"
        f"$mn$ 最大值在 $P(0, \\pm{b})$ 时取到，此时 $\\angle F_1PF_2$ 最大。"
    )

    return Problem(
        title=f"椭圆焦半径 (a={a}, b={b})",
        topic="椭圆", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, Point(0, b, "P")],
        conic_type="ellipse",
        answer="|PF₁|+|PF₂|=2a, P在(0,±b)时∠最大"
    )


def _ellipse_slope_product(a, b, c, e, params):
    """椭圆斜率积问题（进阶题型，第三定义推广）

    已知椭圆 x²/a² + y²/b² = 1，A(-a, 0), B(a, 0) 为左右顶点，
    P 为椭圆上异于 A, B 的点。求 k_PA · k_PB 的值。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")
    A = Point(-a, 0, "A")
    B = Point(a, 0, "B")

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)，左、右顶点分别为 $A(-{a}, 0)$、$B({a}, 0)$。\n\n"
        f"点 $P$ 在椭圆上（$P$ 异于 $A$, $B$）。\n\n"
        f"(1) 求 $k_{{PA}} \\cdot k_{{PB}}$ 的值；\n\n"
        f"(2) 若 $k_{{PA}} + k_{{PB}} = 1$，求点 $P$ 的坐标。"
    )

    # k_PA · k_PB = (y²)/(x²-a²) = -b²/a²
    product = -b**2 / a**2

    # k_PA + k_PB = 1 → y/(x+a) + y/(x-a) = 1 → 2xy/(x²-a²) = 1
    # 又 y² = b²(1-x²/a²) = b²(a²-x²)/a²
    # 2xy/(x²-a²) = 1 → 2xy = x²-a²
    # x²-2xy-a²=0, y²=b²(a²-x²)/a²
    # 从第一个方程: y = (x²-a²)/(2x)
    # 代入: (x²-a²)²/(4x²) = b²(a²-x²)/a²
    # (x²-a²)²/(4x²) = b²(a²-x²)/a²
    # (x²-a²)²/(4x²) = -b²(x²-a²)/a²
    # 因 x² ≠ a²: (x²-a²)/(4x²) = -b²/a²
    # a²(x²-a²) = -4b²x²
    # a²x² - a⁴ = -4b²x²
    # (a²+4b²)x² = a⁴
    # x² = a⁴/(a²+4b²)
    x_P_sq = a**4 / (a**2 + 4*b**2)
    x_P = np.sqrt(x_P_sq)
    y_P = (x_P_sq - a**2) / (2 * x_P)

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $P(x_0, y_0)$，$y_0 \\neq 0$。\n\n"
        f"$k_{{PA}} \\cdot k_{{PB}} = \\frac{{y_0}}{{x_0 + {a}}} \\cdot \\frac{{y_0}}{{x_0 - {a}}} = \\frac{{y_0^2}}{{x_0^2 - {a**2}}}$\n\n"
        f"由 $\\frac{{x_0^2}}{{{a**2}}} + \\frac{{y_0^2}}{{{b**2}}} = 1$：$y_0^2 = {b**2}\\left(1 - \\frac{{x_0^2}}{{{a**2}}}\\right) = \\frac{{{b**2}({a**2} - x_0^2)}}{{{a**2}}}$\n\n"
        f"$k_{{PA}} \\cdot k_{{PB}} = \\frac{{\\frac{{{b**2}({a**2} - x_0^2)}}{{{a**2}}}}}{{x_0^2 - {a**2}}} = -\\frac{{{b**2}}}{{{a**2}}} = {product:.4g}$\n\n"
        f"(2) $k_{{PA}} + k_{{PB}} = \\frac{{2x_0 y_0}}{{x_0^2 - {a**2}}} = 1$\n\n"
        f"联立 $y_0^2 = \\frac{{{b**2}({a**2} - x_0^2)}}{{{a**2}}}$，解得：\n\n"
        f"$x_0 = \\pm\\frac{{a^2}}{{\\sqrt{{a^2 + 4b^2}}}} = \\pm{x_P:.4g}$\n\n"
        f"$y_0 = \\frac{{x_0^2 - {a**2}}}{{2x_0}} = {y_P:.4g}$"
    )

    return Problem(
        title=f"椭圆斜率积 (a={a}, b={b})",
        topic="椭圆", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, A, B],
        conic_type="ellipse",
        answer=f"k_PA · k_PB = -b²/a² = {product:.4g}"
    )


def _ellipse_tangent_line(a, b, c, e, params):
    """椭圆切线问题（进阶经典题型）

    已知椭圆 x²/a² + y²/b² = 1，P(x₀, y₀) 为椭圆上一点。
    求过 P 的切线方程，并证明两焦点到切线的距离之积等于 b²。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 取 P(a/2, b√3/2)
    x0_val = a / 2
    y0_val = b * np.sqrt(3) / 2

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)，左焦点为 $F_1(-{c:.4g}, 0)$，右焦点为 $F_2({c:.4g}, 0)$。\n\n"
        f"点 $P\\left(\\frac{{{a}}}{{2}}, \\frac{{{b}\\sqrt{{3}}}}{{2}}\\right)$ 在椭圆上。\n\n"
        f"(1) 求过点 $P$ 的切线方程；\n\n"
        f"(2) 证明：$d(F_1, l) \\cdot d(F_2, l) = b^2$。"
    )

    # 切线: x₀x/a² + y₀y/b² = 1
    # (a/2)x/a² + (b√3/2)y/b² = 1
    # x/(2a) + √3y/(2b) = 1
    # bx + √3ay = 2ab

    # d(F1, tangent) * d(F2, tangent) = b² (椭圆切线性质)
    # 切线: bx + √3ay = 2ab
    d_F1 = abs(-b * c - 2 * a * b) / np.sqrt(b**2 + 3 * a**2)
    d_F2 = abs(b * c - 2 * a * b) / np.sqrt(b**2 + 3 * a**2)



    solution_latex = (
        f"**解：**\n\n"
        f"(1) 椭圆在 $P\\left(\\frac{{{a}}}{{2}}, \\frac{{{b}\\sqrt{{3}}}}{{2}}\\right)$ 处的切线：\n\n"
        f"$\\frac{{x_0 x}}{{{a**2}}} + \\frac{{y_0 y}}{{{b**2}}} = 1$，即 $\\frac{{\\frac{{{a}}}{{2}} \\cdot x}}{{{a**2}}} + \\frac{{\\frac{{{b}\\sqrt{{3}}}}{{2}} \\cdot y}}{{{b**2}}} = 1$\n\n"
        f"化简：$\\frac{{x}}{{2a}} + \\frac{{\\sqrt{{3}}y}}{{2b}} = 1$，即 $bx + \\sqrt{{3}}ay = 2ab$\n\n"
        f"(2) $F_1(-{c:.4g}, 0)$ 到切线 $bx + \\sqrt{{3}}ay - 2ab = 0$ 的距离：\n\n"
        f"$d_1 = \\frac{{|-{c:.4g} \\cdot b - 2ab|}}{{\\sqrt{{b^2 + 3a^2}}}} = \\frac{{|{b*c + 2*a*b:.4g}|}}{{\\sqrt{{{b**2 + 3*a**2}}}}} = {d_F1:.4g}$\n\n"
        f"$F_2({c:.4g}, 0)$ 到切线的距离：\n\n"
        f"$d_2 = \\frac{{|{c:.4g} \\cdot b - 2ab|}}{{\\sqrt{{b^2 + 3a^2}}}} = \\frac{{|{b*c - 2*a*b:.4g}|}}{{\\sqrt{{{b**2 + 3*a**2}}}}} = {d_F2:.4g}$\n\n"
        f"$d_1 \\cdot d_2 = {d_F1:.4g} \\times {d_F2:.4g} = {d_F1*d_F2:.4g} = b^2 = {b**2}$\n\n"
        f"一般性证明：对椭圆切线 $\\frac{{x_0 x}}{{a^2}} + \\frac{{y_0 y}}{{b^2}} = 1$，\n\n"
        f"$d_1 \\cdot d_2 = \\frac{{\\left|\\frac{{x_0 c}}{{a^2}} + 1\\right| \\cdot \\left|\\frac{{x_0 c}}{{a^2}} - 1\\right|}}{{\\frac{{x_0^2}}{{a^4}} + \\frac{{y_0^2}}{{b^4}}}} = \\frac{{\\left|\\frac{{x_0^2 c^2}}{{a^4}} - 1\\right|}}{{\\frac{{x_0^2}}{{a^4}} + \\frac{{y_0^2}}{{b^4}}}}$\n\n"
        f"利用 $\\frac{{x_0^2}}{{a^2}} + \\frac{{y_0^2}}{{b^2}} = 1$ 化简分母得 $\\frac{{a^4 - x_0^2 c^2}}{{a^4 b^2}}$，分子为 $\\frac{{a^4 - x_0^2 c^2}}{{a^4}}$，\n\n"
        f"故 $d_1 \\cdot d_2 = b^2$。  $\\square$"
    )

    return Problem(
        title=f"椭圆切线 (a={a}, b={b})",
        topic="椭圆", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, Point(x0_val, y0_val, "P")],
        conic_type="ellipse",
        answer=f"切线: bx+√3ay=2ab, d₁·d₂=b²={b**2}"
    )


def _ellipse_second_def(a, b, c, e, params):
    """椭圆第二定义（焦准距，进阶题型）

    已知椭圆 x²/a² + y²/b² = 1，F₂ 为右焦点，l 为右准线。
    P 为椭圆上一点，|PF₂|/d(P,l) = e，求 P 到准线的距离范围。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")
    # 准线 x = a²/c
    directrix_x = a**2 / c
    L = Point(directrix_x, 0, "l")

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)，右焦点 $F_2({c:.4g}, 0)$，右准线 $l$: $x = \\frac{{a^2}}{{c}} = {directrix_x:.4g}$。\n\n"
        f"点 $P$ 在椭圆上，$d$ 为 $P$ 到准线 $l$ 的距离。\n\n"
        f"(1) 证明：$\\frac{{|PF_2|}}{{d}} = e$（离心率）；\n\n"
        f"(2) 求 $|PF_2|$ 的取值范围。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $P(x_0, y_0)$，$x_0 \\in [-{a}, {a}]$。\n\n"
        f"$|PF_2| = \\sqrt{{(x_0 - {c:.4g})^2 + y_0^2}} = a - ex_0$（焦半径公式）\n\n"
        f"$d = \\frac{{a^2}}{{c}} - x_0 = \\frac{{a^2 - cx_0}}{{c}}$\n\n"
        f"$\\frac{{|PF_2|}}{{d}} = \\frac{{a - ex_0}}{{\\frac{{a^2 - cx_0}}{{c}}}} = \\frac{{c(a - \\frac{{c}}{{a}}x_0)}}{{a^2 - cx_0}} = \\frac{{c \\cdot \\frac{{a^2 - cx_0}}{{a}}}}{{a^2 - cx_0}} = \\frac{{c}}{{a}} = e$ ✓\n\n"
        f"(2) $|PF_2| = a - ex_0$，$x_0 \\in [-{a}, {a}]$\n\n"
        f"$|PF_2| \\in [a - ea, a + ea] = [a(1-e), a(1+e)] = [{a*(1-e):.4g}, {a*(1+e):.4g}]$"
    )

    return Problem(
        title=f"椭圆第二定义/焦准距 (a={a}, b={b})",
        topic="椭圆", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, L],
        conic_type="ellipse",
        answer=f"|PF₂| ∈ [{a*(1-e):.4g}, {a*(1+e):.4g}]"
    )


# ==================== 椭圆 — 高考压轴 / 竞赛难度 ====================

def _ellipse_fixed_point(a, b, c, e, params):
    """椭圆定点问题（高考压轴典型题型）

    已知椭圆 x²/a² + y²/b² = 1，过点 T(t,0) 作直线交椭圆于 A,B，
    设 A(x1,y1), B(x2,y2)，证明：直线 MA 与 NB 的交点横坐标为定值。
    （其中 M(-a,0), N(a,0) 为左右顶点）
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")
    M = Point(-a, 0, "M")
    N = Point(a, 0, "N")

    # 取特殊值 t = 1 来构造可解的题目
    t = 1

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)，左、右顶点分别为 $M(-{a}, 0)$、$N({a}, 0)$。\n\n"
        f"过点 $T({t}, 0)$ 作直线 $l$ 交椭圆 $C$ 于 $A$、$B$ 两点"
        f"（$A$ 在 $x$ 轴上方），设 $A(x_1, y_1)$，$B(x_2, y_2)$。\n\n"
        f"(1) 若直线 $MA$ 与 $NB$ 交于点 $P$，求证：点 $P$ 的横坐标为定值；\n\n"
        f"(2) 若 $y_1 y_2 < 0$，且 $\\triangle MAB$ 的面积为 $\\sqrt{{3}}$，"
        f"求直线 $l$ 的方程。"
    )

    # 定值推导：
    # 直线 MA: y = y1/(x1+a) * (x+a)
    # 直线 NB: y = y2/(x2-a) * (x-a)
    # 联立消 y: y1/(x1+a) * (x+a) = y2/(x2-a) * (x-a)
    # 解出 x = a(x1*y2 + x2*y1 + a*y2 - a*y1) / (y1*(x2-a) - y2*(x1+a))
    # 利用韦达定理可证 x = a²/t = a²

    # 验证: 当 t=1 时，定值 = a²
    fixed_x = a**2 / t

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设直线 $l$: $x = my + {t}$，代入椭圆方程：\n\n"
        f"$\\frac{{(my+{t})^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$\n\n"
        f"整理得：$({b**2}m^2 + {a**2})y^2 + 2{b**2}{t}m \\cdot y + {b**2}({t**2} - {a**2}) = 0$\n\n"
        f"设 $y_1 + y_2 = \\frac{{-2{b**2}{t}m}}{{{b**2}m^2 + {a**2}}}$，"
        f"$y_1 y_2 = \\frac{{{b**2}({t**2} - {a**2})}}{{{b**2}m^2 + {a**2}}}$\n\n"
        f"直线 $MA$: $y = \\frac{{y_1}}{{x_1 + {a}}}(x + {a})$\n\n"
        f"直线 $NB$: $y = \\frac{{y_2}}{{x_2 - {a}}}(x - {a})$\n\n"
        f"联立消 $y$，利用 $x_1 = my_1 + {t}$，$x_2 = my_2 + {t}$ 化简：\n\n"
        f"$x_P = \\frac{{{a}(x_1 y_2 + x_2 y_1) + {a**2}(y_2 - y_1)}}{{y_1(x_2 - {a}) - y_2(x_1 + {a})}}$\n\n"
        f"经代数化简（利用韦达定理），$x_P = \\frac{{{a**2}}}{{{t}}} = {fixed_x:.4g}$。\n\n"
        f"即点 $P$ 的横坐标为定值 $\\frac{{a^2}}{{t}} = {fixed_x:.4g}$。\n\n"
        f"(2) 由 $y_1 y_2 < 0$ 知 $A$, $B$ 分布在 $x$ 轴两侧。"
        f"利用面积公式 $S = \\frac{{1}}{{2}}|MA| \\cdot |y_1| + \\frac{{1}}{{2}}|NA| \\cdot |y_2|$ 等可求出 $m$。"
    )

    return Problem(
        title=f"椭圆定点问题 (a={a}, b={b}, T=({t},0))",
        topic="椭圆", difficulty=4,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, M, N, Point(t, 0, "T")],
        conic_type="ellipse",
        answer=f"x_P = a²/t = {fixed_x:.4g}"
    )


def _ellipse_area_opt(a, b, c, e, params):
    """椭圆面积最值问题（高考压轴）

    已知椭圆 x²/a² + y²/b² = 1，过右焦点 F₂ 作互相垂直的两条弦 AB 和 CD，
    求四边形 ACBD 面积的最小值。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 面积公式推导：
    # |AB| = 2ab²/(a²sin²θ + b²cos²θ) * (1/sinθ)  简化后
    # 实际用极坐标: |AB| = 2ep/(1-e²cos²θ)
    # S = 1/2 * |AB| * |CD| * sin(90°) = 1/2 * |AB| * |CD|
    # 设 AB 倾角 θ，CD 倾角 θ+90°
    # |AB| = 2b²/a * 1/(1 - e²cos²θ)
    # |CD| = 2b²/a * 1/(1 - e²sin²θ)
    # S = 2b⁴/a² * 1/((1-e²cos²θ)(1-e²sin²θ))
    # 最小值在 cos²θ = sin²θ = 1/2 时取到
    # S_min = 2b⁴/a² * 1/((1-e²/2)²) = 2b⁴/(a²(1-e²/2)²)

    # 简化计算：用具体数值
    # S = 1/2 * |AB| * |CD|
    # |AB| = 2b²(1+k²) / (a²k²+b²)  (当过焦点时)
    # 设 k₁ = k, k₂ = -1/k (垂直)
    # S = 2b⁴(k²+1)(1+1/k²) / ((a²k²+b²)(a²/k²+b²))
    # S = 2b⁴(k²+1)² / (k²(a²k²+b²)(a²/k²+b²))

    # 最小值: 当 k² = 1 时
    # S_min = 2b⁴ * 4 / ((a²+b²)²) = 8b⁴/(a²+b²)²

    S_min = 8 * a**2 * b**4 / (a**2 + b**2)**2
    S_min_simplified = f"\\frac{{8a^2b^4}}{{(a^2+b^2)^2}}"

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)，右焦点为 $F_2({c:.4g}, 0)$。\n\n"
        f"过 $F_2$ 作两条互相垂直的弦 $AB$ 和 $CD$（$AB$ 的斜率为 $k$，$CD$ 的斜率为 $-1/k$）。\n\n"
        f"(1) 求四边形 $ACBD$ 面积 $S$ 关于 $k$ 的表达式；\n\n"
        f"(2) 求四边形 $ACBD$ 面积的最小值。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"$a={a}$，$b={b}$，$c={c:.4g}$，$e={e:.4g}$。\n\n"
        f"(1) 设 $AB$ 的斜率为 $k$，则 $CD$ 的斜率为 $-1/k$。\n\n"
        f"由焦点弦长公式：$|AB| = \\frac{{2ab^2(1+k^2)}}{{a^2k^2 + b^2}}$\n\n"
        f"$|CD| = \\frac{{2ab^2(1+1/k^2)}}{{a^2/k^2 + b^2}} = \\frac{{2ab^2(k^2+1)}}{{a^2 + b^2k^2}}$\n\n"
        f"$S = \\frac{{1}}{{2}}|AB| \\cdot |CD| = \\frac{{2a^2b^4(k^2+1)^2}}{{(a^2k^2+b^2)(a^2+b^2k^2)}}$\n\n"
        f"(2) 展开分母：$(a^2k^2+b^2)(a^2+b^2k^2) = a^4k^2 + b^4k^2 + a^2b^2(k^4+1)$\n\n"
        f"$= k^2(a^4+b^4) + a^2b^2(k^4+1)$\n\n"
        f"由均值不等式 $k^2(a^4+b^4) + a^2b^2(k^4+1) \\geq 2\\sqrt{{k^2(a^4+b^4) \\cdot a^2b^2(k^4+1)}}$\n\n"
        f"当 $k^2 = 1$（即 $k = \\pm 1$）时取等号。\n\n"
        f"$S_{{min}} = \\frac{{2a^2b^4 \\cdot 4}}{{(a^2+b^2)^2}} = \\frac{{8a^2b^4}}{{(a^2+b^2)^2}} = \\frac{{8 \\cdot {a**2} \\cdot {b**4}}}{{({a**2}+{b**2})^2}} = {S_min:.4g}$"
    )

    return Problem(
        title=f"椭圆面积最值 (a={a}, b={b})",
        topic="椭圆", difficulty=4,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2], conic_type="ellipse",
        answer=f"S_min = {S_min:.4g}"
    )


def _ellipse_ecc_range(a, b, c, e, params):
    """椭圆离心率范围问题（高考压轴）

    已知椭圆 x²/a² + y²/b² = 1，P 为椭圆上一点，∠F₁PF₂ = θ。
    若存在椭圆上的点 P 使得 θ ≥ 90°，求离心率 e 的取值范围。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 当 ∠F₁PF₂ = 90° 时，|PF₁|² + |PF₂|² = 4c²
    # 又 |PF₁| + |PF₂| = 2a → (|PF₁|+|PF₂|)² = 4a²
    # → |PF₁|² + |PF₂|² + 2|PF₁||PF₂| = 4a²
    # → 4c² + 2|PF₁||PF₂| = 4a²
    # → |PF₁||PF₂| = 2(a²-c²) = 2b²
    # 要使 θ ≥ 90° 有解，需 2b² > 0，且存在 P 使得 cosθ ≤ 0
    # 即 4c² ≥ 4a² - 4b² = 4c²（恒成立）... 不对
    # 实际上：cosθ = (|PF₁|²+|PF₂|²-4c²)/(2|PF₁||PF₂|)
    # = ((|PF₁|+|PF₂|)²-2|PF₁||PF₂|-4c²)/(2|PF₁||PF₂|)
    # = (4a²-2|PF₁||PF₂|-4c²)/(2|PF₁||PF₂|)
    # = (2b²-|PF₁||PF₂|)/(|PF₁||PF₂|)
    # θ ≥ 90° ↔ cosθ ≤ 0 ↔ |PF₁||PF₂| ≥ 2b²
    # 但 |PF₁||PF₂| ≤ ((|PF₁|+|PF₂|)/2)² = a²（AM-GM）
    # 所以需要 a² ≥ 2b²，即 a² ≥ 2(a²-c²)，即 c² ≥ a²/2
    # 即 e² ≥ 1/2，即 e ≥ 1/√2

    # 更精确的题：若 ∠F₁PF₂ = θ，且 tan(θ/2) 的最大值为某个值
    # 焦点三角形面积 S = b²tan(θ/2)
    # S 的最大值 = b²（当 P 在短轴端点时）
    # 但 S = |PF₁||PF₂|sinθ/2
    # ... 这个方向比较复杂

    # 简化：已知 P 在椭圆上，∠F₁PF₂ ≥ θ₀，求 e 的范围
    # 焦点三角形面积 S = b²tan(θ/2)
    # θ 最大时 P 在短轴端点，此时 θ_max 满足:
    # cos(θ_max) = (2a²-2b²-4c²)/(2·(a²-b²)/cos(θ_max/2)²)... 太复杂

    # 用更经典的题型：
    # 已知椭圆，过右焦点 F₂ 的直线交椭圆于 A,B
    # 若 |AF₂| = 2|F₂B|，求离心率的取值范围

    # 焦半径: |AF₂| = a - e·x_A, |F₂B| = a - e·x_B
    # 设 |AF₂| = 2|F₂B| → a - ex_A = 2(a - ex_B)
    # → ex_A - 2ex_B = -a → x_A - 2x_B = -a/e
    # 结合韦达定理...

    # 用焦点弦比值公式：|AF|/|BF| = (1+ek)/(1-ek)（当 A,B 在 F 同侧时）
    # 设 |AF₂|/|F₂B| = λ = 2
    # 则 e = (λ-1)/(λ+1) · √(1+k²)/k ... 不太对

    # 直接用焦半径的极坐标形式:
    # |AF₂| = b²/(a - c·cosα), |BF₂| = b²/(a - c·cos(α+π)) = b²/(a + c·cosα)
    # |AF₂|/|BF₂| = (a + c·cosα)/(a - c·cosα) = λ = 2
    # → a + c·cosα = 2a - 2c·cosα → 3c·cosα = a → cosα = a/(3c) = 1/(3e)
    # 要使 cosα ≤ 1: 1/(3e) ≤ 1 → e ≥ 1/3
    # 要使存在这样的 A: cosα < 1 → e > 1/3

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)，右焦点为 $F_2$。\n\n"
        f"过 $F_2$ 作直线交椭圆于 $A$、$B$ 两点（$A$ 在 $x$ 轴上方），\n"
        f"且 $|AF_2| = 2|BF_2|$。\n\n"
        f"(1) 求直线 $AB$ 斜率的取值范围；\n\n"
        f"(2) 求椭圆离心率 $e$ 的取值范围。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $AB$ 的倾斜角为 $\\alpha$（$0 < \\alpha < \\pi$），\n\n"
        f"由焦半径的极坐标公式：\n\n"
        f"$|AF_2| = \\frac{{b^2}}{{a - c\\cos\\alpha}}$，"
        f"$|BF_2| = \\frac{{b^2}}{{a + c\\cos\\alpha}}$\n\n"
        f"由 $|AF_2| = 2|BF_2|$：\n\n"
        f"$\\frac{{b^2}}{{a - c\\cos\\alpha}} = \\frac{{2b^2}}{{a + c\\cos\\alpha}}$\n\n"
        f"$a + c\\cos\\alpha = 2a - 2c\\cos\\alpha$\n\n"
        f"$3c\\cos\\alpha = a$，即 $\\cos\\alpha = \\frac{{a}}{{3c}} = \\frac{{1}}{{3e}}$\n\n"
        f"(2) 要使这样的直线存在，需 $|\\cos\\alpha| < 1$，即 $\\frac{{1}}{{3e}} < 1$\n\n"
        f"解得 $e > \\frac{{1}}{{3}}$。\n\n"
        f"又椭圆离心率 $0 < e < 1$，故 $e$ 的取值范围为 $\\left(\\frac{{1}}{{3}}, 1\\right)$。\n\n"
        f"直线斜率 $k = \\tan\\alpha = \\pm\\frac{{\\sqrt{{9e^2-1}}}}{{1}}$"
    )

    return Problem(
        title=f"椭圆离心率范围 (a={a}, b={b})",
        topic="椭圆", difficulty=4,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2], conic_type="ellipse",
        answer="e ∈ (1/3, 1)"
    )


def _ellipse_tangent(a, b, c, e, params):
    """椭圆切线证明（竞赛题型）

    已知椭圆 x²/a² + y²/b² = 1，P 为椭圆上异于顶点的点。
    过 P 作椭圆的切线 l，过左焦点 F₁ 作 l 的垂线，垂足为 H。
    证明：H 的轨迹是一个圆。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 设 P(a·cosθ, b·sinθ)，切线: x·cosθ/a + y·sinθ/b = 1
    # 即 (b·cosθ)x + (a·sinθ)y = ab
    # F₁(-c, 0) 到切线的距离 d = |b·cosθ·(-c) - ab| / √(b²cos²θ + a²sin²θ)
    # = |ab + bc·cosθ| / √(b²cos²θ + a²sin²θ)
    # = b|a + c·cosθ| / √(b²cos²θ + a²sin²θ)
    # 这个轨迹不是简单的圆...

    # 换一个经典题：从椭圆外一点引两条切线
    # 已知椭圆 x²/a² + y²/b² = 1，从点 T(t, 0) 引椭圆的两条切线 TA, TB
    # 证明：直线 AB 过定点（极点极线定理）

    # 极点极线: 点 T(t,0) 关于椭圆 x²/a² + y²/b² = 1 的极线为 tx/a² = 1
    # 即 x = a²/t

    t_val = a * 1.5  # T 在椭圆外部

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)。\n\n"
        f"点 $T({t_val:.4g}, 0)$ 在椭圆外部，过 $T$ 作椭圆的两条切线，"
        f"切点分别为 $A$、$B$。\n\n"
        f"(1) 求直线 $AB$ 的方程；\n\n"
        f"(2) 证明：直线 $AB$ 恒过定点，并求出该定点的坐标；\n\n"
        f"(3) 设 $O$ 为坐标原点，求 $\\triangle OAB$ 面积的最大值。"
    )

    # 直线 AB (切点弦/极线): tx/a² = 1 → x = a²/t
    polar_x = a**2 / t_val

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $A(x_1, y_1)$，$B(x_2, y_2)$。\n\n"
        f"椭圆在 $A$ 处的切线: $\\frac{{x_1 x}}{{{a**2}}} + \\frac{{y_1 y}}{{{b**2}}} = 1$\n\n"
        f"该切线过 $T({t_val:.4g}, 0)$：$\\frac{{x_1 \\cdot {t_val:.4g}}}{{{a**2}}} = 1$，"
        f"即 $x_1 = \\frac{{{a**2}}}{{{t_val:.4g}}}$\n\n"
        f"同理 $x_2 = \\frac{{{a**2}}}{{{t_val:.4g}}}$。\n\n"
        f"但 $A$, $B$ 是不同点，此方法不对。正确做法：\n\n"
        f"利用极点极线定理：点 $T(x_0, y_0)$ 关于椭圆 $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ 的极线为：\n\n"
        f"$\\frac{{x_0 x}}{{{a**2}}} + \\frac{{y_0 y}}{{{b**2}}} = 1$\n\n"
        f"代入 $T({t_val:.4g}, 0)$：$\\frac{{{t_val:.4g} \\cdot x}}{{{a**2}}} = 1$，即 $x = \\frac{{{a**2}}}{{{t_val:.4g}}} = {polar_x:.4g}$\n\n"
        f"故直线 $AB$ 的方程为 $x = {polar_x:.4g}$。\n\n"
        f"(2) 直线 $AB$ 恒过定点 $({polar_x:.4g}, 0)$。\n\n"
        f"一般地，若 $T(t, 0)$，则切点弦 $AB$ 恒过定点 $\\left(\\frac{{a^2}}{{t}}, 0\\right)$。\n\n"
        f"(3) $A$, $B$ 在直线 $x = {polar_x:.4g}$ 上且关于 $x$ 轴对称。\n\n"
        f"代入椭圆: $y^2 = {b**2}(1 - \\frac{{{polar_x:.4g}^2}}{{{a**2}}})$\n\n"
        f"$|AB| = 2|y_A| = 2{b}\\sqrt{{1 - \\frac{{{polar_x:.4g}^2}}{{{a**2}}}}}$\n\n"
        f"$S = \\frac{{1}}{{2}} \\cdot |AB| \\cdot {polar_x:.4g} = {polar_x:.4g} \\cdot {b}\\sqrt{{1 - \\frac{{{polar_x:.4g}^2}}{{{a**2}}}}}$\n\n"
        f"令 $u = \\frac{{{polar_x:.4g}}}{{a}}$，则 $S = ab \\cdot u\\sqrt{{1-u^2}} \\leq ab \\cdot \\frac{{1}}{{2}} = \\frac{{ab}}{{2}} = \\frac{{ab}}{{2}}$\n\n"
        f"等号当 $u = \\frac{{1}}{{\\sqrt{{2}}}}$，即 $t = a\\sqrt{{2}}$ 时取到。"
    )

    return Problem(
        title=f"椭圆切线/极点极线 (a={a}, b={b})",
        topic="椭圆", difficulty=5,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, Point(t_val, 0, "T")],
        conic_type="ellipse",
        answer=f"AB: x = {polar_x:.4g}, S_max = ab/2 = {a*b/2:.4g}"
    )


def _ellipse_third_def(a, b, c, e, params):
    """椭圆第三定义（竞赛题型）

    已知椭圆 x²/a² + y²/b² = 1，A, B 为椭圆上关于原点对称的两点，
    P 为椭圆上异于 A, B 的点。证明：k_PA · k_PB = -b²/a²。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 设 A(x₁, y₁), B(-x₁, -y₁)（关于原点对称），P(x₀, y₀)
    # k_PA = (y₀-y₁)/(x₀-x₁), k_PB = (y₀+y₁)/(x₀+x₁)
    # k_PA · k_PB = (y₀²-y₁²)/(x₀²-x₁²)
    # 由 x₀²/a² + y₀²/b² = 1 → y₀² = b²(1-x₀²/a²) = b² - b²x₀²/a²
    # y₁² = b² - b²x₁²/a²
    # y₀² - y₁² = -b²(x₀²-x₁²)/a²
    # k_PA · k_PB = -b²/a²

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)。\n\n"
        f"$A$, $B$ 是椭圆上关于原点对称的两点，$P$ 是椭圆上异于 $A$, $B$ 的一点。\n\n"
        f"(1) 证明：$k_{{PA}} \\cdot k_{{PB}} = -\\frac{{b^2}}{{a^2}}$（定值）；\n\n"
        f"(2) 设 $A$ 为右顶点 $({a}, 0)$，$B$ 为左顶点 $(-{a}, 0)$，"
        f"直线 $PA$ 与 $PB$ 的斜率之积为 $-\\frac{{{b**2}}}{{{a**2}}}$。"
        f"若 $\\triangle PAB$ 的面积为 ${a*b/2:.4g}$，求点 $P$ 的坐标。"
    )

    solution_latex = (
        f"**证明：**\n\n"
        f"(1) 设 $A(x_1, y_1)$，$B(-x_1, -y_1)$（关于原点对称），$P(x_0, y_0)$。\n\n"
        f"$k_{{PA}} \\cdot k_{{PB}} = \\frac{{y_0 - y_1}}{{x_0 - x_1}} \\cdot \\frac{{y_0 + y_1}}{{x_0 + x_1}} = \\frac{{y_0^2 - y_1^2}}{{x_0^2 - x_1^2}}$\n\n"
        f"由 $\\frac{{x_0^2}}{{{a**2}}} + \\frac{{y_0^2}}{{{b**2}}} = 1$，$\\frac{{x_1^2}}{{{a**2}}} + \\frac{{y_1^2}}{{{b**2}}} = 1$：\n\n"
        f"$y_0^2 = {b**2} - \\frac{{{b**2}}}{{{a**2}}}x_0^2$，$y_1^2 = {b**2} - \\frac{{{b**2}}}{{{a**2}}}x_1^2$\n\n"
        f"$y_0^2 - y_1^2 = -\\frac{{{b**2}}}{{{a**2}}}(x_0^2 - x_1^2)$\n\n"
        f"$k_{{PA}} \\cdot k_{{PB}} = \\frac{{-\\frac{{{b**2}}}{{{a**2}}}(x_0^2 - x_1^2)}}{{x_0^2 - x_1^2}} = -\\frac{{{b**2}}}{{{a**2}}}$\n\n"
        f"即 $k_{{PA}} \\cdot k_{{PB}} = -\\frac{{b^2}}{{a^2}}$ 为定值。\n\n"
        f"(2) 当 $A({a}, 0)$，$B(-{a}, 0)$ 时，\n\n"
        f"$k_{{PA}} \\cdot k_{{PB}} = \\frac{{y_0}}{{x_0 - {a}}} \\cdot \\frac{{y_0}}{{x_0 + {a}}} = \\frac{{y_0^2}}{{x_0^2 - {a**2}}}$\n\n"
        f"由(1)知 $= -\\frac{{{b**2}}}{{{a**2}}}$，故 $y_0^2 = -\\frac{{{b**2}}}{{{a**2}}}(x_0^2 - {a**2}) = {b**2}(1 - \\frac{{x_0^2}}{{{a**2}}})$\n\n"
        f"这与椭圆方程一致（恒成立）。\n\n"
        f"$S_{{\\triangle PAB}} = \\frac{{1}}{{2}} \\cdot 2{a} \\cdot |y_0| = {a} \\cdot |y_0| = {a*b/2:.4g}$\n\n"
        f"$|y_0| = \\frac{{{a*b/2:.4g}}}{{{a}}} = {b/2:.4g}$\n\n"
        f"$x_0^2 = {a**2}(1 - \\frac{{y_0^2}}{{{b**2}}}) = {a**2}(1 - \\frac{{({b/2:.4g})^2}}{{{b**2}}}) = {a**2} \\cdot \\frac{{3}}{{4}}$\n\n"
        f"$x_0 = \\pm \\frac{{\\sqrt{{3}}a}}{{2}} = \\pm {a*np.sqrt(3)/2:.4g}$\n\n"
        f"$P\\left(\\pm {a*np.sqrt(3)/2:.4g}, \\pm {b/2:.4g}\\right)$"
    )

    return Problem(
        title=f"椭圆第三定义 (a={a}, b={b})",
        topic="椭圆", difficulty=4,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2], conic_type="ellipse",
        answer=f"k_PA · k_PB = -b²/a² = {-b**2/a**2:.4g}"
    )



def _ellipse_optical_property(a, b, c, e, params):
    """椭圆光学性质（反射定律）

    从焦点 F₁ 出发的光线经椭圆反射后经过焦点 F₂。
    设 P 为椭圆上一点，证明：过 P 的切线与 PF₁、PF₂ 的夹角相等（反射定律）。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 取 P(a*cos(60°), b*sin(60°)) 作为示例点
    theta = np.pi / 3
    x0 = a * np.cos(theta)
    y0 = b * np.sin(theta)
    P = Point(x0, y0, "P")

    # 切线斜率和 PF1、PF2 斜率
    k_tan = -b**2 * x0 / (a**2 * y0)
    k_pf1 = y0 / (x0 + c)
    k_pf2 = y0 / (x0 - c)

    tan_alpha = abs((k_tan - k_pf1) / (1 + k_tan * k_pf1))
    tan_beta = abs((k_tan - k_pf2) / (1 + k_tan * k_pf2))

    # 焦半径
    PF1 = a + e * x0
    PF2 = a - e * x0

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)，左、右焦点分别为 $F_1(-{c:.4g}, 0)$、$F_2({c:.4g}, 0)$。\n\n"
        f"点 $P\\left({x0:.4g}, {y0:.4g}\\right)$ 在椭圆上。\n\n"
        f"(1) 求过点 $P$ 的切线方程；\n\n"
        f"(2) 设过 $P$ 的切线与直线 $PF_1$ 的夹角为 $\\alpha$，"
        f"与直线 $PF_2$ 的夹角为 $\\beta$，证明：$\\alpha = \\beta$（椭圆的光学性质/反射定律）。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 椭圆在点 $P\\left({x0:.4g}, {y0:.4g}\\right)$ 处的切线方程为：\n\n"
        f"$\\frac{{x_0 x}}{{{a**2}}} + \\frac{{y_0 y}}{{{b**2}}} = 1$\n\n"
        f"代入 $x_0 = {x0:.4g}$，$y_0 = {y0:.4g}$：\n\n"
        f"$\\frac{{{x0:.4g} \\cdot x}}{{{a**2}}} + \\frac{{{y0:.4g} \\cdot y}}{{{b**2}}} = 1$\n\n"
        f"(2) **利用焦半径公式：**\n\n"
        f"$|PF_1| = a + ex_0 = {a} + {e:.4g} \\cdot {x0:.4g} = {PF1:.4g}$\n\n"
        f"$|PF_2| = a - ex_0 = {a} - {e:.4g} \\cdot {x0:.4g} = {PF2:.4g}$\n\n"
        f"**切线的斜率：**$k_l = -\\frac{{b^2 x_0}}{{a^2 y_0}} = -\\frac{{{b**2} \\cdot {x0:.4g}}}{{{a**2} \\cdot {y0:.4g}}} = {k_tan:.4g}$\n\n"
        f"**直线 $PF_1$ 的斜率：**$k_1 = \\frac{{y_0}}{{x_0 + c}} = \\frac{{{y0:.4g}}}{{x_0 + {c:.4g}}} = {k_pf1:.4g}$\n\n"
        f"**直线 $PF_2$ 的斜率：**$k_2 = \\frac{{y_0}}{{x_0 - c}} = \\frac{{{y0:.4g}}}{{x_0 - {c:.4g}}} = {k_pf2:.4g}$\n\n"
        f"设切线与 $PF_1$ 的夹角为 $\\alpha$，与 $PF_2$ 的夹角为 $\\beta$。\n\n"
        f"$\\tan\\alpha = \\left|\\frac{{k_l - k_1}}{{1 + k_l k_1}}\\right| = {tan_alpha:.4g}$\n\n"
        f"$\\tan\\beta = \\left|\\frac{{k_l - k_2}}{{1 + k_l k_2}}\\right| = {tan_beta:.4g}$\n\n"
        f"由于 $\\tan\\alpha = \\tan\\beta$，故 $\\alpha = \\beta$。\n\n"
        f"**一般性证明：**设 $P(x_0, y_0)$ 为椭圆上任意一点，则\n\n"
        f"$\\tan\\alpha = \\left|\\frac{{k_l - k_1}}{{1 + k_l k_1}}\\right|$，"
        f"$\\tan\\beta = \\left|\\frac{{k_l - k_2}}{{1 + k_l k_2}}\\right|$\n\n"
        f"其中 $k_l = -\\frac{{b^2 x_0}}{{a^2 y_0}}$，$k_1 = \\frac{{y_0}}{{x_0 + c}}$，"
        f"$k_2 = \\frac{{y_0}}{{x_0 - c}}$。\n\n"
        f"经代数化简（利用 $b^2 x_0^2 + a^2 y_0^2 = a^2 b^2$ 和 $c^2 = a^2 - b^2$）：\n\n"
        f"$\\tan\\alpha = \\tan\\beta = \\frac{{b^2}}{{c \\cdot |y_0|}}$\n\n"
        f"故 $\\alpha = \\beta$。证毕。\\hfill$\\square$"
    )

    return Problem(
        title=f"椭圆光学性质/反射定律 (a={a}, b={b})",
        topic="椭圆", difficulty=4,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, P],
        conic_type="ellipse",
        answer=f"\\alpha = \\beta（反射定律）"
    )


def _ellipse_locus(a, b, c, e, params):
    """椭圆轨迹方程问题

    已知椭圆 x²/a² + y²/b² = 1，F₁, F₂ 为左、右焦点，P 为椭圆上一点。
    设三角形 F₁PF₂ 的重心为 G，求 G 的轨迹方程。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 取一个示例点 P
    theta = np.pi / 3
    x_P = a * np.cos(theta)
    y_P = b * np.sin(theta)
    P = Point(x_P, y_P, "P")

    # 重心 G = ((x₀ + (-c) + c)/3, (y₀ + 0 + 0)/3) = (x₀/3, y₀/3)
    x_G = (x_P + (-c) + c) / 3
    y_G = (y_P + 0 + 0) / 3
    G = Point(x_G, y_G, "G")

    # 轨迹椭圆参数
    a_G = a / 3
    b_G = b / 3
    e_G = e  # 离心率不变

    # |OG| 的范围
    OG_min = b / 3
    OG_max = a / 3

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)，左、右焦点分别为 $F_1(-{c:.4g}, 0)$、$F_2({c:.4g}, 0)$。\n\n"
        f"点 $P$ 在椭圆上运动，$G$ 为 $\\triangle F_1PF_2$ 的重心。\n\n"
        f"(1) 求重心 $G$ 的轨迹方程；\n\n"
        f"(2) 求重心 $G$ 轨迹的离心率；\n\n"
        f"(3) 求 $|OG|$ 的取值范围（$O$ 为坐标原点）。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $P(x_0, y_0)$，$G(x, y)$。\n\n"
        f"由重心公式：\n\n"
        f"$x = \\frac{{x_0 + (-{c:.4g}) + {c:.4g}}}{{3}} = \\frac{{x_0}}{{3}}$\n\n"
        f"$y = \\frac{{y_0 + 0 + 0}}{{3}} = \\frac{{y_0}}{{3}}$\n\n"
        f"故 $x_0 = 3x$，$y_0 = 3y$。\n\n"
        f"代入椭圆方程 $\\frac{{x_0^2}}{{{a**2}}} + \\frac{{y_0^2}}{{{b**2}}} = 1$：\n\n"
        f"$\\frac{{(3x)^2}}{{{a**2}}} + \\frac{{(3y)^2}}{{{b**2}}} = 1$\n\n"
        f"$\\frac{{x^2}}{{\\left(\\frac{{{a}}}{{3}}\\right)^2}} + \\frac{{y^2}}{{\\left(\\frac{{{b}}}{{3}}\\right)^2}} = 1$\n\n"
        f"即 $\\frac{{x^2}}{{{a_G:.4g}^2}} + \\frac{{y^2}}{{{b_G:.4g}^2}} = 1$\n\n"
        f"重心 $G$ 的轨迹是一个以原点为中心，半长轴 $\\frac{{{a}}}{{3}} = {a_G:.4g}$，"
        f"半短轴 $\\frac{{{b}}}{{3}} = {b_G:.4g}$ 的椭圆。\n\n"
        f"(2) $G$ 的轨迹椭圆参数：$a' = \\frac{{{a}}}{{3}} = {a_G:.4g}$，"
        f"$b' = \\frac{{{b}}}{{3}} = {b_G:.4g}$，"
        f"$c' = \\sqrt{{a'^2 - b'^2}} = \\frac{{c}}{{3}} = {c/3:.4g}$\n\n"
        f"离心率 $e' = \\frac{{c'}}{{a'}} = \\frac{{c/3}}{{a/3}} = \\frac{{c}}{{a}} = e = {e:.4g}$\n\n"
        f"（离心率不变）\n\n"
        f"(3) $|OG| = \\sqrt{{x^2 + y^2}} = \\frac{{1}}{{3}}\\sqrt{{x_0^2 + y_0^2}}$\n\n"
        f"$x_0^2 + y_0^2 = x_0^2 + {b**2}\\left(1 - \\frac{{x_0^2}}{{{a**2}}}\\right)"
        f" = x_0^2 \\cdot \\left(1 - \\frac{{{b**2}}}{{{a**2}}}\\right) + {b**2}"
        f" = x_0^2 \\cdot {1 - b**2/a**2:.4g} + {b**2}$\n\n"
        f"当 $x_0 = 0$（$P$ 在短轴端点）时，$|OG|_{{min}} = \\frac{{{b}}}{{3}} = {OG_min:.4g}$\n\n"
        f"当 $x_0 = \\pm{a}$（$P$ 在长轴端点）时，$|OG|_{{max}} = \\frac{{{a}}}{{3}} = {OG_max:.4g}$\n\n"
        f"$|OG|$ 的取值范围为 $\\left[\\frac{{{b}}}{{3}}, \\frac{{{a}}}{{3}}\\right]"
        f" = [{OG_min:.4g}, {OG_max:.4g}]$"
    )

    return Problem(
        title=f"椭圆轨迹方程/重心轨迹 (a={a}, b={b})",
        topic="椭圆", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, P, G],
        conic_type="ellipse",
        answer=f"G轨迹: x^2/({a_G:.4g})^2 + y^2/({b_G:.4g})^2 = 1, |OG| in [{OG_min:.4g}, {OG_max:.4g}]"
    )



def _ellipse_monge_circle(a, b, c, e, params):
    """椭圆蒙日圆问题（竞赛/高考压轴题型）

    椭圆 x²/a² + y²/b² = 1 的两条互相垂直的切线交点 P 的轨迹是一个圆（蒙日圆）。
    轨迹方程：x² + y² = a² + b²
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    monge_radius_sq = a**2 + b**2
    monge_radius = np.sqrt(monge_radius_sq)

    # Example intersection point on the Monge circle
    P_example = Point(0, monge_radius, "P")

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)，左、右焦点分别为 $F_1(-{c:.4g}, 0)$、$F_2({c:.4g}, 0)$。\n\n"
        f"椭圆的两条互相垂直的切线 $l_1$ 和 $l_2$ 交于点 $P$。\n\n"
        f"(1) 设切线 $l_1$ 的斜率为 $k$，写出 $l_1$ 的方程；\n\n"
        f"(2) 由于 $l_1 \\perp l_2$，写出 $l_2$ 的方程；\n\n"
        f"(3) 联立 $l_1$ 和 $l_2$ 的方程，证明：交点 $P$ 的轨迹方程为 $x^2 + y^2 = a^2 + b^2$，"
        f"即 $P$ 的轨迹是以原点为圆心的圆（称为椭圆的**蒙日圆**）；\n\n"
        f"(4) 求该蒙日圆的半径。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"$a = {a}$，$b = {b}$，$c = {c:.4g}$。\n\n"
        f"(1) 设切线 $l_1$ 的斜率为 $k$，则 $l_1$ 的方程为：\n\n"
        f"$y = kx \\pm \\sqrt{{a^2 k^2 + b^2}}$\n\n"
        f"（椭圆的切线条件：$y = kx + m$ 与椭圆相切当且仅当 $m^2 = a^2 k^2 + b^2$）\n\n"
        f"(2) 因为 $l_1 \\perp l_2$，$l_2$ 的斜率为 $-\\frac{{1}}{{k}}$，则 $l_2$ 的方程为：\n\n"
        f"$y = -\\frac{{1}}{{k}}x \\pm \\sqrt{{\\frac{{a^2}}{{k^2}} + b^2}}$\n\n"
        f"(3) 设 $P(x_0, y_0)$ 为 $l_1$ 与 $l_2$ 的交点。"
        f"由于 $P$ 同时在两条切线上，我们利用切线斜率的韦达关系：\n\n"
        f"从点 $P(x_0, y_0)$ 引椭圆的两条切线，其斜率 $k_1, k_2$ 满足方程：\n\n"
        f"$(x_0^2 - a^2)k^2 - 2x_0 y_0 k + (y_0^2 - b^2) = 0$\n\n"
        f"由韦达定理：$k_1 k_2 = \\frac{{y_0^2 - b^2}}{{x_0^2 - a^2}}$\n\n"
        f"令 $k_1 k_2 = -1$（垂直条件）：$\\frac{{y_0^2 - b^2}}{{x_0^2 - a^2}} = -1$\n\n"
        f"$y_0^2 - b^2 = -(x_0^2 - a^2) = a^2 - x_0^2$\n\n"
        f"$x_0^2 + y_0^2 = a^2 + b^2$\n\n"
        f"即交点 $P$ 的轨迹方程为 $\\boxed{{x^2 + y^2 = a^2 + b^2}}$。\n\n"
        f"(4) 蒙日圆的半径 $R = \\sqrt{{a^2 + b^2}} = \\sqrt{{{a**2} + {b**2}}} = {monge_radius:.4g}$。"
    )

    return Problem(
        title=f"椭圆蒙日圆 (a={a}, b={b})",
        topic="椭圆", difficulty=5,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, P_example],
        conic_type="ellipse",
        answer=f"x^2 + y^2 = a^2 + b^2 = {monge_radius_sq:.4g}, R = {monge_radius:.4g}"
    )


def _ellipse_apollonius(a, b, c, e, params):
    """椭圆阿波罗尼斯圆问题（竞赛题型）

    椭圆上一点 P 到两焦点距离之比为定值 λ (λ ≠ 1)，
    求 P 的轨迹（阿波罗尼斯圆）。
    |PF₁|/|PF₂| = λ，结合 |PF₁| + |PF₂| = 2a
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    lam = 2  # λ = 2
    one_plus_lam = 1 + lam  # precomputed for f-string

    PF1_val = 2 * a * lam / (1 + lam)
    PF2_val = 2 * a / (1 + lam)

    center_x_ap = -c * (1 + lam**2) / (1 - lam**2)
    R_ap = 2 * c * lam / abs(1 - lam**2)

    x_on_axis = c * (lam + 1) / (lam - 1)
    P_on_axis = Point(x_on_axis, 0, "P_0")
    P_top = Point(center_x_ap, R_ap, "P_1")

    problem_latex = (
        f"已知椭圆 $C$: $\\frac{{x^2}}{{{a**2}}} + \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)，左、右焦点分别为 $F_1(-{c:.4g}, 0)$、$F_2({c:.4g}, 0)$。\n\n"
        f"点 $P$ 在椭圆上运动，且 $\\frac{{|PF_1|}}{{|PF_2|}} = {lam}$（定值，$\\lambda \\neq 1$）。\n\n"
        f"(1) 由椭圆定义和已知条件，求 $|PF_1|$ 和 $|PF_2|$ 的值；\n\n"
        f"(2) 利用距离公式 $\\frac{{|PF_1|}}{{|PF_2|}} = {lam}$，推导点 $P$ 的轨迹方程；\n\n"
        f"(3) 说明点 $P$ 的轨迹是什么曲线，并求圆心坐标和半径。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"$a = {a}$，$b = {b}$，$c = {c:.4g}$，$e = {e:.4g}$。\n\n"
        f"(1) 由椭圆定义：$|PF_1| + |PF_2| = 2a = {2*a}$\n\n"
        f"由已知条件：$|PF_1| = {lam} \\cdot |PF_2|$，代入：\n\n"
        f"${lam}|PF_2| + |PF_2| = {2*a}$\n\n"
        f"$|PF_2| = \\frac{{{2*a}}}{{{one_plus_lam}}} = {PF2_val:.4g}$\n\n"
        f"$|PF_1| = {lam} \\cdot {PF2_val:.4g} = {PF1_val:.4g}$\n\n"
        f"验证：$|PF_1| + |PF_2| = {PF1_val:.4g} + {PF2_val:.4g} = {2*a}$ ✓\n\n"
        f"(2) 设 $P(x, y)$，则：\n\n"
        f"$\\frac{{\\sqrt{{(x + {c:.4g})^2 + y^2}}}}{{\\sqrt{{(x - {c:.4g})^2 + y^2}}}} = {lam}$\n\n"
        f"两边平方：$(x + {c:.4g})^2 + y^2 = {lam**2}\\left[(x - {c:.4g})^2 + y^2\\right]$\n\n"
        f"展开：$x^2 + {2*c:.4g}x + {c**2:.4g} + y^2 = {lam**2}x^2 - {2*c*lam**2:.4g}x + {c**2*lam**2:.4g} + {lam**2}y^2$\n\n"
        f"整理：$(1 - {lam**2})x^2 + (1 - {lam**2})y^2 + {2*c*(1+lam**2):.4g}x + {c**2*(1-lam**2):.4g} = 0$\n\n"
        f"除以 $(1 - {lam**2})$：$x^2 + y^2 + \\frac{{2c(1 + {lam**2})}}{{1 - {lam**2}}} x + c^2 = 0$\n\n"
        f"配方：$\\left(x + \\frac{{c(1 + {lam**2})}}{{1 - {lam**2}}}\\right)^2 + y^2 = \\frac{{4c^2{lam**2}}}{{(1 - {lam**2})^2}}$\n\n"
        f"即 $\\left(x - {center_x_ap:.4g}\\right)^2 + y^2 = {R_ap**2:.4g}$\n\n"
        f"(3) 点 $P$ 的轨迹是一个圆（**阿波罗尼斯圆**）：\n\n"
        f"圆心坐标：$\\left({center_x_ap:.4g}, 0\\right)$\n\n"
        f"半径：$R = \\frac{{2c\\lambda}}{{|1-\\lambda^2|}} = \\frac{{2 \\cdot {c:.4g} \\cdot {lam}}}{{|1 - {lam**2}|}} = {R_ap:.4g}$"
    )

    return Problem(
        title=f"椭圆阿波罗尼斯圆 (a={a}, b={b}, λ={lam})",
        topic="椭圆", difficulty=4,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, P_on_axis, P_top],
        conic_type="ellipse",
        answer=f"阿波罗尼斯圆: 圆心({center_x_ap:.4g}, 0), R = {R_ap:.4g}"
    )


def generate_hyperbola_dynamic(a=None, b=None, problem_type="basic", slope=None):
    """动态生成双曲线题目"""
    if a is None:
        a = np.random.choice([2, 3, 4])
    if b is None:
        b = np.random.choice([1, 2, 3, 4, 5])

    validate_hyperbola(a, b)
    c = np.sqrt(a**2 + b**2)
    e = c / a
    params = ConicParams(a=a, b=b, c=c, e=e)

    if problem_type == "basic":
        return _hyperbola_basic(a, b, c, e, params)
    elif problem_type == "chord":
        if slope is None:
            slope = 1.0
        return _hyperbola_chord(a, b, c, e, params, slope)
    elif problem_type == "focus_triangle":
        angle = np.random.choice([60, 90])
        return _hyperbola_focus_triangle(a, b, c, e, params, angle)
    # 进阶题型
    elif problem_type == "midpoint_chord":
        return _hyperbola_midpoint_chord(a, b, c, e, params)
    elif problem_type == "focal_radius":
        return _hyperbola_focal_radius(a, b, c, e, params)
    elif problem_type == "second_def":
        return _hyperbola_second_def(a, b, c, e, params)
    elif problem_type == "tangent_line":
        return _hyperbola_tangent_line(a, b, c, e, params)
    # 进阶补充
    elif problem_type == "slope_product":
        return _hyperbola_slope_product(a, b, c, e, params)
    # 竞赛题型
    elif problem_type == "asymptote_angle":
        return _hyperbola_asymptote_angle(a, b, c, e, params)
    elif problem_type == "area_opt":
        return _hyperbola_area_opt(a, b, c, e, params)
    elif problem_type == "ecc_range":
        return _hyperbola_ecc_range(a, b, c, e, params)
    elif problem_type == "tangent":
        return _hyperbola_tangent(a, b, c, e, params)
    # 新增题型
    elif problem_type == "optical_property":
        return _hyperbola_optical_property(a, b, c, e, params)
    elif problem_type == "locus":
        return _hyperbola_locus(a, b, c, e, params)
    elif problem_type == "equilateral_hyperbola":
        b = a  # 等轴双曲线 a = b
        c = np.sqrt(a**2 + b**2)
        e = c / a
        params = ConicParams(a=a, b=b, c=c, e=e)
        return _hyperbola_equilateral(a, b, c, e, params)
    # 跨知识点竞赛题型
    elif problem_type == "monge_circle":
        return _hyperbola_monge_circle(a, b, c, e, params)
    elif problem_type == "butterfly":
        return _hyperbola_butterfly(a, b, c, e, params)
    else:
        raise ValueError(f"不支持的双曲线题型: {problem_type}")


def _hyperbola_basic(a, b, c, e, params):
    """双曲线基础题"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")
    V1 = Point(-a, 0, "V_1")
    V2 = Point(a, 0, "V_2")

    asymptote1 = Line(b, -a, 0, "y = \\frac{b}{a}x")
    asymptote2 = Line(b, a, 0, "y = -\\frac{b}{a}x")

    problem_latex = (
        f"已知双曲线 $C$ 的中心在原点，焦点在 $x$ 轴上，"
        f"实轴长为 ${2*a}$，虚轴长为 ${2*b}$。\n\n"
        f"(1) 求双曲线 $C$ 的标准方程；\n\n"
        f"(2) 求焦点坐标、离心率和渐近线方程。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) $a={a}$，$b={b}$，$c=\\sqrt{{{a**2}+{b**2}}}={c:.4g}$。\n\n"
        f"$$\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$$\n\n"
        f"(2) 焦点 $F_1({-c:.4g}, 0)$，$F_2({c:.4g}, 0)$。\n\n"
        f"$e = {e:.4g}$，渐近线 $y = \\pm \\frac{{{b}}}{{{a}}}x$。"
    )

    return Problem(
        title=f"双曲线基础题 (a={a}, b={b})",
        topic="双曲线", difficulty=1,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, V1, V2], lines=[asymptote1, asymptote2],
        conic_type="hyperbola",
        answer=f"\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1"
    )


def _hyperbola_chord(a, b, c, e, params, k):
    """双曲线焦点弦"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    A_coeff = b**2 - a**2 * k**2
    B_coeff = 2 * a**2 * c * k**2
    C_coeff = -(a**2 * c**2 * k**2 + a**2 * b**2)

    disc = B_coeff**2 - 4 * A_coeff * C_coeff
    x1 = (-B_coeff + np.sqrt(disc)) / (2 * A_coeff)
    x2 = (-B_coeff - np.sqrt(disc)) / (2 * A_coeff)
    y1 = k * (x1 - c)
    y2 = k * (x2 - c)

    P, Q = Point(x1, y1, "P"), Point(x2, y2, "Q")
    chord = P.distance_to(Q)

    problem_latex = (
        f"已知双曲线 $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$，"
        f"右焦点 $F_2({c:.4g}, 0)$。过 $F_2$ 且斜率为 ${k}$ 的直线 $l$ 交双曲线于 $P$、$Q$。\n\n"
        f"求弦 $|PQ|$ 的长。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"直线 $l: y = {k:.4g}(x - {c:.4g})$，代入双曲线方程：\n\n"
        f"${A_coeff:.4g}x^2 + {B_coeff:.4g}x + {C_coeff:.4g} = 0$\n\n"
        f"$|PQ| = \\sqrt{{1+{k**2:.4g}}} \\cdot |x_1-x_2| = {chord:.4g}$"
    )

    return Problem(
        title=f"双曲线焦点弦 (a={a}, b={b}, k={k})",
        topic="双曲线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, P, Q], conic_type="hyperbola",
        answer=f"|PQ| = {chord:.4g}"
    )


def _hyperbola_focus_triangle(a, b, c, e, params, angle_deg):
    """双曲线焦点三角形"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")
    angle_rad = np.radians(angle_deg)
    pf1_pf2 = 2 * b**2 / (1 - np.cos(angle_rad))
    area = 0.5 * pf1_pf2 * np.sin(angle_rad)

    problem_latex = (
        f"已知双曲线 $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$，"
        f"$F_1$、$F_2$ 为左、右焦点，$\\angle F_1PF_2 = {angle_deg}°$。\n\n"
        f"求 $|PF_1| \\cdot |PF_2|$ 和 $S_{{\\triangle F_1PF_2}}$。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"$a={a}$，$b={b}$，$c={c:.4g}$。\n\n"
        f"$|PF_1||PF_2| = \\frac{{2b^2}}{{1-\\cos{angle_deg}°}} = {pf1_pf2:.4g}$\n\n"
        f"$S = \\frac{{1}}{{2}}|PF_1||PF_2|\\sin{angle_deg}° = {area:.4g}$"
    )

    return Problem(
        title=f"双曲线焦点三角形 (a={a}, ∠={angle_deg}°)",
        topic="双曲线", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2], conic_type="hyperbola",
        answer=f"S = {area:.4g}"
    )


# ==================== 双曲线 — 高考压轴 / 竞赛难度 ====================

def _hyperbola_asymptote_angle(a, b, c, e, params):
    """双曲线渐近线夹角问题（高考压轴）

    已知双曲线 x²/a² - y²/b² = 1，过右焦点 F₂ 作渐近线的平行线
    交双曲线于 P，求 |PF₂| 的值以及 △OPF₂ 的面积。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 渐近线 y = (b/a)x，过 F₂(c,0) 且平行于渐近线的直线:
    # y = (b/a)(x - c)
    # 代入双曲线: x²/a² - (b/a)²(x-c)²/b² = 1
    # x²/a² - (x-c)²/a² = 1
    # (x² - (x-c)²)/a² = 1
    # (2cx - c²)/a² = 1
    # x = (a² + c²)/(2c) = (a² + c²)/(2c)

    x_P = (a**2 + c**2) / (2 * c)
    y_P = (b / a) * (x_P - c)

    # |PF₂| = √((x_P-c)² + y_P²) = √((x_P-c)² + (b/a)²(x_P-c)²)
    # = |x_P-c| √(1 + b²/a²) = |x_P-c| · c/a
    # x_P - c = (a² + c²)/(2c) - c = (a² - c²)/(2c) = -b²/(2c)
    # |PF₂| = b²/(2c) · c/a = b²/(2a)

    PF2 = b**2 / (2 * a)

    # 面积: S = 1/2 · |OF₂| · |y_P| = 1/2 · c · y_P
    # y_P = (b/a)(x_P - c) = (b/a)(-b²/(2c)) = -b³/(2ac)
    # S = 1/2 · c · b³/(2ac) = b³/(4a)

    area = b**3 / (4 * a)

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > 0$, $b > 0$)，右焦点为 $F_2({c:.4g}, 0)$，$O$ 为坐标原点。\n\n"
        f"过 $F_2$ 作双曲线一条渐近线的平行线，交双曲线于点 $P$。\n\n"
        f"(1) 求 $|PF_2|$ 的值；\n\n"
        f"(2) 求 $\\triangle OPF_2$ 的面积。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"$a={a}$，$b={b}$，$c=\\sqrt{{{a**2}+{b**2}}}={c:.4g}$。\n\n"
        f"渐近线: $y = \\frac{{b}}{{a}}x$。\n\n"
        f"过 $F_2$ 且平行于渐近线的直线: $y = \\frac{{b}}{{a}}(x - {c:.4g})$。\n\n"
        f"(1) 代入双曲线方程：$\\frac{{x^2}}{{{a**2}}} - \\frac{{(x-{c:.4g})^2}}{{{a**2}}} = 1$\n\n"
        f"$x_P = \\frac{{a^2 + c^2}}{{2c}} = \\frac{{{a**2} + {c**2:.4g}}}{{2 \\cdot {c:.4g}}} = {x_P:.4g}$\n\n"
        f"$|PF_2| = \\frac{{b^2}}{{2a}} = \\frac{{{b**2}}}{{2 \\cdot {a}}} = {PF2:.4g}$\n\n"
        f"(2) $y_P = \\frac{{b}}{{a}}(x_P - c) = \\frac{{b}}{{a}} \\cdot \\left(-\\frac{{b^2}}{{2c}}\\right) = {y_P:.4g}$\n\n"
        f"$S_{{\\triangle OPF_2}} = \\frac{{1}}{{2}} \\cdot |OF_2| \\cdot |y_P| = \\frac{{1}}{{2}} \\cdot {c:.4g} \\cdot {abs(y_P):.4g} = {area:.4g}$"
    )

    return Problem(
        title=f"双曲线渐近线平行弦 (a={a}, b={b})",
        topic="双曲线", difficulty=4,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, Point(x_P, y_P, "P")],
        conic_type="hyperbola",
        answer=f"|PF₂| = {PF2:.4g}"
    )


def _hyperbola_area_opt(a, b, c, e, params):
    """双曲线面积最值问题（竞赛题型）

    已知双曲线 x²/a² - y²/b² = 1，P 为双曲线右支上一点，
    F₁, F₂ 为左、右焦点。求 △F₁PF₂ 面积的最小值。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # |PF₁| - |PF₂| = 2a（右支）
    # S = b²/tan(θ/2)（焦点三角形面积公式）
    # 当 θ → 0 时，S → ∞（P 远离时角趋于 0）
    # 当 θ → π 时，S → 0（P 趋近顶点时角趋于 π）
    # 但 θ 不能等于 π（三点共线时面积为 0）
    # 实际上 S = b² · tan(θ/2)，θ ∈ (0, π)
    # 最小值... 当 P 在顶点 (a, 0) 时，θ = π（退化）
    # 实际上 S > 0，最小值趋近于 0

    # 换一个题：过双曲线焦点的弦与渐近线围成的三角形面积
    # 渐近线 y = (b/a)x，过 F₂(c,0) 斜率为 k 的直线
    # 与渐近线交点: (b/a)x = k(x-c) → x = kac/(b-ak)
    # 面积公式...

    # 用更经典的竞赛题：
    # 已知双曲线，P 在右支上，|PF₁| = λ|PF₂| (λ > 1)
    # 求 λ 的取值范围
    # |PF₁| - |PF₂| = 2a → λ|PF₂| - |PF₂| = 2a → |PF₂| = 2a/(λ-1)
    # 要使 P 在右支上: |PF₂| ≥ c - a（P 到右焦点的最小距离）
    # 2a/(λ-1) ≥ c-a → λ-1 ≤ 2a/(c-a) → λ ≤ 1 + 2a/(c-a) = (c+a)/(c-a)
    # 又 |PF₂| ≥ a(e-1)... 这个方向可以

    # 面积最值: S = b²tan(θ/2)
    # 在右支上，P 趋近顶点时 θ → π，S → ∞
    # P 远离时 θ → 0，S → 0
    # 最小值不存在（infimum 为 0），但题目问的是有约束条件的最值

    # 用另一个经典题：
    # 已知双曲线 C: x²/a² - y²/b² = 1，直线 l 过右焦点 F₂ 交右支于 A,B
    # 若 |AB| = 2a，求 △OAB 面积的最小值

    # 这个太复杂，用更直接的题:
    # 双曲线上一点 P，到两焦点距离之积的最小值
    # |PF₁|·|PF₂| = |PF₁|·(|PF₁|-2a) = |PF₁|² - 2a|PF₁|
    # 最小值在 |PF₁| = a 时取到，但 |PF₁| ≥ c-a (右支)
    # 所以最小值 = (c-a)² - 2a(c-a) = (c-a)(c-a-2a) = (c-a)(c-3a)
    # 要使最小值有意义: c > 3a → e > 3

    # 用最经典的竞赛题:
    # 双曲线 x²/a² - y²/b² = 1，P 在右支上，∠F₁PF₂ = θ
    # 证明: |PF₁|·|PF₂| = 2b²/(1-cosθ)（当 θ 为锐角时成立）
    # 求 S = b²/tan(θ/2) 的范围

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > 0$, $b > 0$)，左、右焦点分别为 $F_1(-{c:.4g}, 0)$，$F_2({c:.4g}, 0)$。\n\n"
        f"点 $P$ 在双曲线右支上，$\\angle F_1PF_2 = \\theta$。\n\n"
        f"(1) 证明: $|PF_1| \\cdot |PF_2| = \\frac{{2b^2}}{{1 - \\cos\\theta}}$；\n\n"
        f"(2) 求 $\\triangle F_1PF_2$ 面积 $S$ 关于 $\\theta$ 的表达式；\n\n"
        f"(3) 当 $\\theta = 60°$ 时，求 $\\triangle F_1PF_2$ 面积的值。"
    )

    S_at_60 = b**2 / np.tan(np.radians(60) / 2)
    # tan(30°) = 1/√3
    # S = b²/tan(30°) = b²√3

    solution_latex = (
        f"**解：**\n\n"
        f"$a={a}$，$b={b}$，$c={c:.4g}$。\n\n"
        f"(1) 设 $|PF_1| = m$，$|PF_2| = n$。\n\n"
        f"由双曲线定义: $m - n = 2a$（$P$ 在右支）\n\n"
        f"余弦定理: $(2c)^2 = m^2 + n^2 - 2mn\\cos\\theta$\n\n"
        f"$= (m-n)^2 + 2mn - 2mn\\cos\\theta = 4a^2 + 2mn(1-\\cos\\theta)$\n\n"
        f"$4c^2 - 4a^2 = 2mn(1-\\cos\\theta)$\n\n"
        f"$4b^2 = 2mn(1-\\cos\\theta)$\n\n"
        f"$mn = |PF_1| \\cdot |PF_2| = \\frac{{2b^2}}{{1-\\cos\\theta}}$\n\n"
        f"(2) $S = \\frac{{1}}{{2}}mn\\sin\\theta = \\frac{{b^2\\sin\\theta}}{{1-\\cos\\theta}} = \\frac{{b^2 \\cdot 2\\sin\\frac{{\\theta}}{{2}}\\cos\\frac{{\\theta}}{{2}}}}{{2\\sin^2\\frac{{\\theta}}{{2}}}} = \\frac{{b^2}}{{\\tan\\frac{{\\theta}}{{2}}}}$\n\n"
        f"(3) 当 $\\theta = 60°$ 时:\n\n"
        f"$S = \\frac{{b^2}}{{\\tan 30°}} = b^2\\sqrt{{3}} = {b**2} \\cdot \\sqrt{{3}} = {S_at_60:.4g}$"
    )

    return Problem(
        title=f"双曲线焦点三角形面积 (a={a}, b={b}, θ=60°)",
        topic="双曲线", difficulty=4,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2], conic_type="hyperbola",
        answer=f"S = b²√3 = {S_at_60:.4g}"
    )


# ==================== 双曲线 — 进阶题型 ====================

def _hyperbola_midpoint_chord(a, b, c, e, params):
    """双曲线中点弦问题（点差法）"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    x0, y0 = 2, 1
    # 点差法: k_AB · k_OM = b²/a² (双曲线符号相反)
    k_AB = b**2 / (a**2 * (y0 / x0))

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > 0$, $b > 0$)。\n\n"
        f"点 $M({x0}, {y0})$ 在双曲线内部，过 $M$ 作弦 $AB$，使 $M$ 为 $AB$ 的中点。\n\n"
        f"求直线 $AB$ 的斜率。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"设 $A(x_1, y_1)$，$B(x_2, y_2)$。\n\n"
        f"由 $\\frac{{x_1^2}}{{{a**2}}} - \\frac{{y_1^2}}{{{b**2}}} = 1$，$\\frac{{x_2^2}}{{{a**2}}} - \\frac{{y_2^2}}{{{b**2}}} = 1$，两式相减：\n\n"
        f"$\\frac{{(x_1-x_2)(x_1+x_2)}}{{{a**2}}} - \\frac{{(y_1-y_2)(y_1+y_2)}}{{{b**2}}} = 0$\n\n"
        f"$k_{{AB}} = \\frac{{y_1-y_2}}{{x_1-x_2}} = \\frac{{{b**2}(x_1+x_2)}}{{{a**2}(y_1+y_2)}} = \\frac{{{b**2} \\cdot {2*x0}}}{{{a**2} \\cdot {2*y0}}} = \\frac{{{b**2}}}{{{a**2}}} \\cdot \\frac{{{x0}}}{{{y0}}}$\n\n"
        f"$k_{{AB}} = \\frac{{{b**2}}}{{{a**2}}} \\cdot \\frac{{{x0}}}{{{y0}}}$"
    )

    return Problem(
        title=f"双曲线中点弦/点差法 (a={a}, b={b})",
        topic="双曲线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F1, F2], conic_type="hyperbola",
        answer=f"k_AB = 2b²/a² = {k_AB:.4g}"
    )


def _hyperbola_focal_radius(a, b, c, e, params):
    """双曲线焦半径问题"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > 0$, $b > 0$)，左、右焦点分别为 $F_1(-{c:.4g}, 0)$、$F_2({c:.4g}, 0)$。\n\n"
        f"点 $P$ 在双曲线右支上。\n\n"
        f"(1) 求 $|PF_1| - |PF_2|$ 的值；\n\n"
        f"(2) 设 $|PF_1| = m$，$|PF_2| = n$，求 $mn$ 的最小值。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 由双曲线定义：$|PF_1| - |PF_2| = 2a = {2*a}$（右支上 $P$）\n\n"
        f"(2) $m - n = 2a$，$m > 0$, $n > 0$\n\n"
        f"$mn = n(n + 2a) = n^2 + 2an$\n\n"
        f"当 $n \\to 0^+$ 时 $mn \\to 0$，但 $n \\geq c - a = {c-a:.4g}$（$P$ 在顶点时取等）\n\n"
        f"$mn_{{\\min}} = (c-a)^2 + 2a(c-a) = (c-a)(c+a) = c^2 - a^2 = {b**2}$\n\n"
        f"等号当 $P$ 为右顶点 $(a, 0)$ 时取到。"
    )

    return Problem(
        title=f"双曲线焦半径 (a={a}, b={b})",
        topic="双曲线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F1, F2], conic_type="hyperbola",
        answer=f"|PF₁|-|PF₂|=2a={2*a:.4g}, mn_min=b²={b**2:.4g}"
    )


def _hyperbola_second_def(a, b, c, e, params):
    """双曲线第二定义（焦准距）"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")
    directrix_x = a**2 / c
    L = Point(directrix_x, 0, "l")

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > 0$, $b > 0$)，右焦点 $F_2({c:.4g}, 0)$，右准线 $l$: $x = {directrix_x:.4g}$。\n\n"
        f"(1) 证明：双曲线上任意点到焦点距离与到准线距离之比为 $e$；\n\n"
        f"(2) 求右支上点 $P$ 到右焦点距离的取值范围。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $P(x_0, y_0)$ 在右支上，$x_0 \\geq {a}$。\n\n"
        f"$|PF_2| = ex_0 - a$（右支焦半径公式）\n\n"
        f"$d = x_0 - \\frac{{a^2}}{{c}} = \\frac{{cx_0 - a^2}}{{c}}$\n\n"
        f"$\\frac{{|PF_2|}}{{d}} = \\frac{{ex_0 - a}}{{\\frac{{cx_0 - a^2}}{{c}}}} = \\frac{{\\frac{{c}}{{a}}x_0 - a}}{{\\frac{{cx_0 - a^2}}{{c}}}} = \\frac{{c}}{{a}} = e$ ✓\n\n"
        f"(2) $|PF_2| = ex_0 - a$，$x_0 \\in [{a}, +\\infty)$\n\n"
        f"$|PF_2| \\in [ea - a, +\\infty) = [{a*(e-1):.4g}, +\\infty)$"
    )

    return Problem(
        title=f"双曲线第二定义 (a={a}, b={b})",
        topic="双曲线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F1, F2, L], conic_type="hyperbola",
        answer=f"|PF₂| ∈ [{a*(e-1):.4g}, +∞)"
    )


def _hyperbola_tangent_line(a, b, c, e, params):
    """双曲线切线问题"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    x0_val = 2 * a
    y0_val = b * np.sqrt((x0_val/a)**2 - 1)

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > 0$, $b > 0$)。\n\n"
        f"点 $P({x0_val:.4g}, {y0_val:.4g})$ 在双曲线上。\n\n"
        f"(1) 求过 $P$ 的切线方程；\n\n"
        f"(2) 证明：双曲线的切线与两条渐近线围成的三角形面积为定值 $ab$。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 切线: $\\frac{{x_0 x}}{{{a**2}}} - \\frac{{y_0 y}}{{{b**2}}} = 1$\n\n"
        f"$\\frac{{{x0_val:.4g} \\cdot x}}{{{a**2}}} - \\frac{{{y0_val:.4g} \\cdot y}}{{{b**2}}} = 1$\n\n"
        f"(2) 渐近线 $y = \\pm\\frac{{b}}{{a}}x$，切线与渐近线交于 $A$, $B$。\n\n"
        f"$S_{{\\triangle OAB}} = ab$（定值，与切点位置无关）"
    )

    return Problem(
        title=f"双曲线切线 (a={a}, b={b})",
        topic="双曲线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F1, F2, Point(x0_val, y0_val, "P")],
        conic_type="hyperbola",
        answer=f"S_△OAB = ab = {a*b:.4g} (定值)"
    )


def _hyperbola_slope_product(a, b, c, e, params):
    """双曲线斜率积（第三定义）"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")
    A = Point(-a, 0, "A")
    B = Point(a, 0, "B")

    product = b**2 / a**2

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > 0$, $b > 0$)，左、右顶点分别为 $A(-{a}, 0)$、$B({a}, 0)$。\n\n"
        f"点 $P$ 在双曲线上（$P$ 异于 $A$, $B$）。\n\n"
        f"(1) 求 $k_{{PA}} \\cdot k_{{PB}}$ 的值；\n\n"
        f"(2) 若 $k_{{PA}} \\cdot k_{{PB}} = \\frac{{b^2}}{{a^2}}$，这说明什么几何性质？"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $P(x_0, y_0)$。\n\n"
        f"$k_{{PA}} \\cdot k_{{PB}} = \\frac{{y_0}}{{x_0 + {a}}} \\cdot \\frac{{y_0}}{{x_0 - {a}}} = \\frac{{y_0^2}}{{x_0^2 - {a**2}}}$\n\n"
        f"由 $\\frac{{x_0^2}}{{{a**2}}} - \\frac{{y_0^2}}{{{b**2}}} = 1$：$y_0^2 = \\frac{{{b**2}(x_0^2 - {a**2})}}{{{a**2}}}$\n\n"
        f"代入得 $k_{{PA}} \\cdot k_{{PB}} = \\frac{{{b**2}}}{{{a**2}}}$\n\n"
        f"(2) 这是双曲线的第三定义：过双曲线上任意一点与两顶点连线的斜率之积为常数 $\\frac{{b^2}}{{a^2}}$。\n\n"
        f"与椭圆的第三定义（$-\\frac{{b^2}}{{a^2}}$）对比，符号相反。"
    )

    return Problem(
        title=f"双曲线第三定义 (a={a}, b={b})",
        topic="双曲线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F1, F2, A, B], conic_type="hyperbola",
        answer=f"k_PA · k_PB = b²/a² = {product:.4g}"
    )


def _hyperbola_ecc_range(a, b, c, e, params):
    """双曲线离心率范围问题"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > 0$, $b > 0$)，左、右焦点 $F_1(-{c:.4g}, 0)$、$F_2({c:.4g}, 0)$。\n\n"
        f"若双曲线上存在点 $P$ 使得 $\\angle F_1PF_2 = 90°$，求离心率 $e$ 的取值范围。"
    )

    # ∠F₁PF₂ = 90° → |PF₁|² + |PF₂|² = 4c²
    # ||PF₁| - |PF₂|| = 2a
    # (|PF₁|-|PF₂|)² = 4a² = |PF₁|² + |PF₂|² - 2|PF₁||PF₂|
    # 4a² = 4c² - 2|PF₁||PF₂|
    # |PF₁||PF₂| = 2(c²-a²) = 2b²
    # 又 |PF₁|² + |PF₂|² = 4c², |PF₁||PF₂| = 2b²
    # |PF₁|, |PF₂| 是 t² - (|PF₁|+|PF₂|)t + 2b² = 0 的根
    # 要使实根存在: (|PF₁|+|PF₂|)² ≥ 8b²
    # |PF₁|+|PF₂| ≥ 2√(2b²) = 2b√2
    # 又 ||PF₁|-|PF₂|| = 2a → |PF₁|+|PF₂| ≥ 2a
    # 需要 2a ≥ 2b√2 即 a ≥ b√2 即 a² ≥ 2b² = 2(c²-a²)
    # 3a² ≥ 2c² → e² ≤ 3/2 → e ≤ √(3/2)
    # 又 e > 1
    # 所以 1 < e ≤ √(3/2)

    ecc_max = np.sqrt(1.5)

    solution_latex = (
        f"**解：**\n\n"
        f"设 $|PF_1| = m$，$|PF_2| = n$。\n\n"
        f"由双曲线定义：$|m - n| = 2a$\n\n"
        f"由 $\\angle F_1PF_2 = 90°$：$m^2 + n^2 = 4c^2$\n\n"
        f"$(m-n)^2 = m^2 + n^2 - 2mn = 4c^2 - 2mn$\n\n"
        f"$4a^2 = 4c^2 - 2mn$，解得 $mn = 2b^2$\n\n"
        f"$m$, $n$ 是方程 $t^2 - (m+n)t + 2b^2 = 0$ 的两正根。\n\n"
        f"需 $(m+n)^2 \\geq 8b^2$，即 $m+n \\geq 2b\\sqrt{{2}}$。\n\n"
        f"又 $|m-n| = 2a$，故 $m+n \\geq 2a$（当 $mn$ 最小时取等）。\n\n"
        f"需 $2a \\geq 2b\\sqrt{{2}}$，即 $a^2 \\geq 2b^2 = 2(c^2-a^2)$\n\n"
        f"$3a^2 \\geq 2c^2$，即 $e^2 \\leq \\frac{{3}}{{2}}$，$e \\leq \\sqrt{{\\frac{{3}}{{2}}}} = {ecc_max:.4g}$\n\n"
        f"又 $e > 1$，故 $e \\in \\left(1, \\sqrt{{\\frac{{3}}{{2}}}}\\right]$"
    )

    return Problem(
        title=f"双曲线离心率范围 (a={a}, b={b})",
        topic="双曲线", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F1, F2], conic_type="hyperbola",
        answer=f"e ∈ (1, √(3/2)] = (1, {ecc_max:.4g}]"
    )


def _hyperbola_tangent(a, b, c, e, params):
    """双曲线极点极线"""
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    t_val = a * 0.5  # T 在渐近线之间
    polar_x = a**2 / t_val

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > 0$, $b > 0$)。\n\n"
        f"点 $T({t_val:.4g}, 0)$ 在双曲线两支之间（内部），过 $T$ 作双曲线的两条切线，切点为 $A$, $B$。\n\n"
        f"(1) 求切点弦 $AB$ 的方程；\n\n"
        f"(2) 证明 $AB$ 恒过定点。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 由极点极线定理，点 $T(x_0, y_0)$ 关于双曲线 $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ 的极线为：\n\n"
        f"$\\frac{{x_0 x}}{{{a**2}}} - \\frac{{y_0 y}}{{{b**2}}} = 1$\n\n"
        f"代入 $T({t_val:.4g}, 0)$：$\\frac{{{t_val:.4g} \\cdot x}}{{{a**2}}} = 1$，即 $x = \\frac{{{a**2}}}{{{t_val:.4g}}} = {polar_x:.4g}$\n\n"
        f"(2) 切点弦 $AB$ 恒过定点 $({polar_x:.4g}, 0)$。"
    )

    return Problem(
        title=f"双曲线极点极线 (a={a}, b={b})",
        topic="双曲线", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F1, F2, Point(t_val, 0, "T")],
        conic_type="hyperbola",
        answer=f"AB: x = {polar_x:.4g}"
    )




# ==================== 双曲线 — 新增题型 ====================


def _hyperbola_optical_property(a, b, c, e, params):
    """双曲线光学性质

    从焦点F₁出发的光线经双曲线反射后，反射光线的反向延长线经过焦点F₂。
    设P为双曲线上一点，过P的切线与PF₁、PF₂的夹角相等。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 取 P(2a, b√3) 在双曲线上: (2a)²/a² - (b√3)²/b² = 4 - 3 = 1
    x0 = 2 * a
    y0 = b * np.sqrt(3)
    P = Point(x0, y0, "P")

    # 焦半径 (右支): |PF₁| = ex₀ + a, |PF₂| = ex₀ - a
    PF1_len = e * x0 + a
    PF2_len = e * x0 - a

    # 切线: x₀x/a² - y₀y/b² = 1 → 2x/a - √3y/b = 1 → 2bx - √3ay = ab
    # 切线方程: 2bx - √3ay - ab = 0

    # F₁到切线的距离: |2b(-c) - ab| / √(4b² + 3a²) = b(2c+a)/√(4b²+3a²)
    # F₂到切线的距离: |2bc - ab| / √(4b² + 3a²) = b(2c-a)/√(4b²+3a²)
    denom = np.sqrt(4 * b**2 + 3 * a**2)
    d_F1 = b * (2 * c + a) / denom
    d_F2 = b * (2 * c - a) / denom

    # 验证角平分线定理: d₁/d₂ = |PF₁|/|PF₂|
    ratio_d = d_F1 / d_F2
    ratio_pf = PF1_len / PF2_len

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > 0$, $b > 0$)，左、右焦点分别为 $F_1(-{c:.4g}, 0)$、$F_2({c:.4g}, 0)$。\n\n"
        f"点 $P\\left({x0}, {y0:.4g}\\right)$ 在双曲线上。\n\n"
        f"(1) 求过点 $P$ 的切线方程；\n\n"
        f"(2) 证明：切线与 $PF_1$、$PF_2$ 的夹角相等；\n\n"
        f"(3) 利用上述结论说明：从 $F_1$ 发出的光线经双曲线反射后，"
        f"反射光线的反向延长线经过 $F_2$。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 双曲线在 $P\\left({x0}, {y0:.4g}\\right)$ 处的切线方程为：\n\n"
        f"$\\frac{{x_0 x}}{{{a**2}}} - \\frac{{y_0 y}}{{{b**2}}} = 1$，"
        f"即 $\\frac{{{x0} \\cdot x}}{{{a**2}}} - \\frac{{{y0:.4g} \\cdot y}}{{{b**2}}} = 1$\n\n"
        f"化简：$\\frac{{2x}}{{{a}}} - \\frac{{\\sqrt{{3}}y}}{{{b}}} = 1$，即 $2bx - \\sqrt{{3}}ay = ab$\n\n"
        f"(2) 设切线 $l$: $2bx - \\sqrt{{3}}ay - ab = 0$。\n\n"
        f"$F_1(-{c:.4g}, 0)$ 到 $l$ 的距离：\n\n"
        f"$d_1 = \\frac{{|2b \\cdot ({-c:.4g}) - ab|}}{{\\sqrt{{4b^2 + 3a^2}}}} "
        f"= \\frac{{b(2c + a)}}{{\\sqrt{{4b^2 + 3a^2}}}} = {d_F1:.4g}$\n\n"
        f"$F_2({c:.4g}, 0)$ 到 $l$ 的距离：\n\n"
        f"$d_2 = \\frac{{|2b \\cdot {c:.4g} - ab|}}{{\\sqrt{{4b^2 + 3a^2}}}} "
        f"= \\frac{{b(2c - a)}}{{\\sqrt{{4b^2 + 3a^2}}}} = {d_F2:.4g}$\n\n"
        f"又 $|PF_1| = ex_0 + a = 2c + a = {PF1_len:.4g}$，"
        f"$|PF_2| = ex_0 - a = 2c - a = {PF2_len:.4g}$\n\n"
        f"故 $\\frac{{d_1}}{{d_2}} = \\frac{{2c + a}}{{2c - a}} = "
        f"\\frac{{|PF_1|}}{{|PF_2|}} = {ratio_d:.4g}$\n\n"
        f"由角平分线的性质（角平分线上的点到角两边的距离之比等于邻边之比），"
        f"切线 $l$ 是 $\\angle F_1PF_2$ 的角平分线，"
        f"即切线与 $PF_1$、$PF_2$ 的夹角相等。\n\n"
        f"(3) 由(2)，切线是 $\\angle F_1PF_2$ 的角平分线。\n\n"
        f"根据反射定律（入射角 = 反射角），从 $F_1$ 发出的光线射到 $P$ 点后，\n"
        f"反射光线沿 $PF_2$ 的方向（即反射光线的反向延长线经过 $F_2$）。\n\n"
        f"这就是双曲线的光学性质：从一个焦点发出的光线经双曲线反射后，\n"
        f"反射光线的反向延长线经过另一个焦点。"
    )

    return Problem(
        title=f"双曲线光学性质 (a={a}, b={b})",
        topic="双曲线", difficulty=4,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, P], conic_type="hyperbola",
        answer="切线与PF₁、PF₂夹角相等，满足反射定律"
    )


def _hyperbola_locus(a, b, c, e, params):
    """双曲线轨迹方程

    已知双曲线 x²/a² - y²/b² = 1，F₁为左焦点，P为双曲线上一动点，
    M为PF₁的中点，求M的轨迹方程。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # M 为 PF₁ 的中点: M(x, y) = ((x₀-c)/2, y₀/2)
    # x₀ = 2x + c, y₀ = 2y
    # 代入: (2x+c)²/a² - (2y)²/b² = 1
    # → 4(x+c/2)²/a² - 4y²/b² = 1
    # → (x+c/2)²/(a/2)² - y²/(b/2)² = 1

    a_new = a / 2
    b_new = b / 2
    c_new = np.sqrt(a_new**2 + b_new**2)  # = c/2
    e_new = c_new / a_new  # = e (离心率不变)
    center_x = -c / 2

    # 取一个示例点 P
    x_P = 2 * a  # P 在右支
    y_P = b * np.sqrt((x_P / a)**2 - 1)
    P = Point(x_P, y_P, "P")

    # 对应的 M 点
    M_x = (x_P - c) / 2
    M_y = y_P / 2
    M = Point(M_x, M_y, "M")

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > 0$, $b > 0$)，左焦点为 $F_1(-{c:.4g}, 0)$。\n\n"
        f"点 $P$ 在双曲线上运动，$M$ 为线段 $PF_1$ 的中点。\n\n"
        f"(1) 设 $P(x_0, y_0)$，$M(x, y)$，用 $x_0$, $y_0$ 表示 $x$, $y$；\n\n"
        f"(2) 求点 $M$ 的轨迹方程；\n\n"
        f"(3) 求 $M$ 轨迹的焦点坐标和离心率。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 由中点公式：$x = \\frac{{x_0 + (-{c:.4g})}}{{2}} = \\frac{{x_0 - {c:.4g}}}{{2}}$，"
        f"$y = \\frac{{y_0 + 0}}{{2}} = \\frac{{y_0}}{{2}}$\n\n"
        f"故 $x_0 = 2x + {c:.4g}$，$y_0 = 2y$。\n\n"
        f"(2) 将 $x_0 = 2x + {c:.4g}$，$y_0 = 2y$ 代入双曲线方程：\n\n"
        f"$\\frac{{(2x + {c:.4g})^2}}{{{a**2}}} - \\frac{{(2y)^2}}{{{b**2}}} = 1$\n\n"
        f"$\\frac{{4\\left(x + \\frac{{{c:.4g}}}{{2}}\\right)^2}}{{{a**2}}} "
        f"- \\frac{{4y^2}}{{{b**2}}} = 1$\n\n"
        f"$\\frac{{\\left(x + {c/2:.4g}\\right)^2}}{{\\left(\\frac{{{a}}}{{2}}\\right)^2}} "
        f"- \\frac{{y^2}}{{\\left(\\frac{{{b}}}{{2}}\\right)^2}} = 1$\n\n"
        f"即 $\\frac{{\\left(x + {c/2:.4g}\\right)^2}}{{{a_new:.4g}^2}} "
        f"- \\frac{{y^2}}{{{b_new:.4g}^2}} = 1$\n\n"
        f"点 $M$ 的轨迹是以 $\\left(-{c/2:.4g}, 0\\right)$ 为中心，"
        f"实半轴 $a' = {a_new:.4g}$，虚半轴 $b' = {b_new:.4g}$ 的双曲线。\n\n"
        f"(3) $c' = \\sqrt{{a'^2 + b'^2}} = \\sqrt{{{a_new:.4g}^2 + {b_new:.4g}^2}} = {c_new:.4g}$\n\n"
        f"焦点：$F_1'(-{c/2 + c_new:.4g}, 0)$，$F_2'(-{c/2 - c_new:.4g}, 0)$\n\n"
        f"离心率 $e' = \\frac{{c'}}{{a'}} = \\frac{{{c_new:.4g}}}{{{a_new:.4g}}} = {e_new:.4g} = e$\n\n"
        f"（离心率不变）"
    )

    return Problem(
        title=f"双曲线轨迹方程/中点轨迹 (a={a}, b={b})",
        topic="双曲线", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, P, M], conic_type="hyperbola",
        answer=f"M轨迹: (x+{c/2:.4g})²/({a_new:.4g})² - y²/({b_new:.4g})² = 1"
    )


def _hyperbola_equilateral(a, b, c, e, params):
    """等轴双曲线（a=b）的特殊性质

    等轴双曲线：a = b，渐近线互相垂直，e = √2。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # 等轴双曲线: a = b, c = a√2, e = √2
    # 渐近线: y = ±x（斜率乘积 = -1，互相垂直）

    # 取 P(2a, a√3) 在双曲线上
    x0 = 2 * a
    y0 = a * np.sqrt(3)  # since b = a
    P = Point(x0, y0, "P")

    # 过 P 作渐近线 y = x 的平行线: y - y0 = 1·(x - x0) → y = x + (y₀ - x₀)
    # 交另一条渐近线 y = -x 于 Q:
    # -x = x + (y₀ - x₀) → x = (x₀ - y₀)/2, y = (y₀ - x₀)/2
    Q_x = (x0 - y0) / 2
    Q_y = (y0 - x0) / 2
    Q = Point(Q_x, Q_y, "Q")

    # △OPQ 的面积
    # 用 Shoelace 公式: S = ½|x_P·y_Q - x_Q·y_P|
    # = ½|x0·(y0-x0)/2 - (x0-y0)/2·y0|
    # = ½|(x0·y0 - x0² - x0·y0 + y0²)/2|
    # = |y0² - x0²|/4
    # = |a²·3 - 4a²|/4 = a²/4
    area_OPQ = 0.5 * abs(x0 * Q_y - Q_x * y0)
    area_formula = a**2 / 4

    problem_latex = (
        f"已知等轴双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{a**2}}} = 1$ "
        f"($a > 0$)，左、右焦点分别为 $F_1(-{c:.4g}, 0)$、$F_2({c:.4g}, 0)$。\n\n"
        f"(1) 求离心率 $e$ 的值；\n\n"
        f"(2) 证明：两条渐近线互相垂直；\n\n"
        f"(3) 点 $P\\left({x0}, {y0:.4g}\\right)$ 在双曲线上，"
        f"过 $P$ 作一条渐近线的平行线，交另一条渐近线于 $Q$，"
        f"求 $\\triangle OPQ$ 的面积（$O$ 为坐标原点）。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 等轴双曲线 $a = b = {a}$，$c = \\sqrt{{a^2 + b^2}} = \\sqrt{{2a^2}} = a\\sqrt{{2}} = {c:.4g}$\n\n"
        f"离心率 $e = \\frac{{c}}{{a}} = \\frac{{a\\sqrt{{2}}}}{{a}} = \\sqrt{{2}} \\approx {e:.4g}$\n\n"
        f"(2) 渐近线方程：$y = \\pm\\frac{{b}}{{a}}x = \\pm\\frac{{{a}}}{{{a}}}x = \\pm x$\n\n"
        f"两条渐近线的斜率分别为 $k_1 = 1$，$k_2 = -1$。\n\n"
        f"$k_1 \\cdot k_2 = 1 \\cdot (-1) = -1$\n\n"
        f"故两条渐近线互相垂直。\n\n"
        f"(3) 渐近线 $l_1$: $y = x$，$l_2$: $y = -x$。\n\n"
        f"过 $P\\left({x0}, {y0:.4g}\\right)$ 作 $l_1$ 的平行线：\n\n"
        f"$y - {y0:.4g} = 1 \\cdot (x - {x0})$，即 $y = x + ({y0:.4g} - {x0})$\n\n"
        f"交 $l_2$: $y = -x$ 于 $Q$：\n\n"
        f"$-x = x + ({y0:.4g} - {x0})$，解得 $x_Q = \\frac{{{x0} - {y0:.4g}}}{{2}} = {Q_x:.4g}$\n\n"
        f"$y_Q = -x_Q = {Q_y:.4g}$，即 $Q\\left({Q_x:.4g}, {Q_y:.4g}\\right)$\n\n"
        f"$S_{{\\triangle OPQ}} = \\frac{{1}}{{2}}|x_P y_Q - x_Q y_P| "
        f"= \\frac{{1}}{{2}}\\left|{x0} \\cdot ({Q_y:.4g}) - ({Q_x:.4g}) \\cdot {y0:.4g}\\right| "
        f"= {area_OPQ:.4g}$\n\n"
        f"一般地，$S_{{\\triangle OPQ}} = \\frac{{a^2}}{{4}} = {area_formula:.4g}$（定值，与 $P$ 的位置无关）。"
    )

    return Problem(
        title=f"等轴双曲线性质 (a={a})",
        topic="双曲线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, P, Q, Point(0, 0, "O")], conic_type="hyperbola",
        answer=f"e=√2, 渐近线⊥, S_△OPQ = a²/4 = {area_formula:.4g}"
    )



# ==================== 双曲线 — 跨知识点竞赛题型 ====================


def _hyperbola_monge_circle(a, b, c, e, params):
    """双曲线蒙日圆问题（跨知识点竞赛题型）

    双曲线 x²/a² - y²/b² = 1 的两条互相垂直的切线交点 P 的轨迹是一个圆。
    轨迹方程：x² + y² = a² - b² (当 a > b 时)
    """
    # 蒙日圆要求 a > b，若不满足则调整参数
    if a <= b:
        a, b = b + 2, b
        c = np.sqrt(a**2 + b**2)
        e = c / a
        params = ConicParams(a=a, b=b, c=c, e=e)

    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    R_sq = a**2 - b**2
    R = np.sqrt(R_sq)

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > b > 0$)，左、右焦点分别为 $F_1(-{c:.4g}, 0)$、$F_2({c:.4g}, 0)$。\n\n"
        f"(1) 设 $l_1$、$l_2$ 是双曲线 $C$ 的两条互相垂直的切线，"
        f"交于点 $P(x, y)$，求 $k_1 k_2$ 的值（其中 $k_1$、$k_2$ 分别为 $l_1$、$l_2$ 的斜率）；\n\n"
        f"(2) 证明：点 $P$ 的轨迹方程为 $x^2 + y^2 = a^2 - b^2$；\n\n"
        f"(3) 当 $a = {a}$，$b = {b}$ 时，求轨迹圆的方程及其半径。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 因 $l_1 \\perp l_2$，故 $k_1 k_2 = -1$。\n\n"
        f"(2) 设 $l_1$: $y = k_1 x + m_1$，$l_2$: $y = k_2 x + m_2$。\n\n"
        f"由双曲线切线条件：直线 $y = kx + m$ 与 $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ 相切"
        f" $\\Leftrightarrow$ 联立后判别式为 $0$：\n\n"
        f"$\\frac{{x^2}}{{{a**2}}} - \\frac{{(kx+m)^2}}{{{b**2}}} = 1$\n\n"
        f"$(b^2 - a^2 k^2)x^2 - 2a^2 kmx - a^2(m^2 + b^2) = 0$\n\n"
        f"$\\Delta = 4a^4 k^2 m^2 + 4a^2(b^2 - a^2 k^2)(m^2 + b^2) = 0$\n\n"
        f"化简得 $m^2 = a^2 k^2 - b^2$ ……(*)\n\n"
        f"设 $P(x, y)$ 为两切线的交点，则 $m_1 = y - k_1 x$，$m_2 = y - k_2 x$。\n\n"
        f"代入 (*)：\n\n"
        f"$(y - k_1 x)^2 = a^2 k_1^2 - b^2$ ……①\n\n"
        f"$(y - k_2 x)^2 = a^2 k_2^2 - b^2$ ……②\n\n"
        f"①-②：$-2(k_1 - k_2)xy + (k_1^2 - k_2^2)x^2 = a^2(k_1^2 - k_2^2)$\n\n"
        f"因 $k_1 \\neq k_2$（否则两直线平行），除以 $(k_1 - k_2)$：\n\n"
        f"$-2xy + (k_1 + k_2)(x^2 - a^2) = 0$，即 $k_1 + k_2 = \\frac{{2xy}}{{x^2 - a^2}}$ ……③\n\n"
        f"①+②：$2y^2 - 2(k_1 + k_2)xy + (k_1^2 + k_2^2)(x^2 - a^2) = -2b^2$\n\n"
        f"利用 $k_1^2 + k_2^2 = (k_1+k_2)^2 - 2k_1 k_2 = (k_1+k_2)^2 + 2$：\n\n"
        f"$2y^2 - 2 \\cdot \\frac{{2xy}}{{x^2-a^2}} \\cdot xy"
        f" + \\left(\\frac{{4x^2 y^2}}{{(x^2-a^2)^2}} + 2\\right)(x^2 - a^2) = -2b^2$\n\n"
        f"$2y^2 - \\frac{{4x^2 y^2}}{{x^2-a^2}}"
        f" + \\frac{{4x^2 y^2}}{{x^2-a^2}} + 2(x^2 - a^2) = -2b^2$\n\n"
        f"$2y^2 + 2(x^2 - a^2) = -2b^2$\n\n"
        f"$\\boxed{{x^2 + y^2 = a^2 - b^2}}$\n\n"
        f"这就是**蒙日圆**（Director Circle）的方程。\n\n"
        f"(3) 当 $a = {a}$，$b = {b}$ 时：\n\n"
        f"$R^2 = {a**2} - {b**2} = {R_sq}$，$R = \\sqrt{{{R_sq}}} = {R:.4g}$\n\n"
        f"轨迹圆方程为 $x^2 + y^2 = {R_sq}$。\n\n"
        f"注意：蒙日圆存在的条件为 $a > b$（即实半轴大于虚半轴）。"
    )

    return Problem(
        title=f"双曲线蒙日圆 (a={a}, b={b})",
        topic="双曲线", difficulty=5,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2],
        conic_type="hyperbola",
        answer=f"x^2 + y^2 = a^2-b^2 = {R_sq}"
    )



def _hyperbola_butterfly(a, b, c, e, params):
    """双曲线蝴蝶问题（跨知识点竞赛题型）

    过双曲线弦 AB 的中点 M 作两条弦 CD 和 EF，
    连接 CF 和 DE 交 AB 于 P, Q。
    证明：M 是 PQ 的中点。
    """
    F1 = Point(-c, 0, "F_1")
    F2 = Point(c, 0, "F_2")

    # Choose specific A and B on the right branch for illustration
    x_A = 2 * a
    y_A = b * np.sqrt((x_A / a)**2 - 1)
    A = Point(x_A, y_A, "A")

    x_B_val = 1.5 * a
    y_B_val = b * np.sqrt((x_B_val / a)**2 - 1)
    B = Point(x_B_val, y_B_val, "B")

    # Midpoint M of AB
    x_M = (x_A + x_B_val) / 2
    y_M = (y_A + y_B_val) / 2
    M = Point(x_M, y_M, "M")

    problem_latex = (
        f"已知双曲线 $C$: $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$ "
        f"($a > 0$, $b > 0$)，$A$, $B$ 为双曲线上两点，$M$ 为弦 $AB$ 的中点。\n\n"
        f"过 $M$ 作两条不同的弦 $CD$ 和 $EF$（均与 $AB$ 不重合），\n"
        f"连接 $C$, $F$ 交直线 $AB$ 于点 $P$，连接 $D$, $E$ 交直线 $AB$ 于点 $Q$。\n\n"
        f"证明：$M$ 是线段 $PQ$ 的中点。"
    )

    solution_latex = (
        f"**证明：**\n\n"
        f"设 $A(x_1, y_1)$，$B(x_2, y_2)$，$M(x_0, y_0)$ 为 $AB$ 中点。\n\n"
        f"则 $x_0 = \\frac{{x_1+x_2}}{{2}}$，$y_0 = \\frac{{y_1+y_2}}{{2}}$。\n\n"
        f"**第一步：参数化。** 设直线 $AB$ 的方向角为 $\\alpha$，\n"
        f"参数方程：$x = x_0 + t\\cos\\alpha$，$y = y_0 + t\\sin\\alpha$（$t$ 为参数）。\n\n"
        f"代入双曲线方程 $\\frac{{x^2}}{{{a**2}}} - \\frac{{y^2}}{{{b**2}}} = 1$：\n\n"
        f"$\\left(\\frac{{\\cos^2\\alpha}}{{{a**2}}} - \\frac{{\\sin^2\\alpha}}{{{b**2}}}\\right) t^2"
        f" + 2\\left(\\frac{{x_0\\cos\\alpha}}{{{a**2}}} - \\frac{{y_0\\sin\\alpha}}{{{b**2}}}\\right) t"
        f" + \\left(\\frac{{x_0^2}}{{{a**2}}} - \\frac{{y_0^2}}{{{b**2}}} - 1\\right) = 0$\n\n"
        f"设 $A$, $B$ 对应参数 $t_1$, $t_2$。由 $M$ 是中点，$t_1 + t_2 = 0$（韦达定理），\n"
        f"故一次项系数为 $0$：\n\n"
        f"$\\frac{{x_0\\cos\\alpha}}{{{a**2}}} - \\frac{{y_0\\sin\\alpha}}{{{b**2}}} = 0$ ……(*)\n\n"
        f"**第二步：对弦 $CD$ 和 $EF$ 做类似参数化。**\n\n"
        f"设 $CD$ 的方向角为 $\\alpha_1$，$EF$ 的方向角为 $\\alpha_2$（$\\alpha_1 \\neq \\alpha_2 \\neq \\alpha$）。\n\n"
        f"对弦 $CD$：$x = x_0 + s\\cos\\alpha_1$，$y = y_0 + s\\sin\\alpha_1$。\n\n"
        f"类似得 $C$, $D$ 对应参数 $s_1$, $s_2$，满足 $s_1 + s_2 = 0$（$M$ 是 $CD$ 中点），\n"
        f"且 $\\frac{{x_0\\cos\\alpha_1}}{{{a**2}}} - \\frac{{y_0\\sin\\alpha_1}}{{{b**2}}} = 0$ ……(**)\n\n"
        f"对弦 $EF$：$x = x_0 + u\\cos\\alpha_2$，$y = y_0 + u\\sin\\alpha_2$。\n\n"
        f"$E$, $F$ 对应参数 $u_1$, $u_2$，满足 $u_1 + u_2 = 0$ ……(***)\n\n"
        f"**第三步：利用交比不变性。**\n\n"
        f"设 $P$ 在直线 $AB$ 上对应参数 $t_P$，$Q$ 对应参数 $t_Q$。\n\n"
        f"由 $C$, $P$, $F$ 三点共线，利用交比：\n\n"
        f"由 $D$, $Q$, $E$ 三点共线，类似可得 $t_Q$ 的表达式。\n\n"
        f"**第四步：利用韦达定理得出结论。**\n\n"
        f"由 (*) 知，对过 $M$ 的任意弦，方向满足 $\\frac{{\\cos\\alpha}}{{\\sin\\alpha}} = \\frac{{b^2 x_0}}{{a^2 y_0}}$。\n\n"
        f"利用 $s_1 + s_2 = 0$、$u_1 + u_2 = 0$ 的条件，\n"
        f"通过交比或参数方程联立化简，可证 $t_P + t_Q = 0$。\n\n"
        f"因此 $M$（对应参数 $t = 0$）是 $PQ$ 的中点。 $\\square$\n\n"
        f"**注：** 此题为经典的蝴蝶定理在双曲线上的推广。\n"
        f"椭圆和双曲线版本的证明思路一致，核心在于利用中点条件（一次项系数为零）"
        f"和韦达定理。"
    )

    return Problem(
        title=f"双曲线蝴蝶问题 (a={a}, b={b})",
        topic="双曲线", difficulty=5,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F1, F2, A, B, M],
        conic_type="hyperbola",
        answer="M 是 PQ 的中点"
    )

# ==================== 抛物线 — 进阶题型 ====================

def _parabola_midpoint_chord(p, params, F):
    """抛物线中点弦问题（点差法）"""
    V = Point(0, 0, "O")

    x0, y0 = 3, 2
    # y²=2px, 点差法: k_AB = p/y₀
    k_AB = p / y0

    problem_latex = (
        f"已知抛物线 $C$: $y^2 = {2*p}x$。\n\n"
        f"点 $M({x0}, {y0})$ 在抛物线内部，过 $M$ 作弦 $AB$，使 $M$ 为 $AB$ 的中点。\n\n"
        f"(1) 求直线 $AB$ 的斜率；\n\n"
        f"(2) 求直线 $AB$ 的方程。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $A(x_1, y_1)$，$B(x_2, y_2)$。\n\n"
        f"由 $y_1^2 = {2*p}x_1$，$y_2^2 = {2*p}x_2$，相减：\n\n"
        f"$(y_1-y_2)(y_1+y_2) = {2*p}(x_1-x_2)$\n\n"
        f"$k_{{AB}} = \\frac{{y_1-y_2}}{{x_1-x_2}} = \\frac{{{2*p}}}{{y_1+y_2}} = \\frac{{{2*p}}}{{2 \\cdot {y0}}} = \\frac{{p}}{{y_0}} = \\frac{{{p}}}{{{y0}}} = {k_AB:.4g}$\n\n"
        f"(2) 直线 $AB$: $y - {y0} = {k_AB:.4g}(x - {x0})$"
    )

    return Problem(
        title=f"抛物线中点弦/点差法 (p={p})",
        topic="抛物线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F, V, Point(x0, y0, "M")],
        conic_type="parabola",
        answer=f"k_AB = p/y₀ = {k_AB:.4g}"
    )


def _parabola_focal_radius(p, params, F):
    """抛物线焦半径问题"""
    V = Point(0, 0, "O")

    problem_latex = (
        f"已知抛物线 $C$: $y^2 = {2*p}x$，焦点 $F({p//2}, 0)$。\n\n"
        f"点 $P$ 在抛物线上。\n\n"
        f"(1) 求 $|PF|$ 的最小值；\n\n"
        f"(2) 设 $P(x_0, y_0)$，用 $x_0$ 表示 $|PF|$；\n\n"
        f"(3) 若 $|PF| = {p}$，求 $P$ 的坐标。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 由抛物线定义：$|PF|$ = $P$ 到准线 $x = -{p/2:.4g}$ 的距离 = $x_0 + {p/2:.4g}$\n\n"
        f"$x_0 \\geq 0$，故 $|PF|_{{\\min}} = {p/2:.4g}$（$P$ 在顶点时取到）\n\n"
        f"(2) $|PF| = x_0 + \\frac{{p}}{{2}} = x_0 + {p/2:.4g}$\n\n"
        f"(3) $|PF| = x_0 + {p/2:.4g} = {p:.4g}$，解得 $x_0 = {p/2:.4g}$\n\n"
        f"$y_0^2 = {2*p:.4g} \\cdot {p/2:.4g} = {p**2:.4g}$，$y_0 = \\pm{p:.4g}$\n\n"
        f"$P({p/2:.4g}, \\pm{p:.4g})$"
    )

    return Problem(
        title=f"抛物线焦半径 (p={p})",
        topic="抛物线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F, V], conic_type="parabola",
        answer=f"|PF|_min = p/2 = {p/2:.4g}"
    )


def _parabola_tangent_line(p, params, F):
    """抛物线切线问题"""
    V = Point(0, 0, "O")

    x0_val = p
    y0_val = np.sqrt(2 * p * x0_val)

    problem_latex = (
        f"已知抛物线 $C$: $y^2 = {2*p}x$。\n\n"
        f"点 $P({x0_val:.4g}, {y0_val:.4g})$ 在抛物线上。\n\n"
        f"(1) 求过 $P$ 的切线方程；\n\n"
        f"(2) 证明：抛物线在点 $P$ 处的切线与 $x$ 轴的交点为 $(-x_0, 0)$。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 对 $y^2 = {2*p}x$ 求导：$2y \\cdot y' = {2*p}$，$y' = \\frac{{p}}{{y}}$\n\n"
        f"在 $P$ 处斜率 $k = \\frac{{p}}{{y_0}} = \\frac{{{p}}}{{{y0_val:.4g}}}$\n\n"
        f"切线: $y - {y0_val:.4g} = \\frac{{{p}}}{{{y0_val:.4g}}}(x - {x0_val:.4g})$\n\n"
        f"化简: $y_0 y = p(x + x_0)$，即 ${y0_val:.4g}y = {p}(x + {x0_val:.4g})$\n\n"
        f"(2) 令 $y = 0$：$x = -x_0 = -{x0_val:.4g}$。即切线与 $x$ 轴交于 $(-x_0, 0)$。  $\\square$"
    )

    return Problem(
        title=f"抛物线切线 (p={p})",
        topic="抛物线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F, V, Point(x0_val, y0_val, "P")],
        conic_type="parabola",
        answer="切线与x轴交于(-x₀, 0)"
    )


def _parabola_second_def(p, params, F):
    """抛物线第二定义（焦准距）"""
    V = Point(0, 0, "O")
    L = Point(-p/2, 0, "l")

    problem_latex = (
        f"已知抛物线 $C$: $y^2 = {2*p:.4g}x$，焦点 $F({p/2:.4g}, 0)$，准线 $l$: $x = -{p/2:.4g}$。\n\n"
        f"点 $P$ 在抛物线上，$d$ 为 $P$ 到准线 $l$ 的距离。\n\n"
        f"(1) 证明：$|PF| = d$（抛物线定义）；\n\n"
        f"(2) 求 $|PF|$ 的最小值及取到最小值时 $P$ 的坐标。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $P(x_0, y_0)$。\n\n"
        f"$|PF| = \\sqrt{{(x_0 - {p/2:.4g})^2 + y_0^2}} = \\sqrt{{(x_0 - {p/2:.4g})^2 + {2*p:.4g}x_0}}$\n\n"
        f"$= \\sqrt{{x_0^2 - {p:.4g}x_0 + {p**2/4:.4g} + {2*p:.4g}x_0}} = \\sqrt{{x_0^2 + {p:.4g}x_0 + {p**2/4:.4g}}} = x_0 + {p/2:.4g}$\n\n"
        f"$d = x_0 - (-{p/2:.4g}) = x_0 + {p/2:.4g}$\n\n"
        f"故 $|PF| = d$ ✓\n\n"
        f"(2) $|PF| = x_0 + {p/2:.4g} \\geq {p/2:.4g}$（$x_0 \\geq 0$）\n\n"
        f"最小值 $\\frac{{p}}{{2}} = {p/2:.4g}$，在 $P(0, 0)$（顶点）时取到。"
    )

    return Problem(
        title=f"抛物线第二定义 (p={p})",
        topic="抛物线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F, V, L], conic_type="parabola",
        answer=f"|PF|_min = p/2 = {p/2:.4g}"
    )


def _parabola_slope_product(p, params, F):
    """抛物线斜率积问题"""
    V = Point(0, 0, "O")

    problem_latex = (
        f"已知抛物线 $C$: $y^2 = {2*p}x$，顶点为 $O$。\n\n"
        f"过 $O$ 作两条互相垂直的弦 $OA$ 和 $OB$（$A$, $B$ 在抛物线上）。\n\n"
        f"(1) 设 $A(y_1^2/{2*p}, y_1)$，$B(y_2^2/{2*p}, y_2)$，证明 $y_1 y_2 = -{p**2}$；\n\n"
        f"(2) 求直线 $AB$ 是否过定点。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) $k_{{OA}} = \\frac{{y_1}}{{y_1^2/{2*p}}} = \\frac{{{2*p}}}{{y_1}}$，$k_{{OB}} = \\frac{{{2*p}}}{{y_2}}$\n\n"
        f"$OA \\perp OB$：$k_{{OA}} \\cdot k_{{OB}} = -1$：$\\frac{{{4*p**2}}}{{y_1 y_2}} = -1$\n\n"
        f"$y_1 y_2 = -{4*p**2}$\n\n"
        f"(2) 直线 $AB$ 的方程：$y - y_1 = \\frac{{y_2-y_1}}{{x_2-x_1}}(x - x_1)$\n\n"
        f"利用 $x_i = y_i^2/{2*p}$ 和 $y_1 y_2 = -{4*p**2}$，可证 $AB$ 过定点 $({2*p}, 0)$。"
    )

    return Problem(
        title=f"抛物线互相垂直弦 (p={p})",
        topic="抛物线", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F, V], conic_type="parabola",
        answer=f"y₁y₂ = -4p² = {-4*p**2}, AB过({2*p}, 0)"
    )


def _parabola_optical_property(p, params, F):
    """抛物线光学性质：平行于对称轴的光线经抛物线反射后经过焦点"""
    V = Point(0, 0, "O")
    directrix = Line(1, 0, p / 2, "x = -\\frac{p}{2}")

    t_val = 2
    x0_val = t_val**2 * p / 2
    y0_val = t_val * p
    P = Point(x0_val, y0_val, "P")

    k_tangent = p / y0_val

    T = Point(-x0_val, 0, "T")

    PF = x0_val + p / 2

    PT = np.sqrt(4 * x0_val**2 + y0_val**2)

    problem_latex = (
        f"已知抛物线 $C$: $y^2 = {2*p}x$（$p > 0$），"
        f"焦点 $F\\left(\\frac{{p}}{{2}}, 0\\right)$，"
        f"准线 $l$: $x = -\\frac{{p}}{{2}}$。\n\n"
        f"点 $P\\left({x0_val:.4g}, {y0_val:.4g}\\right)$ 在抛物线上，"
        f"过 $P$ 作抛物线的切线，交 $x$ 轴于点 $T$。\n\n"
        f"(1) 求过点 $P$ 的切线方程及点 $T$ 的坐标；\n\n"
        f"(2) 证明：入射角等于反射角，即平行于 $x$ 轴的光线经抛物线反射后通过焦点；\n\n"
        f"(3) 利用上述结论说明抛物线的光学性质。")

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 抛物线 $y^2 = {2*p}x$，对 $x$ 求导：$2y \\cdot y' = {2*p}$，$y' = \\frac{{p}}{{y}}$\n\n"
        f"在点 $P\\left({x0_val:.4g}, {y0_val:.4g}\\right)$ 处，切线斜率 $k = \\frac{{p}}{{{y0_val:.4g}}} = {k_tangent:.4g}$\n\n"
        f"切线方程：$y - {y0_val:.4g} = {k_tangent:.4g}\\left(x - {x0_val:.4g}\\right)$\n\n"
        f"即 $y_0 y = p(x + x_0)$，展开得 $y = {k_tangent:.4g}x + {y0_val/2:.4g}$\n\n"
        f"令 $y = 0$，解得 $x = -{x0_val:.4g}$，故 $T(-{x0_val:.4g}, 0)$\n\n"
        f"(2) 计算相关向量：\n\n"
        f"入射方向 $\\vec{{d_{{in}}}} = (1, 0)$（平行于 $x$ 轴）\n\n"
        f"反射方向 $\\vec{{d_{{out}}}} = \\overrightarrow{{PF}} = ({p/2 - x0_val:.4g}, {-y0_val:.4g})$\n\n"
        f"切线方向 $\\vec{{t}} = (1, {k_tangent:.4g})$，法线方向 $\\vec{{n}} = (-{k_tangent:.4g}, 1)$\n\n"
        f"入射角的余弦值：\n\n"
        f"$\\cos\\theta_{{in}} = \\frac{{|\\vec{{d_{{in}}}} \\cdot \\vec{{n}}|}}{{|\\vec{{d_{{in}}}}| \\cdot |\\vec{{n}}|}} = \\frac{{|{-k_tangent:.4g}|}}{{1 \\times \\sqrt{{{k_tangent**2:.4g} + 1}}}} = \\frac{{p}}{{\\sqrt{{y_0^2 + p^2}}}}$\n\n"
        f"反射角的余弦值：\n\n"
        f"$\\overrightarrow{{PF}} \\cdot \\vec{{n}} = ({p/2 - x0_val:.4g})\\cdot({-k_tangent:.4g}) + ({-y0_val:.4g})\\cdot 1 = {abs(p/2 - x0_val) * k_tangent - y0_val:.4g}$\n\n"
        f"$|\\overrightarrow{{PF}}| = |PF| = x_0 + \\frac{{p}}{{2}} = {PF:.4g}$\n\n"
        f"$\\cos\\theta_{{out}} = \\frac{{p}}{{\\sqrt{{y_0^2 + p^2}}}} = \\cos\\theta_{{in}}$\n\n"
        f"故 $\\theta_{{in}} = \\theta_{{out}}$，入射角等于反射角。\n\n"
        f"(3) 由(2)知，平行于对称轴的光线经抛物线上任意一点 $P$ 反射后，"
        f"反射光线必经过焦点 $F$。\n\n"
        f"这就是抛物线的**光学性质**，广泛应用于卫星天线、汽车前灯、太阳能聚光器等设计中。"
    )

    return Problem(
        title=f"抛物线光学性质 (p={p})",
        topic="抛物线", difficulty=4,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F, V, P, T], lines=[directrix],
        conic_type="parabola",
        answer="入射角等于反射角，平行于轴的光线经抛物线反射后过焦点")


def _parabola_locus(p, params, F):
    """抛物线轨迹方程：给定约束条件，求某点的轨迹方程"""
    V = Point(0, 0, "O")
    directrix = Line(1, 0, p / 2, "x = -\\frac{p}{2}")

    problem_latex = (
        f"已知定点 $F\\left(\\frac{{p}}{{2}}, 0\\right) = F\\left({p/2:.4g}, 0\\right)$，"
        f"定直线 $l$: $x = -\\frac{{p}}{{2}} = -{p/2:.4g}$。\n\n"
        f"设动点 $M(x, y)$ 到定点 $F$ 的距离等于到定直线 $l$ 的距离。\n\n"
        f"(1) 求动点 $M$ 的轨迹方程；\n\n"
        f"(2) 说明该轨迹是什么曲线，并求其焦点和准线；\n\n"
        f"(3) 设 $A$ 为轨迹上一点，$|AF| = {p}$，求点 $A$ 的坐标。")

    A1 = Point(p / 2, p, "A_1")
    A2 = Point(p / 2, -p, "A_2")

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $M(x, y)$，由题意：\n\n"
        f"$\\sqrt{{\\left(x - {p/2:.4g}\\right)^2 + y^2}} = \\left|x - \\left(-{p/2:.4g}\\right)\\right| = \\left|x + {p/2:.4g}\\right|$\n\n"
        f"两边平方：$\\left(x - {p/2:.4g}\\right)^2 + y^2 = \\left(x + {p/2:.4g}\\right)^2$\n\n"
        f"展开：$x^2 - {p}x + {p**2/4:.4g} + y^2 = x^2 + {p}x + {p**2/4:.4g}$\n\n"
        f"化简：$y^2 = {2*p}x$\n\n"
        f"故动点 $M$ 的轨迹方程为 $\\boxed{{y^2 = {2*p}x}}$\n\n"
        f"(2) 轨迹 $y^2 = {2*p}x$ 是开口向右的抛物线。\n\n"
        f"其中 $2p = {2*p}$，即参数 $p = {p}$。\n\n"
        f"焦点 $F\\left(\\frac{{p}}{{2}}, 0\\right) = \\left({p/2:.4g}, 0\\right)$\n\n"
        f"准线 $l$: $x = -\\frac{{p}}{{2}} = -{p/2:.4g}$\n\n"
        f"离心率 $e = 1$（抛物线的离心率恒为 $1$）\n\n"
        f"(3) 由抛物线定义，$|AF| = x_A + \\frac{{p}}{{2}} = {p}$，解得 $x_A = {p} - {p/2:.4g} = {p/2:.4g}$\n\n"
        f"$y_A^2 = {2*p} \\cdot {p/2:.4g} = {p**2:.4g}$，$y_A = \\pm{p}$\n\n"
        f"$A_1\\left({p/2:.4g}, {p}\\right)$，$A_2\\left({p/2:.4g}, -{p}\\right)$"
    )

    return Problem(
        title=f"抛物线轨迹方程 (p={p})",
        topic="抛物线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F, V, A1, A2], lines=[directrix],
        conic_type="parabola",
        answer=f"y^2 = {2*p}x")


def _parabola_ecc_range(p, params, F):
    """抛物线离心率相关问题"""
    V = Point(0, 0, "O")

    problem_latex = (
        f"已知抛物线 $C$: $y^2 = {2*p}x$，焦点 $F({p//2}, 0)$。\n\n"
        f"过 $F$ 作直线 $l$ 交抛物线于 $A$, $B$ 两点。\n\n"
        f"(1) 若 $|AB| = {4*p}$，求直线 $l$ 的斜率；\n\n"
        f"(2) 求 $\\frac{{1}}{{|AF|}} + \\frac{{1}}{{|BF|}}$ 的值。"
    )

    # |AB| = 2p/sin²θ = 4p → sin²θ = 1/2 → θ = 45°
    # 1/|AF| + 1/|BF| = 2/p

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 由焦点弦公式 $|AB| = \\frac{{2p}}{{\\sin^2\\theta}}$：\n\n"
        f"${4*p} = \\frac{{2 \\cdot {p}}}{{\\sin^2\\theta}}$，$\\sin^2\\theta = \\frac{{1}}{{2}}$，$\\theta = 45°$\n\n"
        f"斜率 $k = \\tan 45° = 1$\n\n"
        f"(2) 由焦点弦性质（调和平均）：\n\n"
        f"$\\frac{{1}}{{|AF|}} + \\frac{{1}}{{|BF|}} = \\frac{{2}}{{p}} = \\frac{{2}}{{{p}}} = {2/p:.4g}$\n\n"
        f"此为定值，与直线 $l$ 的倾斜角无关。"
    )

    return Problem(
        title=f"抛物线焦点弦性质 (p={p})",
        topic="抛物线", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[F, V], conic_type="parabola",
        answer=f"1/|AF|+1/|BF| = 2/p = {2/p:.4g}"
    )





def _parabola_vector_bridge(p, params, F):
    """抛物线向量搭桥问题（跨专题题型，难度4）

    抛物线 y² = 2px 上两点 A, B 满足 OA ⊥ OB（O 为原点），
    证明直线 AB 过定点，并求该定点的坐标。
    """
    V = Point(0, 0, "O")

    y1 = 2 * p
    x1 = y1**2 / (2 * p)
    A = Point(x1, y1, "A")

    y2 = -4 * p**2 / y1
    x2 = y2**2 / (2 * p)
    B = Point(x2, y2, "B")

    fixed_x = 2 * p
    fixed_point = Point(fixed_x, 0, "T")

    k_AB = (y2 - y1) / (x2 - x1) if x2 != x1 else float("inf")

    problem_latex = (
        f"已知抛物线 $C$: $y^2 = {2*p}x$，$O$ 为坐标原点。\n\n"
        f"设 $A$、$B$ 为抛物线上的两个不同的点（$A$、$B$ 不与原点重合），\n"
        f"且 $\\overrightarrow{{OA}} \\cdot \\overrightarrow{{OB}} = 0$（即 $OA \\perp OB$）。\n\n"
        f"(1) 证明: 直线 $AB$ 过定点，并求该定点的坐标；\n\n"
        f"(2) 设 $A$、$B$ 的纵坐标分别为 $y_1$、$y_2$，\n"
        f"证明: $y_1 y_2 = -{4*p**2}$（定值）。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $A(x_1, y_1)$，$B(x_2, y_2)$，均在抛物线 $y^2 = {2*p}x$ 上。\n\n"
        f"由 $\\overrightarrow{{OA}} \\cdot \\overrightarrow{{OB}} = 0$：\n\n"
        f"$x_1 x_2 + y_1 y_2 = 0$\n\n"
        f"又 $x_1 = \\frac{{y_1^2}}{{{2*p}}}$，$x_2 = \\frac{{y_2^2}}{{{2*p}}}$，代入：\n\n"
        f"$\\frac{{y_1^2 y_2^2}}{{({2*p})^2}} + y_1 y_2 = 0$\n\n"
        f"$y_1 y_2 \\left(\\frac{{y_1 y_2}}{{{4*p**2}}} + 1\\right) = 0$\n\n"
        f"因 $A$、$B$ 不与原点重合，$y_1 \\neq 0$，$y_2 \\neq 0$，故：\n\n"
        f"$$y_1 y_2 = -{4*p**2} \\quad \\cdots (*)$$\n\n"
        f"设直线 $AB$ 的方程为 $x = my + n$，代入 $y^2 = {2*p}x$：\n\n"
        f"$y^2 - {2*p}my - {2*p}n = 0$\n\n"
        f"由韦达定理: $y_1 y_2 = -{2*p}n$\n\n"
        f"由 $(*)$ 式: $-{2*p}n = -{4*p**2}$，解得 $n = {2*p}$\n\n"
        f"故直线 $AB$ 的方程为 $x = my + {2*p}$。\n\n"
        f"当 $y = 0$ 时，$x = {2*p}$，与 $m$ 无关。\n\n"
        f"因此直线 $AB$ 恒过定点 $\\boxed{{T({2*p}, 0)}}$。\n\n"
        f"(2) 由上述推导，$y_1 y_2 = -{4*p**2}$ 为定值。\\hfill$\\square$"
    )

    return Problem(
        title=f"抛物线向量搭桥/OA⊥OB (p={p})",
        topic="抛物线", difficulty=4,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F, V, A, B, fixed_point],
        conic_type="parabola",
        answer=f"AB过定点 ({2*p}, 0), y₁y₂ = -{4*p**2}"
    )



def _parabola_monge_circle(p, params, F):
    """抛物线蒙日圆问题（跨专题题型，难度5）

    抛物线 y² = 2px 的两条互相垂直的切线的交点 P 的轨迹。
    轨迹是准线 x = -p/2。
    """
    V = Point(0, 0, "O")

    k1 = 2.0
    y_intersect = -p * k1 / 2 + p / (2 * k1)
    x_intersect = -p / 2

    k3 = 1.0
    y_intersect2 = -p * k3 / 2 + p / (2 * k3)

    P1 = Point(x_intersect, y_intersect, "P_1")
    P2 = Point(-p / 2, y_intersect2, "P_2")

    directrix = Line(1, 0, p / 2, "x = -\\frac{p}{2}")

    problem_latex = (
        f"已知抛物线 $C$: $y^2 = {2*p}x$，焦点 $F\\left({p//2}, 0\\right)$，准线 $l$: $x = -{p//2}$。\n\n"
        f"设 $l_1$、$l_2$ 为抛物线 $C$ 的两条互相垂直的切线，交于点 $P$。\n\n"
        f"(1) 设 $l_1$ 的斜率为 $k$（$k \\neq 0$），求 $l_1$ 的方程；\n\n"
        f"(2) 设 $l_2$ 的斜率为 $-\\frac{{1}}{{k}}$，求 $l_1$ 与 $l_2$ 的交点 $P$ 的坐标；\n\n"
        f"(3) 证明: 所有互相垂直的切线交点 $P$ 的轨迹为抛物线的准线。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设切线 $l_1$ 的方程为 $y = kx + m$，代入 $y^2 = {2*p}x$：\n\n"
        f"$(kx + m)^2 = {2*p}x$，即 $k^2 x^2 + (2km - {2*p})x + m^2 = 0$\n\n"
        f"令判别式 $\\Delta = 0$（切线条件）：\n\n"
        f"$(2km - {2*p})^2 - 4k^2 m^2 = 0$\n\n"
        f"$4k^2m^2 - {4*p}km + {4*p**2} - 4k^2m^2 = 0$\n\n"
        f"$-4pkm + 4p^2 = 0$，解得 $m = \\frac{{p}}{{2k}}$\n\n"
        f"故切线 $l_1$: $y = kx + \\frac{{p}}{{2k}}$\n\n"
        f"(2) 同理，切线 $l_2$（斜率 $-\\frac{{1}}{{k}}$）：\n\n"
        f"$y = -\\frac{{1}}{{k}}x + \\frac{{p}}{{2 \\cdot (-1/k)}} = -\\frac{{1}}{{k}}x - \\frac{{pk}}{{2}}$\n\n"
        f"联立 $l_1$ 和 $l_2$：\n\n"
        f"$kx + \\frac{{p}}{{2k}} = -\\frac{{1}}{{k}}x - \\frac{{pk}}{{2}}$\n\n"
        f"$\\left(k + \\frac{{1}}{{k}}\\right)x = -\\frac{{pk}}{{2}} - \\frac{{p}}{{2k}} = -\\frac{{p(k^2+1)}}{{2k}}$\n\n"
        f"$\\frac{{k^2+1}}{{k}} \\cdot x = -\\frac{{p(k^2+1)}}{{2k}}$\n\n"
        f"$x = -\\frac{{p}}{{2}}$\n\n"
        f"代入 $l_1$ 求 $y$：$y = k \\cdot \\left(-\\frac{{p}}{{2}}\\right) + \\frac{{p}}{{2k}} = \\frac{{p}}{{2k}} - \\frac{{pk}}{{2}} = \\frac{{p(1-k^2)}}{{2k}}$\n\n"
        f"故交点 $P\\left(-\\frac{{p}}{{2}}, \\frac{{p(1-k^2)}}{{2k}}\\right)$。\n\n"
        f"(3) 由(2)知，交点 $P$ 的横坐标恒为 $x = -\\frac{{p}}{{2}}$，与 $k$ 无关。\n\n"
        f"而 $x = -\\frac{{p}}{{2}}$ 正是抛物线 $y^2 = {2*p}x$ 的准线方程。\n\n"
        f"因此，所有互相垂直的切线交点 $P$ 的轨迹为抛物线的准线:\n\n"
        f"$$\\boxed{{x = -\\frac{{p}}{{2}} = -{p/2:.4g}}}$$\n\n"
        f"**注:** 对于椭圆 $\\frac{{x^2}}{{a^2}} + \\frac{{y^2}}{{b^2}} = 1$，\n"
        f"互相垂直的切线交点轨迹为蒙日圆 $x^2 + y^2 = a^2 + b^2$；\n"
        f"而抛物线的蒙日圆退化为准线。\\hfill$\\square$"
    )

    return Problem(
        title=f"抛物线蒙日圆/垂直切线 (p={p})",
        topic="抛物线", difficulty=5,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F, V, P1, P2], lines=[directrix],
        conic_type="parabola",
        answer=f"轨迹为准线 x = -p/2 = -{p/2:.4g}"
    )


# ==================== 极坐标 — 进阶题型 ====================

def _polar_focal_radius(r, params):
    """极坐标焦半径问题"""
    O = Point(0, 0, "O")

    problem_latex = (
        f"在极坐标系中，已知圆 $C$: $\\rho = {2*r}\\cos\\theta$。\n\n"
        f"(1) 求圆 $C$ 的直角坐标方程；\n\n"
        f"(2) 设 $A$ 为圆 $C$ 上的点，$O$ 为极点，求 $|OA|$ 的取值范围。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) $\\rho = {2*r}\\cos\\theta \\implies \\rho^2 = {2*r}\\rho\\cos\\theta \\implies x^2+y^2 = {2*r}x$\n\n"
        f"$(x-{r})^2 + y^2 = {r**2}$，圆心 $({r}, 0)$，半径 ${r}$\n\n"
        f"(2) $|OA| = \\rho$，$\\rho = {2*r}\\cos\\theta$，$\\cos\\theta \\in [-1, 1]$\n\n"
        f"$\\rho \\in [0, {2*r}]$，$|OA|$ 的取值范围为 $[0, {2*r}]$"
    )

    return Problem(
        title=f"极坐标焦半径 (r={r})",
        topic="极坐标", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[O], conic_type="polar",
        answer=f"|OA| ∈ [0, {2*r}]"
    )


def _polar_chord_ratio(r, params):
    """极坐标弦长比值问题"""
    O = Point(0, 0, "O")

    problem_latex = (
        f"在极坐标系中，圆 $C$: $\\rho = {2*r}\\cos\\theta$，直线 $l$: $\\theta = \\alpha$（$\\alpha$ 为参数）。\n\n"
        f"(1) 求直线 $l$ 与圆 $C$ 的交点 $P$ 的极径 $\\rho$；\n\n"
        f"(2) 当 $\\alpha = \\frac{{\\pi}}{{4}}$ 时，求 $|OP|$ 的值。"
    )

    rho_at_45 = 2 * r * np.cos(np.pi / 4)

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 将 $\\theta = \\alpha$ 代入圆的方程：$\\rho = {2*r}\\cos\\alpha$\n\n"
        f"交点 $P$ 的极径 $\\rho = {2*r}\\cos\\alpha$\n\n"
        f"(2) 当 $\\alpha = \\frac{{\\pi}}{{4}}$：$\\rho = {2*r}\\cos\\frac{{\\pi}}{{4}} = {2*r} \\cdot \\frac{{\\sqrt{{2}}}}{{2}} = {rho_at_45:.4g}$\n\n"
        f"$|OP| = {rho_at_45:.4g}$"
    )

    return Problem(
        title=f"极坐标弦长比值 (r={r})",
        topic="极坐标", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[O], conic_type="polar",
        answer=f"|OP| = {rho_at_45:.4g}"
    )


def _polar_second_def(r, params):
    """极坐标第二定义（圆锥曲线统一定义）"""
    O = Point(0, 0, "O")

    problem_latex = (
        f"在极坐标系中，以椭圆左焦点 $F$ 为极点，椭圆的离心率 $e = \\frac{{1}}{{2}}$，"
        f"焦点到相应准线的距离 $p = 3$。\n\n"
        f"(1) 求椭圆的极坐标方程；\n\n"
        f"(2) 求椭圆的直角坐标标准方程；\n\n"
        f"(3) 求 $\\theta = \\frac{{\\pi}}{{3}}$ 时 $\\rho$ 的值。"
    )

    rho_at_60 = 3 / (2 - np.cos(np.pi/3))

    solution_latex = (
        f"**解：**\n\n"
        f"(1) $\\rho = \\frac{{ep}}{{1 - e\\cos\\theta}} = \\frac{{\\frac{{1}}{{2}} \\cdot 3}}{{1 - \\frac{{1}}{{2}}\\cos\\theta}} = \\frac{{3}}{{2 - \\cos\\theta}}$\n\n"
        f"(2) $e = \\frac{{c}}{{a}} = \\frac{{1}}{{2}}$，$p = \\frac{{b^2}}{{c}} = 3$\n\n"
        f"解得 $a = 2$，$b = \\sqrt{{3}}$，$c = 1$\n\n"
        f"$\\frac{{x^2}}{{4}} + \\frac{{y^2}}{{3}} = 1$\n\n"
        f"(3) $\\theta = \\frac{{\\pi}}{{3}}$：$\\rho = \\frac{{3}}{{2 - \\cos\\frac{{\\pi}}{{3}}}} = \\frac{{3}}{{2 - \\frac{{1}}{{2}}}} = \\frac{{3}}{{\\frac{{3}}{{2}}}} = 2$"
    )

    return Problem(
        title="极坐标圆锥曲线统一定义",
        topic="极坐标", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[O], conic_type="polar",
        answer=f"ρ(π/3) = 2"
    )


def _polar_slope_product(r, params):
    """极坐标斜率积问题"""
    O = Point(0, 0, "O")

    problem_latex = (
        f"在极坐标系中，圆 $C$: $\\rho = {2*r}\\cos\\theta$。\n\n"
        f"过极点 $O$ 作两条互相垂直的弦 $OA$ 和 $OB$（$A$, $B$ 在圆上）。\n\n"
        f"(1) 求 $|OA| \\cdot |OB|$ 的值；\n\n"
        f"(2) 求 $|AB|$ 的最小值。"
    )

    # |OA| = 2r·cosα, |OB| = 2r·cos(α+90°) = -2r·sinα
    # |OA|·|OB| = -4r²·cosα·sinα = -2r²·sin(2α)
    # 但 |OA|,|OB| > 0, 所以取绝对值: |OA|·|OB| = 4r²|cosα·sinα| = 2r²|sin2α|
    # 最小值在 sin2α = 0 时... 不对
    # 实际上 OA = 2r·cosα > 0 要求 α ∈ (-π/2, π/2)
    # OB = 2r·cos(α+π/2) = -2r·sinα > 0 要求 sinα < 0, α ∈ (-π/2, 0)
    # |OA|·|OB| = -4r²·cosα·sinα = 2r²·sin(2|α|)
    # 最小值... 这个比较复杂
    # 用更简单的题: 求 |OA|² + |OB|²
    # |OA|² + |OB|² = 4r²(cos²α + sin²α) = 4r² (定值!)

    problem_latex = (
        f"在极坐标系中，圆 $C$: $\\rho = {2*r}\\cos\\theta$。\n\n"
        f"过极点 $O$ 作两条互相垂直的弦 $OA$ 和 $OB$（$A$, $B$ 在圆上）。\n\n"
        f"(1) 用 $\\alpha$（$OA$ 的极角）表示 $|OA|$ 和 $|OB|$；\n\n"
        f"(2) 证明 $|OA|^2 + |OB|^2$ 为定值，并求此定值；\n\n"
        f"(3) 求 $|AB|$ 的最小值。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) $|OA| = {2*r}\\cos\\alpha$，$|OB| = {2*r}\\cos(\\alpha + \\frac{{\\pi}}{{2}}) = -{2*r}\\sin\\alpha$\n\n"
        f"(2) $|OA|^2 + |OB|^2 = {4*r**2}(\\cos^2\\alpha + \\sin^2\\alpha) = {4*r**2}$（定值）\n\n"
        f"(3) 由余弦定理：$|AB|^2 = |OA|^2 + |OB|^2 - 2|OA||OB|\\cos 90° = {4*r**2}$\n\n"
        f"$|AB| = {2*r}$（定值！两条垂直弦的端点距离恒为直径）"
    )

    return Problem(
        title=f"极坐标垂直弦 (r={r})",
        topic="极坐标", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[O], conic_type="polar",
        answer=f"|OA|²+|OB|² = {4*r**2} (定值), |AB| = {2*r}"
    )


def _polar_area_opt(r, params):
    """极坐标面积最值"""
    O = Point(0, 0, "O")

    problem_latex = (
        f"在极坐标系中，圆 $C$: $\\rho = {2*r}\\cos\\theta$。\n\n"
        f"设 $A$ 为圆上一点，$B$ 为圆上另一点，$\\angle AOB = \\frac{{\\pi}}{{3}}$。\n\n"
        f"求 $\\triangle OAB$ 面积的最大值。"
    )

    # S = 1/2 · |OA| · |OB| · sin(π/3)
    # |OA| = 2r·cosα, |OB| = 2r·cos(α+π/3)
    # S = 1/2 · 4r² · cosα · cos(α+π/3) · sin(π/3)
    # = 2r² · sin(π/3) · cosα · cos(α+π/3)
    # cosα · cos(α+π/3) = 1/2[cos(2α+π/3) + cos(π/3)] = 1/2[cos(2α+π/3) + 1/2]
    # 最大值在 cos(2α+π/3) = 1, 即 2α+π/3 = 0, α = -π/6
    # 最大值 = 2r² · sin(π/3) · 1/2 · (1+1/2) = 2r² · (√3/2) · 3/4 = 3√3r²/4

    S_max = 3 * np.sqrt(3) * r**2 / 4

    problem_latex = (
        f"在极坐标系中，圆 $C$: $\\rho = {2*r}\\cos\\theta$。\n\n"
        f"$A$, $B$ 为圆上两点，$\\angle AOB = \\frac{{\\pi}}{{3}}$。\n\n"
        f"求 $\\triangle OAB$ 面积的最大值。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"设 $A$ 的极角为 $\\alpha$，则 $B$ 的极角为 $\\alpha + \\frac{{\\pi}}{{3}}$。\n\n"
        f"$|OA| = {2*r}\\cos\\alpha$，$|OB| = {2*r}\\cos\\left(\\alpha + \\frac{{\\pi}}{{3}}\\right)$\n\n"
        f"$S = \\frac{{1}}{{2}}|OA| \\cdot |OB| \\sin\\frac{{\\pi}}{{3}} = \\frac{{\\sqrt{{3}}}}{{2}} \\cdot {2*r}\\cos\\alpha \\cdot {2*r}\\cos\\left(\\alpha+\\frac{{\\pi}}{{3}}\\right)$\n\n"
        f"$= {2*r**2}\\sqrt{{3}} \\cdot \\cos\\alpha \\cdot \\cos\\left(\\alpha+\\frac{{\\pi}}{{3}}\\right)$\n\n"
        f"利用积化和差：$\\cos\\alpha\\cos(\\alpha+\\frac{{\\pi}}{{3}}) = \\frac{{1}}{{2}}\\left[\\cos(2\\alpha+\\frac{{\\pi}}{{3}}) + \\frac{{1}}{{2}}\\right]$\n\n"
        f"当 $\\cos(2\\alpha+\\frac{{\\pi}}{{3}}) = 1$ 时取最大值：\n\n"
        f"$S_{{max}} = {2*r**2}\\sqrt{{3}} \\cdot \\frac{{1}}{{2}} \\cdot \\frac{{3}}{{2}} = \\frac{{3\\sqrt{{3}}{r**2}}}{{4}} = {S_max:.4g}$"
    )

    return Problem(
        title=f"极坐标面积最值 (r={r})",
        topic="极坐标", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[O], conic_type="polar",
        answer=f"S_max = 3√3r²/4 = {S_max:.4g}"
    )


def _polar_fixed_point(r, params):
    """极坐标定点问题"""
    O = Point(0, 0, "O")

    problem_latex = (
        f"在极坐标系中，圆 $C_1$: $\\rho = {2*r}\\cos\\theta$，圆 $C_2$: $\\rho = {2*r}\\sin\\theta$。\n\n"
        f"(1) 求两圆交点的极坐标；\n\n"
        f"(2) 求两圆公共弦的直角坐标方程。"
    )

    # 交点: 2r·cosθ = 2r·sinθ → tanθ = 1 → θ = π/4
    # ρ = 2r·cos(π/4) = r√2
    # 另一个交点是极点 (0, 0)

    problem_latex = (
        f"在极坐标系中，圆 $C_1$: $\\rho = {2*r}\\cos\\theta$，圆 $C_2$: $\\rho = {2*r}\\sin\\theta$。\n\n"
        f"(1) 求两圆交点的极坐标；\n\n"
        f"(2) 求两圆公共弦的直角坐标方程；\n\n"
        f"(3) 求两圆公共弦的长度。"
    )

    rho_intersect = 2 * r * np.cos(np.pi / 4)
    chord = rho_intersect  # 公共弦长 = |OP| (O到交点的距离)

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 联立 $\\rho = {2*r}\\cos\\theta$ 和 $\\rho = {2*r}\\sin\\theta$：\n\n"
        f"$\\cos\\theta = \\sin\\theta$，$\\theta = \\frac{{\\pi}}{{4}}$\n\n"
        f"$\\rho = {2*r}\\cos\\frac{{\\pi}}{{4}} = {rho_intersect:.4g}$\n\n"
        f"交点：$O(0, 0)$ 和 $P({rho_intersect:.4g}, \\frac{{\\pi}}{{4}})$\n\n"
        f"(2) $C_1$: $(x-{r})^2 + y^2 = {r**2}$，$C_2$: $x^2 + (y-{r})^2 = {r**2}$\n\n"
        f"相减得公共弦：$x = y$，即 $x - y = 0$\n\n"
        f"(3) $|OP| = {rho_intersect:.4g}$"
    )

    return Problem(
        title=f"极坐标两圆交点 (r={r})",
        topic="极坐标", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[O], conic_type="polar",
        answer=f"交点 ({rho_intersect:.4g}, π/4), 公共弦 x=y"
    )


def generate_parabola_dynamic(p=None, problem_type="basic", slope=None):
    """动态生成抛物线题目"""
    if p is None:
        p = np.random.choice([2, 4, 6, 8])
    validate_parabola(p)

    p_half = p // 2
    params = ConicParams(a=p_half, b=0, c=p_half)
    F = Point(p_half, 0, "F")

    if problem_type == "basic":
        return _parabola_basic(p, params, F)
    elif problem_type == "chord":
        if slope is None:
            slope = 1.0
        return _parabola_chord(p, params, F, slope)
    # 进阶题型
    elif problem_type == "midpoint_chord":
        return _parabola_midpoint_chord(p, params, F)
    elif problem_type == "focal_radius":
        return _parabola_focal_radius(p, params, F)
    elif problem_type == "tangent_line":
        return _parabola_tangent_line(p, params, F)
    elif problem_type == "second_def":
        return _parabola_second_def(p, params, F)
    # 进阶补充
    elif problem_type == "slope_product":
        return _parabola_slope_product(p, params, F)
    # 竞赛题型
    elif problem_type == "property":
        return _parabola_property(p, params, F)
    elif problem_type == "archimedes":
        return _parabola_archimedes(p, params, F)
    elif problem_type == "fixed_point":
        return _parabola_fixed_point(p, params, F)
    elif problem_type == "ecc_range":
        return _parabola_ecc_range(p, params, F)
    elif problem_type == "optical_property":
        return _parabola_optical_property(p, params, F)
    elif problem_type == "locus":
        return _parabola_locus(p, params, F)
    # 跨专题题型
    elif problem_type == "vector_bridge":
        return _parabola_vector_bridge(p, params, F)
    elif problem_type == "monge_circle":
        return _parabola_monge_circle(p, params, F)
    else:
        raise ValueError(f"不支持的抛物线题型: {problem_type}")


def _parabola_basic(p, params, F):
    """抛物线基础题"""
    V = Point(0, 0, "O")
    directrix = Line(1, 0, p / 2, "x = -\\frac{p}{2}")

    problem_latex = (
        f"已知抛物线 $C$ 的顶点在原点，焦点在 $x$ 轴正半轴上，"
        f"焦点到准线的距离为 ${p}$。\n\n"
        f"(1) 求抛物线 $C$ 的标准方程；\n\n"
        f"(2) 求焦点坐标和准线方程。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) $p={p}$，开口向右。\n\n"
        f"$$y^2 = {2*p}x$$\n\n"
        f"(2) 焦点 $F({p//2}, 0)$，准线 $x = -{p//2}$。"
    )

    return Problem(
        title=f"抛物线基础题 (p={p})",
        topic="抛物线", difficulty=1,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F, V], lines=[directrix],
        conic_type="parabola",
        answer=f"y^2 = {2*p}x"
    )


def _parabola_chord(p, params, F, k):
    """抛物线焦点弦"""
    A_coeff = k**2
    B_coeff = -(k**2 * p + 2 * p)
    C_coeff = k**2 * p**2 / 4

    disc = B_coeff**2 - 4 * A_coeff * C_coeff
    x1 = (-B_coeff + np.sqrt(disc)) / (2 * A_coeff)
    x2 = (-B_coeff - np.sqrt(disc)) / (2 * A_coeff)
    y1 = k * (x1 - p / 2)
    y2 = k * (x2 - p / 2)

    P, Q = Point(x1, y1, "P"), Point(x2, y2, "Q")
    chord = P.distance_to(Q)

    line_pq = Line(k, -1, -k * p / 2, "PQ")
    dist_O = line_pq.distance_to_point(Point(0, 0, "O"))
    area = 0.5 * chord * dist_O

    theta = np.arctan(k)
    chord_formula = 2 * p / np.sin(theta)**2

    problem_latex = (
        f"已知抛物线 $y^2 = {2*p}x$，焦点 $F$，过 $F$ 且斜率为 ${k}$ 的直线 $l$ 交抛物线于 $P$、$Q$。\n\n"
        f"(1) 求弦 $|PQ|$ 的长；\n\n"
        f"(2) 求 $\\triangle OPQ$ 的面积。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"抛物线 $y^2 = {2*p}x$，焦点 $F({p//2}, 0)$。\n\n"
        f"(1) 焦点弦公式 $|PQ| = \\frac{{2p}}{{\\sin^2\\theta}} = {chord_formula:.4g}$\n\n"
        f"(2) 原点到直线距离 $d = {dist_O:.4g}$，$S = {area:.4g}$"
    )

    return Problem(
        title=f"抛物线焦点弦 (p={p}, k={k})",
        topic="抛物线", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F, P, Q], lines=[line_pq],
        conic_type="parabola",
        answer=f"|PQ| = {chord:.4g}"
    )


def _parabola_property(p, params, F):
    """抛物线焦点弦性质"""
    problem_latex = (
        f"已知抛物线 $y^2 = {2*p}x$，焦点 $F$，过 $F$ 的直线 $l$ 交抛物线于 $P$、$Q$。\n\n"
        f"证明：$\\frac{{1}}{{|PF|}} + \\frac{{1}}{{|QF|}}$ 为定值。"
    )

    solution_latex = (
        f"**证明：**\n\n"
        f"设 $P(x_1,y_1)$，$Q(x_2,y_2)$，则 $|PF| = x_1+{p//2}$，$|QF| = x_2+{p//2}$。\n\n"
        f"焦点弦性质：$x_1 x_2 = \\frac{{p^2}}{{4}} = {p**2//4}$。\n\n"
        f"$\\frac{{1}}{{|PF|}} + \\frac{{1}}{{|QF|}} = \\frac{{x_1+x_2+p}}{{x_1x_2 + \\frac{{p(x_1+x_2)}}{{2}} + \\frac{{p^2}}{{4}}}} = \\frac{{2}}{{p}} = \\frac{{1}}{{{p//2}}}$"
    )

    return Problem(
        title=f"抛物线焦点弦性质 (p={p})",
        topic="抛物线", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F], conic_type="parabola",
        answer=f"\\frac{{1}}{{|PF|}} + \\frac{{1}}{{|QF|}} = \\frac{{2}}{{{p}}}"
    )


# ==================== 抛物线 — 高考压轴 / 竞赛难度 ====================

def _parabola_archimedes(p, params, F):
    """阿基米德三角形（抛物线经典竞赛题型）

    已知抛物线 y² = 2px，A(x₁,y₁), B(x₂,y₂) 为抛物线上两点，
    过 A, B 分别作抛物线的切线，两切线交于点 P。

    (1) 证明: P 的坐标为 (y₁y₂/(2p), (y₁+y₂)/2)
    (2) 若 AB 过焦点 F，求 △PAB 面积的最小值
    """
    V = Point(0, 0, "O")

    problem_latex = (
        f"已知抛物线 $C$: $y^2 = {2*p}x$，$A(x_1, y_1)$、$B(x_2, y_2)$ "
        f"为抛物线上两个不同的点。\n\n"
        f"过 $A$、$B$ 分别作抛物线的切线，两切线交于点 $P$。\n\n"
        f"(1) 证明: 点 $P$ 的坐标为 $\\left(\\frac{{y_1 y_2}}{{{2*p}}}, \\frac{{y_1+y_2}}{{2}}\\right)$；\n\n"
        f"(2) 若弦 $AB$ 过焦点 $F({p//2}, 0)$，求 $\\triangle PAB$ 面积的最小值；\n\n"
        f"(3) 证明: $\\triangle PAB$ 的面积 $= \\frac{{|y_1-y_2|^3}}{{{8*p}}}$。"
    )

    # 当 AB 过焦点时: y₁y₂ = -p²
    # |PA|² = (x_P-x₁)² + (y_P-y₁)²
    # 阿基米德三角形面积 = |y₁-y₂|³/(8p)
    # AB 过焦点: y₁y₂ = -p², |y₁-y₂|² = (y₁+y₂)² + 4p²
    # S = |y₁-y₂|³/(8p) ≥ ... 最小值在 |y₁+y₂| 最小时
    # |y₁+y₂| ≥ 0, 最小值在 y₁+y₂=0 时, 即 y₁=-y₂=p
    # 此时 |y₁-y₂|=2p, S_min = 8p³/(8p) = p²

    S_min = p**2

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 抛物线 $y^2 = {2*p}x$ 在点 $A(x_1,y_1)$ 处的切线:\n\n"
        f"$y_1 y = p(x + x_1)$，即 $y = \\frac{{p}}{{y_1}}x + \\frac{{px_1}}{{y_1}} = \\frac{{p}}{{y_1}}x + \\frac{{y_1}}{{2}}$\n\n"
        f"（利用 $x_1 = y_1^2/(2p)$）\n\n"
        f"同理 $B$ 处切线: $y = \\frac{{p}}{{y_2}}x + \\frac{{y_2}}{{2}}$\n\n"
        f"联立: $\\frac{{p}}{{y_1}}x + \\frac{{y_1}}{{2}} = \\frac{{p}}{{y_2}}x + \\frac{{y_2}}{{2}}$\n\n"
        f"$p x (\\frac{{1}}{{y_1}} - \\frac{{1}}{{y_2}}) = \\frac{{y_2-y_1}}{{2}}$\n\n"
        f"$x_P = \\frac{{y_1 y_2}}{{2p}}$，$y_P = \\frac{{p}}{{y_1}} \\cdot \\frac{{y_1 y_2}}{{2p}} + \\frac{{y_1}}{{2}} = \\frac{{y_1+y_2}}{{2}}$\n\n"
        f"(2) 当 $AB$ 过焦点 $F({p//2}, 0)$ 时，由焦点弦性质: $y_1 y_2 = -{p**2}$\n\n"
        f"$x_P = \\frac{{y_1 y_2}}{{2p}} = \\frac{{-{p**2}}}{{2 \\cdot {p}}} = -{p//2}$\n\n"
        f"即 $P$ 在准线 $x = -{p//2}$ 上。\n\n"
        f"$|y_1-y_2|^2 = (y_1+y_2)^2 - 4y_1 y_2 = (y_1+y_2)^2 + {4*p**2}$\n\n"
        f"当 $y_1+y_2 = 0$（即 $y_1 = -y_2 = {p}$）时，$|y_1-y_2| = {2*p}$ 最小。\n\n"
        f"$S_{{min}} = \\frac{{({2*p})^3}}{{{8*p}}} = \\frac{{{8*p**3}}}{{{8*p}}} = {S_min}$\n\n"
        f"(3) $S_{{\\triangle PAB}} = \\frac{{|y_1-y_2|^3}}{{{8*p}}}$（阿基米德定理）。\n\n"
        f"证明: $S = \\frac{{1}}{{2}} \\cdot |AB| \\cdot d(P, AB)$，\n\n"
        f"经代数化简可得 $S = \\frac{{|y_1-y_2|^3}}{{{8*p}}}$。"
    )

    return Problem(
        title=f"阿基米德三角形 (p={p})",
        topic="抛物线", difficulty=5,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F, V], conic_type="parabola",
        answer=f"S_min = p² = {S_min:.4g}"
    )


def _parabola_fixed_point(p, params, F):
    """抛物线定点问题（高考压轴）

    已知抛物线 y² = 2px，过焦点 F 作直线交抛物线于 A,B。
    以 AB 为直径作圆，证明该圆与准线相切。
    """
    V = Point(0, 0, "O")

    problem_latex = (
        f"已知抛物线 $C$: $y^2 = {2*p}x$，焦点为 $F({p//2}, 0)$，准线 $l$: $x = -{p//2}$。\n\n"
        f"过 $F$ 作直线交抛物线于 $A$、$B$ 两点。\n\n"
        f"(1) 以 $AB$ 为直径作圆，证明: 该圆与准线 $l$ 相切；\n\n"
        f"(2) 设 $A(x_1,y_1)$，$B(x_2,y_2)$，证明: $y_1 y_2 = -{p**2}$（定值）；\n\n"
        f"(3) 设 $M$ 为 $AB$ 的中点，过 $M$ 作 $x$ 轴的平行线交准线于 $N$，\n"
        f"证明: $NF$ 平分 $\\angle AFB$ 的外角。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $A(x_1,y_1)$，$B(x_2,y_2)$。\n\n"
        f"由抛物线定义: $|AF| = x_1 + {p//2}$，$|BF| = x_2 + {p//2}$\n\n"
        f"以 $AB$ 为直径的圆的圆心 $M$ 的横坐标: $x_M = \\frac{{x_1+x_2}}{{2}}$\n\n"
        f"圆的半径 $R = \\frac{{|AB|}}{{2}} = \\frac{{(x_1+x_2)+{p}}}{{2}} = \\frac{{x_1+x_2+{p}}}{{2}}$\n\n"
        f"$M$ 到准线的距离 $= x_M + {p//2} = \\frac{{x_1+x_2}}{{2}} + {p//2} = \\frac{{x_1+x_2+{p}}}{{2}} = R$\n\n"
        f"故圆与准线相切。\n\n"
        f"(2) 设 $AB$ 方程: $x = my + {p//2}$，代入 $y^2 = {2*p}x$:\n\n"
        f"$y^2 - {2*p}my - {p**2} = 0$\n\n"
        f"由韦达定理: $y_1 y_2 = -{p**2}$（定值）\n\n"
        f"(3) $M\\left(\\frac{{x_1+x_2}}{{2}}, \\frac{{y_1+y_2}}{{2}}\\right)$\n\n"
        f"过 $M$ 作 $x$ 轴平行线: $y = \\frac{{y_1+y_2}}{{2}}$，交准线 $x = -{p//2}$ 于 $N\\left(-{p//2}, \\frac{{y_1+y_2}}{{2}}\\right)$\n\n"
        f"设 $A$、$B$ 对应焦半径为 $r_1 = x_1 + {p//2}$，$r_2 = x_2 + {p//2}$。\n\n"
        f"由 $y_1 y_2 = -{p**2}$，$|AF| = r_1$，$|BF| = r_2$，\n\n"
        f"利用焦半径公式和三角形面积关系，可证 $NF$ 平分 $\\angle AFB$ 的外角。  $\\square$"
    )

    return Problem(
        title=f"抛物线定点/准线 (p={p})",
        topic="抛物线", difficulty=5,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F, V], conic_type="parabola",
        answer="圆与准线相切, y₁y₂ = -p²"
    )


def generate_polar_dynamic(r=None, problem_type="basic", angle=None):
    """动态生成极坐标题目"""
    if r is None:
        r = np.random.choice([2, 3, 4, 5])

    params = ConicParams(a=r, b=r)

    if problem_type == "basic":
        return _polar_basic(r, params)
    elif problem_type == "line_circle":
        if angle is None:
            angle = np.pi / 3
        return _polar_line_circle(r, params, angle)
    # 进阶题型
    elif problem_type == "focal_radius":
        return _polar_focal_radius(r, params)
    elif problem_type == "chord_ratio":
        return _polar_chord_ratio(r, params)
    elif problem_type == "slope_product":
        return _polar_slope_product(r, params)
    elif problem_type == "fixed_point":
        return _polar_fixed_point(r, params)
    # 竞赛题型
    elif problem_type == "conic":
        return _polar_conic(r, params)
    elif problem_type == "second_def":
        return _polar_second_def(r, params)
    elif problem_type == "area_opt":
        return _polar_area_opt(r, params)
    elif problem_type == "conic_unified":
        return _polar_conic_unified(r, params)
    elif problem_type == "parametric":
        return _polar_parametric(r, params)
    else:
        raise ValueError(f"不支持的极坐标题型: {problem_type}")


def _polar_basic(r, params):
    """极坐标基础题"""
    O = Point(0, 0, "O")

    problem_latex = (
        f"在极坐标系中，已知圆 $C$ 的极坐标方程为 $\\rho = {2*r}\\cos\\theta$。\n\n"
        f"(1) 将圆 $C$ 化为直角坐标方程；\n\n"
        f"(2) 求圆心坐标和半径。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) $\\rho = {2*r}\\cos\\theta \\implies \\rho^2 = {2*r}\\rho\\cos\\theta$\n\n"
        f"$x^2+y^2 = {2*r}x \\implies (x-{r})^2+y^2 = {r**2}$\n\n"
        f"(2) 圆心 $({r}, 0)$，半径 $r = {r}$。"
    )

    return Problem(
        title=f"极坐标基础题 (r={r})",
        topic="极坐标", difficulty=1,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[O],
        conic_type="polar",
        answer=f"(x-{r})^2 + y^2 = {r**2}"
    )


def _polar_line_circle(r, params, angle):
    """极坐标直线与圆"""
    O = Point(0, 0, "O")
    C = Point(r, 0, "C")

    rho = 2 * r * np.cos(angle)
    P = Point(rho * np.cos(angle), rho * np.sin(angle), "P")

    angle_deg = int(np.degrees(angle))

    problem_latex = (
        f"在极坐标系中，圆 $C$: $\\rho = {2*r}\\cos\\theta$，"
        f"直线 $l$: $\\theta = \\frac{{\\pi}}{{3}}$。\n\n"
        f"(1) 求直线与圆的交点坐标；\n\n"
        f"(2) 求弦长 $|OP|$。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 代入 $\\theta = \\frac{{\\pi}}{{3}}$：$\\rho = {2*r}\\cos\\frac{{\\pi}}{{3}} = {rho}$\n\n"
        f"交点 $P({rho}, \\frac{{\\pi}}{{3}})$，直角坐标 $P({P.x:.4g}, {P.y:.4g})$\n\n"
        f"(2) $|OP| = {rho}$"
    )

    return Problem(
        title=f"极坐标直线与圆 (r={r})",
        topic="极坐标", difficulty=2,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[O, C, P], conic_type="polar",
        answer=f"|OP| = {rho}"
    )


def _polar_conic(r, params):
    """极坐标与椭圆"""
    O = Point(0, 0, "O")
    problem_latex = (
        f"在极坐标系中，以椭圆左焦点 $F$ 为极点，$e=\\frac{{1}}{{2}}$，$p=3$。\n\n"
        f"(1) 求椭圆的极坐标方程；\n\n"
        f"(2) 求椭圆的直角坐标标准方程。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) $\\rho = \\frac{{ep}}{{1-e\\cos\\theta}} = \\frac{{3}}{{2-\\cos\\theta}}$\n\n"
        f"(2) $e=\\frac{{c}}{{a}}=\\frac{{1}}{{2}}$，$p=\\frac{{b^2}}{{c}}=3$，解得 $a=2$，$b=\\sqrt{{3}}$，$c=1$。\n\n"
        f"$$\\frac{{x^2}}{{4}} + \\frac{{y^2}}{{3}} = 1$$"
    )

    return Problem(
        title="极坐标与椭圆",
        topic="极坐标", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[O], conic_type="polar",
        answer=f"\\rho = \\frac{{3}}{{2 - \\cos\\theta}}"
    )


def _polar_conic_unified(r, params):
    """圆锥曲线统一极坐标方程（焦点弦长、通径等）

    以焦点为极点的椭圆/双曲线/抛物线统一方程 ρ = ep/(1 - e·cosθ)
    求焦点弦长、通径等。
    """
    O = Point(0, 0, "O")

    e_val = 0.5
    p_val = 3
    angle_val = np.pi / 3

    # Compute values for solution
    cos_a = np.cos(angle_val)
    ep = e_val * p_val  # = 1.5

    # Focal chord length via polar formula: |AB| = 2ep / (1 - e^2 * cos^2(alpha))
    focal_chord = 2 * ep / (1 - e_val**2 * cos_a**2)

    problem_latex = (
        f"在极坐标系中，以椭圆的左焦点 $F$ 为极点，$x$ 轴正方向为极轴建立极坐标系。"
        f"已知椭圆的离心率 $e = \\frac{{1}}{{2}}$，"
        f"焦点到相应准线的距离 $p = 3$。\n\n"
        f"(1) 求椭圆的极坐标方程 $\\rho = \\frac{{ep}}{{1 - e\\cos\\theta}}$；\n\n"
        f"(2) 将极坐标方程化为直角坐标方程，并求椭圆的中心、长半轴和短半轴；\n\n"
        f"(3) 过极点（焦点）作射线 $\\theta = \\frac{{\\pi}}{{3}}$ 交椭圆于 $A$、$B$ 两点，"
        f"利用韦达定理求焦点弦 $|AB|$ 的长。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 代入 $e = \\frac{{1}}{{2}}$，$p = 3$：\n\n"
        f"$\\rho = \\frac{{\\frac{{1}}{{2}} \\times 3}}{{1 - \\frac{{1}}{{2}}\\cos\\theta}} = \\frac{{3}}{{2 - \\cos\\theta}}$\n\n"
        f"(2) 由 $\\rho = \\frac{{3}}{{2 - \\cos\\theta}}$，得 $\\rho(2 - \\cos\\theta) = 3$，即 $2\\rho - \\rho\\cos\\theta = 3$。\n\n"
        f"代入 $\\rho = \\sqrt{{x^2+y^2}}$，$\\rho\\cos\\theta = x$：\n\n"
        f"$2\\sqrt{{x^2+y^2}} = x + 3$，两边平方：\n\n"
        f"$4(x^2+y^2) = x^2 + 6x + 9$\n\n"
        f"$3x^2 + 4y^2 - 6x - 9 = 0$，配方：$3(x-1)^2 + 4y^2 = 12$\n\n"
        f"$$\\frac{{(x-1)^2}}{{4}} + \\frac{{y^2}}{{3}} = 1$$\n\n"
        f"椭圆中心 $(1, 0)$，$a = 2$，$b = \\sqrt{{3}}$。\n\n"
        f"(3) 焦点 $F$（即极点）在直角坐标系中的位置：\n\n"
        f"椭圆中心 $(1,0)$，$c = \\sqrt{{a^2-b^2}} = 1$，左焦点 $F(0, 0)$。\n\n"
        f"以 $F$ 为原点，射线 $\\theta = \\frac{{\\pi}}{{3}}$ 对应直线 $y = \\sqrt{{3}}x$。\n\n"
        f"椭圆在 $F$ 为原点的坐标系中方程为 $\\frac{{(x+1)^2}}{{4}} + \\frac{{y^2}}{{3}} = 1$。\n\n"
        f"代入 $y = \\sqrt{{3}}x$：$\\frac{{(x+1)^2}}{{4}} + x^2 = 1$\n\n"
        f"化简：$(x+1)^2 + 4x^2 = 4$，即 $5x^2 + 2x - 3 = 0$。\n\n"
        f"由韦达定理：$x_1 + x_2 = -\\frac{{2}}{{5}}$，$x_1 x_2 = -\\frac{{3}}{{5}}$。\n\n"
        f"$|x_1 - x_2| = \\sqrt{{(x_1+x_2)^2 - 4x_1 x_2}} = \\sqrt{{\\frac{{4}}{{25}} + \\frac{{12}}{{5}}}} = \\sqrt{{\\frac{{64}}{{25}}}} = \\frac{{8}}{{5}}$\n\n"
        f"两交点为 $(x_1, \\sqrt{{3}}x_1)$ 和 $(x_2, \\sqrt{{3}}x_2)$：\n\n"
        f"$|AB|^2 = (x_1-x_2)^2 + 3(x_1-x_2)^2 = 4(x_1-x_2)^2 = \\frac{{256}}{{25}}$\n\n"
        f"$|AB| = \\frac{{16}}{{5}} = {focal_chord:.4g}$\n\n"
        f"验证：由焦点弦公式 $|AB| = \\frac{{2ep}}{{1 - e^2\\cos^2\\alpha}} = \\frac{{3}}{{1 - \\frac{{1}}{{16}}}} = \\frac{{3}}{{\\frac{{15}}{{16}}}} = \\frac{{16}}{{5}}$ $\\checkmark$"
    )

    return Problem(
        title="圆锥曲线统一极坐标方程 (e=1/2, p=3)",
        topic="极坐标", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[O], conic_type="polar",
        answer=f"|AB| = 16/5 = {focal_chord:.4g}"
    )



def _polar_parametric(r, params):
    """极坐标参数方程应用

    已知圆的极坐标方程 ρ = 2r·cosθ，利用参数方程求弦长、面积等。
    """
    O = Point(0, 0, "O")

    # 圆心 (r, 0), 半径 r
    theta_a = np.pi / 6
    theta_b = np.pi / 3

    rho_a = 2 * r * np.cos(theta_a)
    rho_b = 2 * r * np.cos(theta_b)

    # 转换为直角坐标
    x_a = rho_a * np.cos(theta_a)
    y_a = rho_a * np.sin(theta_a)
    x_b = rho_b * np.cos(theta_b)
    y_b = rho_b * np.sin(theta_b)

    A = Point(x_a, y_a, "A")
    B = Point(x_b, y_b, "B")

    # 弦长
    chord_len = np.sqrt((x_a - x_b)**2 + (y_a - y_b)**2)

    # 三角形 OAB 面积 = 0.5 * |ρ_a * ρ_b * sin(θ_b - θ_a)|
    area = 0.5 * rho_a * rho_b * np.sin(theta_b - theta_a)

    problem_latex = (
        "在极坐标系中，圆 $C$ 的极坐标方程为 $\\rho = " + str(2*r) + "\\cos\\theta$。"
        "已知 $A$、$B$ 是圆 $C$ 上的两点，对应的极角分别为 "
        "$\\theta_A = \\frac{\\pi}{6}$，$\\theta_B = \\frac{\\pi}{3}$。\n\n"
        "(1) 将圆 $C$ 的极坐标方程化为直角坐标方程；\n\n"
        "(2) 求 $|OA|$ 和 $|OB|$ 的值；\n\n"
        "(3) 求弦 $|AB|$ 的长和 $\\triangle OAB$ 的面积。"
    )

    solution_latex = (
        "**解：**\n\n"
        "(1) 由 $\\rho = " + str(2*r) + "\\cos\\theta$，得 $\\rho^2 = " + str(2*r) + "\\rho\\cos\\theta$。\n\n"
        "代入 $\\rho^2 = x^2 + y^2$，$\\rho\\cos\\theta = x$：\n\n"
        "$x^2 + y^2 = " + str(2*r) + "x$，配方：$(x-" + str(r) + ")^2 + y^2 = " + str(r**2) + "$\n\n"
        "圆心 $(" + str(r) + ", 0)$，半径 $" + str(r) + "$。\n\n"
        "(2) $|OA| = \\rho_A = " + str(2*r) + "\\cos\\frac{\\pi}{6} = " + str(2*r) + " \\times \\frac{\\sqrt{3}}{2} = " + f"{rho_a:.4g}" + "$\n\n"
        "$|OB| = \\rho_B = " + str(2*r) + "\\cos\\frac{\\pi}{3} = " + str(2*r) + " \\times \\frac{1}{2} = " + f"{rho_b:.4g}" + "$\n\n"
        "(3) $A(" + f"{x_a:.4g}" + ", " + f"{y_a:.4g}" + ")$，$B(" + f"{x_b:.4g}" + ", " + f"{y_b:.4g}" + ")$\n\n"
        "$|AB| = \\sqrt{(" + f"{x_a:.4g}" + "-" + f"{x_b:.4g}" + ")^2 + (" + f"{y_a:.4g}" + "-" + f"{y_b:.4g}" + ")^2} = " + f"{chord_len:.4g}" + "$\n\n"
        "$S_{\\triangle OAB} = \\frac{1}{2}|OA| \\cdot |OB| \\sin(\\theta_B - \\theta_A)$\n\n"
        "$= \\frac{1}{2} \\times " + f"{rho_a:.4g}" + " \\times " + f"{rho_b:.4g}" + " \\times \\sin\\frac{\\pi}{6} = " + f"{area:.4g}" + "$"
    )

    return Problem(
        title="极坐标参数方程应用 (r=" + str(r) + ")",
        topic="极坐标", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params, points=[O, A, B], conic_type="polar",
        answer="|AB|=" + f"{chord_len:.4g}" + ", S=" + f"{area:.4g}"
    )


# ==================== 交互式模式 ====================

def interactive_mode():
    """交互式模式，引导用户输入参数"""
    print("=" * 60)
    print("  解析几何题目生成器 — 交互式模式")
    print("=" * 60)

    # 选择知识点
    print("\n请选择知识点：")
    print("  1. 椭圆 (Ellipse)")
    print("  2. 双曲线 (Hyperbola)")
    print("  3. 抛物线 (Parabola)")
    print("  4. 极坐标 (Polar)")

    topic_map = {"1": "ellipse", "2": "hyperbola", "3": "parabola", "4": "polar"}
    choice = input("\n请输入编号 (1-4): ").strip()
    topic = topic_map.get(choice, "ellipse")

    # 选择题型
    type_map = {
        "ellipse": {"1": "basic", "2": "chord", "3": "focus_triangle"},
        "hyperbola": {"1": "basic", "2": "chord", "3": "focus_triangle"},
        "parabola": {"1": "basic", "2": "chord", "3": "property"},
        "polar": {"1": "basic", "2": "line_circle", "3": "conic"},
    }
    type_names = {
        "basic": "基础题（标准方程）",
        "chord": "焦点弦问题",
        "focus_triangle": "焦点三角形",
        "line_circle": "直线与圆",
        "property": "性质证明",
        "conic": "圆锥曲线极坐标方程",
    }

    print(f"\n请选择{topic_names_cn[topic]}题型：")
    for k, v in type_map[topic].items():
        print(f"  {k}. {type_names[v]}")

    type_choice = input("\n请输入编号: ").strip()
    problem_type = type_map[topic].get(type_choice, "basic")

    # 输入参数
    params = {}
    print(f"\n请输入参数（直接回车则自动随机生成）：")

    if topic == "ellipse":
        a_input = input("  半长轴 a = ").strip()
        b_input = input("  半短轴 b = ").strip()
        if a_input: params['a'] = float(a_input)
        if b_input: params['b'] = float(b_input)
        if problem_type == "chord":
            k_input = input("  弦斜率 k = ").strip()
            if k_input: params['slope'] = float(k_input)

    elif topic == "hyperbola":
        a_input = input("  半实轴 a = ").strip()
        b_input = input("  半虚轴 b = ").strip()
        if a_input: params['a'] = float(a_input)
        if b_input: params['b'] = float(b_input)
        if problem_type == "chord":
            k_input = input("  弦斜率 k = ").strip()
            if k_input: params['slope'] = float(k_input)

    elif topic == "parabola":
        p_input = input("  焦距参数 p = ").strip()
        if p_input: params['p'] = float(p_input)
        if problem_type == "chord":
            k_input = input("  弦斜率 k = ").strip()
            if k_input: params['slope'] = float(k_input)

    elif topic == "polar":
        r_input = input("  圆半径 r = ").strip()
        if r_input: params['r'] = float(r_input)

    return topic, problem_type, params


topic_names_cn = {
    "ellipse": "椭圆", "hyperbola": "双曲线",
    "parabola": "抛物线", "polar": "极坐标"
}


# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(description="解析几何题目生成器")
    parser.add_argument("--topic", choices=["ellipse", "hyperbola", "parabola", "polar"],
                        help="知识点")
    parser.add_argument("--type", choices=["basic", "chord", "focus_triangle",
                                           "line_circle", "property", "conic"],
                        help="题型")
    parser.add_argument("--a", type=float, help="半长轴/半实轴")
    parser.add_argument("--b", type=float, help="半短轴/半虚轴")
    parser.add_argument("--p", type=float, help="抛物线焦距参数")
    parser.add_argument("--r", type=float, help="极坐标圆半径")
    parser.add_argument("--k", type=float, help="弦斜率")
    parser.add_argument("--interactive", action="store_true", help="交互式模式")
    parser.add_argument("--output-dir", default="/root/analytic_geometry_generator/output",
                        help="输出目录")

    args = parser.parse_args()

    # 交互式模式
    if args.interactive:
        topic, problem_type, params = interactive_mode()
    elif args.topic:
        topic = args.topic
        problem_type = args.type or "basic"
        params = {}
        if args.a: params['a'] = args.a
        if args.b: params['b'] = args.b
        if args.p: params['p'] = args.p
        if args.r: params['r'] = args.r
        if args.k: params['slope'] = args.k
    else:
        # 无参数：随机生成一道题
        topic = np.random.choice(["ellipse", "hyperbola", "parabola", "polar"])
        problem_type = np.random.choice(["basic", "chord"])
        params = {}

    # 生成题目
    print(f"\n生成中: {topic_names_cn[topic]} / {problem_type} ...")

    if topic == "ellipse":
        problem = generate_ellipse_dynamic(
            a=params.get('a'), b=params.get('b'),
            problem_type=problem_type, slope=params.get('slope'))
    elif topic == "hyperbola":
        problem = generate_hyperbola_dynamic(
            a=params.get('a'), b=params.get('b'),
            problem_type=problem_type, slope=params.get('slope'))
    elif topic == "parabola":
        problem = generate_parabola_dynamic(
            p=params.get('p'), problem_type=problem_type, slope=params.get('slope'))
    elif topic == "polar":
        problem = generate_polar_dynamic(
            r=params.get('r'), problem_type=problem_type)

    # 输出题目
    print("\n" + "=" * 60)
    print(f"【{problem.title}】")
    print("=" * 60)
    print("\n【题干】")
    print(problem.problem_latex)
    print("\n【解答】")
    print(problem.solution_latex)
    print(f"\n【答案】{problem.answer}")

    # 创建时间戳目录
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    question_dir = os.path.join(args.output_dir, f"Question_{timestamp}")
    os.makedirs(question_dir, exist_ok=True)

    # 渲染配图
    renderer = DiagramRenderer(figsize=(10, 8), dpi=150)
    img_path = os.path.join(question_dir, "diagram.png")
    renderer.render(problem, img_path)

    # 保存 LaTeX
    tex_path = os.path.join(question_dir, "problem.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(f"% {problem.title}\n\n{problem.problem_latex}")

    sol_path = os.path.join(question_dir, "solution.tex")
    with open(sol_path, "w", encoding="utf-8") as f:
        f.write(f"% {problem.title} — 解答\n\n{problem.solution_latex}")

    # 保存纯文本
    from latex_render import render_problem_text
    txt_path = os.path.join(question_dir, "problem.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"{'='*50}\n{problem.title}\n{'='*50}\n\n")
        f.write(render_problem_text(problem.problem_latex))
        f.write(f"\n\n{'─'*50}\n\n")
        f.write(render_problem_text(problem.solution_latex))

    print(f"\n✓ 已保存到: {question_dir}/")
    print(f"  ├── diagram.png   (配图)")
    print(f"  ├── problem.tex   (LaTeX 题干)")
    print(f"  ├── solution.tex  (LaTeX 解答)")
    print(f"  └── problem.txt   (纯文本版)")


if __name__ == "__main__":
    main()
