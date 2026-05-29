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
        f"的左焦点为 $F_1$，过 $F_1$ 且斜率为 ${k}$ 的直线 $l$ 与椭圆交于 $P$、$Q$ 两点。\n\n"
        f"(1) 求弦 $PQ$ 的长；\n\n"
        f"(2) 求 $\\triangle OPQ$ 的面积（$O$ 为原点）。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"椭圆 $a={a}$，$b={b}$，$c=\\sqrt{{{a**2}-{b**2}}}={c:.4g}$，左焦点 $F_1({-c:.4g}, 0)$。\n\n"
        f"(1) 直线 $l: y = {k}(x + {c:.4g})$。\n\n"
        f"联立椭圆方程得：${A_coeff}x^2 + {B_coeff:.4g}x + {C_coeff:.4g} = 0$\n\n"
        f"$|PQ| = \\sqrt{{1+{k**2}}} \\cdot \\sqrt{{\\Delta}} / {A_coeff} = {chord_length:.4g}$\n\n"
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
        f"直线 $l: y = {k}(x - {c:.4g})$，代入双曲线方程：\n\n"
        f"${A_coeff}x^2 + {B_coeff:.4g}x + {C_coeff:.4g} = 0$\n\n"
        f"$|PQ| = \\sqrt{{1+{k**2}}} \\cdot |x_1-x_2| = {chord:.4g}$"
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


def generate_parabola_dynamic(p=None, problem_type="basic", slope=None):
    """动态生成抛物线题目"""
    if p is None:
        p = np.random.choice([2, 4, 6, 8])
    validate_parabola(p)

    params = ConicParams(a=p / 2, b=0, c=p / 2)
    F = Point(p / 2, 0, "F")

    if problem_type == "basic":
        return _parabola_basic(p, params, F)
    elif problem_type == "chord":
        if slope is None:
            slope = 1.0
        return _parabola_chord(p, params, F, slope)
    elif problem_type == "property":
        return _parabola_property(p, params, F)
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
        f"(2) 焦点 $F({p/2}, 0)$，准线 $x = -{p/2}$。"
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
        f"抛物线 $y^2 = {2*p}x$，焦点 $F({p/2}, 0)$。\n\n"
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
        f"设 $P(x_1,y_1)$，$Q(x_2,y_2)$，则 $|PF| = x_1+{p/2}$，$|QF| = x_2+{p/2}$。\n\n"
        f"焦点弦性质：$x_1 x_2 = \\frac{{p^2}}{{4}} = {p**2/4}$。\n\n"
        f"$\\frac{{1}}{{|PF|}} + \\frac{{1}}{{|QF|}} = \\frac{{x_1+x_2+p}}{{x_1x_2 + \\frac{{p(x_1+x_2)}}{{2}} + \\frac{{p^2}}{{4}}}} = \\frac{{2}}{{p}} = \\frac{{1}}{{{p/2}}}$"
    )

    return Problem(
        title=f"抛物线焦点弦性质 (p={p})",
        topic="抛物线", difficulty=3,
        problem_latex=problem_latex, solution_latex=solution_latex,
        conic_params=params,
        points=[F], conic_type="parabola",
        answer=f"\\frac{{1}}{{|PF|}} + \\frac{{1}}{{|QF|}} = \\frac{{2}}{{{p}}}"
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
    elif problem_type == "conic":
        return _polar_conic(r, params)
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
        conic_params=params, conic_type="polar",
        answer=f"\\rho = \\frac{{3}}{{2 - \\cos\\theta}}"
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

    # 渲染配图
    renderer = DiagramRenderer(figsize=(10, 8), dpi=150)
    img_path = os.path.join(args.output_dir, f"{topic}_{problem_type}_output.png")
    renderer.render(problem, img_path)
    print(f"\n✓ 配图已保存: {img_path}")


if __name__ == "__main__":
    main()
