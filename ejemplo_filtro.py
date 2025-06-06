import os
import random
import sys
import time
from datetime import datetime

import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from AxLS.circuiterror import compute_error

sys.path.append(os.path.join(os.path.dirname(__file__), "AxLS"))

from AxLS.circuit import Circuit
from AxLS.ml_algorithms.decision_tree import DecisionTreeCircuit
from AxLS.utils import read_dataset

### CONSTANTS
benchmark = "BK_16b"
RTL = f"AxLS/ALS-benchmark-circuits/{benchmark}/{benchmark}.v"
TECH = "NanGate15nm"


BUILD_DIR = f"build/{benchmark}"
DATASET = f"{BUILD_DIR}/12bit_dataset"
TB = f"{BUILD_DIR}/.tb.v"
APPROX_TB = f"{BUILD_DIR}/.approx_tb.v"
ORIGINAL_OUTPUT = f"{BUILD_DIR}/.exact_output"
APPROX_OUTPUT = f"{BUILD_DIR}/.approx_output"
APPROX_CIRCUIT = f"{BUILD_DIR}/.approx.v"

SHOW_PROGRESS = False

print(f"Empezando ejemplo de filtro a las {datetime.now().strftime('%I:%M %p')}")


### GET TRAINING DATA
def generate_sparse_pairs(threshold=300, max_val=4080, sparse_count=3_000):
    # Full pairs for the lower range
    dense_pairs = [[i, j] for i in range(threshold) for j in range(threshold)]

    # Sparse random pairs for the full range
    sparse_pairs = set()
    while len(sparse_pairs) < sparse_count:
        i = random.randint(0, max_val - 1)
        j = random.randint(0, max_val - 1)
        if i >= threshold or j >= threshold:
            sparse_pairs.add((i, j))

    # Combine and return
    return dense_pairs + [list(pair) for pair in sparse_pairs]


def save_pairs_to_file(filename, pairs):
    with open(filename, "w") as f:
        for a, b in pairs:
            f.write(f"{a:02X} {b:02X}\n")


inputs = generate_sparse_pairs()
save_pairs_to_file(DATASET, inputs)

circuit = Circuit(RTL, "NanGate15nm")
circuit.write_tb(TB, DATASET, show_progress=SHOW_PROGRESS)
circuit.exact_output(TB, ORIGINAL_OUTPUT)
og_area = float(circuit.get_area())
outputs = read_dataset(ORIGINAL_OUTPUT, 10)

### TRAIN TREE
train_start_time = time.time()

MAX_DEPTH = 3
ONE_TREE_PER_OUTPUT = False
# for MAX_DEPTH in [3, 4, 5]:
#     for ONE_TREE_PER_OUTPUT in [True, False]:
for MAX_DEPTH in [ 4]:
    for ONE_TREE_PER_OUTPUT in [False]:

        clf = DecisionTreeCircuit(
            circuit.inputs,
            circuit.outputs,
            max_depth=MAX_DEPTH,
            one_tree_per_output=ONE_TREE_PER_OUTPUT,
        )

        clf.train(inputs, outputs)

        print(f"Finalizado entrenamiento, duró {time.time() - train_start_time}s")

        clf.to_verilog_file(benchmark, APPROX_CIRCUIT)

### VERIFY CHARACTERISTICS
        approx_circuit = Circuit(APPROX_CIRCUIT, "NanGate15nm", topmodule=benchmark)
        approx_circuit.resynth()
        mred = approx_circuit.simulate(TB, APPROX_OUTPUT)
        mred = compute_error("mred", ORIGINAL_OUTPUT, APPROX_OUTPUT)
        med = compute_error("med", ORIGINAL_OUTPUT, APPROX_OUTPUT)
        approx_area = float(approx_circuit.get_area())
        area = approx_area / og_area

