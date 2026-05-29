r"""
LaTeX → Unicode 数学符号渲染器
Renders LaTeX math expressions as Unicode symbols for terminal display.

支持：
- 分数 \frac{a}{b} → a/b
- 上标 x^{2} → x²
- 下标 x_{1} → x₁
- 希腊字母 \alpha → α
- 数学运算符 \times → ×, \pm → ±
- 根号 \sqrt{x} → √x
- 求和/积分 \sum → Σ, \int → ∫
- 括号 \left( \right) → ( )
- 三角函数 \sin → sin
- 移除 $ 和 $$ 定界符
"""

import re
from typing import List


# ==================== 映射表 ====================

GREEK_MAP = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\epsilon": "ε", r"\zeta": "ζ", r"\eta": "η", r"\theta": "θ",
    r"\iota": "ι", r"\kappa": "κ", r"\lambda": "λ", r"\mu": "μ",
    r"\nu": "ν", r"\xi": "ξ", r"\pi": "π", r"\rho": "ρ",
    r"\sigma": "σ", r"\tau": "τ", r"\upsilon": "υ", r"\phi": "φ",
    r"\chi": "χ", r"\psi": "ψ", r"\omega": "ω",
    r"\Alpha": "Α", r"\Beta": "Β", r"\Gamma": "Γ", r"\Delta": "Δ",
    r"\Theta": "Θ", r"\Lambda": "Λ", r"\Xi": "Ξ", r"\Pi": "Π",
    r"\Sigma": "Σ", r"\Phi": "Φ", r"\Psi": "Ψ", r"\Omega": "Ω",
}

OPERATOR_MAP = {
    r"\times": "×", r"\cdot": "·", r"\div": "÷",
    r"\pm": "±", r"\mp": "∓",
    r"\leq": "≤", r"\geq": "≥", r"\neq": "≠",
    r"\approx": "≈", r"\equiv": "≡",
    r"\infty": "∞",
    r"\sum": "∑", r"\prod": "∏", r"\int": "∫",
    r"\partial": "∂", r"\nabla": "∇",
    r"\rightarrow": "→", r"\leftarrow": "←",
    r"\Rightarrow": "⇒", r"\Leftarrow": "⇐",
    r"\leftrightarrow": "↔",
    r"\forall": "∀", r"\exists": "∃",
    r"\in": "∈", r"\notin": "∉",
    r"\subset": "⊂", r"\supset": "⊃",
    r"\cup": "∪", r"\cap": "∩",
    r"\emptyset": "∅",
    r"\ldots": "…", r"\cdots": "⋯",
    r"\triangle": "△",
    r"\circ": "°",
    r"\star": "★",
    r"\diamond": "◇",
}

SUPERSCRIPT_MAP = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾",
    "n": "ⁿ", "i": "ⁱ",
}

SUBSCRIPT_MAP = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎",
    "a": "ₐ", "e": "ₑ", "o": "ₒ", "x": "ₓ",
}

FUNCTION_NAMES = [
    "sin", "cos", "tan", "cot", "sec", "csc",
    "arcsin", "arccos", "arctan",
    "sinh", "cosh", "tanh",
    "log", "ln", "exp", "lim",
]


# ==================== 核心转换器 ====================

def latex_to_unicode(text: str) -> str:
    """
    将 LaTeX 数学表达式转换为 Unicode 终端显示。

    Args:
        text: 包含 LaTeX 的文本

    Returns:
        转换后的 Unicode 文本
    """
    # 移除 $$ 块级定界符
    text = text.replace("$$", "")
    # 移除 $ 行内定界符
    text = text.replace("$", "")

    # 处理 \text{...} → 保持原文
    text = re.sub(r'\\text\{([^}]*)\}', r'\1', text)

    # 处理 \frac{a}{b}
    text = _convert_fracs(text)

    # 处理 \sqrt{...}
    text = _convert_sqrt(text)

    # 处理上标 ^{...} 或 ^x
    text = _convert_superscript(text)

    # 处理下标 _{...} 或 _x
    text = _convert_subscript(text)

    # 处理 \left( \right)
    text = text.replace(r"\left(", "(")
    text = text.replace(r"\right)", ")")
    text = text.replace(r"\left[", "[")
    text = text.replace(r"\right]", "]")
    text = text.replace(r"\left|", "|")
    text = text.replace(r"\right|", "|")
    text = text.replace(r"\left\{", "{")
    text = text.replace(r"\right\}", "}")

    # 替换希腊字母
    for latex, unicode_char in GREEK_MAP.items():
        text = text.replace(latex, unicode_char)

    # 替换运算符
    for latex, unicode_char in OPERATOR_MAP.items():
        text = text.replace(latex, unicode_char)

    # 处理数学函数名（\sin → sin）
    for func in FUNCTION_NAMES:
        text = text.replace(f"\\{func}", func)

    # 处理 \mathrm{...}
    text = re.sub(r'\\mathrm\{([^}]*)\}', r'\1', text)

    # 处理 \mathbf{...}
    text = re.sub(r'\\mathbf\{([^}]*)\}', r'\1', text)

    # 处理 \quad 和 \qquad
    text = text.replace(r"\quad", "  ")
    text = text.replace(r"\qquad", "    ")

    # 处理 \, \; \! 空格
    text = text.replace(r"\,", " ")
    text = text.replace(r"\;", " ")
    text = text.replace(r"\!", "")

    # 移除剩余的 \command
    text = re.sub(r'\\[a-zA-Z]+', '', text)

    # 清理多余的花括号
    text = text.replace("{", "").replace("}", "")

    # 清理多余空格
    text = re.sub(r'  +', ' ', text)

    return text.strip()


