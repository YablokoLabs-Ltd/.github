# Sovra Verify — brand assets

**Sovra Verify — Don't Just Answer. Prove It.**

![Sovra Verify logo](png/sovra-verify-logo.png)

## The idea

- **Shield**: sovereignty. Sensitive documents stay private.
- **Document with claim lines**: the file being audited. The teal line is the claim that was checked.
- **Check mark breaking out of the page**: proof. The answer comes with evidence.

## Files

| Asset | SVG | PNG |
|---|---|---|
| Logo (light backgrounds) | `svg/sovra-verify-logo.svg` | `png/sovra-verify-logo.png` (2x), `png/sovra-verify-logo-small.png` |
| Logo (dark backgrounds) | `svg/sovra-verify-logo-dark.svg` | `png/sovra-verify-logo-dark.png` (2x), `png/sovra-verify-logo-dark-small.png` |
| Mark (transparent) | `svg/sovra-verify-mark.svg` | `png/sovra-verify-mark-{64…1024}.png` |
| App icon (rounded tile) | `svg/sovra-verify-icon.svg` | `png/sovra-verify-icon-{48…1024}.png` (180 = Apple touch, 192/512 = PWA) |
| Favicon (simplified for 16–32 px) | `svg/sovra-verify-favicon.svg` | `png/sovra-verify-favicon-{16,32}.png`, `favicon.ico` |

Text in the SVGs is converted to outlines, so they render the same everywhere without the font installed.

## Colors

| Role | Hex |
|---|---|
| Navy (shield top → bottom) | `#1B3A6B` → `#0B1A36` |
| Teal (verify gradient) | `#10B981` → `#2DD4BF` |
| "Verify" on light | `#0D9488` |
| Tagline on light / dark | `#475569` / `#94A3B8` |
| Dark background | `#0B1220` |

Typeface: Inter Display Bold (wordmark), Inter SemiBold (tagline).

## Regenerating

`generate.py` builds every file above. It needs `uharfbuzz`, `fonttools`, `cairosvg`, `pillow`, and the Inter fonts (path set in `FD` at the top of the script).

```sh
python3 generate.py .
```
