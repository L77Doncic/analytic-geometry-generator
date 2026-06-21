"""
全面测试所有 60 种题型的生成能力
测试项：题目生成、LaTeX渲染、配图渲染、答案完整性、数学正确性
"""

import sys
import os
import re
import traceback
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interactive_generator import (
    generate_ellipse_dynamic, generate_hyperbola_dynamic,
    generate_parabola_dynamic, generate_polar_dynamic
)
from diagram_renderer import DiagramRenderer
from latex_render import render_problem_text

# 输出目录 — 相对于项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "test")
os.makedirs(OUTPUT_DIR, exist_ok=True)

renderer = DiagramRenderer(figsize=(10, 8), dpi=100)


# ── 数学正确性验证辅助函数 ──

def _extract_number(text: str) -> float | None:
    """从答案字符串中提取最终数值（取最后一个数值 token）"""
    # 匹配所有数值: 12.5, -3.14, 4g 格式, √3 ≈ 1.732 等
    # 取最后一个，因为答案通常形如 "S = b²√3 = 27.71" 或 "|PQ| = 6.5"
    matches = re.findall(r'=?\s*(-?\d+\.?\d*(?:[eE][+-]?\d+)?)', text)
    if matches:
        try:
            return float(matches[-1])
        except ValueError:
            return None
    return None


def _check_point_on_ellipse(x: float, y: float, a: float, b: float, tol: float = 0.1) -> bool:
    """检查点 (x, y) 是否在椭圆 x²/a² + y²/b² = 1 上"""
    val = x**2 / a**2 + y**2 / b**2
    return abs(val - 1.0) < tol


def _check_point_on_hyperbola(x: float, y: float, a: float, b: float, tol: float = 0.1) -> bool:
    """检查点 (x, y) 是否在双曲线 x²/a² - y²/b² = 1 上"""
    val = x**2 / a**2 - y**2 / b**2
    return abs(val - 1.0) < tol


def _check_point_on_parabola(x: float, y: float, p: float, tol: float = 0.1) -> bool:
    """检查点 (x, y) 是否在抛物线 y² = 2px 上"""
    val = y**2
    expected = 2 * p * x
    return abs(val - expected) < tol * max(1, abs(expected))


def _check_conic_params(params, topic: str) -> list[str]:
    """验证 ConicParams 的基本数学关系"""
    errors = []
    if params is None:
        return errors

    # 离心率范围检查
    if params.e < 0:
        errors.append(f"离心率 e={params.e} < 0，不合法")
    if topic == "椭圆" and params.e >= 1:
        errors.append(f"椭圆离心率 e={params.e} >= 1，不合法")
    if topic == "双曲线" and params.e <= 1:
        errors.append(f"双曲线离心率 e={params.e} <= 1，不合法")

    # a 为正数（抛物线只有 p，a 可以为 0）
    if params.a <= 0 and topic != "抛物线":
        errors.append(f"a={params.a} <= 0")
    # b 为正数（抛物线没有 b 参数，b=0 是正常的）
    if params.b <= 0 and topic != "抛物线":
        errors.append(f"b={params.b} <= 0")

    # c 的关系
    if topic == "椭圆":
        expected_c = np.sqrt(params.a**2 - params.b**2)
        if abs(params.c - expected_c) > 0.01 * max(1, expected_c):
            errors.append(f"椭圆 c={params.c:.4g}，应为 √(a²-b²)={expected_c:.4g}")
    elif topic == "双曲线":
        expected_c = np.sqrt(params.a**2 + params.b**2)
        if abs(params.c - expected_c) > 0.01 * max(1, expected_c):
            errors.append(f"双曲线 c={params.c:.4g}，应为 √(a²+b²)={expected_c:.4g}")

    return errors


