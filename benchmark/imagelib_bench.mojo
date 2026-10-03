from std.time import perf_counter_ns
from std.pathlib import Path
from image_reader import ImageBuffer, ImageReader, ImageReaderTrait
from std.sys import argv
from std.math import sqrt

def main():
    var args = argv()

    if len(args)<2:
        print("No input file specified")
        return

    var file_path = args[1]
    var iterations = 30

    if len(args) >= 3:
        try:
            iterations = Int(args[2])
        except e:
            iterations = 0

    if iterations <= 0:
        print("Invalid number of iterations: " + String(iterations) + ". Must be a positive integer.")
        return

    # Warm-up run
    var path = Path(file_path)
    try:
        var bytes = path.read_bytes()

        var reader = ImageReader(8)
        test(reader, bytes.copy(), iterations)
    except e:
        print(e)

def test[type: ImageReaderTrait](mut reader: type, bytes: List[UInt8], iterations: Int) raises:
    # Warm-up run
    _ = reader.read(bytes.copy())

    # Benchmark loop storing individual times in milliseconds
    var times = List[Float64]()
    for _ in range(iterations):
        var start = perf_counter_ns()
        _ = reader.read(bytes.copy())
        var end = perf_counter_ns()
        var elapsed_ms = Float64(end - start) / 1_000_000.0
        times.append(elapsed_ms)

    var n = len(times)
    if n == 0:
        print("Error: No measurements collected.")
        return

    # 1. Calculate Mean (required for standard deviation)
    var sum_val = 0.0
    for i in range(n):
        sum_val += times[i]
    var mean = sum_val / Float64(n)

    # 2. Calculate Sample Standard Deviation (matching Python's statistics.stdev)
    var stdev = 0.0
    if n > 1:
        var variance_sum = 0.0
        for i in range(n):
            var diff = times[i] - mean
            variance_sum += diff * diff
        stdev = sqrt(variance_sum / Float64(n - 1))

    # 3. Sort times to calculate median
    for i in range(n):
        for j in range(0, n - i - 1):
            if times[j] > times[j + 1]:
                var temp = times[j]
                times[j] = times[j + 1]
                times[j + 1] = temp

    # 4. Calculate Median
    var median_time: Float64
    if n % 2 == 1:
        median_time = times[n // 2]
    else:
        median_time = (times[n // 2 - 1] + times[n // 2]) / 2.0

    # Round values to 2 decimal places to match Python style
    var median_rounded = Float64(Int(median_time * 100.0 + 0.5)) / 100.0
    var stdev_rounded = Float64(Int(stdev * 100.0 + 0.5)) / 100.0

    # Print formatted results comparable to Python output
    print("  Mojo Median:", median_rounded, "ms (±", stdev_rounded, "ms)")