import os
import sys
import time
import webbrowser
from collections import deque
from datetime import datetime

import graphviz
import matplotlib.pyplot as plt
from sklearn.tree import _tree, export_graphviz

sys.path.append(os.path.join(os.path.dirname(__file__), "AxLS"))

from AxLS.circuit import Circuit
from AxLS.ml_algorithms.decision_tree import DecisionTreeCircuit
from AxLS.utils import read_dataset

### CONSTANTS
benchmark = "KS_16b"
RTL = f"AxLS/ALS-benchmark-circuits/{benchmark}/{benchmark}.v"
TECH = "NanGate15nm"

BENCHMARK_DIR = f"benchmarks/{benchmark}"
DATASET = f"{BENCHMARK_DIR}/10s_dataset"


BUILD_DIR = f"build/{benchmark}"
TB = f"{BUILD_DIR}/.tb.v"
APPROX_TB = f"{BUILD_DIR}/.approx_tb.v"
ORIGINAL_OUTPUT = f"{BUILD_DIR}/.exact_output"
APPROX_OUTPUT = f"{BUILD_DIR}/.approx_output"
APPROX_CIRCUIT = f"{BUILD_DIR}/.approx.v"

VALIDATION_DATASET = f"{BUILD_DIR}/.v_dataset"
VALIDATION_TB = f"{BUILD_DIR}/.v_tb.v"
VALIDATION_EXACT_OUTPUT = f"{BUILD_DIR}/.v_exact_output"
VALIDATION_APPROX_OUTPUT = f"{BUILD_DIR}/.v_approx_output"

SHOW_PROGRESS = False
VALIDATION = 0.2

### GET TRAINING DATA
print(f"Empezando ejemplo de filtro a las {datetime.now().strftime('%I:%M %p')}")

circuit = Circuit(RTL, "NanGate15nm")

with open(DATASET, "r") as file:
    total_lines = sum(1 for _ in file)
test_dataset_size = int(round((1 - VALIDATION) * total_lines))
circuit.write_tb(TB, DATASET, iterations=test_dataset_size, show_progress=SHOW_PROGRESS)

circuit.exact_output(TB, ORIGINAL_OUTPUT)
og_area = float(circuit.get_area())


### CREATE VALIDATION SET
def _copy_last_n_lines(input_file: str, output_file: str, n: int) -> None:
    """
    Copy the last N lines from an input file to an output file.

    Used to create a validation dataset from the original dataset.
    """
    with open(input_file, "r") as infile:
        last_n_lines = deque(infile, maxlen=n)

    with open(output_file, "w") as outfile:
        outfile.writelines(last_n_lines)


with open(DATASET, "r") as file:
    total_lines = sum(1 for _ in file)
validation_dataset_size = int(round(VALIDATION * total_lines))
_copy_last_n_lines(DATASET, VALIDATION_DATASET, validation_dataset_size)
circuit.write_tb(VALIDATION_TB, VALIDATION_DATASET, show_progress=SHOW_PROGRESS)
circuit.exact_output(VALIDATION_TB, VALIDATION_EXACT_OUTPUT)

### TRAIN TREE
outputs = read_dataset(ORIGINAL_OUTPUT, 10)
inputs = read_dataset(DATASET, 16, max_lines=len(outputs))

train_start_time = time.time()

clf = DecisionTreeCircuit(circuit.inputs, circuit.outputs, max_depth=3)

clf.train(inputs, outputs)

print(f"Finalizado entrenamiento, duró {time.time() - train_start_time}s")

clf.to_verilog_file(benchmark, APPROX_CIRCUIT)


### VERIFY CHARACTERISTICS
approx_circuit = Circuit(APPROX_CIRCUIT, "NanGate15nm", topmodule=benchmark)
approx_circuit.resynth()
mred = approx_circuit.simulate_and_compute_error(
    TB, ORIGINAL_OUTPUT, APPROX_OUTPUT, "mred"
)
approx_area = float(approx_circuit.get_area())
area = approx_area / og_area

v_mred = approx_circuit.simulate_and_compute_error(
    VALIDATION_TB, VALIDATION_EXACT_OUTPUT, VALIDATION_APPROX_OUTPUT, "mred"
)

