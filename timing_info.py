# Script to get timing information how long it takes to synthesize and simulate
# each circuit. After executing it will print a dictionary of timing info that
# can be copy-pasted to other scripts.

import os
from pprint import pprint
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "AxLS"))

from AxLS.circuit import Circuit


class Benchmark:
    # If samples == 0 does an exhaustive set
    def __init__(self, name: str, input_bits: int):
        self.name = name
        self.input_bits = input_bits


def count_lines(file_path):
    with open(file_path, "rb") as f:
        line_count = sum(buf.count(b"\n") for buf in iter(lambda: f.read(4096), b""))
    return line_count


BENCHMARKS = [
    # name, input bits, validation set
    Benchmark("voter", 1001),
    Benchmark("RForest", 52 * 10),
    Benchmark("DTree", 10 * 30),
    Benchmark("max_128b", 128 * 4),
    Benchmark("adder_128b", 128 + 128),
    # ❌ duró más de 1h en simular (interrumpí temprano) Benchmark("hyp_128b", 128 + 128),
    Benchmark("barshift_128b", 128 + 7),
    # ❌ como en 10 mins avanzó 100 datos 😬 (duraría como 267 horas) Benchmark("sqrt_128b", 128),
    Benchmark("div_64b", 64 + 64),  # dura como ~70 mins
    # ❌ duraría como 4 horas Benchmark("mul_64b", 64 + 64),
    Benchmark("sobel", 9 * 9),
    Benchmark("square_64b", 64),
    Benchmark("BK_32b", 32 + 32),
    Benchmark("fwrdk2j", 32 + 32),
    # ❌ circuito no sintetiza bien Benchmark("invk2j", 32 + 32),
    Benchmark("KS_32b", 32 + 32),
    Benchmark("Mul_32b", 32 + 32),
    Benchmark("CLA_16b", 16 + 16 + 1),
    Benchmark("Mul_16b", 16 + 16),
    Benchmark("BK_16b", 16 + 16),
    Benchmark("CSkipA_16b", 16 + 16),
    Benchmark("KS_16b", 16 + 16),
    Benchmark("LFA_16b", 16 + 16),
    # ❌ duraría como 13 horas (???) Benchmark("log2_32b", 32),
    Benchmark("sin_24b", 24),
    Benchmark("WT_8b", 8 + 8),
    Benchmark("int2float", 11),
    Benchmark("fir", 8 + 1 + 1),
    Benchmark("RCA_4b", 4 + 4 + 1),
    Benchmark("dec", 8),
]

VALIDATION_PERCENT = 0.20
MAX_BITS_EXHAUSTIVE = 16
total_time = 0
DATASET_SIZE = 1000
SHOW_PROGRESS = False

results = {}

for benchmark in BENCHMARKS:
    rtl = f"AxLS/ALS-benchmark-circuits/{benchmark.name}/{benchmark.name}.v"
    build_dir = f"build/{benchmark.name}"
    dataset = f"{build_dir}/dataset"
    saif = f"{build_dir}/.saif"
    tb = f"{build_dir}/.tb.v"
    test_output = f"{build_dir}/.saif_tb_output"

    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    print(f"\nTiming benchmark {benchmark.name}")

    start_synth_time = time.time()
    circuit = Circuit(rtl, "NanGate15nm")
    end_synth_time = time.time()

    synth_time = end_synth_time - start_synth_time
    print(f"Synthetization time taken: {synth_time}")

    if benchmark.input_bits <= MAX_BITS_EXHAUSTIVE:
        size = 2**benchmark.input_bits
        print(f"Exhaustive dataset, {size} samples.")
        circuit.generate_dataset(dataset, size, "shuffle_bag")
        circuit.write_tb(tb, dataset, show_progress=SHOW_PROGRESS)
    else:
        size = DATASET_SIZE
        print(f"{size} samples")
        circuit.generate_dataset(dataset, size, "uniform")

        circuit.write_tb(tb, dataset, iterations=size, show_progress=SHOW_PROGRESS)

    print("Starting simulation...")
    start_sim_time = time.time()
    circuit.simulate(tb, test_output)
    end_sim_time = time.time()

    sim_time = end_sim_time - start_sim_time
    print(f"Simulation time: {sim_time}")

    time_per_sample = sim_time / size

    print(f"Seconds per sample simulated: {time_per_sample}")

    results[benchmark.name] = {
        "synth_time": synth_time,
        "sim_time": sim_time,
        "time_per_sample": time_per_sample,
        "samples": size,
    }


pprint(results)

# Add after execution dict here to copy-paste

