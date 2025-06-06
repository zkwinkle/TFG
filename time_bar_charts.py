import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Define font size
plt.rcParams.update({"font.size": 16})

# Load the CSV
csvs = [
    "10s_dt_results.csv",
    "inconst_results.csv",
    "outconst_results.csv",
    "probprun_results.csv",
]
methods = ["decision_tree", "inconst", "outconst", "probprun"]
dfs = [pd.read_csv(csv) for csv in csvs]

df_all = pd.concat(dfs, ignore_index=True)


groups = {
    0.01: ["RCA_4b", "int2float"],
    0.25: [
        "int2float",
        "BK_16b",
        "KS_16b",
        "CSkipA_16b",
        "LFA_16b",
        "CLA_16b",
        "BK_32b",
        "KS_32b",
    ],
    0.5: ["RCA_4b", "WT_8b", "KS_16b", "LFA_16b", "KS_32b"],
}


for threshold, circuits in groups.items():
    data = {circuit: {} for circuit in circuits}
    for circuit in circuits:
        for method in methods:
            sub = df_all[
                (df_all['circuit'] == circuit)
                & (df_all['method'] == method)
                & (df_all['mred'] <= threshold)
            ]
            if not sub.empty:
                best = sub.loc[sub['area'].idxmax()]
                data[circuit][method] = best['time']
            else:
                data[circuit][method] = None  # or np.nan

    # Create bar chart
    x = list(data.keys())
    x_pos = range(len(x))
    bar_width = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, method in enumerate(methods):
        y = [data[c].get(method) for c in x]
        ax.bar([p + i * bar_width for p in x_pos], y, bar_width, label=method)

    ax.set_xticks([p + 1.5 * bar_width for p in x_pos])
    ax.set_xticklabels(x)
    ax.set_ylabel("Time (s)")
    ax.set_title(f"(MRED ≤ {int(threshold*100)}%)")
    ax.legend()
    plt.tight_layout()
    fig.savefig(f"informe final/imágenes/{threshold}_threshold_time_comparison.svg")
    plt.pause(0.2)
    plt.show(block=False)
    plt.pause(0.2)


plt.show()
