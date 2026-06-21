"""
解析几何精确配图渲染器
Analytic Geometry Diagram Renderer

使用 Matplotlib 渲染精确的几何图形，所有关键点、直线、曲线的位置
与题干数学参数严格一致。
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
from typing import List, Tuple, Optional
import os

from problem_generator import Problem, Point, Line, ConicParams


class DiagramRenderer:
    """解析几何配图渲染器"""

    # 配色方案
    COLORS = {
        'curve': '#2E86AB',      # 曲线颜色 (蓝色)
        'line': '#E8451E',       # 直线颜色 (红色)
        'point': '#2E86AB',      # 点颜色
        'point_fill': '#FFD700', # 点填充颜色 (金色)
        'focus': '#E8451E',      # 焦点颜色
        'focus_fill': '#FFD700', # 焦点填充
        'label': '#333333',      # 标签颜色
        'grid': '#E0E0E0',       # 网格颜色
        'axis': '#666666',       # 坐标轴颜色
        'fill': '#E8F4FD',       # 填充颜色
        'asymptote': '#9B59B6',  # 渐近线颜色 (紫色)
        'directrix': '#27AE60',  # 准线颜色 (绿色)
        'tangent': '#F39C12',    # 切线颜色 (橙色)
    }

    def __init__(self, figsize: Tuple[float, float] = (8, 6), dpi: int = 150):
        self.figsize = figsize
        self.dpi = dpi
        self._setup_chinese_font()

    def _setup_chinese_font(self):
        """设置中文字体支持"""
        # 尝试使用系统中可用的中文字体
        font_candidates = [
            'WenQuanYi Micro Hei',
            'WenQuanYi Zen Hei',
            'Noto Sans CJK SC',
            'SimHei',
            'Microsoft YaHei',
            'DejaVu Sans',
        ]

        for font_name in font_candidates:
            try:
                matplotlib.rcParams['font.sans-serif'] = [font_name] + matplotlib.rcParams['font.sans-serif']
                matplotlib.rcParams['axes.unicode_minus'] = False
                # 测试字体是否可用
                fig, ax = plt.subplots(1, 1, figsize=(1, 1))
                ax.set_title('测试')
                plt.close(fig)
                return
            except Exception:
                continue

    def _setup_figure(self, x_range: Tuple[float, float] = (-6, 6),
                      y_range: Tuple[float, float] = (-6, 6)) -> Tuple[plt.Figure, plt.Axes]:
        """设置图形"""
        fig, ax = plt.subplots(1, 1, figsize=self.figsize, dpi=self.dpi)

        # 设置坐标轴范围
        x_margin = (x_range[1] - x_range[0]) * 0.15
        y_margin = (y_range[1] - y_range[0]) * 0.15
        ax.set_xlim(x_range[0] - x_margin, x_range[1] + x_margin)
        ax.set_ylim(y_range[0] - y_margin, y_range[1] + y_margin)

        # 绘制网格
        ax.grid(True, linestyle='-', alpha=0.3, color=self.COLORS['grid'], linewidth=0.5)

        # 绘制坐标轴
        ax.axhline(y=0, color=self.COLORS['axis'], linewidth=1.2, zorder=2)
        ax.axvline(x=0, color=self.COLORS['axis'], linewidth=1.2, zorder=2)

        # 添加箭头
        arrow_kwargs = dict(
            arrowstyle='->',
            color=self.COLORS['axis'],
            linewidth=1.5,
            mutation_scale=15
        )

        # x轴箭头
        ax.annotate('', xy=(x_range[1] + x_margin * 0.8, 0),
                    xytext=(x_range[1] + x_margin * 0.3, 0),
                    arrowprops=arrow_kwargs)
        # y轴箭头
        ax.annotate('', xy=(0, y_range[1] + y_margin * 0.8),
                    xytext=(0, y_range[1] + y_margin * 0.3),
                    arrowprops=arrow_kwargs)

        # 轴标签
        label_offset_x = x_margin * 0.15
        label_offset_y = y_margin * 0.15
        ax.text(x_range[1] + x_margin * 0.85, -label_offset_y, '$x$',
                fontsize=12, ha='center', va='center', color=self.COLORS['axis'])
        ax.text(-label_offset_x, y_range[1] + y_margin * 0.85, '$y$',
                fontsize=12, ha='center', va='center', color=self.COLORS['axis'])

        # 原点
        ax.text(-label_offset_x * 1.5, -label_offset_y * 1.5, '$O$',
                fontsize=11, ha='center', va='center', color=self.COLORS['label'])

        # 刻度
        ax.set_xticks(range(int(x_range[0]), int(x_range[1]) + 1))
        ax.set_yticks(range(int(y_range[0]), int(y_range[1]) + 1))
        ax.tick_params(labelsize=8, colors=self.COLORS['axis'])

        # 等比例显示
        ax.set_aspect('equal')

        return fig, ax

    def _plot_point(self, ax: plt.Axes, point: Point,
                    color: str = None, fill_color: str = None,
                    size: float = 50, zorder: int = 10,
                    label_offset: Tuple[float, float] = (0.15, 0.15)):
        """绘制点"""
        if color is None:
            color = self.COLORS['point']
        if fill_color is None:
            fill_color = self.COLORS['point_fill']

        # 焦点特殊处理 — 标签以 F 开头且第二位是数字或下标
        if point.label and point.label.startswith('F') and (
                len(point.label) == 1 or point.label[1] in '0123456789_'):
            color = self.COLORS['focus']
            fill_color = self.COLORS['focus_fill']

        ax.scatter(point.x, point.y, c=fill_color, s=size,
                   edgecolors=color, linewidths=1.5, zorder=zorder)

        # 标注标签
        if point.label:
            label = f'${point.label}$'
            ax.text(point.x + label_offset[0], point.y + label_offset[1],
                    label, fontsize=11, color=self.COLORS['label'],
                    ha='left', va='bottom', zorder=zorder + 1)

    def _plot_line(self, ax: plt.Axes, line: Line,
                   x_range: Tuple[float, float],
                   color: str = None, linewidth: float = 1.5,
                   linestyle: str = '-', alpha: float = 0.8,
                   zorder: int = 5, extend: bool = True):
        """绘制直线"""
        if color is None:
            color = self.COLORS['line']

        if extend:
            x = np.linspace(x_range[0] - 2, x_range[1] + 2, 500)
        else:
            x = np.linspace(x_range[0], x_range[1], 500)

        if line.b != 0:
            y = (-line.a * x - line.c) / line.b
        else:
            # 垂直线
            x_val = -line.c / line.a if line.a != 0 else 0
            ax.axvline(x=x_val, color=color, linewidth=linewidth,
                       linestyle=linestyle, alpha=alpha, zorder=zorder)
            return

        ax.plot(x, y, color=color, linewidth=linewidth,
                linestyle=linestyle, alpha=alpha, zorder=zorder)

    def _plot_ellipse(self, ax: plt.Axes, params: ConicParams,
                      color: str = None, linewidth: float = 2,
                      fill: bool = False, alpha: float = 0.9, zorder: int = 3):
        """绘制椭圆"""
        if color is None:
            color = self.COLORS['curve']

        theta = np.linspace(0, 2 * np.pi, 1000)
        x = params.center[0] + params.a * np.cos(theta)
        y = params.center[1] + params.b * np.sin(theta)

        if fill:
            ax.fill(x, y, color=self.COLORS['fill'], alpha=0.3, zorder=zorder - 1)

        ax.plot(x, y, color=color, linewidth=linewidth, alpha=alpha, zorder=zorder)

    def _plot_hyperbola(self, ax: plt.Axes, params: ConicParams,
                        color: str = None, linewidth: float = 2,
                        x_range: Tuple[float, float] = (-10, 10),
                        alpha: float = 0.9, zorder: int = 3):
        """绘制双曲线"""
        if color is None:
            color = self.COLORS['curve']

        cx, cy = params.center

        # 右支
        x_right = np.linspace(params.a, x_range[1] + 2, 500)
        y_right_pos = params.b * np.sqrt((x_right / params.a)**2 - 1)
        y_right_neg = -y_right_pos

        # 左支
        x_left = np.linspace(x_range[0] - 2, -params.a, 500)
        y_left_pos = params.b * np.sqrt((x_left / params.a)**2 - 1)
        y_left_neg = -y_left_pos

        ax.plot(cx + x_right, cy + y_right_pos, color=color, linewidth=linewidth,
                alpha=alpha, zorder=zorder)
        ax.plot(cx + x_right, cy + y_right_neg, color=color, linewidth=linewidth,
                alpha=alpha, zorder=zorder)
        ax.plot(cx + x_left, cy + y_left_pos, color=color, linewidth=linewidth,
                alpha=alpha, zorder=zorder)
        ax.plot(cx + x_left, cy + y_left_neg, color=color, linewidth=linewidth,
                alpha=alpha, zorder=zorder)

    def _plot_hyperbola_asymptotes(self, ax: plt.Axes, params: ConicParams,
                                   x_range: Tuple[float, float] = (-10, 10),
                                   linewidth: float = 1.2, alpha: float = 0.6):
        """绘制双曲线渐近线"""
        cx, cy = params.center
        slope = params.b / params.a
        x = np.linspace(x_range[0] - 2, x_range[1] + 2, 200)
        y1 = slope * (x - cx) + cy
        y2 = -slope * (x - cx) + cy

        ax.plot(x, y1, color=self.COLORS['asymptote'], linewidth=linewidth,
                linestyle='--', alpha=alpha, zorder=2, label='渐近线')
        ax.plot(x, y2, color=self.COLORS['asymptote'], linewidth=linewidth,
                linestyle='--', alpha=alpha, zorder=2)

    def _plot_parabola(self, ax: plt.Axes, params: ConicParams,
                       color: str = None, linewidth: float = 2,
                       y_range: Tuple[float, float] = (-6, 6),
                       alpha: float = 0.9, zorder: int = 3):
        """绘制抛物线 y² = 2px (p = 2a)"""
        if color is None:
            color = self.COLORS['curve']

        cx, cy = params.center
        p = 2 * params.a  # y² = 2px

        # 上半支
        y_upper = np.linspace(y_range[0] - 2, y_range[1] + 2, 500)
        x_upper = y_upper**2 / (2 * p)

        # 过滤掉太远的点
        mask = x_upper <= max(abs(y_range[0]), abs(y_range[1])) * 2
        ax.plot(cx + x_upper[mask], cy + y_upper[mask], color=color, linewidth=linewidth,
                alpha=alpha, zorder=zorder)

    def _plot_polar_circle(self, ax: plt.Axes, r: float,
                           color: str = None, linewidth: float = 2,
                           alpha: float = 0.9, zorder: int = 3):
        """绘制极坐标圆 ρ = 2r·cosθ"""
        if color is None:
            color = self.COLORS['curve']

        theta = np.linspace(-np.pi / 2, np.pi / 2, 500)
        rho = 2 * r * np.cos(theta)
        x = rho * np.cos(theta)
        y = rho * np.sin(theta)

        ax.plot(x, y, color=color, linewidth=linewidth, alpha=alpha, zorder=zorder)

    def render(self, problem: Problem, output_path: str = None) -> str:
        """
        渲染题目配图

        Args:
            problem: Problem 对象
            output_path: 输出路径，None 则自动生成

        Returns:
            保存的文件路径
        """
        # 根据题目类型确定坐标范围
        x_range, y_range = self._get_plot_range(problem)

        fig, ax = self._setup_figure(x_range, y_range)

        # 绘制曲线
        if problem.conic_type == "ellipse":
            self._plot_ellipse(ax, problem.conic_params, fill=True)
        elif problem.conic_type == "hyperbola":
            self._plot_hyperbola(ax, problem.conic_params, x_range=x_range)
            self._plot_hyperbola_asymptotes(ax, problem.conic_params, x_range=x_range)
        elif problem.conic_type == "parabola":
            self._plot_parabola(ax, problem.conic_params, y_range=y_range)
        elif problem.conic_type == "polar":
            self._plot_polar_circle(ax, problem.conic_params.a)

        # 绘制直线
        for line in problem.lines:
            line_color = self.COLORS['line']
            line_style = '-'
            if 'asymptote' in line.label.lower() or '渐近' in line.label:
                line_color = self.COLORS['asymptote']
                line_style = '--'
            elif 'directrix' in line.label.lower() or '准线' in line.label:
                line_color = self.COLORS['directrix']
                line_style = '-.'
            self._plot_line(ax, line, x_range, color=line_color, linestyle=line_style)

        # 绘制点
        for point in problem.points:
            self._plot_point(ax, point)

        # 添加标题
        ax.set_title(problem.title, fontsize=14, fontweight='bold',
                     color=self.COLORS['label'], pad=15)

        # 保存
        if output_path is None:
            _project_root = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(_project_root, "output",
                                       f"{problem.topic}_difficulty{problem.difficulty}.png")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=self.dpi, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)

        return output_path

    def _get_plot_range(self, problem: Problem) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """根据题目参数确定合适的坐标范围"""
        params = problem.conic_params
        margin = 2

        cx, cy = params.center

        if problem.conic_type == "ellipse":
            x_range = (cx - params.a - margin, cx + params.a + margin)
            y_range = (cy - params.b - margin, cy + params.b + margin)
        elif problem.conic_type == "hyperbola":
            x_range = (cx - params.c - margin, cx + params.c + margin)
            y_range = (cy - params.b - margin * 2, cy + params.b + margin * 2)
        elif problem.conic_type == "parabola":
            x_range = (cx - margin, cx + params.a * 4 + margin)
            y_range = (cy - params.a * 3 - margin, cy + params.a * 3 + margin)
        elif problem.conic_type == "polar":
            r = params.a
            x_range = (-margin, 2 * r + margin)
            y_range = (-r - margin, r + margin)
        else:
            x_range = (-8, 8)
            y_range = (-6, 6)

        # 确保所有点在范围内
        for point in problem.points:
            x_range = (min(x_range[0], point.x - margin),
                       max(x_range[1], point.x + margin))
            y_range = (min(y_range[0], point.y - margin),
                       max(y_range[1], point.y + margin))

        # 确保正方形比例
        x_span = x_range[1] - x_range[0]
        y_span = y_range[1] - y_range[0]
        max_span = max(x_span, y_span)

        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2

        x_range = (x_center - max_span / 2, x_center + max_span / 2)
        y_range = (y_center - max_span / 2, y_center + max_span / 2)

        return x_range, y_range


def main():
    """测试渲染器"""
    from problem_generator import ProblemGenerator

    generator = ProblemGenerator(seed=42)
    renderer = DiagramRenderer(figsize=(10, 8), dpi=150)

    topics = ["ellipse", "hyperbola", "parabola", "polar"]
    difficulties = [1, 2, 3]

    print("开始渲染所有题目配图...")

    for topic in topics:
        for diff in difficulties:
            problem = generator.generate(topic, diff)
            path = renderer.render(problem)
            print(f"✓ 已生成: {path}")

    print("\n所有配图渲染完成！")


if __name__ == "__main__":
    main()
