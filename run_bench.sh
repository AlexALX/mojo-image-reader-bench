#!/bin/bash

# Set target directory (defaults to current directory 'samples')
TARGET_DIR="${1:-samples}"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

echo "=================================================="
echo "Starting benchmarks in directory: $TARGET_DIR"
echo "=================================================="

# Recursively find image files (case-insensitive) with spaces support (-print0)
find "$TARGET_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.bmp" -o -iname "*.gif" \) -print0 | while IFS= read -r -d '' file; do
    echo ""
    echo "--------------------------------------------------"
    echo "Processing file: $file"
    echo "--------------------------------------------------"

    echo "--- Mojo Benchmark ---"
    #mojo -I ./imagelib/ benchmark/imagelib_bench.mojo "$file" 100 bench
    ./build/imagelib_bench "$file" 100 bench

    echo "--- Pillow Benchmark ---"
    python benchmark/pillow.py "$file" 100 bench
done

echo ""
echo "=================================================="
echo "All benchmarks successfully completed!"
echo "=================================================="