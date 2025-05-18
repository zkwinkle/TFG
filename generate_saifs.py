from datetime import datetime
import os
import subprocess
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'AxLS'))

from AxLS.circuit import Circuit


class Benchmark:
    # If samples == 0 does an exhaustive set
    def __init__(self, name: str, input_bits: int):
        self.name = name
        self.input_bits = input_bits

def count_lines(file_path):
    with open(file_path, 'rb') as f:
        line_count = sum(buf.count(b'\n') for buf in iter(lambda: f.read(4096), b''))
    return line_count



print(f"Execution starting at {datetime.now().strftime('%I:%M %p')}")
BENCHMARKS = [
    # name, input bits, # vcd2saif time
    Benchmark("voter", 1001), # 9mins (549.53)
    # Benchmark("RForest", 52 * 10), # 6mins (343.29)
    # Benchmark("DTree", 10 * 30), # 1.5 mins (80.87)
    Benchmark("max_128b", 128 * 4), # 4.5mins (273.32)
    Benchmark("adder_128b", 128 + 128), # 1.5min (109.61)
    # ❌ no sirve? o es tan lento que no lo he visto iterar 1 sample Benchmark("hyp_128b", 128 + 128),
    Benchmark("barshift_128b", 128 + 7), # 3min (203.19)
    # ❌ como en 10 mins avanzó 100 datos 😬  Benchmark("sqrt_128b", 128),
    # Benchmark("div_64b", 64 + 64), # 20mins... (1201.76)
    # ❌ duraría como 4 horas Benchmark("mul_64b", 64 + 64),
    # Benchmark("sobel", 9 * 9), # 1.5mins (88.06s)
    Benchmark("square_64b", 64), # 17mins... (1027.07)
    # Benchmark("BK_32b", 32 + 32), # 30.86
    # Benchmark("fwrdk2j", 32 + 32), # 8mins... (487.46)
    # ❌ circuito no sintetiza bien Benchmark("invk2j", 32 + 32),
    # Benchmark("KS_32b", 32 + 32), # 36.82
    # Benchmark("Mul_32b", 32 + 32), # 8.5mins (507.08)
    # Benchmark("CLA_16b", 16 + 16 + 1), # 13.65
    # Benchmark("Mul_16b", 16 + 16), # 3.5mins (221.48)
    # Benchmark("BK_16b", 16 + 16), # 13.29
    # Benchmark("CSkipA_16b", 16 + 16), # 13.28
    # Benchmark("KS_16b", 16 + 16), # 17.00
    # Benchmark("LFA_16b", 16 + 16), # 13.67
    # ❌ duraría como 13 horas (???) Benchmark("log2_32b", 32),
    # Benchmark("sin_24b", 24), # 2mins (137.59)
    # Benchmark("WT_8b", 8 + 8), # 5mins (321.15)
    # Benchmark("int2float", 11), # 1.31
    Benchmark("fir", 8 + 1 + 1), # ⚠️vcd2saif error (looks like it generates an invalid value once in a while: Invalid bitstring: 0xxxxxxxz)
    # Benchmark("RCA_4b", 4 + 4 + 1), #0.04
    Benchmark("dec", 8), # 0.61
]
# Took about 1h4min to execute the first time, where 7 of the benchmarks errored
# out during vcd2saif
# Second execution with fixed vcd2saif and benchmarks that couldn't complete
# took 37mins, in total looks like generating saifs adjusting for a 2s
# simulation takes 1h41m in total.


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
#
## Conclusión:
# Voy a generar testbenches que usen el set de datos y matchear el % de
# validación cuando lo ejecute, menos archivos y menos tener que agregar cambios
# a la herramienta.

VALIDATION_PERCENT = 0.20
MAX_BITS_EXHAUSTIVE = 16
TIME_PER_SIM = 10 #10s
total_time = 0

for benchmark in BENCHMARKS:
    rtl = f"AxLS/ALS-benchmark-circuits/{benchmark.name}/{benchmark.name}.v"
    benchmark_dir = f"benchmarks/{benchmark.name}"
    dataset = f"{benchmark_dir}/dataset"
    vcd = f"{benchmark_dir}/.vcd"
    saif = f"{benchmark_dir}/.saif"
    tb = f"{benchmark_dir}/.vcd_tb.v"
    test_output = f"{benchmark_dir}/.saif_tb_output"
    show_progress = False

    print(f"\nGenerating SAIF for benchmark {benchmark.name}")

    start_time = time.time()

    circuit = Circuit(rtl, "NanGate15nm")

    if benchmark.input_bits <= MAX_BITS_EXHAUSTIVE:
        print("Exhaustive dataset using full set.")

        circuit.write_tb(tb, dataset, dump_vcd=vcd, show_progress=show_progress)
    else:
        with open(dataset) as f:
            samples = sum(1 for _ in f)

        print(f"Total samples: {samples}")

        test_set_samples = int(round((1 - VALIDATION_PERCENT) * samples))
        print(f"Using test dataset only, the first {test_set_samples} samples.")

        circuit.write_tb(tb, dataset, iterations=test_set_samples, dump_vcd=vcd, show_progress=show_progress)

    print("Starting simulation...")
    start_sim_time = time.time()
    circuit.simulate(tb, test_output)
    print(f"Simulation time: {time.time() - start_sim_time}")

    print("Calling vcd2saif...")
    start_vcd2saif_time = time.time()
    subprocess.run(['./vcd2saif_rs/target/release/vcd2saif_rs', benchmark.name, vcd, saif])
    print(f"vcd2saif time: {time.time() - start_vcd2saif_time}")

    iteration_time = time.time() - start_time
    total_time += iteration_time

    print(f"Time taken for {benchmark.name}: {iteration_time:.2f} seconds")
    print(f"Total time so far: {total_time:.2f} seconds")
