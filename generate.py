#!/usr/bin/env python3
import json
import os

PARENT = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PARENT, "themes")
PALETTES_FILE = os.path.join(PARENT, "colors.json")
if not os.path.exists(PALETTES_FILE):
    PALETTES_FILE = os.path.join(PARENT, "..", "colors.json")

AUTHOR = "Xscriptor"
SCHEMA = "https://zed.dev/schema/themes/v0.2.0.json"

os.makedirs(DIST_DIR, exist_ok=True)

with open(PALETTES_FILE) as f:
    palettes = json.load(f)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


def alpha_hex(h, a):
    r, g, b = hex_to_rgb(h)
    return f"{rgb_to_hex(r, g, b)}{round(a * 255):02x}"


def blend(ha, hb, pct):
    ra, ga, ba = hex_to_rgb(ha)
    rb, gb, bb = hex_to_rgb(hb)
    return rgb_to_hex(
        round(ra + (rb - ra) * pct),
        round(ga + (gb - ga) * pct),
        round(ba + (bb - ba) * pct),
    )


def relative_luminance(r, g, b):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast_ratio(ha, hb):
    r1, g1, b1 = hex_to_rgb(ha)
    r2, g2, b2 = hex_to_rgb(hb)
    l1 = relative_luminance(r1, g1, b1)
    l2 = relative_luminance(r2, g2, b2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def accessible_comment(bg, fg, comment_candidate):
    if contrast_ratio(comment_candidate, bg) >= 3.0:
        return comment_candidate
    for pct in (0.15, 0.25, 0.35, 0.5, 0.65, 0.8):
        candidate = blend(bg, fg, pct)
        if contrast_ratio(candidate, bg) >= 3.0:
            return candidate
    return blend(bg, fg, 0.65)


ANSI_NAMES = [
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "bright_black",
    "bright_red",
    "bright_green",
    "bright_yellow",
    "bright_blue",
    "bright_magenta",
    "bright_cyan",
    "bright_white",
]


for name, c in palettes.items():
    bg = c["background"]
    fg = c["foreground"]

    comment_color = accessible_comment(bg, fg, c["color8"])

    def col(idx):
        return c[f"color{idx}"]

    r, g, b = hex_to_rgb(bg)
    appearance = "dark" if relative_luminance(r, g, b) < 0.5 else "light"

    active_line = blend(bg, fg, 0.05)
    selection = alpha_hex(fg, 0.15)

    syntax = {
        "comment": comment_color,
        "comment.doc": comment_color,
        "constant": col(3),
        "constant.numeric": col(3),
        "constant.character.escape": col(1),
        "constant.builtin": col(3),
        "string": col(2),
        "string.regex": col(2),
        "string.special": col(1),
        "keyword": col(5),
        "keyword.control": col(5),
        "keyword.function": col(9),
        "keyword.return": col(5),
        "keyword.operator": col(5),
        "function": col(4),
        "function.call": col(4),
        "function.builtin": col(4),
        "function.macro": col(9),
        "function.special": col(4),
        "type": col(6),
        "type.builtin": col(6),
        "type.enum": col(6),
        "constructor": col(6),
        "variable": fg,
        "variable.builtin": col(1),
        "variable.parameter": col(4),
        "variable.member": fg,
        "variable.function": col(4),
        "operator": col(5),
        "punctuation": fg,
        "punctuation.delimiter": comment_color,
        "punctuation.bracket": fg,
        "markup.heading": col(6),
        "markup.list": col(1),
        "markup.bold": fg,
        "markup.italic": fg,
        "markup.link": col(6),
        "markup.quote": col(8),
        "markup.raw": col(2),
        "markup.highlight": col(3),
        "tag": col(1),
        "tag.attribute": col(3),
        "tag.delimiter": comment_color,
        "embedding": col(5),
        "emphasis.strong": {"color": fg, "font_weight": 700},
        "emphasis.italic": {"color": fg, "font_style": "italic"},
        "emphasis.underline": {"color": col(6)},
    }
    syntax = {
        key: ({"color": value} if isinstance(value, str) else value)
        for key, value in syntax.items()
    }

    accent_indexes = [5, 4, 6, 2, 3, 1, 12]
    player_indexes = [5, 4, 6, 2, 3, 1, 12, 13]

    style = {
        "background": bg,
        "text": fg,
        "border": col(8),
        "scrollbar.thumb.border": col(8),
        "accents": [col(i) for i in accent_indexes],
        "players": [
            {
                "background": col(i),
                "cursor": col(i),
                "selection": selection if position == 0 else alpha_hex(col(i), 0.15),
            }
            for position, i in enumerate(player_indexes)
        ],
        "text.accent": col(5),
        "icon.accent": col(5),
        "error": col(1),
        "warning": col(3),
        "info": col(6),
        "hint": col(2),
        "editor.background": bg,
        "editor.foreground": fg,
        "editor.gutter.background": bg,
        "editor.active_line.background": active_line,
        "editor.highlighted_line.background": active_line,
        "editor.line_number": comment_color,
        "editor.active_line_number": col(5),
        "editor.invisible": comment_color,
        "editor.wrap_guide": comment_color,
        "syntax": syntax,
        "terminal.background": bg,
        "terminal.foreground": fg,
        "terminal.ansi.background": bg,
    }
    for idx, ansi_name in enumerate(ANSI_NAMES):
        style[f"terminal.ansi.{ansi_name}"] = col(idx)

    theme_family = {
        "$schema": SCHEMA,
        "name": f"Xscriptor {name}",
        "author": AUTHOR,
        "themes": [
            {
                "name": f"Xscriptor {name}",
                "appearance": appearance,
                "style": style,
            }
        ],
    }

    filepath = os.path.join(DIST_DIR, f"Xscriptor {name}.json")
    with open(filepath, "w") as f:
        json.dump(theme_family, f, indent=2)
        f.write("\n")
    print(f"  ok  Xscriptor {name} ({appearance})")