def _check_points_on_conic(problem, topic: str, a: float = None, b: float = None, p: float = None) -> list[str]:
    """验证关键点是否在对应的圆锥曲线上"""
    errors = []
    if not problem.points:
        return errors

    for pt in problem.points:
        x, y = pt.x, pt.y
        # 跳过焦点等不在曲线上的特殊点
        if pt.label and ("F" in pt.label or "f" in pt.label):
            continue
        # 跳过原点和无穷远点
        if abs(x) < 1e-10 and abs(y) < 1e-10:
            continue

        if topic == "椭圆" and a and b:
            if not _check_point_on_ellipse(x, y, a, b, tol=0.15):
                errors.append(f"点 {pt.label}({x:.4g},{y:.4g}) 不在椭圆上")
        elif topic == "双曲线" and a and b:
            if not _check_point_on_hyperbola(x, y, a, b, tol=0.15):
                errors.append(f"点 {pt.label}({x:.4g},{y:.4g}) 不在双曲线上")
        elif topic == "抛物线" and p:
            if x >= 0 and not _check_point_on_parabola(x, y, p, tol=0.15):
                errors.append(f"点 {pt.label}({x:.4g},{y:.4g}) 不在抛物线上")

    return errors


# ── 定义所有题型 ──

ALL_TYPES = {
    "椭圆": {
        "gen": generate_ellipse_dynamic,
        "args": {"a": 5, "b": 3},
        "types": [
            "basic", "chord", "focus_triangle",
            "midpoint_chord", "focal_radius", "slope_product", "tangent_line", "second_def",
            "fixed_point", "area_opt", "ecc_range", "tangent", "third_def",
            "optical_property", "locus",
            "monge_circle", "apollonius",
        ]
    },
    "双曲线": {
        "gen": generate_hyperbola_dynamic,
        "args": {"a": 3, "b": 4},
        "types": [
            "basic", "chord", "focus_triangle",
            "midpoint_chord", "focal_radius", "second_def", "tangent_line", "slope_product",
            "asymptote_angle", "area_opt", "ecc_range", "tangent",
            "optical_property", "locus", "equilateral_hyperbola",
            "monge_circle", "butterfly",
        ]
    },
    "抛物线": {
        "gen": generate_parabola_dynamic,
        "args": {"p": 4},
        "types": [
            "basic", "chord",
            "midpoint_chord", "focal_radius", "tangent_line", "second_def", "slope_product",
            "property", "archimedes", "fixed_point", "ecc_range",
            "optical_property", "locus",
            "vector_bridge", "monge_circle",
        ]
    },
    "极坐标": {
        "gen": generate_polar_dynamic,
        "args": {"r": 3},
        "types": [
            "basic", "line_circle",
            "focal_radius", "chord_ratio", "slope_product", "fixed_point",
            "conic", "second_def", "area_opt",
            "conic_unified",
            "parametric",
        ]
    },
}

results = []
total = sum(len(v["types"]) for v in ALL_TYPES.values())
current = 0
math_warnings = []

print(f"开始测试 {total} 种题型...\n")

