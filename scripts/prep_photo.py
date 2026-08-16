"""
prep_photo.py
Turns a normal photo into a clean, high-contrast grayscale image ready
for ASCII conversion:
  1. Remove background (rembg) so only the subject remains.
  2. Boost local contrast with CLAHE so flat lighting gets real
     highlights/shadows.
  3. Composite onto pure white so background maps to blank ASCII space.

Usage:
    python scripts/prep_photo.py source-photo.jpg
"""

import sys
import io
import numpy as np
import cv2
from PIL import Image
from rembg import remove


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/prep_photo.py <photo.jpg>")

    in_path = sys.argv[1]
    out_path = "source-prepped.png"

    with open(in_path, "rb") as f:
        input_bytes = f.read()

    print("Removing background...")
    result_bytes = remove(input_bytes)
    fg = Image.open(io.BytesIO(result_bytes)).convert("RGBA")

    # composite the transparent-background cutout onto pure white
    white_bg = Image.new("RGBA", fg.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, fg).convert("RGB")

    # convert to grayscale numpy array for CLAHE
    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)

    print("Boosting local contrast (CLAHE)...")
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)

    Image.fromarray(contrasted).save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()