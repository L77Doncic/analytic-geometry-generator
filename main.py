"""
解析几何题目生成系统 - 主程序
Analytic Geometry Problem Generator - Main Entry Point

运行方式：
    python3 main.py

功能：
1. 生成所有类型的解析几何题目
2. 渲染精确配图
3. 输出LaTeX格式的题干和解答
"""

import os
import sys
from datetime import datetime

from problem_generator import ProblemGenerator, Problem
from diagram_renderer import DiagramRenderer
from latex_render import render_problem_text


def print_separator(char: str = "=", length: int = 70):
    """打印分隔线"""
    print(char * length)


def print_problem(problem: Problem, show_solution: bool = False):
    """打印题目信息"""
    print_separator()
    print(f"【{problem.title}】")
    print(f"知识点: {problem.topic} | 难度: {'★' * problem.difficulty}{'☆' * (3 - problem.difficulty)}")
    print_separator("-")
    print("\n【题干】")
    print(problem.problem_latex)

    if show_solution:
        print("\n【解答】")
        print(problem.solution_latex)

    print(f"\n【答案】{problem.answer}")
    print()


def generate_all_problems(generator: ProblemGenerator, renderer: DiagramRenderer,
                          output_dir: str, show_solution: bool = False):
    """生成所有类型的题目并渲染配图"""
    topics = ["ellipse", "hyperbola", "parabola", "polar"]
    topic_names = {
        "ellipse": "椭圆",
        "hyperbola": "双曲线",
        "parabola": "抛物线",
        "polar": "极坐标"
    }
    difficulties = [1, 2, 3]
    difficulty_names = {1: "基础", 2: "进阶", 3: "竞赛"}

    all_problems = []

    print("\n" + "=" * 70)
    print("解析几何题目生成系统")
    print("=" * 70)
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"输出目录: {output_dir}")
    print("=" * 70)

    for topic in topics:
        print(f"\n\n{'#' * 70}")
        print(f"# 知识点: {topic_names[topic]}")
        print(f"{'#' * 70}")

        for diff in difficulties:
            print(f"\n>>> 正在生成 {topic_names[topic]} - {difficulty_names[diff]} 题目...")

            # 生成题目
            problem = generator.generate(topic, diff)
            all_problems.append(problem)

            # 打印题目
            print_problem(problem, show_solution)

            # 渲染配图
            img_path = os.path.join(output_dir, f"{topic_names[topic]}_difficulty{diff}.png")
            renderer.render(problem, img_path)

            # 保存 LaTeX 题干
            tex_path = os.path.join(output_dir, f"{topic_names[topic]}_difficulty{diff}.tex")
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(f"% {problem.title}\n\n")
                f.write(problem.problem_latex)

            # 保存 LaTeX 解答
            sol_path = os.path.join(output_dir, f"{topic_names[topic]}_difficulty{diff}_solution.tex")
            with open(sol_path, "w", encoding="utf-8") as f:
                f.write(f"% {problem.title} — 解答\n\n")
                f.write(problem.solution_latex)

            # 保存纯文本版
            txt_path = os.path.join(output_dir, f"{topic_names[topic]}_difficulty{diff}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"{'='*50}\n")
                f.write(f"{problem.title}\n")
                f.write(f"{'='*50}\n\n")
                f.write(render_problem_text(problem.problem_latex))
                f.write(f"\n\n{'─'*50}\n\n")
                f.write(render_problem_text(problem.solution_latex))

            print(f"✓ 配图+文字已保存: {img_path}")

    return all_problems


def main():
    """主函数"""
    # 配置
    base_dir = "/root/analytic_geometry_generator/output"
    timestamp = datetime.now().strftime("Question_%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_dir, timestamp)
    seed = 42  # 随机种子，保证可复现
    show_solution = True  # 是否显示解答

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 初始化组件
    print("正在初始化系统...")
    generator = ProblemGenerator(seed=seed)
    renderer = DiagramRenderer(figsize=(10, 8), dpi=150)

    # 生成所有题目
    problems = generate_all_problems(generator, renderer, output_dir, show_solution)

    # 统计信息
    print("\n\n" + "=" * 70)
    print("生成统计")
    print("=" * 70)
    print(f"总题目数: {len(problems)}")
    print(f"  - 椭圆题目: 3 (基础/进阶/竞赛)")
    print(f"  - 双曲线题目: 3 (基础/进阶/竞赛)")
    print(f"  - 抛物线题目: 3 (基础/进阶/竞赛)")
    print(f"  - 极坐标题目: 3 (基础/进阶/竞赛)")
    print(f"配图数量: {len(problems)}")
    print(f"\n输出目录: {output_dir}")
    print("=" * 70)

    # 列出所有输出文件
    print("\n输出文件列表:")
    for f in sorted(os.listdir(output_dir)):
        filepath = os.path.join(output_dir, f)
        size_kb = os.path.getsize(filepath) / 1024
        print(f"  - {f} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