print("\n---- Características de aproximación -----")
print(f"Error relativo: {mred * 100}%")
print(f"OG Area: {og_area:.1f}")
print(f"Approx Area: {approx_area:.1f}")
print(f"Área: {area * 100:.2f}%")

print("\n---- Validación -----")
print(f"Error relativo: {v_mred * 100}%")

print("\nVerifiqué que matchea manualmente con lo del informe ✅")

# =======================
# PROCESAMIENTO IMAGEN
# =======================


def sumar(a, b):
    if a > 0xFFFF or b > 0xFFFF or a < 0 or b < 0:
        raise ValueError("Operands must be 16-bit unsigned integers (0 to 65535)")

    a_bits = [int(x) for x in f"{a:016b}"]
    b_bits = [int(x) for x in f"{b:016b}"]
    input_bits = a_bits + b_bits  # 32 bits total

    output_bits = clf.clf.predict([input_bits])[0]
    result = int("".join(str(bit) for bit in output_bits), 2)

    return result


def show_tree(
    clf,
    filename,
    feature_names=None,
    class_names=None,
):
    dot_data = export_graphviz(
        clf,
        out_file=None,
        feature_names=feature_names,
        class_names=class_names,
        filled=True,
        rounded=True,
        special_characters=True,
        proportion=True,
        label="none",
    )

    graph = graphviz.Source(dot_data)
    filepath = f"{filename}.pdf"
    graph.render(filename=filename, format="pdf", cleanup=True)
    webbrowser.open("file://" + os.path.realpath(filepath))


def plot_custom_tree(
    clf, feature_names=None, max_depth=None, figsize=(12, 8), filename=None, show=True
):
    tree = clf.tree_
    feature_names = feature_names or [f"X[{i}]" for i in range(tree.n_features)]

    positions = {}
    labels = {}
    node_x_counter = [0]

    def recurse(node, depth=0):
        if max_depth is not None and depth > max_depth:
            return

        left = tree.children_left[node]
        right = tree.children_right[node]

        if left != _tree.TREE_LEAF:
            recurse(left, depth + 1)

        x = node_x_counter[0]
        node_x_counter[0] += 1
        y = -depth
        positions[node] = (x, y)

        if tree.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_names[tree.feature[node]]
            label = f"{name}"
        else:
            label = "Hoja"

        percent = (tree.n_node_samples[node] / tree.n_node_samples[0]) * 100
        label += f"\n{percent:.1f}% muestras"

        if tree.feature[node] == _tree.TREE_UNDEFINED:
            predicted_value = int(
                "".join([str(int(bit.argmax())) for bit in tree.value[node]]), 2
            )
            label += f"\nValor: {predicted_value}"

        labels[node] = label

        if right != _tree.TREE_LEAF:
            recurse(right, depth + 1)

    recurse(0)

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_axis_off()

    for node, (x, y) in positions.items():
        name = feature_names[tree.feature[node]]
        for child, condition in zip(
            [tree.children_left[node], tree.children_right[node]], [f"{name} = 0", f"{name} = 1"]
        ):
            if child != _tree.TREE_LEAF and child in positions:
                cx, cy = positions[child]
                ax.plot([x, cx], [y, cy], "k-", lw=1)

                # Add True/False labels in the middle of the edge
                mid_x = (x + cx) / 2
                mid_y = (y + cy) / 2
                ax.text(
                    mid_x,
                    mid_y,
                    condition,
                    ha="center",
                    va="center",
                    fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", lw=0.5),
                )

    for node, (x, y) in positions.items():
        ax.text(
            x,
            y,
            labels[node],
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="lightblue", ec="black", lw=1),
            fontsize=9,
        )

    all_x = [x for x, _ in positions.values()]
    all_y = [y for _, y in positions.values()]
    ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
    ax.set_ylim(min(all_y) - 1, max(all_y) + 1)

    plt.tight_layout()

    if filename is not None:
        fig.savefig(filename)

    if show:
        plt.show()


plot_custom_tree(
    clf.clf, feature_names=clf.circuit_inputs, filename=f"{BUILD_DIR}/tree.svg"
)
