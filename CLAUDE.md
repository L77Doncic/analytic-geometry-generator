# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

解析几何题目生成系统 — a Python tool that auto-generates solvable analytic geometry problems (ellipse, hyperbola, parabola, polar coordinates) with precise Matplotlib diagrams, LaTeX solutions, and a Textual TUI interface. Targets Chinese high school and competition-level math (高考 / 竞赛).

## Commands

```bash
# Install dependencies
pip install numpy matplotlib textual rich python-pptx

# Launch TUI (default mode)
python3 run.py

# CLI mode — generate a specific problem
python3 run.py --cli --topic ellipse --a 5 --b 3

# Interactive mode (guided prompts)
python3 run.py --interactive

# Batch generation (all topics × all difficulties, generates PPT)
python3 main.py

# Run all 53 problem types test
python3 test_all_types.py

# Build standalone executable
pip install pyinstaller
python3 build_exe.py
```

## Architecture

The system has two parallel generation paths that share the same data model:

**Path 1 — Static templates** (`problem_generator.py`):
- `ProblemGenerator.generate(topic, difficulty)` dispatches to 12 fixed templates (4 topics × 3 difficulties)
- Used by `main.py` for batch generation

**Path 2 — Dynamic generation** (`interactive_generator.py`):
- `generate_*_dynamic(problem_type=..., a=..., b=..., ...)` supports ~53 problem types with user-specified parameters
- Entry functions: `generate_ellipse_dynamic()`, `generate_hyperbola_dynamic()`, `generate_parabola_dynamic()`, `generate_polar_dynamic()`
- Used by TUI and CLI modes

**Shared data model** (defined in `problem_generator.py`):
- `Problem` — title, topic, difficulty, problem_latex, solution_latex, conic_params, points, lines, conic_type, answer
- `ConicParams` — center, a, b, c, e, rotation (auto-computes c and e from a, b)
- `Point` — x, y, label
- `Line` — a, b, c (ax + by + c = 0 form), with distance_to_point(), slope()

**Rendering pipeline**:
1. `DiagramRenderer` (`diagram_renderer.py`) — Matplotlib parametric plots, 1000 sample points, equal-aspect axes, Chinese font auto-detection
2. `latex_render.py` — LaTeX → Unicode for terminal (fractions → x²/25, sqrt → √, Greek → α β θ)
3. `tui_app.py` — Textual TUI with draggable split pane, chat-style input, sidebar with commands
4. `create_ppt.py` — python-pptx presentation generation (Claude Design System colors)

**Output**: Each generation creates `output/Question_YYYYMMDD_HHMMSS/` with `diagram.png`, `problem.tex`, `solution.tex`, `problem.txt`.

## Problem Types Reference

Each conic section supports basic → intermediate → competition difficulty levels. The `problem_type` string keys used by `generate_*_dynamic()`:

| Topic | Types |
|-------|-------|
| Ellipse | basic, chord, focus_triangle, midpoint_chord, focal_radius, slope_product, tangent_line, second_def, fixed_point, area_opt, ecc_range, tangent, third_def, optical_property, locus |
| Hyperbola | basic, chord, focus_triangle, midpoint_chord, focal_radius, second_def, tangent_line, slope_product, asymptote_angle, area_opt, ecc_range, tangent, optical_property, locus, equilateral_hyperbola |
| Parabola | basic, chord, midpoint_chord, focal_radius, tangent_line, second_def, slope_product, property, archimedes, fixed_point, ecc_range, optical_property, locus |
| Polar | basic, line_circle, focal_radius, chord_ratio, slope_product, fixed_point, conic, second_def, area_opt, conic_unified |

## Adding New Problem Types — Checklist

When adding a new problem type, the following files must be updated. **All steps marked REQUIRED** must be completed for the new type to work end-to-end.

### 1. `interactive_generator.py` — Core implementation (REQUIRED)

**a) Add the problem generation function:**
```python
def _ellipse_new_type(a, b, c, e, params):
    """椭圆新题型 — 简要描述"""
    # 1. 构造关键点 (F1, F2, P, Q, ...)
    # 2. 构造关键直线 (弦, 切线, 渐近线, ...)
    # 3. 数学推导 (联立方程, 韦达定理, 面积公式, ...)
    # 4. 生成 problem_latex (LaTeX 题干)
    # 5. 生成 solution_latex (LaTeX 解答)
    # 6. 计算 answer
    return Problem(title=..., topic=..., difficulty=..., ...)
```

