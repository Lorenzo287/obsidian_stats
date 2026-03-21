import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from settings import PROD_OUTPUT_CSV

df = pd.read_csv(PROD_OUTPUT_CSV)

# gaussian function
mu = 510  # ideal sleep duration 8.5h
sigma = 60  # std dev
df["sleep"] = np.exp(-((df["sleep"] - mu) ** 2) / (2 * sigma**2))

df["rate"] = df["compl"] / df["tasks"].replace(0, 1)

scaler = MinMaxScaler()
df[["read", "music", "sleep", "yt", "compl", "sd", "tasks", "rate"]] = (
    scaler.fit_transform(
        df[["read", "music", "sleep", "yt", "compl", "sd", "tasks", "rate"]]
    )
)

# assumption of productivity
df["prod"] = df["rate"] * (df["compl"])

numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns
if "week" in numeric_columns:
    numeric_columns = [col for col in numeric_columns if col != "week"]
correlation_matrix = df[numeric_columns].corr()

correlation_with_compl = (
    correlation_matrix["prod"].drop("prod").drop("rate")
)  # exclude 'compl'
sorted_columns = correlation_with_compl.sort_values(
    ascending=False
).index.tolist()  # sort

ordered_columns = ["prod"] + sorted_columns
ordered_correlation_matrix = correlation_matrix[ordered_columns].loc[ordered_columns]

plt.figure(figsize=(8, 6))
sns.heatmap(ordered_correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Matrix")
plt.show()
