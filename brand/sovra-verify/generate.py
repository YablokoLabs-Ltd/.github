import os, sys
import uharfbuzz as hb
import cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = sys.argv[1]
FD = "/usr/share/fonts/opentype/inter/"
WORD_FONT = FD + "InterDisplay-Bold.otf"
TAG_FONT = FD + "Inter-SemiBold.otf"

def ntos(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s

def shape(fontfile, text, size, x, y, tracking=0.0, split_at=None):
    """Shape text with HarfBuzz and return outline path data (text -> paths).
    If split_at is given, returns two paths: clusters < split_at and >= split_at."""
    face = hb.Face(hb.Blob.from_file_path(fontfile))
    font = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    tt = TTFont(fontfile); gs = tt.getGlyphSet(); upem = tt["head"].unitsPerEm
    order = tt.getGlyphOrder(); s = size / upem
    pens = [SVGPathPen(gs, ntos=ntos), SVGPathPen(gs, ntos=ntos)]
    cx = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = pens[1 if (split_at is not None and info.cluster >= split_at) else 0]
        gx = x + (cx + pos.x_offset) * s
        gs[order[info.codepoint]].draw(TransformPen(pen, (s, 0, 0, -s, gx, y - pos.y_offset * s)))
        cx += pos.x_advance + tracking * upem
    width = (cx - tracking * upem) * s
    paths = [p.getCommands() for p in pens]
    return (paths if split_at is not None else paths[0]), width

# ---------- palette ----------
NAVY_1, NAVY_2 = "#1B3A6B", "#0B1A36"     # shield gradient (top -> bottom)
TEAL_1, TEAL_2 = "#2DD4BF", "#10B981"     # verify gradient
PAPER, FOLD, LINE = "#F8FAFC", "#CBD5E1", "#94A3B8"

def mark(p, edge=False):
    """The Sovra Verify mark in a 512x512 box. p = id prefix."""
    return f'''
  <defs>
    <linearGradient id="{p}sh" x1="256" y1="56" x2="256" y2="456" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{NAVY_1}"/><stop offset="1" stop-color="{NAVY_2}"/>
    </linearGradient>
    <linearGradient id="{p}ok" x1="196" y1="330" x2="352" y2="206" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{TEAL_2}"/><stop offset="1" stop-color="{TEAL_1}"/>
    </linearGradient>
  </defs>
  <!-- shield: sovereignty / data stays private -->
  <path d="M256 56 L408 106 V232 C408 342 344 416 256 458 C168 416 104 342 104 232 V106 Z" fill="url(#{p}sh)"{' stroke="url(#'+p+'ok)" stroke-width="10" stroke-linejoin="round"' if edge else ''}/>
  <!-- document under audit -->
  <path d="M190 136 H292 L332 176 V326 Q332 344 314 344 H190 Q172 344 172 326 V154 Q172 136 190 136 Z" fill="{PAPER}"/>
  <path d="M292 136 V162 Q292 176 306 176 H332 Z" fill="{FOLD}"/>
  <!-- claims; the highlighted one is the verified claim -->
  <rect x="196" y="176" width="72" height="14" rx="7" fill="{LINE}"/>
  <rect x="196" y="206" width="112" height="14" rx="7" fill="url(#{p}ok)"/>
  <rect x="196" y="236" width="88" height="14" rx="7" fill="{LINE}"/>
  <!-- proof: check mark breaking out of the page, knocked out of the shield -->
  <path d="M206 292 L246 330 L342 228" fill="none" stroke="url(#{p}sh)" stroke-width="58" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M206 292 L246 330 L342 228" fill="none" stroke="url(#{p}ok)" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>'''

def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">\n'
            f'  <title>{title}</title>{body}\n</svg>\n')

def write(name, content):
    path = os.path.join(OUT, "svg", name)
    with open(path, "w") as f: f.write(content)
    return path

def png(svgpath, name, width):
    cairosvg.svg2png(url=svgpath, write_to=os.path.join(OUT, "png", name), output_width=width)

os.makedirs(os.path.join(OUT, "svg"), exist_ok=True)
os.makedirs(os.path.join(OUT, "png"), exist_ok=True)

