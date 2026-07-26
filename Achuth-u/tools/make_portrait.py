"""
Direct portrait renderer - converts photo-ready.png into portrait.svg
Usage: python tools/make_portrait.py
"""
import numpy as np
import cv2
from PIL import Image
import xml.sax.saxutils as sax

INPUT_PATH  = 'assets/photo-ready.png'
OUTPUT_PATH = 'portrait.svg'
GLYPH_RAMP  = " .,:;~+*xXO#@"
GRID_WIDTH  = 68
FONT_SIZE   = 8
LINE_HEIGHT = 9.5
LETTER_W    = 4.9
CYBER_BLUE  = '#3BA8FF'


def main():
    # Load & resize
    img = Image.open(INPUT_PATH).convert('L')
    w, h = img.size
    aspect = h / float(w)
    grid_h = int(GRID_WIDTH * aspect * 0.50)
    img_resized = img.resize((GRID_WIDTH, grid_h), Image.Resampling.LANCZOS)
    px = np.array(img_resized)

    # Sharpen
    kernel = np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]], dtype=np.float32)
    px = cv2.filter2D(px.astype(np.uint8), -1, kernel)
    px = np.clip(px.astype(np.int32), 0, 255).astype(np.uint8)

    # Pixels to ASCII
    ramp_len = len(GLYPH_RAMP)
    rows = []
    for row in px:
        line = ''
        for pixel in row:
            inv = 255 - int(pixel)
            idx = int(inv / 255.0 * (ramp_len - 1))
            idx = max(0, min(ramp_len - 1, idx))
            line += GLYPH_RAMP[idx]
        rows.append(line)

    num_rows = len(rows)
    svg_w = int(GRID_WIDTH * LETTER_W + 24)
    svg_h = int(num_rows   * LINE_HEIGHT + 24)

    tspan_lines = []
    for i, row in enumerate(rows):
        y = int(14 + i * LINE_HEIGHT)
        tspan_lines.append('    <tspan x="10" y="{}">{}</tspan>'.format(y, sax.escape(row)))

    tspans_block = "\n".join(tspan_lines)

    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <style>
      @keyframes revealDown {{
        from {{ height: 0; }}
        to   {{ height: {h}px; }}
      }}
      @keyframes subtleGlow {{
        0%, 100% {{ opacity: .92; }}
        50%       {{ opacity: 1; }}
      }}
      .ascii {{
        font-family: 'Courier New', Consolas, monospace;
        font-size: {fs}px;
        font-weight: 700;
        fill: {blue};
        letter-spacing: .6px;
        animation: subtleGlow 3.5s ease-in-out infinite;
      }}
    </style>
    <filter id="glow">
      <feGaussianBlur stdDeviation=".6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="rev">
      <rect x="0" y="0" width="{w}" height="0">
        <animate attributeName="height" from="0" to="{h}"
                 dur="2s" fill="freeze"
                 calcMode="spline" keySplines="0.22 1 0.36 1"/>
      </rect>
    </clipPath>
  </defs>
  <g clip-path="url(#rev)" filter="url(#glow)">
    <text class="ascii" xml:space="preserve">
{tspans}
    </text>
  </g>
</svg>
""".format(w=svg_w, h=svg_h, fs=FONT_SIZE, blue=CYBER_BLUE, tspans=tspans_block)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(svg)

    print("[OK] portrait.svg rendered: {} cols x {} rows -> {}".format(GRID_WIDTH, num_rows, OUTPUT_PATH))


if __name__ == '__main__':
    main()
