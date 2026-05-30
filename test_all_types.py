"""
全面测试所有 53 种题型的生成能力
测试项：题目生成、LaTeX渲染、配图渲染、答案完整性
"""

import sys
import os
import traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interactive_generator import (
    generate_ellipse_dynamic, generate_hyperbola_dynamic,
    generate_parabola_dynamic, generate_polar_dynamic
)
from diagram_renderer import DiagramRenderer
from latex_render import render_problem_text

OUTPUT_DIR = "/root/analytic_geometry_generator/output/test"
os.makedirs(OUTPUT_DIR, exist_ok=True)

renderer = DiagramRenderer(figsize=(10, 8), dpi=100)

# 定义所有题型
ALL_TYPES = {
    "椭圆": {
        "gen": generate_ellipse_dynamic,
        "args": {"a": 5, "b": 3},
        "types": [
            "basic", "chord", "focus_triangle",
            "midpoint_chord", "focal_radius", "slope_product", "tangent_line", "second_def",
            "fixed_point", "area_opt", "ecc_range", "tangent", "third_def",
            "optical_property", "locus",
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
        ]
    },
}

results = []
total = sum(len(v["types"]) for v in ALL_TYPES.values())
current = 0

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
            assert problem.problem_latex, f"题干为空"
            assert len(problem.problem_latex) > 20, f"题干过短 ({len(problem.problem_latex)} chars)"

            # 3. 验证解答
            assert problem.solution_latex, f"解答为空"
            assert len(problem.solution_latex) > 20, f"解答过短"

            # 4. 验证答案
            assert problem.answer, f"答案为空"

            # 5. LaTeX渲染
            rendered = render_problem_text(problem.problem_latex)
            assert rendered, f"LaTeX渲染失败"

            # 6. 配图渲染
            img_path = os.path.join(OUTPUT_DIR, f"{topic}_{ptype}.png")
            renderer.render(problem, img_path)
            assert os.path.exists(img_path), f"配图文件未生成"
            assert os.path.getsize(img_path) > 1000, f"配图文件过小 ({os.path.getsize(img_path)} bytes)"

            # 7. 验证关键点
            assert len(problem.points) > 0, f"无关键点"

            results.append({
                "topic": topic, "type": ptype, "status": "✓",
                "difficulty": problem.difficulty,
                "title": problem.title,
                "points": len(problem.points),
                "img_size": os.path.getsize(img_path),
            })
            print(f"  ✓ {label} — {problem.title} (d={problem.difficulty}, {len(problem.points)}点, {os.path.getsize(img_path)//1024}KB)")

        except Exception as e:
            results.append({
                "topic": topic, "type": ptype, "status": "✗",
                "error": str(e),
                "traceback": traceback.format_exc(),
            })
            print(f"  ✗ {label} — ERROR: {e}")

# 生成报告
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