**b) Register in the dispatcher** — Add `elif` branch in the corresponding `generate_*_dynamic()` function:
```python
elif problem_type == "new_type":
    return _ellipse_new_type(a, b, c, e, params)
```

**c) (Optional) Update `interactive_mode()`** — If the type should appear in the interactive menu, add it to the `type_map` dictionary.

### 2. `test_all_types.py` — Test coverage (REQUIRED)

Add the new type string to the `ALL_TYPES` dictionary under the corresponding topic:
```python
"椭圆": {
    "gen": generate_ellipse_dynamic,
    "args": {"a": 5, "b": 3},
    "types": [
        "basic", "chord", ..., "new_type",  # ← add here
    ]
},
```

Then run `python3 test_all_types.py` to verify all types pass.

### 3. `tui_app.py` — TUI (REQUIRED — 4 places)

**a) `type_map` dictionary (~line 128)** — Add Chinese keyword → problem_type mappings:
```python
type_map = {
    ...
    "新题型关键词": "new_type", "new_type": "new_type",
}
```

**b) `hard_types` or `mid_types` dictionary (~line 179/190)** — Add to the appropriate difficulty level for random selection:
```python
# 竞赛/压轴难度
hard_types = {
    "ellipse": ["fixed_point", "area_opt", ..., "new_type"],  # ← add here
    ...
}
# 进阶难度
mid_types = {
    "ellipse": ["chord", "focus_triangle", ..., "new_type"],  # ← add here
    ...
}
```

**c) Sidebar help text (~line 385)** — Add the new type to the sidebar display list:
```python
yield Static("  ── 竞赛/压轴 ──", classes="muted")
yield Static("  new_type — 新题型描述", classes="help-item")  # ← add here
```

**d) `_show_help()` method (~line 631)** — Add the new type to the Ctrl+H help page:
```python
    ── 竞赛/压轴题型 ──
      new_type     新题型描述（适用知识点）  # ← add here
```

### 4. `CLAUDE.md` — This file (REQUIRED)

Update the Problem Types Reference table above to include the new type.

### 5. `docs/technical-docs.md` — Technical documentation (REQUIRED)

Update the type coverage table in the documentation to include the new type:
```markdown
| **椭圆** | 标准方程、焦点 | 焦点弦、中点弦 | 定点证明、面积最值、新题型 |
```

### 6. `problem_generator.py` — Data model (RARELY NEEDED)

Only update if the new problem type requires:
- New fields in `Problem`, `ConicParams`, `Point`, or `Line`
- New helper methods (e.g., a new geometric computation)

The existing data model covers most cases. Check if `Point`, `Line`, `ConicParams` already support your needs before modifying.

### 7. `diagram_renderer.py` — Rendering (RARELY NEEDED)

Only update if the new problem type introduces:
- A new curve type not yet supported (e.g., a new conic variant)
- New visual elements (e.g., a new type of annotation or marker)

The existing renderer handles ellipses, hyperbolas, parabolas, polar circles, lines, and points. Most new problem types reuse these primitives.

### Summary Table

| File | When to update | Effort |
|------|---------------|--------|
| `interactive_generator.py` (function) | **Always** | High — math derivation + LaTeX |
| `interactive_generator.py` (dispatcher) | **Always** | Low — add one `elif` |
| `test_all_types.py` | **Always** | Low — add one string |
| `tui_app.py` (type_map) | **Always** | Low — add keyword mapping |
| `tui_app.py` (hard_types/mid_types) | **Always** | Low — add to difficulty list |
| `tui_app.py` (sidebar help) | **Always** | Low — add one line |
| `tui_app.py` (Ctrl+H help page) | **Always** | Low — add one line |
| `CLAUDE.md` | **Always** | Low — add table row |
| `docs/technical-docs.md` | **Always** | Low — update coverage table |
| `problem_generator.py` | Only if new data model | Medium |
| `diagram_renderer.py` | Only if new curve type | Medium |

## Key Conventions

- All math text is stored as LaTeX strings internally; rendered to Unicode only for terminal display
- Ellipse requires a > b; hyperbola uses c = √(a² + b²); parabola uses y² = 2px form
- Random seed can be passed to `ProblemGenerator(seed=N)` for reproducible generation
- The TUI parser (`parse_user_input` in `tui_app.py`) recognizes Chinese keywords: 椭圆/双曲线/抛物线/极坐标, difficulty shortcuts: 基础/进阶/竞赛/压轴/难
- Matplotlib uses `Agg` backend (non-interactive) — always saves to file, never displays
- Output directory defaults to `/root/analytic_geometry_generator/output`
