from datetime import datetime
import os
from pprint import pprint
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "AxLS"))

from AxLS.configuration import ApproxSynthesisConfig
from AxLS.runner import Results, run
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
    # name, input bits
    Benchmark("voter", 1001),
    Benchmark("RForest", 52 * 10),
    Benchmark("DTree", 10 * 30),
    Benchmark("max_128b", 128 * 4),
    Benchmark("adder_128b", 128 + 128),
    # ❌ no sirve? o es tan lento que no lo he visto iterar 1 sample Benchmark("hyp_128b", 128 + 128),
    Benchmark("barshift_128b", 128 + 7),
    # ❌ como en 10 mins avanzó 100 datos 😬  Benchmark("sqrt_128b", 128),
    Benchmark("div_64b", 64 + 64),
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
    # ❌ no puede generar el output exacto, tira puras X Benchmark("fir", 8 + 1 + 1),
    Benchmark("RCA_4b", 4 + 4 + 1),
    Benchmark("dec", 8),
]

METHODS = ["inconst", "outconst", "probprun", "decision_tree"]
METRICS = ["mred", "med", "hd", "wce", "time", "area"]
TECH = "NanGate15nm"
VALIDATION_PERCENT = 0.20
MAX_BITS_EXHAUSTIVE = 16
ERROR_THRESHOLDS = [ 0.01, 0.05, 0.1 ]

def print_results(config, results_tuple: tuple[Results, Results | None]):
    (results, validation_results) = results_tuple

    print("\n---- Results -----")
    for metric in config.metrics:
        value = results[metric]
        print(f"{metric.value}: {metric.to_user_friendly_display(value)}")

    if validation_results:
        print("\n---- Results on Validation Set -----")
        for metric, value in validation_results.items():
            print(f"{metric.value}: {metric.to_user_friendly_display(value)}")



def validation(benchmark) -> float:
    if benchmark.input_bits <= MAX_BITS_EXHAUSTIVE:
        return 0.0
    else:
        return VALIDATION_PERCENT

def metrics(benchmark) -> list[str]:
    if benchmark.name in {"div_64b", "Mul_32b"}:
        # Por alguna razón esto falla para estos circuitos 🤷🏻‍♀️ a pesar de revisar
        # que todos los valores leídos fueran int.
        # Para div_64b:
          # TypeError: unsupported operand type(s) for ^: 'int' and 'float'
        # Para Mul_32b:
          # TypeError: unsupported operand type(s) for ^: 'float' and 'float'
        return [m for m in METRICS if m != "hd"]
    else:
        return METRICS


def dt_benchmark(benchmark: Benchmark, rtl: str, dataset: str):
    # Synth time probando con adder_128:
    # - max_depth=8: 12s
    # - max_depth=12: 221s (pero resynth duró aún más?)
    # Primero probar max_depths más pequeños y luego ver para qué circuitos
    # podrían servir más grandes.
    MAX_DEPTHS = [3, 5, 8]

    CSV = "dt_results.csv"

    for max_depth in MAX_DEPTHS:
        for resynthesis in [False, True]:
            for one_tree_per_output in [False, True]:
                config = ApproxSynthesisConfig(
                    method="decision_tree",
                    circuit=Circuit(rtl, TECH),
                    dataset=dataset,
                    metrics=metrics(benchmark),
                    resynthesis=resynthesis,
                    max_depth=max_depth,
                    one_tree_per_output=one_tree_per_output,
                    validation=validation(benchmark),
                    csv=CSV,
                )
                print(f"{datetime.now().strftime('%I:%M %p')}: Configuration loaded successfully, starting decision_tree execution...")

                results = run(config)

                print("Finished execution:")
                print(f"- circuit: {benchmark.name}")
                print(f"- max_depth: {max_depth}")
                print(f"- resynthesis: {resynthesis}")
                print(f"- one_tree_per_output: {one_tree_per_output}")

                print_results(config, results)


def inconst_benchmark(benchmark: Benchmark, rtl: str, dataset: str):
    CSV = "inconst_results.csv"

    for error in ERROR_THRESHOLDS:
        config = ApproxSynthesisConfig(
            method="inconst",
            circuit=Circuit(rtl, TECH),
            dataset=dataset,
            metrics=metrics(benchmark),
            resynthesis=True,
            error=error,
            validation=validation(benchmark),
            csv=CSV,
        )
        print(f"{datetime.now().strftime('%I:%M %p')}: Configuration loaded successfully, starting inconst execution...")

        results = run(config)

        print("Finished execution:")
        print(f"- circuit: {benchmark.name}")
        print(f"- error: {error}")

        print_results(config, results)

def outconst_benchmark(benchmark: Benchmark, rtl: str, dataset: str):
    CSV = "outconst_results.csv"

    for error in ERROR_THRESHOLDS:
        config = ApproxSynthesisConfig(
            method="outconst",
            circuit=Circuit(rtl, TECH),
            dataset=dataset,
            metrics=metrics(benchmark),
            resynthesis=True,
            error=error,
            validation=validation(benchmark),
            csv=CSV,
        )
        print(f"{datetime.now().strftime('%I:%M %p')}: Configuration loaded successfully, starting inconst execution...")

        results = run(config)

        print("Finished execution:")
        print(f"- circuit: {benchmark.name}")
        print(f"- error: {error}")

        print_results(config, results)


total_time = 0
for benchmark in BENCHMARKS:
    rtl = f"AxLS/ALS-benchmark-circuits/{benchmark.name}/{benchmark.name}.v"
    benchmark_dir = f"benchmarks/{benchmark.name}"
    dataset = f"{benchmark_dir}/dataset"
    saif = f"{benchmark_dir}/.saif"
    test_output = f"{benchmark_dir}/.saif_tb_output"
    show_progress = False

    print(f"Execution for benchmark {benchmark.name} starting at {datetime.now().strftime('%I:%M %p')}")

    start_time = time.time()

    # dt_benchmark(benchmark, rtl, dataset)
    inconst_benchmark(benchmark, rtl, dataset)
    outconst_benchmark(benchmark, rtl, dataset)

    iteration_time = time.time() - start_time
    total_time += iteration_time

    print(f"Benchmark time: {iteration_time}")
    print(f"Total time: {total_time}")
