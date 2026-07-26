"""
Monochrome ASCII Portrait Generator for Cyberpunk GitHub Profile.

Converts `assets/photo-ready.png` into a futuristic blue ASCII art SVG portrait
with sequential row-drawing animations using SVG clipPath keyframes.

Output: portrait.svg
"""

import os
import xml.sax.saxutils as xml_escape
import numpy as np
import cv2
from PIL import Image

# Configuration Constants
INPUT_PHOTO_PATH = os.path.join("assets", "photo-ready.png")
OUTPUT_SVG_PATH = "portrait.svg"

# ASCII Glyph Ramp (from dark/space to heavy character)
GLYPH_RAMP = " '.,:;~+*xXO#"

# Grid & Font Dimensions
GRID_WIDTH = 58  # Number of ASCII columns
FONT_SIZE = 9    # Font size in pixels
LINE_HEIGHT = 10.5  # Vertical spacing per row
LETTER_SPACING = 5.2  # Horizontal spacing per char

# Color Palette
CYBER_BLUE_PRIMARY = "#3BA8FF"
CYBER_BLUE_GLOW = "#1F6FEB"


def load_and_preprocess_image(image_path: str, grid_width: int) -> np.ndarray:
    """
    Load image, calculate aspect ratio, and resize into a character grid array.

    Args:
        image_path (str): Path to photo-ready PNG.
        grid_width (int): Target character columns.

    Returns:
        np.ndarray: Grayscale pixel values matrix (2D).
    """
    if not os.path.exists(image_path):
        print(f"[!] Warning: {image_path} not found. Creating placeholder array...")
        # Create synthetic profile matrix
        height = int(grid_width * 1.1)
        synthetic = np.full((height, grid_width), 255, dtype=np.uint8)
        cv2.circle(synthetic, (grid_width // 2, height // 3), grid_width // 4, 40, -1)
        return synthetic

    img = Image.open(image_path).convert("L")
    w, h = img.size
    # Adjust for monospace character height-to-width ratio (~1.8 to 2.0)
    aspect_ratio = h / float(w)
    grid_height = int(grid_width * aspect_ratio * 0.52)

    img_resized = img.resize((grid_width, grid_height), Image.Resampling.LANCZOS)
    return np.array(img_resized)


def pixels_to_ascii(pixel_matrix: np.ndarray) -> list[str]:
    """
    Convert pixel intensity matrix into list of ASCII string rows.
    Inverts subject intensity so subject glows in blue on dark backgrounds.

    Args:
        pixel_matrix (np.ndarray): 2D array of grayscale pixels.

    Returns:
        list[str]: List of string lines containing ASCII characters.
    """
    ramp_length = len(GLYPH_RAMP)
    ascii_rows = []

    for row in pixel_matrix:
        line_chars = []
        for pixel in row:
            # Invert: dark pixels in photo become high index (heavy glyphs)
            inverted_intensity = 255 - pixel
            ramp_index = int((inverted_intensity / 255.0) * (ramp_length - 1))
            ramp_index = max(0, min(ramp_length - 1, ramp_index))
            line_chars.append(GLYPH_RAMP[ramp_index])
        ascii_rows.append("".join(line_chars))

    return ascii_rows


def generate_ascii_svg(ascii_rows: list[str], output_path: str) -> None:
    """
    Generate an animated cyberpunk SVG file with sequential row draw animation.

    Args:
        ascii_rows (list[str]): Lines of ASCII text.
        output_path (str): File path for portrait.svg output.
    """
    num_rows = len(ascii_rows)
    max_cols = max(len(row) for row in ascii_rows) if ascii_rows else GRID_WIDTH

    svg_width = int(max_cols * LETTER_SPACING + 20)
    svg_height = int(num_rows * LINE_HEIGHT + 30)

    # Escape XML characters (e.g. '<', '>', '&')
    escaped_rows = [xml_escape.escape(row) for row in ascii_rows]

    # Build text tspans
    tspan_elements = []
    for idx, row_text in enumerate(escaped_rows):
        y_pos = int(20 + idx * LINE_HEIGHT)
        tspan_elements.append(
            f'    <tspan x="10" y="{y_pos}">{row_text}</tspan>'
        )

    tspans_code = "\n".join(tspan_elements)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <defs>
    <style>
      @keyframes drawDown {{
        0% {{
          height: 0px;
        }}
        100% {{
          height: {svg_height}px;
        }}
      }}
      @keyframes subtlePulse {{
        0%, 100% {{
          opacity: 0.95;
        }}
        50% {{
          opacity: 1;
        }}
      }}
      .ascii-text {{
        font-family: 'Courier New', Consolas, 'Fira Code', monospace;
        font-size: {FONT_SIZE}px;
        font-weight: 700;
        fill: {CYBER_BLUE_PRIMARY};
        letter-spacing: 0.8px;
        dominant-baseline: alphabetic;
        animation: subtlePulse 3s infinite ease-in-out;
      }}
      .reveal-rect {{
        animation: drawDown 1.8s cubic-bezier(0.25, 1, 0.5, 1) forwards;
      }}
    </style>
    <filter id="cyber-glow" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="0.8" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <clipPath id="portrait-reveal-clip">
      <rect class="reveal-rect" x="0" y="0" width="{svg_width}" height="0">
        <animate attributeName="height" from="0" to="{svg_height}" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.25 1 0.5 1" />
      </rect>
    </clipPath>
  </defs>

  <!-- Animated ASCII Portrait Content -->
  <g clip-path="url(#portrait-reveal-clip)" filter="url(#cyber-glow)">
    <text class="ascii-text" xml:space="preserve">
{tspans_code}
    </text>
  </g>
</svg>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[OK] ASCII portrait SVG rendered successfully to: {output_path}")


def main() -> None:
    """Main rendering entry point."""
    print("[+] Processing photo into ASCII matrix...")
    pixel_matrix = load_and_preprocess_image(INPUT_PHOTO_PATH, GRID_WIDTH)
    ascii_rows = pixels_to_ascii(pixel_matrix)
    generate_ascii_svg(ascii_rows, OUTPUT_SVG_PATH)


if __name__ == "__main__":
    main()
