# Xscriptor Themes for Zed

Twelve Xscriptor color palettes ported to Zed as a single theme extension.

| Theme | Appearance |
|-------|------------|
| Xscriptor X | dark |
| Xscriptor Madrid | light |
| Xscriptor Lahabana | dark |
| Xscriptor Miami | dark |
| Xscriptor Paris | dark |
| Xscriptor Tokio | dark |
| Xscriptor Oslo | dark |
| Xscriptor Helsinki | light |
| Xscriptor Berlin | dark |
| Xscriptor London | light |
| Xscriptor Praha | dark |
| Xscriptor Bogota | dark |

Every theme is generated from the palettes in `colors.json` (background, foreground and the 16 ANSI colors) and keeps the original Xscriptor names.

## Install

### From the Zed extension registry

Once the extension is published: open the Extensions page in Zed (`zed: extensions`), search for **Xscriptor Themes** and install it. Then pick a theme from the theme selector (`theme selector: toggle`) or set it in `settings.json`:

```json
{
  "theme": {
    "mode": "dark",
    "dark": "Xscriptor X",
    "light": "Xscriptor Madrid"
  }
}
```

### Manual install

Copy the theme files into Zed's user themes directory:

```sh
cp themes/*.json "${XDG_CONFIG_HOME:-$HOME/.config}/zed/themes/"
```

### Install as a dev extension

From the Extensions page, click **Install Dev Extension** and select this directory (the one containing `extension.toml`).

## Regenerate

```sh
python3 generate.py
```

`generate.py` reads `colors.json` and rewrites `themes/`, one Zed theme family per palette.

## Format notes

The themes target the current Zed theme schema (`https://zed.dev/schema/themes/v0.2.0.json`, one theme family per file):

- Legacy CSS-style colors (`rgba(...)`) were converted to Zed's hex formats (`#rrggbb`, `#rrggbbaa`).
- Terminal colors use the flat `terminal.ansi.*` keys.
- The cursor and selection colors are mapped to the first entry of `players`.
- Diagnostics colors (`editor.diagnostics.*`) are mapped to the current `error`, `warning`, `info` and `hint` roles.
- Syntax entries are objects (`{"color": ...}`); bold is `700`; `underline` emphasis is not supported by the schema, so only its color is kept.
- The accent color drives `text.accent`, `icon.accent` and the `accents` array.
- UI roles that the palettes do not define (panels, tabs, elements, etc.) fall back to Zed's defaults.

## Publishing

The extension is ready to submit to the [Zed extension registry](https://github.com/zed-industries/extensions):

1. Fork `zed-industries/extensions`.
2. Add this repository as a submodule under `extensions/xscriptor-theme` (HTTPS URL) and add an entry to the top-level `extensions.toml`:

   ```toml
   [xscriptor-theme]
   submodule = "extensions/xscriptor-theme"
   version = "0.1.0"
   ```

3. Run `pnpm sort-extensions` and open a PR.

Checklist: extension ID ends with `-theme`, provides only themes, ships an allowed license (MIT), and all user-facing text is in English.
