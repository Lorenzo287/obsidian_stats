import pandas as pd
from settings import PROD_OUTPUT_CSV


def load_data(file_path):
    return pd.read_csv(file_path)


def add_year_to_week(df):
    df["year"] = pd.to_datetime(df["date"]).dt.year
    df["year_week"] = (
        df["year"].astype(str) + "-W" + df["week"].astype(str).str.zfill(2)
    )
    return df


def order_days_by_productivity(df):  # can change mean() to sum()
    day_avg_prod = df.groupby("day")["prod_score"].mean().reset_index()
    day_avg_prod = day_avg_prod.sort_values(by="prod_score", ascending=False)
    return day_avg_prod


def most_productive_weeks(df):  # can change mean() to sum()
    week_prod_score = df.groupby("year_week")["prod_score"].mean().reset_index()
    week_prod_score = week_prod_score.sort_values(by="prod_score", ascending=False)
    return week_prod_score


def highlight_current_week(df):
    latest_week = df["year_week"].max()
    return latest_week


def main(file_path):
    df = load_data(file_path)
    df = add_year_to_week(df)

    ordered_days = order_days_by_productivity(df)
    print("\nMost productive weekdays:")
    print(ordered_days[["day", "prod_score"]].to_string(index=False))

    productive_weeks = most_productive_weeks(df)
    latest_week = highlight_current_week(df)

    print("\nMost productive weeks:")
    cnt = 0
    for _, row in productive_weeks.iterrows():
        cnt += 1
        formatted_score = f"{row['prod_score']:.6f}"
        if row["year_week"] == latest_week:
            print(f"{cnt}) {row['year_week']}  {formatted_score} <-- Current week")
        else:
            print(f"{cnt:02}) {row['year_week']}  {formatted_score}")
    print()


main(PROD_OUTPUT_CSV)
