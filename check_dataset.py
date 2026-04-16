# import pandas as pd
# import os

# folder = r"C:\Users\anshi\Downloads\archive (1)"

# for file in os.listdir(folder):
#     if file.endswith(".csv"):
#         path = os.path.join(folder, file)
#         df   = pd.read_csv(path)

#         print(f"\n{'='*50}")
#         print(f"File     : {file}")
#         print(f"Shape    : {df.shape}")
#         print(f"Columns  : {df.columns.tolist()}")
#         print(f"Sample   :\n{df.head(3)}")
#         print(f"Null vals:\n{df.isnull().sum()}")

import json
import os

folder    = r"C:\Users\anshi\Downloads\archive (1)"
json_path = os.path.join(folder, "data.jsonl")

print(f"Reading: {json_path}")

records = []
with open(json_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            records.append(json.loads(line))

print(f"Total records : {len(records)}")
print(f"First record  : {records[0]}")
print(f"All keys      : {list(records[0].keys())}")
print(f"\nSecond record : {records[1]}")
print(f"\nThird record  : {records[2]}")