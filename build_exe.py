"""
构建 .exe 可执行文件
Build executable using PyInstaller

用法：
  pip install pyinstaller
  python build_exe.py

输出：
  dist/geometry-generator/geometry-generator (Linux)
  dist/geometry-generator/geometry-generator.exe (Windows)
"""

import subprocess
import sys
import os

def build():
    """构建可执行文件"""
    print("=" * 60)
    print("  解析几何题目生成器 — 构建 .exe")
    print("=" * 60)

    # PyInstaller 参数
    args = [
        sys.executable, "-m", "PyInstaller",
        "--name=geometry-generator",
        "--onefile",                    # 单文件打包
        "--console",                    # 保留终端（TUI应用）
        "--clean",                      # 清理缓存
        "--noconfirm",                  # 不确认覆盖
        # 包含数据文件
        "--add-data=problem_generator.py:.",
        "--add-data=interactive_generator.py:.",
        "--add-data=diagram_renderer.py:.",
        "--add-data=tui_app.py:.",
        # 隐含导入
        "--hidden-import=numpy",
        "--hidden-import=matplotlib",
        "--hidden-import=textual",
        "--hidden-import=rich",
        # 排除不需要的模块（减小体积）
        "--exclude-module=tkinter",
        "--exclude-module=PyQt5",
        "--exclude-module=PyQt6",
        # 图标（可选）
        # "--icon=icon.ico",
        # 入口脚本
        "tui_app.py",
    ]

    print("\n执行命令:")
    print(" ".join(args))
    print("\n构建中...")

    result = subprocess.run(args, cwd=os.path.dirname(os.path.abspath(__file__)))

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("  ✓ 构建成功！")
        print("=" * 60)
        print(f"\n  可执行文件位置:")
        if sys.platform == "win32":
            print(f"    dist\\geometry-generator\\geometry-generator.exe")
        else:
            print(f"    dist/geometry-generator/geometry-generator")
        print(f"\n  运行方式:")
        if sys.platform == "win32":
            print(f"    dist\\geometry-generator\\geometry-generator.exe")
        else:
            print(f"    ./dist/geometry-generator/geometry-generator")
    else:
        print("\n  ✗ 构建失败！")
        sys.exit(1)


if __name__ == "__main__":
    build()