for topic, config in ALL_TYPES.items():
    gen = config["gen"]
    args = config["args"]

    for ptype in config["types"]:
        current += 1
        label = f"[{current}/{total}] {topic} / {ptype}"

        try:
            # 1. 生成题目
            problem = gen(problem_type=ptype, **args)

            # 2. 验证题干
            assert problem.problem_latex, "题干为空"
            assert len(problem.problem_latex) > 20, f"题干过短 ({len(problem.problem_latex)} chars)"

            # 3. 验证解答
            assert problem.solution_latex, "解答为空"
            assert len(problem.solution_latex) > 20, "解答过短"

            # 4. 验证答案
            assert problem.answer, "答案为空"

            # 5. LaTeX渲染
            rendered = render_problem_text(problem.problem_latex)
            assert rendered, "LaTeX渲染失败"

            # 6. 配图渲染
            img_path = os.path.join(OUTPUT_DIR, f"{topic}_{ptype}.png")
            renderer.render(problem, img_path)
            assert os.path.exists(img_path), "配图文件未生成"
            assert os.path.getsize(img_path) > 1000, f"配图文件过小 ({os.path.getsize(img_path)} bytes)"

            # 7. 验证关键点
            assert len(problem.points) > 0, "无关键点"

            # 8. 数学正确性验证
            math_errors = []

            # 8a. 验证 ConicParams
            if problem.conic_params:
                param_errors = _check_conic_params(problem.conic_params, topic)
                math_errors.extend(param_errors)

            # 8b. 验证点在曲线上（仅对 basic 类型做严格检查，因为其他类型可能有辅助线上的点）
            if ptype == "basic":
                point_errors = _check_points_on_conic(
                    problem, topic,
                    a=args.get("a"), b=args.get("b"), p=args.get("p")
                )
                math_errors.extend(point_errors)

            # 8c. 验证答案可解析为数值
            ans_val = _extract_number(problem.answer)
            if ans_val is not None:
                # 面积、长度等不应为负数（除非是坐标值）
                if "面积" in problem.title or "S" in problem.answer:
                    if ans_val < 0:
                        math_errors.append(f"面积答案为负数: {ans_val}")
                if "距离" in problem.title or "|PQ|" in problem.answer:
                    if ans_val < 0:
                        math_errors.append(f"距离答案为负数: {ans_val}")

            if math_errors:
                math_warnings.append({
                    "topic": topic, "type": ptype,
                    "errors": math_errors
                })

            results.append({
                "topic": topic, "type": ptype, "status": "✓",
                "difficulty": problem.difficulty,
                "title": problem.title,
                "points": len(problem.points),
                "img_size": os.path.getsize(img_path),
                "math_warnings": math_errors,
            })
            warn_str = f" ⚠ {len(math_errors)}个数学警告" if math_errors else ""
            print(f"  ✓ {label} — {problem.title} (d={problem.difficulty}, {len(problem.points)}点, {os.path.getsize(img_path)//1024}KB){warn_str}")

        except Exception as e:
            results.append({
                "topic": topic, "type": ptype, "status": "✗",
                "error": str(e),
                "traceback": traceback.format_exc(),
            })
            print(f"  ✗ {label} — ERROR: {e}")

# ── 生成报告 ──
print("\n" + "=" * 70)
print("测试报告")
print("=" * 70)

passed = [r for r in results if r["status"] == "✓"]
failed = [r for r in results if r["status"] == "✗"]

print(f"\n总计: {total} 种题型")
print(f"通过: {len(passed)} ✓")
print(f"失败: {len(failed)} ✗")
print(f"通过率: {len(passed)/total*100:.1f}%")

if failed:
    print(f"\n{'─'*70}")
    print("失败详情:")
    for r in failed:
        print(f"  ✗ {r['topic']}/{r['type']}: {r['error']}")

if math_warnings:
    print(f"\n{'─'*70}")
    print(f"数学正确性警告 ({len(math_warnings)} 项):")
    for w in math_warnings:
        print(f"  ⚠ {w['topic']}/{w['type']}:")
        for err in w["errors"]:
            print(f"    - {err}")

print(f"\n{'─'*70}")
print("按知识点统计:")
for topic in ALL_TYPES:
    topic_results = [r for r in results if r["topic"] == topic]
    topic_passed = [r for r in topic_results if r["status"] == "✓"]
    print(f"  {topic}: {len(topic_passed)}/{len(topic_results)} 通过")

print(f"\n{'─'*70}")
print("按难度统计:")
for d in range(1, 6):
    d_results = [r for r in results if r.get("difficulty") == d]
    d_passed = [r for r in d_results if r["status"] == "✓"]
    if d_results:
        print(f"  难度 {d}: {len(d_passed)}/{len(d_results)} 通过")

# 退出码：有失败则返回 1，支持 CI 集成
if failed:
    print(f"\n❌ {len(failed)} 项测试失败")
    sys.exit(1)
else:
    print(f"\n✅ 全部 {total} 种题型测试通过")
    sys.exit(0)
