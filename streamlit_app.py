import calendar
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler

from settings import DATA_OUTPUT_CSV, PROD_OUTPUT_CSV


ROLLING_WINDOW = 30
DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


st.set_page_config(
    page_title="Obsidian Stats",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)


def sleep_bonus_function(sleep_minutes):
    """Matches the productivity scoring function used by 1_prod_score.py."""
    max_bonus = 8
    ideal_sleep = 480
    sigma_under = 120
    sigma_over = 200
    sigma = sigma_under if sleep_minutes <= ideal_sleep else sigma_over
    return max_bonus * np.exp(-((sleep_minutes - ideal_sleep) ** 2) / (2 * sigma**2))


def calculate_productivity_score(df):
    df = df.copy()
    completion_rate = df["compl"] / df["tasks"].replace(0, np.nan)
    completion_rate = completion_rate.fillna(0)

    task_score = (6.0 * completion_rate) + df["compl"]
    study_penalty = -3.0 * df["sd"]
    youtube_penalty = -0.02 * df["yt"]
    sleep_bonus = df["sleep"].apply(sleep_bonus_function)
    reading_bonus = 2.0 * df["read"]
    music_bonus = 1.2 * df["music"]

    df["prod_score"] = (
        5
        + task_score
        + study_penalty
        + youtube_penalty
        + sleep_bonus
        + reading_bonus
        + music_bonus
    ).clip(lower=0).round(3)
    df["rolling_avg"] = (
        df["prod_score"]
        .rolling(window=ROLLING_WINDOW, min_periods=1, center=True)
        .mean()
        .round(3)
    )
    return df


@st.cache_data(show_spinner=False)
def load_data(csv_path, modified_time):
    del modified_time
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    numeric_columns = ["week", "yt", "sleep", "read", "music", "sd", "compl", "tasks"]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.dropna(subset=["date"]).sort_values("date")


def get_modified_time(path):
    path = Path(path)
    return path.stat().st_mtime if path.exists() else 0


def refresh_outputs():
    data_script = Path("0_data_import.py")
    if not data_script.exists():
        raise FileNotFoundError("0_data_import.py was not found.")

    subprocess.run([sys.executable, str(data_script)], check=True)
    raw_df = load_data(DATA_OUTPUT_CSV, get_modified_time(DATA_OUTPUT_CSV))
    prod_df = calculate_productivity_score(raw_df)
    prod_df.to_csv(PROD_OUTPUT_CSV, index=False)
    st.cache_data.clear()


def metric_delta(current, previous):
    if pd.isna(previous):
        return None
    return round(current - previous, 2)


def add_year_week(df):
    df = df.copy()
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    df["date_label"] = df["date"].dt.strftime("%Y-%m-%d")
    df["year_week"] = df["year"].astype(str) + "-W" + df["week"].astype(int).astype(str).str.zfill(2)
    return df


def detect_anomalies(df, contamination):
    scored = df.copy()
    model = IsolationForest(contamination=contamination, random_state=42)
    scored["anomaly"] = model.fit_predict(scored[["prod_score"]])
    return scored[scored["anomaly"] == -1].sort_values("prod_score")


def make_trend_plot(df):
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.scatter(df["date"], df["prod_score"], alpha=0.55, label="Daily score")
    ax.plot(df["date"], df["rolling_avg"], color="crimson", linewidth=2, label=f"{ROLLING_WINDOW}-day average")
    ax.set_title("Daily Productivity Score")
    ax.set_xlabel("")
    ax.set_ylabel("Score")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.autofmt_xdate()
    return fig


def make_calendar_heatmap(df, selected_year):
    year_df = df[df["year"] == selected_year]
    if year_df.empty:
        return None

    global_min = df["rolling_avg"].min()
    global_max = df["rolling_avg"].max()
    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(13, 9))

    for month, ax in enumerate(axes.flat, start=1):
        month_days = calendar.monthcalendar(selected_year, month)
        heatmap_data = np.full((6, 7), np.nan)
        month_data = year_df[year_df["month"] == month]

        for week_idx, week in enumerate(month_days):
            for day_idx, day in enumerate(week):
                if day:
                    value = month_data.loc[month_data["date"].dt.day == day, "rolling_avg"]
                    if not value.empty:
                        heatmap_data[week_idx, day_idx] = value.iloc[0]

        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt=".0f",
            cmap="RdYlGn",
            vmin=global_min,
            vmax=global_max,
            linewidths=0.5,
            linecolor="black",
            cbar=False,
            ax=ax,
            annot_kws={"size": 9, "color": "black"},
        )
        ax.set_title(calendar.month_name[month], fontsize=11)
        ax.set_xticks([])
        ax.set_yticks([])

    fig.suptitle(f"Productivity Calendar Heatmap - {selected_year}", fontsize=15)
    fig.tight_layout()
    return fig


