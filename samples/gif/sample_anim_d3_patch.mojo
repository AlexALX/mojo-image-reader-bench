from std.sys import argv

def patch_gif_disposal_to_3(input_path: String, output_path: String, target_frame_index: Int) raises:
    """
    Opens a GIF file, locates the Graphic Control Extension (0x21 0xF9 0x04)
    for the target frame, and rewrites its packed flags byte to Disposal Method = 3.
    """
    # 1. Read input file into a byte buffer
    var data: List[UInt8]
    with open(input_path, "r") as f:
        data = f.read_bytes()

    # Graphic Control Extension header: [Extension Introducer, GCE Label, Block Size]
    # In the GIF specification, this sequence is always: 0x21, 0xF9, 0x04
    var gce_marker: List[UInt8] = [0x21, 0xF9, 0x04]

    var current_gce_index = 0
    var patched = False
    var pos = 0
    var data_len = len(data)

    print("Searching for Graphic Control Extension blocks...")

    # 2. Scan byte stream for GCE headers
    while pos < data_len - 3:
        if data[pos] == gce_marker[0] and data[pos+1] == gce_marker[1] and data[pos+2] == gce_marker[2]:

            if current_gce_index == target_frame_index:
                # The Packed Fields byte is exactly 3 bytes after the marker start
                var packed_fields_pos = pos + 3
                var packed_byte = data[packed_fields_pos]

                # Disposal Method bitmask inside the packed fields byte:
                # Bits:  7   6 5 4   3   2 1 0
                # Fields: Reserved | Disposal | User Input | Trans Color Flag
                #
                # Step A: Clear existing disposal bits (3, 4, 5) using 0xE3 mask (11100011)
                # Step B: Set disposal method value to 3 (binary 011). Shift left by 2 bits (3 << 2 = 12 or 0x0C)
                var new_packed_byte = (packed_byte & 0xE3) | (3 << 2)

                # Write modified byte back into data array
                data[packed_fields_pos] = new_packed_byte

                print("[Success] GCE block for frame index", target_frame_index, "found at offset:", pos)
                print("Old packed byte:", hex(Int(packed_byte)), "-> New packed byte:", hex(Int(new_packed_byte)))
                patched = True
                break

            current_gce_index += 1
            pos += 3 # Skip header of the found block
        else:
            pos += 1

    # 3. Save output data if modification succeeded
    if patched:
        with open(output_path, "w") as f:
            f.write_bytes(data)
        print("[Done] Patch applied successfully. File saved as:", output_path)
    else:
        print("[Error] Could not find frame index", target_frame_index, ". Total frames found:", current_gce_index)
        raise Error("Target frame GCE block not found")

def main():
    # File configuration configuration defaults
    var input_file = "sample_anim_d3_not_pached.gif"
    var output_file = "sample_anim_d3.gif"

    # 3rd frame has index 2 (zero-based index)
    var target_index = 3

    try:
        patch_gif_disposal_to_3(input_file, output_file, target_index)
    except e:
        print("An error occurred while executing the script:", e)
