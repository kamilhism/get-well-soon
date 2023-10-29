import pandas as pd

with open("../../data/raw/not_sick.txt", "r") as file_not_sick:
    data_not_sick = [{"text": line.strip(), "label": 0} for line in file_not_sick]

with open("../../data/raw/sick.txt", "r") as file_sick:
    data_sick = [{"text": line.strip(), "label": 1} for line in file_sick]

combined_data = data_not_sick + data_sick

df = pd.DataFrame(combined_data)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

total_rows = len(df)
split_point = int(total_rows * 0.1)

df_10_percent = df[:split_point]
df_remaining = df[split_point:]

df_10_percent.to_csv("../../data/processed/test.csv", index=False)
df_remaining.to_csv("../../data/processed/train.csv", index=False)
