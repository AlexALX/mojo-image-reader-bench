import os
# Limit the number of threads for C-library backends (OpenMP, MKL, etc.) to 1
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import time
import subprocess
import statistics
from PIL import Image
import numpy as np
import os
import sys

if len(sys.argv) < 2:
    print("No input file specified")
    sys.exit(1)

# Configuration paths and settings
TEST_IMAGE = sys.argv[1]

ITERATIONS = 30

# Number of iterations for statistical stability
if len(sys.argv) > 2:
    try:
        ITERATIONS = int(sys.argv[2])
    except ValueError:
        ITERATIONS = 0

    if ITERATIONS <= 0:
        print(f"Invalid number of iterations: {ITERATIONS}. Must be a positive integer.")
        sys.exit(1)


def get_pillow_ppm_bytes(jpeg_bytes: bytes) -> bytes:
    """
    Decodes JPEG bytes using Pillow and serializes the image into
    Raw PPM (P6 format) bytes to match the exact output format of Mojo.
    """
    import io
    with Image.open(io.BytesIO(jpeg_bytes)) as img:
        mode = img.mode

        if mode == '1':
            target_mode = 'L'
        elif mode in ('L', 'LA', 'RGB', 'RGBA'):
            target_mode = mode
        elif mode == 'P':
            if 'transparency' in img.info:
                target_mode = 'RGBA'
            else:
                target_mode = 'RGB'
        else:
            target_mode = 'RGBA' if 'A' in mode else 'RGB'

        if img.mode != target_mode:
            img = img.convert(target_mode)

        width, height = img.size
        pixels = img.tobytes()

        # Construct P6 PPM header: "P6\nWIDTH HEIGHT\n255\n"
        #header = f"P6\n{width} {height}\n255\n".encode('ascii')
        return pixels

def benchmark_pillow(jpeg_bytes: bytes) -> tuple[float, float]:
    """
    Measures the pure decoding and PPM conversion time for Pillow + NumPy.
    """
    # Warm-up run
    _ = get_pillow_ppm_bytes(jpeg_bytes)

    times = []
    for _ in range(ITERATIONS):
        start = time.perf_counter()
        _ = get_pillow_ppm_bytes(jpeg_bytes)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to milliseconds

    return statistics.median(times), statistics.stdev(times) if len(times) > 1 else 0.0

def main():
    if not os.path.exists(TEST_IMAGE):
        print(f"Error: Test image '{TEST_IMAGE}' not found!")
        return

    # Preload JPEG bytes into memory to isolate processing performance from disk I/O
    with open(TEST_IMAGE, "rb") as f:
        jpeg_bytes = f.read()

    try:
        pil_median, pil_std = benchmark_pillow(jpeg_bytes)
        print(f"  Pillow Median: {pil_median:.2f} ms (±{pil_std:.2f} ms)")
    except Exception as e:
        print(f"Error during Pillow benchmark: {e}")
        return

if __name__ == "__main__":
    main()