# =======================
# PROCESAMIENTO IMAGEN
# =======================


        def sumar(a, b):
            if a > 0xFFFF or b > 0xFFFF or a < 0 or b < 0:
                raise ValueError("Operands must be 16-bit unsigned integers (0 to 65535)")

            a_bits = [int(x) for x in f"{a:016b}"]
            b_bits = [int(x) for x in f"{b:016b}"]
            input_bits = a_bits + b_bits  # 32 bits total

            if isinstance(clf.clf, list):
                output_bits = [dt.predict([input_bits])[0] for dt in clf.clf]
            else:
                output_bits = clf.clf.predict([input_bits])[0]
            result = int("".join(str(bit) for bit in output_bits), 2)

            return result


        def apply_gaussian_filter(img: np.ndarray, custom_add):
            if img.ndim == 2:  # grayscale
                img = img[..., None]  # shape (H, W, 1)

            h, w, c = img.shape
            out = np.zeros_like(img)

            for ch in range(c):
                print("channel", ch)
                for i in range(1, h - 1):
                    print("row", i)
                    for j in range(1, w - 1):
                        val = 0

                        val = custom_add(val, img[i - 1, j - 1, ch].astype(np.uint16))  # 1
                        val = custom_add(val, img[i - 1, j, ch].astype(np.uint16) << 1)  # 2
                        val = custom_add(val, img[i - 1, j + 1, ch].astype(np.uint16))  # 1

                        val = custom_add(val, img[i, j - 1, ch].astype(np.uint16) << 1)  # 2
                        val = custom_add(val, img[i, j, ch].astype(np.uint16) << 2)  # 4
                        val = custom_add(val, img[i, j + 1, ch].astype(np.uint16) << 1)  # 2

                        val = custom_add(val, img[i + 1, j - 1, ch].astype(np.uint16))  # 1
                        val = custom_add(val, img[i + 1, j, ch].astype(np.uint16) << 1)  # 2
                        val = custom_add(val, img[i + 1, j + 1, ch].astype(np.uint16))  # 1

                        result = val >> 4  # divide by 16

                        if result > 255:
                            raise ValueError(
                                f"Value overflow at pixel ({i},{j}), channel {ch}: {result}"
                            )

                        out[i, j, ch] = np.uint8(result)

            return out.squeeze().astype(np.uint8)


        def sum_many(a_arr: np.ndarray, b_arr: np.ndarray):
            if (
                np.any(a_arr > 0xFFFF)
                or np.any(b_arr > 0xFFFF)
                or np.any(a_arr < 0)
                or np.any(b_arr < 0)
            ):
                raise ValueError("Operands must be 16-bit unsigned integers (0 to 65535)")

            a_bits = ((a_arr[:, None] & (1 << np.arange(15, -1, -1))) > 0).astype(int)
            b_bits = ((b_arr[:, None] & (1 << np.arange(15, -1, -1))) > 0).astype(int)
            input_bits = np.hstack([a_bits, b_bits])  # shape (N, 32)

            if isinstance(clf.clf, list):
                output_bits = np.stack(
                    [dt.predict(input_bits) for dt in clf.clf], axis=1
                )  # shape (N, num_bits)
            else:
                output_bits = clf.clf.predict(input_bits)  # shape (N, num_bits)

            powers = 1 << np.arange(output_bits.shape[1] - 1, -1, -1)
            return (output_bits * powers).sum(axis=1)


        def apply_gaussian_filter_parallel(img: np.ndarray, custom_add_parallel):
            if img.ndim == 2:
                img = img[..., None]

            h, w, c = img.shape
            out = np.zeros_like(img)

            start = time.time()
            top_left_pixels = np.array(
                [
                    img[i - 1, j - 1, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            top_pixels = np.array(
                [
                    img[i - 1, j, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            top_right_pixels = np.array(
                [
                    img[i - 1, j + 1, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            center_left_pixels = np.array(
                [
                    img[i, j - 1, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            center_pixels = np.array(
                [
                    img[i, j, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            center_right_pixels = np.array(
                [
                    img[i, j + 1, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            bottom_left_pixels = np.array(
                [
                    img[i - 1, j - 1, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            bottom_pixels = np.array(
                [
                    img[i - 1, j, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            bottom_right_pixels = np.array(
                [
                    img[i - 1, j + 1, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )

            print(f"{time.time() - start:.2f}s creating arrays")

            start = time.time()
            vals = np.zeros_like(top_left_pixels)

            vals = custom_add_parallel(vals, top_left_pixels)  # 1
            vals = custom_add_parallel(vals, top_pixels << 1)  # 2
            vals = custom_add_parallel(vals, top_right_pixels)  # 1

            vals = custom_add_parallel(vals, center_left_pixels << 1)  # 2
            vals = custom_add_parallel(vals, center_pixels << 2)  # 4
            vals = custom_add_parallel(vals, center_right_pixels << 1)  # 2

            vals = custom_add_parallel(vals, bottom_left_pixels)  # 1
            vals = custom_add_parallel(vals, bottom_pixels << 1)  # 2
            vals = custom_add_parallel(vals, bottom_right_pixels)  # 1

            print(f"{time.time() - start:.2f}s doing sums")

            results = vals >> 4  # sum + div 16

            results = np.clip(np.abs(results), 0, 255)

            out = results.astype(np.uint8).reshape((h - 2, w - 2, c))

            return out.squeeze()


        def apply_sobel_x_filter_parallel(img: np.ndarray, custom_add_parallel):
            if img.ndim == 2:
                img = img[..., None]

            h, w, c = img.shape
            out = np.zeros_like(img)

            start = time.time()

            top_left_pixels = np.array(
                [
                    img[i - 1, j - 1, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            top_right_pixels = np.array(
                [
                    img[i - 1, j + 1, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            center_left_pixels = np.array(
                [
                    img[i, j - 1, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            center_right_pixels = np.array(
                [
                    img[i, j + 1, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            bottom_left_pixels = np.array(
                [
                    img[i + 1, j - 1, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )
            bottom_right_pixels = np.array(
                [
                    img[i + 1, j + 1, ch]
                    for i in range(1, h - 1)
                    for j in range(1, w - 1)
                    for ch in range(c)
                ],
                dtype=np.uint16,
            )

            print(f"{time.time() - start:.2f}s creating arrays")

            start = time.time()
            pos = np.zeros_like(top_left_pixels)
            neg = np.zeros_like(top_left_pixels)

            # POS side of kernel: right side (1s and 2s)
            pos = custom_add_parallel(pos, top_right_pixels)  # +1
            pos = custom_add_parallel(pos, center_right_pixels << 1)  # +2
            pos = custom_add_parallel(pos, bottom_right_pixels)  # +1

            # NEG side of kernel: left side (1s and 2s)
            neg = custom_add_parallel(neg, top_left_pixels)  # +1
            neg = custom_add_parallel(neg, center_left_pixels << 1)  # +2
            neg = custom_add_parallel(neg, bottom_left_pixels)  # +1

            print(f"{time.time() - start:.2f}s doing sums")

            # Final result: Gx = pos - neg (manually outside the custom fn)
            results = pos.astype(np.int32) - neg.astype(np.int32)
            results = np.clip(np.abs(results), 0, 255)

            out = results.astype(np.uint8).reshape((h - 2, w - 2, c))
            return out.squeeze()


        img = np.array(Image.open("peppers.png"))

        print("Aplicando gaussiano bueno")
        blurred = apply_gaussian_filter_parallel(img, lambda a, b: a + b)

        OUT_DIR="informe final/imágenes"

        Image.fromarray(blurred).save(
            f"{OUT_DIR}/blurred.png"
        )

        print("Aplicando gaussiano aproximado")
        blurred_approx = apply_gaussian_filter_parallel(img, sum_many)

        Image.fromarray(blurred_approx).save(
            f"{OUT_DIR}/blurred_approx_{MAX_DEPTH}{'_one_tree_per_output' if ONE_TREE_PER_OUTPUT else ''}_bak.png"
        )

        img = np.array(Image.open("peppers.png").convert("L"))

        print("Aplicando sobel bueno")
        edged = apply_sobel_x_filter_parallel(img, lambda a, b: a + b)

        Image.fromarray(edged).save(
            f"{OUT_DIR}/edged.png"
        )

        print("Aplicando sobel aproximado")
        edged_approx = apply_sobel_x_filter_parallel(img, sum_many)

        Image.fromarray(edged_approx).save(
            f"{OUT_DIR}/edged_approx_{MAX_DEPTH}{'_one_tree_per_output' if ONE_TREE_PER_OUTPUT else ''}_bak.png"
        )

        def compute_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
            # If RGB, compute SSIM over each channel and average
            if img1.ndim == 3:
                ssim_val = np.mean([
                    ssim(img1[:, :, i], img2[:, :, i], data_range=img2[:, :, i].max() - img2[:, :, i].min())
                    for i in range(img1.shape[2])
                ])
            else:  # grayscale
                ssim_val = ssim(img1, img2, data_range=img2.max() - img2.min())
            return ssim_val

        print("\n---- Características de aproximación -----")
        print("MAX DEPTH:",MAX_DEPTH)
        print("ONE_TREE_PER_OUTPUT:",ONE_TREE_PER_OUTPUT)
        print(f"Error MRED: {mred * 100}%")
        print(f"Error MED: {med}")
        print(f"Área: {area * 100:.2f}%")
        print("\n-- Métricas imagen --")
        print("Gauss SSIM:", compute_ssim(blurred, blurred_approx))
        print("Sobel SSIM:", compute_ssim(edged, edged_approx))