def _convert_fracs(text: str) -> str:
    """转换 \frac{num}{den} 为 num/den"""
    pattern = r'\\frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    max_iter = 20
    while re.search(pattern, text) and max_iter > 0:
        text = re.sub(pattern, r'\1/\2', text)
        max_iter -= 1
    return text


def _convert_sqrt(text: str) -> str:
    r"""转换 \sqrt{...} 为 √(...)"""
    pattern = r'\\sqrt\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    max_iter = 10
    while re.search(pattern, text) and max_iter > 0:
        text = re.sub(pattern, r'√(\1)', text)
        max_iter -= 1
    return text


def _convert_superscript(text: str) -> str:
    """转换 ^{...} 或 ^x 为 Unicode 上标"""
    # ^{内容} — 仅当内容不含反斜杠（纯文本/数字）时转换
    pattern = r'\^\{([^{}]*)\}'
    max_iter = 10
    while re.search(pattern, text) and max_iter > 0:
        def replace_sup(m):
            content = m.group(1)
            if '\\' in content:
                return m.group(0)
            return _to_superscript(content)
        text = re.sub(pattern, replace_sup, text)
        max_iter -= 1

    # ^单个字符
    text = re.sub(r'\^([0-9n+i])', lambda m: SUPERSCRIPT_MAP.get(m.group(1), f'^{m.group(1)}'), text)

    return text


def _convert_subscript(text: str) -> str:
    """转换 _{...} 或 _x 为 Unicode 下标"""
    # _{内容} — 仅当内容不含反斜杠（纯文本/数字）时转换
    pattern = r'_\{([^{}]*)\}'
    max_iter = 10
    while re.search(pattern, text) and max_iter > 0:
        def replace_sub(m):
            content = m.group(1)
            if '\\' in content:
                # 含 LaTeX 命令，保持原样
                return m.group(0)
            return _to_subscript(content)
        text = re.sub(pattern, replace_sub, text)
        max_iter -= 1

    # _单个字符
    text = re.sub(r'_([0-9aehox])', lambda m: SUBSCRIPT_MAP.get(m.group(1), f'_{m.group(1)}'), text)

    return text


def _to_superscript(text: str) -> str:
    """将文本转换为 Unicode 上标"""
    result = []
    for ch in text:
        if ch in SUPERSCRIPT_MAP:
            result.append(SUPERSCRIPT_MAP[ch])
        elif ch == ' ':
            result.append(' ')
        else:
            result.append(ch)
    return ''.join(result)


def _to_subscript(text: str) -> str:
    """将文本转换为 Unicode 下标"""
    result = []
    for ch in text:
        if ch in SUBSCRIPT_MAP:
            result.append(SUBSCRIPT_MAP[ch])
        elif ch == ' ':
            result.append(' ')
        else:
            result.append(ch)
    return ''.join(result)


def render_problem_text(text: str) -> str:
    """
    渲染题目文本，将 LaTeX 转为 Unicode 并添加视觉装饰。

    Args:
        text: 原始 LaTeX 文本

    Returns:
        渲染后的终端显示文本
    """
    lines = text.split("\n")
    result = []
    for line in lines:
        rendered = latex_to_unicode(line)
        result.append(rendered)
    return "\n".join(result)


# ==================== 测试 ====================

if __name__ == "__main__":
    test_cases = [
        r"$\frac{x^2}{a^2} + \frac{y^2}{b^2} = 1$",
        r"$c = \sqrt{a^2 - b^2}$",
        r"$e = \frac{c}{a} < 1$",
        r"$\alpha + \beta = \pi$",
        r"$\int_0^1 x^2 dx = \frac{1}{3}$",
        r"$|PF_1| + |PF_2| = 2a$",
        r"$\triangle F_1PF_2$",
        r"$\frac{1}{|PF|} + \frac{1}{|QF|} = \frac{2}{p}$",
    ]

    for tc in test_cases:
        print(f"Input:  {tc}")
        print(f"Output: {latex_to_unicode(tc)}")
        print()
