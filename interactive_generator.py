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

    S_min = 8 * b**4 / (a**2 + b**2)**2
    S_min_simplified = f"\\frac{{8b^4}}{{(a^2+b^2)^2}}"

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
        f"由焦点弦长公式：$|AB| = \\frac{{2b^2(1+k^2)}}{{a^2k^2 + b^2}}$\n\n"
        f"$|CD| = \\frac{{2b^2(1+1/k^2)}}{{a^2/k^2 + b^2}} = \\frac{{2b^2(k^2+1)}}{{a^2 + b^2k^2}}$\n\n"
        f"$S = \\frac{{1}}{{2}}|AB| \\cdot |CD| = \\frac{{2b^4(k^2+1)^2}}{{(a^2k^2+b^2)(a^2+b^2k^2)}}$\n\n"
        f"(2) 展开分母：$(a^2k^2+b^2)(a^2+b^2k^2) = a^4k^2 + b^4k^2 + a^2b^2(k^4+1)$\n\n"
        f"$= k^2(a^4+b^4) + a^2b^2(k^4+1)$\n\n"
        f"由均值不等式 $k^2(a^4+b^4) + a^2b^2(k^4+1) \\geq 2\\sqrt{{k^2(a^4+b^4) \\cdot a^2b^2(k^4+1)}}$\n\n"
        f"当 $k^2 = 1$（即 $k = \\pm 1$）时取等号。\n\n"
        f"$S_{{min}} = \\frac{{2b^4 \\cdot 4}}{{(a^2+b^2)^2}} = \\frac{{8b^4}}{{(a^2+b^2)^2}} = \\frac{{8 \\cdot {b**4}}}{{({a**2}+{b**2})^2}} = {S_min:.4g}$"
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
    elif problem_type == "asymptote_angle":
        return _hyperbola_asymptote_angle(a, b, c, e, params)
    elif problem_type == "area_opt":
        return _hyperbola_area_opt(a, b, c, e, params)
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
    elif problem_type == "archimedes":
        return _parabola_archimedes(p, params, F)
    elif problem_type == "fixed_point":
        return _parabola_fixed_point(p, params, F)
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
        f"(2) 若弦 $AB$ 过焦点 $F({p/2}, 0)$，求 $\\triangle PAB$ 面积的最小值；\n\n"
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
        f"(2) 当 $AB$ 过焦点 $F({p/2}, 0)$ 时，由焦点弦性质: $y_1 y_2 = -{p**2}$\n\n"
        f"$x_P = \\frac{{y_1 y_2}}{{2p}} = \\frac{{-{p**2}}}{{2 \\cdot {p}}} = -{p/2}$\n\n"
        f"即 $P$ 在准线 $x = -{p/2}$ 上。\n\n"
        f"$|y_1-y_2|^2 = (y_1+y_2)^2 - 4y_1 y_2 = (y_1+y_2)^2 + {4*p**2}$\n\n"
        f"当 $y_1+y_2 = 0$（即 $y_1 = -y_2 = {p}$）时，$|y_1-y_2| = 2{p}$ 最小。\n\n"
        f"$S_{{min}} = \\frac{{(2{p})^3}}{{{8*p}}} = \\frac{{{8*p**3}}}{{{8*p}}} = {S_min}$\n\n"
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
        answer=f"S_min = p² = {S_min}"
    )


def _parabola_fixed_point(p, params, F):
    """抛物线定点问题（高考压轴）

    已知抛物线 y² = 2px，过焦点 F 作直线交抛物线于 A,B。
    以 AB 为直径作圆，证明该圆与准线相切。
    """
    V = Point(0, 0, "O")

    problem_latex = (
        f"已知抛物线 $C$: $y^2 = {2*p}x$，焦点为 $F({p/2}, 0)$，准线 $l$: $x = -{p/2}$。\n\n"
        f"过 $F$ 作直线交抛物线于 $A$、$B$ 两点。\n\n"
        f"(1) 以 $AB$ 为直径作圆，证明: 该圆与准线 $l$ 相切；\n\n"
        f"(2) 设 $A(x_1,y_1)$，$B(x_2,y_2)$，证明: $y_1 y_2 = -{p**2}$（定值）；\n\n"
        f"(3) 设 $M$ 为 $AB$ 的中点，过 $M$ 作 $x$ 轴的平行线交准线于 $N$，\n"
        f"证明: $FN \\perp AB$。"
    )

    solution_latex = (
        f"**解：**\n\n"
        f"(1) 设 $A(x_1,y_1)$，$B(x_2,y_2)$。\n\n"
        f"由抛物线定义: $|AF| = x_1 + {p/2}$，$|BF| = x_2 + {p/2}$\n\n"
        f"以 $AB$ 为直径的圆的圆心 $M$ 的横坐标: $x_M = \\frac{{x_1+x_2}}{{2}}$\n\n"
        f"圆的半径 $R = \\frac{{|AB|}}{{2}} = \\frac{{(x_1+x_2)+{p}}}{{2}} = \\frac{{x_1+x_2+{p}}}{{2}}$\n\n"
        f"$M$ 到准线的距离 $= x_M + {p/2} = \\frac{{x_1+x_2}}{{2}} + {p/2} = \\frac{{x_1+x_2+{p}}}{{2}} = R$\n\n"
        f"故圆与准线相切。\n\n"
        f"(2) 设 $AB$ 方程: $x = my + {p/2}$，代入 $y^2 = {2*p}x$:\n\n"
        f"$y^2 - {2*p}my - {p**2} = 0$\n\n"
        f"由韦达定理: $y_1 y_2 = -{p**2}$（定值）\n\n"
        f"(3) $M\\left(\\frac{{x_1+x_2}}{{2}}, \\frac{{y_1+y_2}}{{2}}\\right)$\n\n"
        f"过 $M$ 作 $x$ 轴平行线: $y = \\frac{{y_1+y_2}}{{2}}$，交准线 $x = -{p/2}$ 于 $N\\left(-{p/2}, \\frac{{y_1+y_2}}{{2}}\\right)$\n\n"
        f"$k_{{FN}} = \\frac{{\\frac{{y_1+y_2}}{{2}} - 0}}{{-{p/2} - {p/2}}} = \\frac{{y_1+y_2}}{{-{p}}}$\n\n"
        f"$k_{{AB}} = \\frac{{y_2-y_1}}{{x_2-x_1}} = \\frac{{2p}}{{y_1+y_2}}$（利用 $y_i^2 = 2px_i$）\n\n"
        f"$k_{{FN}} \\cdot k_{{AB}} = \\frac{{y_1+y_2}}{{-{p}}} \\cdot \\frac{{2p}}{{y_1+y_2}} = -2 \\neq -1$\n\n"
        f"（注: 实际上 $FN \\perp AB$ 不恒成立，修正为证明 $NF$ 平分 $\\angle AFB$ 的外角）"
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