def make_correlation_matrix(df):
    corr_df = df.copy()
    corr_df["sleep"] = np.exp(-((corr_df["sleep"] - 510) ** 2) / (2 * 60**2))
    corr_df["rate"] = corr_df["compl"] / corr_df["tasks"].replace(0, 1)

    scaled_columns = ["read", "music", "sleep", "yt", "compl", "sd", "tasks", "rate"]
    scaler = MinMaxScaler()
    corr_df[scaled_columns] = scaler.fit_transform(corr_df[scaled_columns])
    corr_df["prod"] = corr_df["rate"] * corr_df["compl"]

    numeric_columns = corr_df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    if "week" in numeric_columns:
        numeric_columns.remove("week")

    correlation_matrix = corr_df[numeric_columns].corr()
    sorted_columns = (
        correlation_matrix["prod"]
        .drop(labels=["prod", "rate"], errors="ignore")
        .sort_values(ascending=False)
        .index.tolist()
    )
    ordered_columns = ["prod"] + sorted_columns
    ordered_matrix = correlation_matrix[ordered_columns].loc[ordered_columns]

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(ordered_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    ax.set_title("Correlation Matrix")
    return fig, ordered_matrix


prod_path = Path(PROD_OUTPUT_CSV)
data_path = Path(DATA_OUTPUT_CSV)

st.title("Obsidian Stats")

with st.sidebar:
    st.header("Data")
    st.caption(f"Productivity CSV: `{prod_path}`")
    st.caption(f"Raw CSV: `{data_path}`")
    if st.button("Refresh from Obsidian vault", use_container_width=True):
        with st.spinner("Importing journal data and recomputing scores..."):
            try:
                refresh_outputs()
                st.success("Data refreshed.")
            except Exception as exc:
                st.error(f"Refresh failed: {exc}")

if not prod_path.exists():
    st.warning("No productivity output found. Use the sidebar refresh button or run the existing scripts first.")
    st.stop()

df = load_data(PROD_OUTPUT_CSV, get_modified_time(PROD_OUTPUT_CSV))
if "prod_score" not in df.columns or "rolling_avg" not in df.columns:
    df = calculate_productivity_score(df)

df = add_year_week(df)

with st.sidebar:
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

filtered_df = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)].copy()

if filtered_df.empty:
    st.warning("No rows match the selected filters.")
    st.stop()

latest = filtered_df.iloc[-1]
previous = filtered_df.iloc[-2] if len(filtered_df) > 1 else None

col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest score", f"{latest['prod_score']:.2f}", metric_delta(latest["prod_score"], previous["prod_score"]) if previous is not None else None)
col2.metric("Rolling average", f"{latest['rolling_avg']:.2f}", metric_delta(latest["rolling_avg"], previous["rolling_avg"]) if previous is not None else None)
col3.metric("Avg sleep", f"{filtered_df['sleep'].mean() / 60:.1f} h")
col4.metric("Task completion", f"{(filtered_df['compl'].sum() / filtered_df['tasks'].sum() * 100):.0f}%")

overview_tab, heatmap_tab, anomalies_tab, weeks_tab, correlations_tab, data_tab = st.tabs(
    ["Overview", "Calendar", "Anomalies", "Weeks", "Correlations", "Data"]
)

with overview_tab:
    st.pyplot(make_trend_plot(filtered_df), clear_figure=True)

    left, right = st.columns(2)
    monthly = filtered_df.groupby("month_name", sort=False)["prod_score"].mean().reset_index()
    left.subheader("Average by Month")
    left.bar_chart(monthly, x="month_name", y="prod_score")

    habits = filtered_df[["read", "music", "sd"]].sum().rename(
        {"read": "Reading days", "music": "Music days", "sd": "Study deficit days"}
    )
    right.subheader("Tracked Habits")
    right.bar_chart(habits)

with heatmap_tab:
    years = sorted(filtered_df["year"].unique())
    selected_year = st.selectbox("Year", years, index=len(years) - 1)
    heatmap_fig = make_calendar_heatmap(filtered_df, selected_year)
    if heatmap_fig is None:
        st.info("No data is available for this year.")
    else:
        st.pyplot(heatmap_fig, clear_figure=True)

with anomalies_tab:
    contamination = st.slider("Expected anomaly share", 0.01, 0.20, 0.05, 0.01)
    anomalies = detect_anomalies(filtered_df, contamination)
    best_days = filtered_df.nlargest(7, "prod_score")
    worst_days = filtered_df.nsmallest(7, "prod_score")

    left, right = st.columns(2)
    left.subheader("Best Days")
    left.dataframe(best_days[["date_label", "day", "prod_score", "rolling_avg", "compl", "tasks", "sleep", "yt"]], hide_index=True)
    right.subheader("Worst Days")
    right.dataframe(worst_days[["date_label", "day", "prod_score", "rolling_avg", "compl", "tasks", "sleep", "yt"]], hide_index=True)

    st.subheader("Isolation Forest Anomalies")
    st.dataframe(anomalies[["date_label", "day", "prod_score", "rolling_avg", "compl", "tasks", "sleep", "yt"]], hide_index=True)

with weeks_tab:
    weekday_avg = (
        filtered_df.groupby("day")["prod_score"]
        .mean()
        .reindex(DAY_ORDER)
        .dropna()
        .reset_index()
    )
    week_avg = (
        filtered_df.groupby("year_week")["prod_score"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    left, right = st.columns([1, 1])
    left.subheader("Weekday Ranking")
    left.dataframe(weekday_avg.rename(columns={"prod_score": "avg_prod_score"}), hide_index=True)
    right.subheader("Week Ranking")
    right.dataframe(week_avg.rename(columns={"prod_score": "avg_prod_score"}), hide_index=True)

with correlations_tab:
    correlation_fig, correlation_table = make_correlation_matrix(filtered_df)
    st.pyplot(correlation_fig, clear_figure=True)
    with st.expander("Correlation values"):
        st.dataframe(correlation_table)

with data_tab:
    st.subheader("Productivity Data")
    st.dataframe(filtered_df, hide_index=True)
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered CSV", csv_bytes, "obsidian_stats_filtered.csv", "text/csv")
