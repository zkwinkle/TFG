import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), "AxLS"))

from AxLS.circuit import Circuit

### CONSTANTS
benchmarks = ["BK_16b", "KS_16b", "CLA_16b", "CSkipA_16b", "LFA_16b"]
TECH = "NanGate15nm"

areas = []
for benchmark in benchmarks:
    RTL = f"AxLS/ALS-benchmark-circuits/{benchmark}/{benchmark}.v"

    circuit = Circuit(RTL, "NanGate15nm")
    og_area = float(circuit.get_area())
    areas.append(og_area)
    print(f"{benchmark}: {og_area}")


min_area = min(areas)
min_index = areas.index(min_area)
print(f"Lowest area is {benchmarks[min_index]} with {min_area}")
