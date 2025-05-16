import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'AxLS'))

from AxLS.circuit import Circuit


class Benchmark:
    # If samples == 0 does an exhaustive set
    def __init__(self, name: str, input_bits: int):
        self.name = name
        self.input_bits = input_bits


BENCHMARKS = [
    # name, input bits, validation set
    Benchmark("voter", 1001),
    Benchmark("RForest", 52 * 10),
    Benchmark("DTree", 10 * 30),
    Benchmark("max_128b", 128 * 4),
    Benchmark("adder_128b", 128 + 128),
    Benchmark("hyp_128b", 128 + 128),
    Benchmark("barshift_128b", 128 + 7),
    Benchmark("sqrt_128b", 128),
    Benchmark("div_64b", 64 + 64),
    Benchmark("mul_64b", 64 + 64),
    Benchmark("sobel", 9 * 9),
    Benchmark("square_64b", 64),
    Benchmark("BK_32b", 32 + 32),
    Benchmark("fwrdk2j", 32 + 32),
    Benchmark("invk2j", 32 + 32),
    Benchmark("KS_32b", 32 + 32),
    Benchmark("Mul_32b", 32 + 32),
    Benchmark("CLA_16b", 16 + 16 + 1),
    Benchmark("Mul_16b", 16 + 16),
    Benchmark("BK_16b", 16 + 16),
    Benchmark("CSkipA_16b", 16 + 16),
    Benchmark("KS_16b", 16 + 16),
    Benchmark("LFA_16b", 16 + 16),
    Benchmark("log2_32b", 32),
    Benchmark("sin_24b", 24),
    Benchmark("WT_8b", 8 + 8),
    Benchmark("int2float", 11),
    Benchmark("fir", 8 + 1 + 1),
    Benchmark("RCA_4b", 4 + 4 + 1),
    Benchmark("dec", 8),
]

# Problema: probprun podría usar menos info para el SAIF para poder hacer validación. Pero entonces estaría difícil usar el vcd2file de rust.
# Porque tendría que hacer simulación on the go para generar el vcd del dataset de validación, bueno not really. Ocuparía poder pasarle un validation saif tho??
# Pero mae, qué putas?
# Nono creo que no... porque no estaríamos probando el probprun estaríamos evaluando el rendimiento del circuito que ya se creó.
# OK pero entonces para eso ocupo hacer manualmente testbenches que solo toquen el set de datos de prueba para generar el vcd.
# Y el pedazo de validación usado tiene que matchear.
# Eso sería más a la segura si el flag de validación aceptara un set de datos aparte en vez de un %....
# Bueno, podría también aceptar un archivo aparte de un %!!
# Pero IDK no quiero generar todos esos pares de sets de datos diferentes, creo que mejor solo hago que el % matchee entre los SAIFs y la validación que le paso a la
# herramienta.

VALIDATION_PERCENT = 0.20
MAX_BITS_EXHAUSTIVE = 16

for benchmark in BENCHMARKS:
    rtl = f"AxLS/ALS-benchmark-circuits/{benchmark.name}/{benchmark.name}.v"
    benchmark_dir = f"benchmarks/{benchmark.name}"
    dataset = f"{benchmark_dir}/dataset"

    print(f"Generating dataset for benchmark {benchmark.name}")

    circuit = Circuit(rtl, "NanGate15nm")

    if not os.path.exists(benchmark_dir):
        os.makedirs(benchmark_dir)

    if benchmark.input_bits <= MAX_BITS_EXHAUSTIVE:
        print(f"Exhaustive dataset, {2**benchmark.input_bits} samples.")
        circuit.generate_dataset(dataset, 2**benchmark.input_bits, "shuffle_bag")
    elif benchmark.input_bits <= 128:
        print("1 million samples")
        circuit.generate_dataset(dataset, 1_000_000, "uniform")
    else:
        print("10 million samples")
        circuit.generate_dataset(dataset, 10_000_000, "uniform")
