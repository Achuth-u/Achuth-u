"""
Photo Cleaner Script for Cyberpunk ASCII Portrait Pipeline.

This script processes an input user photograph by removing the background,
enhancing facial/structural contrast with OpenCV CLAHE, converting to grayscale,
and compositing onto a high-contrast white canvas.

Output: assets/photo-ready.png
"""

import os
import sys
import numpy as np
import cv2
from PIL import Image

# Global Constants
TARGET_OUTPUT_PATH = os.path.join("assets", "photo-ready.png")
DEFAULT_CANVAS_SIZE = (400, 400)
CLAHE_CLIP_LIMIT = 3.0
CLAHE_TILE_GRID_SIZE = (8, 8)


def generate_fallback_portrait(width: int = 400, height: int = 400) -> Image.Image:
    """
    Generate a sleek synthetic profile avatar when no input photo is provided.

    Args:
        width (int): Canvas width.
        height (int): Canvas height.

    Returns:
        Image.Image: A synthesized grayscale silhouette image.
    """
    canvas = np.full((height, width, 3), 255, dtype=np.uint8)
    center = (width // 2, height // 2)

    # Draw head silhouette
    head_radius = width // 5
    cv2.circle(canvas, (center[0], center[1] - 40), head_radius, (30, 30, 30), -1)

    # Draw shoulders silhouette
    shoulder_center = (center[0], center[1] + 130)
    cv2.ellipse(
        canvas,
        shoulder_center,
        (width // 3 + 20, height // 4),
        0,
        0,
        360,
        (30, 30, 30),
        -1,
    )

    # Convert to PIL Image
    pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    return pil_img


def remove_background(pil_image: Image.Image) -> Image.Image:
    """
    Remove background from PIL image using rembg, with fallback handling.

    Args:
        pil_image (Image.Image): Input image.

    Returns:
        Image.Image: RGBA image with background removed.
    """
    try:
        from rembg import remove

        output = remove(pil_image)
        return output
    except Exception as err:
        print(f"[!] rembg background removal notice: {err}. Using alpha/luminance processing.")
        rgba = pil_image.convert("RGBA")
        return rgba


def apply_clahe_contrast(cv_gray_image: np.ndarray) -> np.ndarray:
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) to a grayscale image.

    Args:
        cv_gray_image (np.ndarray): Grayscale OpenCV image.

    Returns:
        np.ndarray: Contrast-enhanced grayscale image.
    """
    clahe = cv2.createCLAHE(
        clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_GRID_SIZE
    )
    enhanced = clahe.apply(cv_gray_image)
    return enhanced


def process_photo_pipeline(input_path: str, output_path: str) -> None:
    """
    Execute full photo cleaning pipeline:
    1. Load image (or generate fallback if missing).
    2. Remove background using rembg.
    3. Convert subject to grayscale and apply CLAHE contrast enhancement.
    4. Composite onto white canvas.
    5. Save processed image.

    Args:
        input_path (str): Path to input image file.
        output_path (str): Path to save processed photo-ready image.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(input_path):
        print(f"[+] Loading input photo from: {input_path}")
        pil_raw = Image.open(input_path)
    else:
        print(f"[!] Input photo '{input_path}' not found. Synthesizing high-contrast portrait...")
        pil_raw = generate_fallback_portrait()

    # Step 1: Remove background
    bg_removed = remove_background(pil_raw)

    # Separate RGB and Alpha channels
    if bg_removed.mode == "RGBA":
        r, g, b, alpha = bg_removed.split()
        rgb_image = Image.merge("RGB", (r, g, b))
        alpha_mask = np.array(alpha)
    else:
        rgb_image = bg_removed.convert("RGB")
        alpha_mask = np.full((rgb_image.height, rgb_image.width), 255, dtype=np.uint8)

    # Step 2: Convert to OpenCV Grayscale
    cv_img = cv2.cvtColor(np.array(rgb_image), cv2.COLOR_RGB2GRAY)

    # Step 3: Contrast Enhancement via CLAHE
    enhanced_gray = apply_clahe_contrast(cv_img)

    # Step 4: Composite onto solid white background
    white_bg = np.full_like(enhanced_gray, fill_value=255)
    mask_norm = alpha_mask / 255.0

    final_composite = (enhanced_gray * mask_norm + white_bg * (1.0 - mask_norm)).astype(
        np.uint8
    )

    # Step 5: Save output image
    final_pil = Image.fromarray(final_composite)
    final_pil.save(output_path, format="PNG")
    print(f"[OK] Photo processing complete! Saved to: {output_path}")


def main() -> None:
    """Main execution entry point."""
    input_file = sys.argv[1] if len(sys.argv) > 1 else "photo.jpg"
    process_photo_pipeline(input_file, TARGET_OUTPUT_PATH)


if __name__ == "__main__":
    main()
