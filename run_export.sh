#!/bin/bash

# Set target directory (defaults to current directory 'samples')
TARGET_DIR="${1:-samples}"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

echo "=================================================="
echo "Starting export tests in directory: $TARGET_DIR"
echo "=================================================="

# Recursively find image files (case-insensitive) with spaces support (-print0)
find "$TARGET_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.bmp" -o -iname "*.gif" \) -print0 | while IFS= read -r -d '' file; do
    echo ""
    echo "--------------------------------------------------"
    echo "Processing file: $file"
    echo "--------------------------------------------------"

    echo "--- Mojo Export Test ---"
    #mojo -I ./imagelib/ imagelib/image_reader/main.mojo "$file"
    ./build/imagelib_reader "$file" "export/$file.ppm"
done

echo ""
echo "=================================================="
echo "All exports successfully completed!"
echo "=================================================="