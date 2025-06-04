import pandas as pd
import numpy as np

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
    print(f"\n=========== {threshold} ==========")
    for circuit in circuits:
        row_data = [circuit]

        # Get decision tree metadata
        dt_filtered = df_all[
            (df_all["circuit"] == circuit)
            & (df_all["method"] == "decision_tree")
            & (df_all["mred"] <= threshold)
        ]
        # if not dt_filtered.empty:
        #     best_dt = dt_filtered.loc[dt_filtered["mred"].idxmin()]
        #     row_data.append(int(best_dt["max_depth"]))
        #     row_data.append("Sí" if best_dt.get("one_tree_per_output", False) else "No")
        # else:
        #     row_data += ["-", "-"]

        # Append Area values
        for method in methods:
            sub = df_all[
                (df_all["circuit"] == circuit)
                & (df_all["method"] == method)
                & (df_all["mred"] <= threshold)
            ]
            if not sub.empty:
                best = sub.loc[sub["area"].idxmin()]
                row_data.append(f"{best['mred'] * 100:.2f}")
                if not np.isnan(best['v_mred']):
                    row_data.append(f"{best['v_mred'] * 100:.2f}")
                else:
                    row_data.append("-")
            else:
                row_data.append("-")

        # Format LaTeX row
        print(" & ".join(map(str, row_data)) + r" \\")
