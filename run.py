#!/usr/bin/env python3
"""
解析几何题目生成器 — 统一入口
Analytic Geometry Generator — Entry Point

用法：
  # 启动 TUI 交互界面（默认）
  python3 run.py

  # 命令行模式 — 生成指定题目
  python3 run.py --cli --topic ellipse --a 5 --b 3

  # 交互式模式 — 命令行引导输入
  python3 run.py --interactive
"""

import sys
import os
import argparse

# 确保当前目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(
        description="解析几何题目生成器 — 支持 TUI、CLI、交互式三种模式"
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--cli", action="store_true",
                            help="命令行模式，需配合 --topic, --a, --b 等参数")
    mode_group.add_argument("--interactive", action="store_true",
                            help="交互式模式，命令行引导输入参数")

    # 透传给 interactive_generator.main 的参数
    parser.add_argument("--topic", type=str, help="题目类型: ellipse/hyperbola/parabola/polar")
    parser.add_argument("--type", type=str, dest="problem_type", help="具体题型，如 basic, chord 等")
    parser.add_argument("--a", type=float, help="半长轴/半实轴 a")
    parser.add_argument("--b", type=float, help="半短轴/半虚轴 b")

    args, remaining = parser.parse_known_args()

    if args.cli:
        # 命令行模式：重组 argv 传给 interactive_generator.main
        from interactive_generator import main as cli_main
        new_argv = [sys.argv[0]]
        if args.topic:
            new_argv += ["--topic", args.topic]
        if args.problem_type:
            new_argv += ["--type", args.problem_type]
        if args.a is not None:
            new_argv += ["--a", str(args.a)]
        if args.b is not None:
            new_argv += ["--b", str(args.b)]
        new_argv += remaining
        sys.argv = new_argv
        cli_main()
    elif args.interactive:
        # 交互式模式
        from interactive_generator import interactive_mode
        interactive_mode()
    else:
        # TUI 模式（默认）
        from tui_app import GeometryTUI
        app = GeometryTUI()
        app.run()


if __name__ == "__main__":
    main()
