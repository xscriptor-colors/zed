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


def ensure_contrast(color, bg, fg, min_ratio=3.0):
    if contrast_ratio(color, bg) >= min_ratio:
        return color
    for step in range(1, 21):
        candidate = blend(color, fg, step / 20)
        if contrast_ratio(candidate, bg) >= min_ratio:
            return candidate
    return blend(color, fg, 0.75)


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

DIM_NAMES = ANSI_NAMES[:8]

STATUS_NAMES = (
    "error",
    "warning",
    "info",
    "hint",
    "success",
    "created",
    "modified",
    "deleted",
    "conflict",
    "renamed",
    "hidden",
    "ignored",
    "unreachable",
)


for name, palette in palettes.items():
    c = {key: value.lower() for key, value in palette.items()}
    bg = c["background"]
    fg = c["foreground"]

    def raw(idx):
        return c[f"color{idx}"]

    def col(idx):
        return ensure_contrast(raw(idx), bg, fg)

    comment_color = accessible_comment(bg, fg, c["color8"])

    r, g, b = hex_to_rgb(bg)
    appearance = "dark" if relative_luminance(r, g, b) < 0.5 else "light"

    active_line = blend(bg, fg, 0.05)
    selection = alpha_hex(fg, 0.15)

    surface = blend(bg, fg, 0.04)
    raised = blend(bg, fg, 0.07)
    hover = blend(bg, fg, 0.10)
    active = blend(bg, fg, 0.14)
    border = blend(bg, fg, 0.20)
    border_variant = blend(bg, fg, 0.12)
    border_disabled = blend(bg, fg, 0.07)
    text_disabled = blend(bg, fg, 0.38)
    text_placeholder = blend(bg, fg, 0.45)

    syntax = {
        "attribute": col(3),
        "boolean": col(3),
        "comment": comment_color,
        "comment.doc": comment_color,
        "constant": col(3),
        "constant.builtin": col(3),
        "constant.character.escape": col(1),
        "constant.numeric": col(3),
        "constructor": col(6),
        "diff.minus": col(1),
        "diff.plus": col(2),
        "embedded": col(5),
        "embedding": col(5),
        "emphasis": {"color": fg, "font_style": "italic"},
        "emphasis.italic": {"color": fg, "font_style": "italic"},
        "emphasis.strong": {"color": fg, "font_weight": 700},
        "emphasis.underline": {"color": col(6)},
        "enum": col(6),
        "function": col(4),
        "function.builtin": col(4),
        "function.call": col(4),
        "function.macro": col(9),
        "function.special": col(4),
        "hint": comment_color,
        "keyword": col(5),
        "keyword.control": col(5),
        "keyword.function": col(9),
        "keyword.operator": col(5),
        "keyword.return": col(5),
        "label": col(5),
        "link_text": col(6),
        "link_uri": col(6),
        "markup.bold": fg,
        "markup.heading": col(6),
        "markup.highlight": col(3),
        "markup.italic": fg,
        "markup.link": col(6),
        "markup.list": col(1),
        "markup.quote": comment_color,
        "markup.raw": col(2),
        "namespace": fg,
        "number": col(3),
        "operator": col(5),
        "preproc": col(5),
        "predictive": {"color": comment_color, "font_style": "italic"},
        "primary": fg,
        "property": fg,
        "punctuation": fg,
        "punctuation.bracket": fg,
        "punctuation.delimiter": comment_color,
        "punctuation.list_marker": col(1),
        "punctuation.markup": comment_color,
        "punctuation.special": col(1),
        "selector": col(3),
        "selector.pseudo": col(5),
        "string": col(2),
        "string.escape": col(1),
        "string.regex": col(2),
        "string.special": col(1),
        "string.special.symbol": col(3),
        "tag": col(1),
        "tag.attribute": col(3),
        "tag.delimiter": comment_color,
        "tag.doctype": comment_color,
        "text.literal": col(2),
        "title": col(6),
        "type": col(6),
        "type.builtin": col(6),
        "type.enum": col(6),
        "variable": fg,
        "variable.builtin": col(1),
        "variable.function": col(4),
        "variable.member": fg,
        "variable.parameter": col(4),
        "variable.special": col(1),
        "variant": col(6),
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
        "border": border,
        "border.variant": border_variant,
        "border.focused": raw(5),
        "border.selected": raw(5),
        "border.disabled": border_disabled,
        "border.transparent": "#00000000",
        "surface.background": surface,
        "panel.background": surface,
        "panel.focused_border": raw(5),
        "pane.focused_border": raw(5),
        "elevated_surface.background": surface,
        "element.background": surface,
        "element.hover": hover,
        "element.active": active,
        "element.selected": active,
        "element.disabled": surface,
        "element.selection_background": alpha_hex(raw(5), 0.25),
        "ghost_element.background": "#00000000",
        "ghost_element.hover": hover,
        "ghost_element.active": active,
        "ghost_element.selected": active,
        "ghost_element.disabled": surface,
        "drop_target.background": alpha_hex(fg, 0.25),
        "status_bar.background": raised,
        "title_bar.background": raised,
        "title_bar.inactive_background": surface,
        "toolbar.background": bg,
        "tab_bar.background": surface,
        "tab.active_background": bg,
        "tab.inactive_background": surface,
        "accents": [raw(i) for i in accent_indexes],
        "players": [
            {
                "background": raw(i),
                "cursor": raw(i),
                "selection": selection if position == 0 else alpha_hex(raw(i), 0.15),
            }
            for position, i in enumerate(player_indexes)
        ],
        "text.accent": raw(5),
        "text.muted": comment_color,
        "text.disabled": text_disabled,
        "text.placeholder": text_placeholder,
        "icon": fg,
        "icon.accent": raw(5),
        "icon.muted": comment_color,
        "icon.disabled": text_disabled,
        "icon.placeholder": text_placeholder,
        "link_text.hover": raw(6),
        "predictive": comment_color,
        "predictive.background": alpha_hex(fg, 0.08),
        "predictive.border": border_variant,
        "error": col(1),
        "warning": col(3),
        "info": col(6),
        "hint": col(2),
        "success": col(2),
        "created": col(2),
        "modified": col(3),
        "deleted": col(1),
        "conflict": col(4),
        "renamed": col(6),
        "hidden": comment_color,
        "ignored": comment_color,
        "unreachable": comment_color,
        "version_control.added": col(2),
        "version_control.deleted": col(1),
        "version_control.modified": col(3),
        "version_control.conflict": col(4),
        "version_control.renamed": col(6),
        "version_control.ignored": comment_color,
        "version_control.word_added": alpha_hex(col(2), 0.35),
        "version_control.word_deleted": alpha_hex(col(1), 0.60),
        "version_control.conflict_marker.ours": alpha_hex(col(2), 0.20),
        "version_control.conflict_marker.theirs": alpha_hex(col(4), 0.20),
        "editor.background": bg,
        "editor.foreground": fg,
        "editor.gutter.background": bg,
        "editor.active_line.background": active_line,
        "editor.highlighted_line.background": active_line,
        "editor.line_number": comment_color,
        "editor.active_line_number": col(5),
        "editor.hover_line_number": comment_color,
        "editor.invisible": comment_color,
        "editor.wrap_guide": comment_color,
        "editor.active_wrap_guide": alpha_hex(fg, 0.18),
        "editor.indent_guide": alpha_hex(fg, 0.10),
        "editor.indent_guide_active": alpha_hex(fg, 0.30),
        "editor.document_highlight.bracket_background": alpha_hex(raw(4), 0.25),
        "editor.document_highlight.read_background": alpha_hex(raw(6), 0.18),
        "editor.document_highlight.write_background": alpha_hex(raw(1), 0.18),
        "editor.subheader.background": surface,
        "panel.indent_guide": alpha_hex(fg, 0.10),
        "panel.indent_guide_active": alpha_hex(fg, 0.30),
        "panel.indent_guide_hover": alpha_hex(fg, 0.22),
        "search.match_background": alpha_hex(raw(3), 0.35),
        "search.active_match_background": alpha_hex(raw(4), 0.45),
        "scrollbar.thumb.background": alpha_hex(fg, 0.25),
        "scrollbar.thumb.border": border,
        "scrollbar.thumb.hover_background": alpha_hex(fg, 0.40),
        "scrollbar.thumb.active_background": alpha_hex(fg, 0.55),
        "scrollbar.track.background": "#00000000",
        "scrollbar.track.border": surface,
        "minimap.thumb.background": alpha_hex(fg, 0.20),
        "minimap.thumb.border": border,
        "minimap.thumb.hover_background": alpha_hex(fg, 0.30),
        "minimap.thumb.active_background": alpha_hex(fg, 0.40),
        "syntax": syntax,
        "terminal.background": bg,
        "terminal.foreground": fg,
        "terminal.bright_foreground": raw(15),
        "terminal.dim_foreground": comment_color,
        "terminal.ansi.background": bg,
    }
    for idx, ansi_name in enumerate(ANSI_NAMES):
        style[f"terminal.ansi.{ansi_name}"] = raw(idx)
    for idx, ansi_name in enumerate(DIM_NAMES):
        style[f"terminal.ansi.dim_{ansi_name}"] = blend(raw(idx), bg, 0.30)
    for status_name in STATUS_NAMES:
        style[f"{status_name}.background"] = alpha_hex(style[status_name], 0.15)
        style[f"{status_name}.border"] = alpha_hex(style[status_name], 0.50)

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