results = {
    "BK_16b": {
        "samples": 1000,
        "sim_time": 0.04077649116516113,
        "synth_time": 0.26937270164489746,
        "time_per_sample": 4.077649116516113e-05,
    },
    "BK_32b": {
        "samples": 1000,
        "sim_time": 0.07310843467712402,
        "synth_time": 0.3550410270690918,
        "time_per_sample": 7.310843467712403e-05,
    },
    "CLA_16b": {
        "samples": 1000,
        "sim_time": 0.0439305305480957,
        "synth_time": 0.24657011032104492,
        "time_per_sample": 4.3930530548095705e-05,
    },
    "CSkipA_16b": {
        "samples": 1000,
        "sim_time": 0.041257619857788086,
        "synth_time": 0.2343900203704834,
        "time_per_sample": 4.1257619857788085e-05,
    },
    "DTree": {
        "samples": 1000,
        "sim_time": 0.14479851722717285,
        "synth_time": 0.8949270248413086,
        "time_per_sample": 0.00014479851722717284,
    },
    "KS_16b": {
        "samples": 1000,
        "sim_time": 0.05211949348449707,
        "synth_time": 0.29339003562927246,
        "time_per_sample": 5.211949348449707e-05,
    },
    "KS_32b": {
        "samples": 1000,
        "sim_time": 0.0912017822265625,
        "synth_time": 0.4713900089263916,
        "time_per_sample": 9.12017822265625e-05,
    },
    "LFA_16b": {
        "samples": 1000,
        "sim_time": 0.03991293907165527,
        "synth_time": 0.2514817714691162,
        "time_per_sample": 3.9912939071655276e-05,
    },
    "Mul_16b": {
        "samples": 1000,
        "sim_time": 0.984166145324707,
        "synth_time": 2.8256194591522217,
        "time_per_sample": 0.000984166145324707,
    },
    "Mul_32b": {
        "samples": 1000,
        "sim_time": 8.246580600738525,
        "synth_time": 12.945366859436035,
        "time_per_sample": 0.008246580600738525,
    },
    "RCA_4b": {
        "samples": 512,
        "sim_time": 0.017174720764160156,
        "synth_time": 0.19147253036499023,
        "time_per_sample": 3.3544376492500305e-05,
    },
    "RForest": {
        "samples": 1000,
        "sim_time": 3.8795690536499023,
        "synth_time": 9.732320785522461,
        "time_per_sample": 0.0038795690536499025,
    },
    "WT_8b": {
        "samples": 65536,
        "sim_time": 5.794118642807007,
        "synth_time": 0.35889363288879395,
        "time_per_sample": 8.84112341736909e-05,
    },
    "adder_128b": {
        "samples": 1000,
        "sim_time": 0.35483455657958984,
        "synth_time": 1.0747268199920654,
        "time_per_sample": 0.00035483455657958987,
    },
    "barshift_128b": {
        "samples": 1000,
        "sim_time": 0.7420856952667236,
        "synth_time": 2.8474745750427246,
        "time_per_sample": 0.0007420856952667236,
    },
    "dec": {
        "samples": 256,
        "sim_time": 0.04936504364013672,
        "synth_time": 0.31301283836364746,
        "time_per_sample": 0.00019283220171928406,
    },
    "div_64b": {
        "samples": 1000,
        "sim_time": 34.50052452087402,
        "synth_time": 75.75366640090942,
        "time_per_sample": 0.03450052452087402,
    },
    "fir": {
        "samples": 1024,
        "sim_time": 0.025197982788085938,
        "synth_time": 0.25740480422973633,
        "time_per_sample": 2.4607405066490173e-05,
    },
    "fwrdk2j": {
        "samples": 1000,
        "sim_time": 12.38129448890686,
        "synth_time": 26.67474341392517,
        "time_per_sample": 0.01238129448890686,
    },
    "int2float": {
        "samples": 2048,
        "sim_time": 0.07524633407592773,
        "synth_time": 0.36542606353759766,
        "time_per_sample": 3.674137406051159e-05,
    },
    "max_128b": {
        "samples": 1000,
        "sim_time": 1.0192341804504395,
        "synth_time": 2.7990400791168213,
        "time_per_sample": 0.0010192341804504395,
    },
    "sin_24b": {
        "samples": 1000,
        "sim_time": 7.965087413787842,
        "synth_time": 5.667546033859253,
        "time_per_sample": 0.007965087413787842,
    },
    "sobel": {
        "samples": 1000,
        "sim_time": 0.33495569229125977,
        "synth_time": 0.6936068534851074,
        "time_per_sample": 0.00033495569229125975,
    },
    "square_64b": {
        "samples": 1000,
        "sim_time": 17.519314765930176,
        "synth_time": 24.76021146774292,
        "time_per_sample": 0.017519314765930175,
    },
    "voter": {
        "samples": 1000,
        "sim_time": 7.31502366065979,
        "synth_time": 17.268110275268555,
        "time_per_sample": 0.00731502366065979,
    },
}

# Ordered list
slowest_to_fastest = [
    "div_64b",
    "square_64b",
    "fwrdk2j",
    "Mul_32b",
    "sin_24b",
    "voter",
    "RForest",
    "max_128b",
    "Mul_16b",
    "barshift_128b",
    "adder_128b",
    "sobel",
    "dec",
    "DTree",
    "KS_32b",
    "WT_8b",
    "BK_32b",
    "KS_16b",
    "CLA_16b",
    "CSkipA_16b",
    "BK_16b",
    "LFA_16b",
    "int2float",
    "RCA_4b",
    "fir",
]