# ---------- 1. mark (transparent) ----------
m = write("sovra-verify-mark.svg", svg(512, 512, mark("m"), "Sovra Verify"))
for s in (64, 128, 256, 512, 1024):
    png(m, f"sovra-verify-mark-{s}.png", s)

# ---------- 2. app icon (rounded tile) ----------
tile = f'''
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="512" y2="512" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#E6FFFA"/><stop offset="1" stop-color="#CCFBF1"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="112" fill="url(#bg)"/>
  <g transform="translate(256 262) scale(0.86) translate(-256 -256)">{mark("i")}
  </g>'''
ic = write("sovra-verify-icon.svg", svg(512, 512, tile, "Sovra Verify"))
for s in (48, 64, 128, 180, 192, 256, 512, 1024):
    png(ic, f"sovra-verify-icon-{s}.png", s)

# ---------- 2b. favicon: simplified for 16-32px (shield + check only) ----------
fav = f'''
  <defs>
    <linearGradient id="fsh" x1="256" y1="24" x2="256" y2="496" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{NAVY_1}"/><stop offset="1" stop-color="{NAVY_2}"/>
    </linearGradient>
    <linearGradient id="fok" x1="140" y1="360" x2="380" y2="170" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{TEAL_2}"/><stop offset="1" stop-color="{TEAL_1}"/>
    </linearGradient>
  </defs>
  <path d="M256 24 L456 88 V240 C456 372 372 456 256 500 C140 456 56 372 56 240 V88 Z" fill="url(#fsh)"/>
  <path d="M150 268 L224 340 L366 182" fill="none" stroke="url(#fok)" stroke-width="72" stroke-linecap="round" stroke-linejoin="round"/>'''
fv = write("sovra-verify-favicon.svg", svg(512, 512, fav, "Sovra Verify"))
for s in (16, 32):
    png(fv, f"sovra-verify-favicon-{s}.png", s)
from PIL import Image
Image.open(os.path.join(OUT, "png", "sovra-verify-icon-48.png")).save(os.path.join(OUT, "favicon.ico"),
    sizes=[(16, 16), (32, 32), (48, 48)],
    append_images=[Image.open(os.path.join(OUT, "png", f"sovra-verify-favicon-{n}.png")) for n in (16, 32)])

# ---------- 3. horizontal logo (light + dark) ----------
def logo(dark):
    MARK_H = 220
    pad = 40
    word_size, tag_size = 112, 27
    tx = pad + MARK_H + 36
    (sovra, verify), ww = shape(WORD_FONT, "Sovra Verify", word_size, tx, 0, split_at=6)
    tag, tw = shape(TAG_FONT, "DON’T JUST ANSWER. PROVE IT.", tag_size, tx + 4, 0, tracking=0.14)
    # vertical layout: centre the text block on the mark
    cap = word_size * 0.727          # Inter cap height ratio
    gap = 44
    block = cap + gap + tag_size * 0.727
    H = MARK_H + pad * 2
    top = (H - block) / 2
    base_word = top + cap
    base_tag = base_word + gap + tag_size * 0.727
    W = int(round(tx + max(ww, tw + 4) + pad + 8))
    c_sovra = "#F8FAFC" if dark else "#0B1A36"
    c_verify = TEAL_1 if dark else "#0D9488"
    c_tag = "#94A3B8" if dark else "#475569"
    bg = f'\n  <rect width="{W}" height="{H}" fill="#0B1220"/>' if dark else ""
    p = "d" if dark else "l"
    body = (f'{bg}\n  <g transform="translate({pad} {pad}) scale({MARK_H/512})">{mark(p, edge=dark)}\n  </g>'
            f'\n  <path transform="translate(0 {base_word:.2f})" fill="{c_sovra}" d="{sovra}"/>'
            f'\n  <path transform="translate(0 {base_word:.2f})" fill="{c_verify}" d="{verify}"/>'
            f'\n  <path transform="translate(0 {base_tag:.2f})" fill="{c_tag}" d="{tag}"/>')
    return W, H, body

for dark in (False, True):
    W, H, body = logo(dark)
    name = "sovra-verify-logo-dark" if dark else "sovra-verify-logo"
    lp = write(name + ".svg", svg(W, H, body, "Sovra Verify — Don’t Just Answer. Prove It."))
    png(lp, name + ".png", W * 2)
    png(lp, name + "-small.png", W // 2)
print("done")
