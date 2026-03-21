import pandas as pd
from sklearn.ensemble import IsolationForest
from settings import PROD_OUTPUT_CSV


def load_data(file_path):
    df = pd.read_csv(file_path)
    return df


def detect_anomalies(df, contamination=0.05):
    model = IsolationForest(contamination=contamination, random_state=42)
    df["anomaly"] = model.fit_predict(df[["prod_score"]])
    df["anomaly"] = df["anomaly"].apply(lambda x: "YES" if x == -1 else "")
    return df


def print_best_worst_days(df, n):
    best_days = df.nlargest(n, "prod_score")
    worst_days = df.nsmallest(n, "prod_score")
    print("\nBest Days:")
    print(best_days.to_string(index=False))
    print("\nWorst Days:")
    print(f"{worst_days.to_string(index=False)}\n")


def main(file_path, n):
    df = load_data(file_path)
    df = detect_anomalies(df)
    print_best_worst_days(df, n)


main(PROD_OUTPUT_CSV, 7)  # N of days shown
