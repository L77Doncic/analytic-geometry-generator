#!/usr/bin/env python3
"""
解析几何题目生成器 — 统一入口
Analytic Geometry Generator — Entry Point

用法：
  # 启动 TUI 交互界面
  python3 run.py

  # 命令行模式
  python3 run.py --cli --topic ellipse --a 5 --b 3

  # 交互式模式
  python3 run.py --interactive
"""

import sys
import os

# 确保当前目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # 命令行模式
        from interactive_generator import main as cli_main
        sys.argv = sys.argv[:1] + sys.argv[2:]  # 移除 --cli
        cli_main()
    elif len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # 交互式模式
        from interactive_generator import interactive_mode, main as cli_main
        sys.argv = [sys.argv[0]]
        cli_main()
    else:
        # TUI 模式（默认）
        from tui_app import GeometryTUI
        app = GeometryTUI()
        app.run()


if __name__ == "__main__":
    main()
