"""
High-fidelity ASCII portrait renderer.
Produces a recognizable face portrait with clear facial features.
"""
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import xml.sax.saxutils as sax
import os

# ── Configuration ────────────────────────────────────────────────────────
INPUT_PATH   = 'assets/photo-original.jpg'   # full-colour original
OUTPUT_PATH  = 'portrait.svg'

# Wider glyph ramp from empty → dense; 20 levels for smooth gradients
GLYPH_RAMP   = "  ..'',,::;;~~++**xxXXOO##@@"

# Grid: wider = more horizontal resolution; rows auto-calculated
GRID_WIDTH   = 80
# Correction factor: monospace chars are ~2x taller than wide
ASPECT_CORR  = 0.45

FONT_SIZE    = 7.5
LINE_HEIGHT  = 8.8
LETTER_W     = 4.55
CYBER_BLUE   = '#3BA8FF'
GLOW_COLOR   = '#58A6FF'


def load_and_crop_portrait(path: str) -> np.ndarray:
    """
    Load full-colour image, auto-crop to the head+shoulders region,
    and return as grayscale numpy array.
    """
    img_bgr = cv2.imread(path)
    if img_bgr is None:
        raise FileNotFoundError(f"Cannot read {path}")

    h, w = img_bgr.shape[:2]
    # Portrait photo: head is typically in top 85%, centered
    crop_h = int(h * 0.85)
    crop_w = int(w * 0.90)
    x_off  = (w - crop_w) // 2
    cropped = img_bgr[0:crop_h, x_off:x_off + crop_w]

    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    return gray


def enhance_for_ascii(gray: np.ndarray) -> np.ndarray:
    """
    Apply a chain of enhancement steps optimised for ASCII conversion:
    1. Histogram normalisation (full range 0-255)
    2. CLAHE (local contrast)
    3. Unsharp-mask sharpening
    4. Gamma brightening for faces (dark skin → mid-range)
    """
    # 1. Full-range normalise
    norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

    # 2. CLAHE – preserve local face detail
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    cl = clahe.apply(norm)

    # 3. Unsharp mask for crispness
    blur = cv2.GaussianBlur(cl, (0, 0), sigmaX=1.5)
    sharp = cv2.addWeighted(cl, 1.8, blur, -0.8, 0)
    sharp = np.clip(sharp, 0, 255).astype(np.uint8)

    # 4. Slight gamma brighten so mid-tone skin maps to readable chars
    gamma   = 0.75
    lut     = np.array([min(255, int((i / 255.0) ** gamma * 255)) for i in range(256)], dtype=np.uint8)
    result  = cv2.LUT(sharp, lut)

    return result


def remove_pure_white_bg(enhanced: np.ndarray, threshold: int = 240) -> np.ndarray:
    """
    Force pixels brighter than threshold to pure white (255).
    This separates background from subject so background → spaces in ASCII.
    """
    out = enhanced.copy()
    out[out >= threshold] = 255
    return out


def pixels_to_ascii(px: np.ndarray) -> list:
    """
    Map each pixel to a glyph.
    White (255) background → space character.
    Dark (0) pixels       → dense glyphs like @ # O X.
    """
    ramp     = GLYPH_RAMP
    ramp_len = len(ramp)
    rows     = []

    for row in px:
        line = ''
        for pixel in row:
            p = int(pixel)
            if p >= 248:              # pure/near-white background
                line += ' '
            else:
                # Invert: dark → high ramp index (dense glyph)
                inv = 255 - p
                idx = int(inv / 255.0 * (ramp_len - 1))
                idx = max(0, min(ramp_len - 1, idx))
                line += ramp[idx]
        rows.append(line)

    return rows


def build_svg(rows: list, out_path: str) -> None:
    """Generate animated cyberpunk SVG from ASCII rows."""
    num_rows = len(rows)
    max_cols = max(len(r) for r in rows) if rows else GRID_WIDTH

    svg_w = int(max_cols * LETTER_W + 20)
    svg_h = int(num_rows * LINE_HEIGHT + 20)

    tspan_parts = []
    for i, row in enumerate(rows):
        y = int(14 + i * LINE_HEIGHT)
        tspan_parts.append(
            '    <tspan x="10" y="{}">{}</tspan>'.format(y, sax.escape(row))
        )
    tspans_block = '\n'.join(tspan_parts)

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg"'
        ' viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
        '  <defs>\n'
        '    <style>\n'
        '      @keyframes revealDown {{\n'
        '        from {{ height: 0; }}\n'
        '        to   {{ height: {h}px; }}\n'
        '      }}\n'
        '      @keyframes cyberPulse {{\n'
        '        0%, 100% {{ opacity: .88; }}\n'
        '        50%       {{ opacity: 1.0; }}\n'
        '      }}\n'
        '      .ascii {{\n'
        '        font-family: "Courier New", Consolas, "Fira Code", monospace;\n'
        '        font-size: {fs}px;\n'
        '        font-weight: 700;\n'
        '        fill: {blue};\n'
        '        letter-spacing: .5px;\n'
        '        animation: cyberPulse 4s ease-in-out infinite;\n'
        '      }}\n'
        '    </style>\n'
        '    <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">\n'
        '      <feGaussianBlur stdDeviation=".5" result="b"/>\n'
        '      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>\n'
        '    </filter>\n'
        '    <clipPath id="rev">\n'
        '      <rect x="0" y="0" width="{w}" height="0">\n'
        '        <animate attributeName="height"\n'
        '                 from="0" to="{h}"\n'
        '                 dur="2.2s" fill="freeze"\n'
        '                 calcMode="spline"\n'
        '                 keySplines="0.2 1 0.3 1"/>\n'
        '      </rect>\n'
        '    </clipPath>\n'
        '  </defs>\n'
        '  <g clip-path="url(#rev)" filter="url(#glow)">\n'
        '    <text class="ascii" xml:space="preserve">\n'
        '{tspans}\n'
        '    </text>\n'
        '  </g>\n'
        '</svg>\n'
    ).format(w=svg_w, h=svg_h, fs=FONT_SIZE, blue=CYBER_BLUE, tspans=tspans_block)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg)

    print('[OK] portrait.svg saved -> {} cols x {} rows -> {}'.format(
        max_cols, num_rows, out_path))


def main():
    print('[+] Loading and cropping portrait...')
    gray = load_and_crop_portrait(INPUT_PATH)

    print('[+] Enhancing contrast for ASCII conversion...')
    enhanced = enhance_for_ascii(gray)

    print('[+] Cleaning background...')
    cleaned = remove_pure_white_bg(enhanced, threshold=242)

    # Resize to ASCII grid
    h, w = cleaned.shape
    aspect = h / float(w)
    grid_h = int(GRID_WIDTH * aspect * ASPECT_CORR)
    print('[+] Resizing to {}x{} ASCII grid...'.format(GRID_WIDTH, grid_h))
    resized = cv2.resize(cleaned, (GRID_WIDTH, grid_h), interpolation=cv2.INTER_AREA)

    print('[+] Converting pixels to ASCII characters...')
    rows = pixels_to_ascii(resized)

    print('[+] Building SVG...')
    build_svg(rows, OUTPUT_PATH)

    # Print a text preview to terminal
    print('\n--- ASCII PREVIEW (first 15 rows) ---')
    for r in rows[:15]:
        print(r)
    print('...')


if __name__ == '__main__':
    main()
