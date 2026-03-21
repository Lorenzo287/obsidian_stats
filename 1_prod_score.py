import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from settings import DATA_OUTPUT_CSV, PROD_OUTPUT_CSV


def sleep_bonus_function(sleep_minutes):
    """Applies a Gaussian-like function for sleep impact with less penalty for oversleeping"""
    A = 8  # Maximum sleep bonus
    mu = 480  # Ideal sleep duration (8 hours)
    sigma_under = 120  # Penalty for undersleeping
    sigma_over = 200  # Gentler penalty for oversleeping

    if sleep_minutes <= mu:
        sigma = sigma_under
    else:
        sigma = sigma_over

    return A * np.exp(-((sleep_minutes - mu) ** 2) / (2 * sigma**2))


def calculate_productivity_score(df):
    """Vectorized computation of the productivity score"""
    completion_rate = df["compl"] / df["tasks"]
    completion_rate.fillna(0, inplace=True)  # Avoid division by zero

    task_score = (6.0 * completion_rate) + df["compl"]
    study_penalty = -3.0 * df["sd"]
    youtube_penalty = -0.02 * df["yt"]
    sleep_bonus = df["sleep"].apply(sleep_bonus_function)
    reading_bonus = 2.0 * df["read"]
    music_bonus = 1.2 * df["music"]

    df["prod_score"] = round(
        (
            5
            + task_score
            + study_penalty
            + youtube_penalty
            + sleep_bonus
            + reading_bonus
            + music_bonus
        ).clip(lower=0),
        3,
    )


def process_csv(input_file, output_file):
    df = pd.read_csv(input_file)
    df["date"] = pd.to_datetime(df["date"])  # Convert date to datetime
    calculate_productivity_score(df)  # Apply vectorized function

    N = 30  # Compute rolling average with window size N
    df["rolling_avg"] = round(
        df["prod_score"].rolling(window=N, min_periods=1, center=True).mean(), 3
    )

    # Plot productivity score
    plt.figure(figsize=(10, 5))
    plt.plot(
        df["date"],
        df["prod_score"],
        marker="o",
        linestyle="",
        alpha=0.5,
        label="Daily Score",
    )
    plt.plot(
        df["date"],
        df["rolling_avg"],
        linestyle="-",
        color="red",
        linewidth=2,
        label=(f"{N}-Day Average"),
    )

    # Polynomial Fit
    """
    degree = 3  # Degree of polynomial
    x_numeric = df["date"].map(pd.Timestamp.toordinal)
    mask = df["prod_score"].notnull()

    coeffs = np.polyfit(x_numeric[mask], df["prod_score"][mask], degree)
    poly_func = np.poly1d(coeffs)

    x_fit = pd.date_range(start=df["date"].min(), end=df["date"].max(), periods=1000)
    x_ord = x_fit.map(pd.Timestamp.toordinal)
    y_fit = poly_func(x_ord)
    date_fit = x_fit

    plt.plot(
       date_fit,
       y_fit,
       color="green",
       linewidth=2,
       alpha=0.6,
       label=f"Poly (deg {degree})",
    )
    """
    plt.title("Daily Productivity Score Over Time")

    # Dynamic x-axis formatting
    date_range = (df["date"].max() - df["date"].min()).days
    if date_range > 365:
        plt.gca().xaxis.set_major_locator(mdates.YearLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    else:
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    plt.xticks(rotation=0)
    plt.grid()
    plt.legend()
    plt.show()

    # df = df[['date', 'week', 'day', 'prod_score', 'rolling_avg']]
    df.to_csv(output_file, index=False)


input_csv = DATA_OUTPUT_CSV
output_csv = PROD_OUTPUT_CSV
process_csv(input_csv, output_csv)
