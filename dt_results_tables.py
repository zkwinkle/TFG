import re
import numpy as np
import pandas as pd

# Load the CSV
df = pd.read_csv(
    "10s_dt_results.csv", dtype={"resynthesis": bool, "one_tree_per_output": bool}
)

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
    "dec",
]
MAX_DEPTHS = [3, 4, 5, 6, 8, 10]

# Filter data
filtered_df = df[df["circuit"].isin(BENCHMARKS) & df["max_depth"].isin(MAX_DEPTHS)]

COLUMNS = [
    "circuit",
    "resynthesis",
    "max_depth",
    "one_tree_per_output",
    "mred",
    "v_mred",
    "hd",
    "v_hd",
    "wce",
    "v_wce",
    "time",
    "area",
]

def is_number(s):
    # Regular expression to match integers and floats
    pattern = r'^-?\d+(\.\d+)?$'
    return bool(re.match(pattern, s))

for circuit in BENCHMARKS:
    for max_depth in MAX_DEPTHS:
        for resynthesis in [True, False]:
            for one_tree_per_output in [True, False]:
                row = filtered_df[
                    (filtered_df["circuit"] == circuit)
                    & (filtered_df["max_depth"] == max_depth)
                    & (filtered_df["resynthesis"] == resynthesis)
                    & (filtered_df["one_tree_per_output"] == one_tree_per_output)
                ]

                values = []
                for column in COLUMNS:
                    if row[column].hasnans:
                        value = [" "]
                    else:
                        value = row[column].values

                    if isinstance(value[0], str):
                        value = value[0]
                    elif isinstance(value[0], np.bool):
                        value = value[0]
                        if value:
                            value = "Sí"
                        else:
                            value = "No"
                    else:
                        value = sum(value) / len(value)
                        value = str(value)

                    if is_number(value):
                        value = f"\\num{{{value}}}"

                    value = value.replace("_", "\\_")
                    values.append(value)

                table_row = " & ".join(values)
                table_row += r" \\"
                print(table_row)
