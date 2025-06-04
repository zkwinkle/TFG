import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load the CSV
df = pd.read_csv("10s_dt_results.csv")

# Define font size
plt.rcParams.update({"font.size": 16})

# Define filters
BENCHMARKS = [
    "DTree",
    "barshift_128b",
    "sobel",
    "BK_32b",
    "KS_32b",
    "CLA_16b",
    "BK_16b",
    "CSkipA_16b",
    "KS_16b",
    "LFA_16b",
    "WT_8b",
    "int2float",
    "RCA_4b",
]
MAX_DEPTHS = [3, 4, 5, 6, 8, 10]
depth_range = max(MAX_DEPTHS) - min(MAX_DEPTHS)

# "resynthesis" o "one_tree_per_output"
VARIABLE = "one_tree_per_output"

# Filter data
filtered_df = df[df["circuit"].isin(BENCHMARKS) & df["max_depth"].isin(MAX_DEPTHS)]


# Function to plot grouped bar charts
def plot_grouped_bars(metric, ylabel, percent=False, log=False, y_lim=None):
    fig, ax = plt.subplots(figsize=(16, 6))

    bar_width = 0.07
    x_labels = BENCHMARKS
    x = np.arange(len(x_labels))

    total = len(MAX_DEPTHS) * 2
    start = -(total - 1) / 2
    offsets = {
        (var, depth): (start + i) * bar_width
        for i, (var, depth) in enumerate(
            (v, d) for v in [False, True] for d in MAX_DEPTHS
        )
    }

    colors = {False: "skyblue", True: "salmon"}

    for variable in [False, True]:
        for depth in MAX_DEPTHS:
            values = []
            for circuit in x_labels:
                row = filtered_df[
                    (filtered_df["circuit"] == circuit)
                    & (filtered_df[VARIABLE] == variable)
                    & (filtered_df["max_depth"] == depth)
                ]
                if metric == "mred" and not row["v_mred"].hasnans:
                    value = row["v_mred"].values
                else:
                    value = row[metric].values

                value = sum(value) / len(value)

                if percent:
                    value *= 100

                values.append(value)

            label_if_true, label_if_false = {
                "resynthesis": ("Resynthesis", "No Resynthesis"),
                "one_tree_per_output": ("Un árbol por salida", "Árbol multi-salida"),
            }[VARIABLE]

            alpha = 0.4 + 0.6 * ((depth - min(MAX_DEPTHS)) / depth_range)
            x_pos = x + offsets[(variable, depth)]

            # Dema pequeñitos quedan los labels :(
            # Tal vez podría como popner labels horizontales más grandes con una
            # línea punteada que conecte con la barra y los labels a diferentes
            # alturas para que no choquen. Sería bueno que las alturas
            # correspondan en order con los valores reales.
            #
            # if y_lim is not None:
            #     for xi, v in zip(x_pos, values):
            #         if v > y_lim:
            #             ax.text(xi + bar_width, y_lim, f"{v:.2f}", ha='center', va='bottom', fontsize=4, rotation=60)


            ax.bar(
                x_pos,
                values,
                bar_width,
                label=f"{label_if_true if variable else label_if_false} - D{depth}",
                color=colors[variable],
                alpha=alpha,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha="right")
    ax.set_ylabel(ylabel)
    if y_lim is not None:
        ax.set_ylim(top=y_lim)
    if log:
        ax.set_yscale("log")
    # ax.set_title(f'{metric.upper()} Comparison by Circuit and Resynthesis')
    # ax.legend()
    ax.legend(bbox_to_anchor=(1, 1), loc="upper left")
    plt.tight_layout()

    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    return fig


# Generate the three plots
fig_mred = plot_grouped_bars("mred", "MRED (%)", percent=True, log=False, y_lim=None)
fig_area = plot_grouped_bars("area", "Área (% de original)", percent=True, log=False, y_lim=None)
fig_time = plot_grouped_bars("time", "Tiempo (s)", log=False)

fig_mred.savefig(f"informe final/imágenes/mred_{VARIABLE}_comparison.svg")
fig_area.savefig(f"informe final/imágenes/area_{VARIABLE}_comparison.svg")
fig_time.savefig(f"informe final/imágenes/time_{VARIABLE}_comparison.svg")
