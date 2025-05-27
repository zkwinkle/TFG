import re
import numpy as np
import pandas as pd

# Load the CSV
# Cambiar esto para otros métodos
df = pd.read_csv("probprun_results.csv", dtype={"resynthesis": bool})

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

# Filter data
filtered_df = df[df["circuit"].isin(BENCHMARKS)]

COLUMNS = [
    "circuit",
    "resynthesis",
    "error",
    "mred",
    "v_mred",
    "hd",
    "v_hd",
    "wce",
    "v_wce",
    "time",
    "area",
]

ERRORS = [
    0.01,
    0.05,
    0.1,
    0.25,
    0.5
]


def is_number(s):
    # Regular expression to match integers and floats
    pattern = r'^-?\d+(\.\d+)?([eE][-+]?\d+)?$'
    return bool(re.match(pattern, s))


for circuit in BENCHMARKS:
    for error in ERRORS:
        for resynthesis in [True, False]:
            row = filtered_df[
                (filtered_df["circuit"] == circuit)
                & (filtered_df["resynthesis"] == resynthesis)
                & (filtered_df["error"] == error)
            ]

            values = []

            if row.size == 0:
                continue

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
