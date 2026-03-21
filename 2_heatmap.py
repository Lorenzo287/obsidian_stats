import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
from settings import PROD_OUTPUT_CSV

year = 2025

df = pd.read_csv(PROD_OUTPUT_CSV)
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day

# Scaling across the entire database (all years)
global_min = df["rolling_avg"].min()
global_max = df["rolling_avg"].max()


def create_calendar_heatmap(year, df, ax):

    for month, ax_month in enumerate(ax.flat, start=1):
        month_days = calendar.monthcalendar(year, month)
        heatmap_data = np.full((6, 7), np.nan)

        month_data = df[(df["year"] == year) & (df["month"] == month)]

        for week_idx, week in enumerate(month_days):
            for day_idx, day in enumerate(week):
                if day != 0:
                    value = month_data.loc[month_data["day"] == day, "rolling_avg"]
                    if not value.empty:
                        heatmap_data[week_idx, day_idx] = value.values[0]

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
            ax=ax_month,
            annot_kws={"size": 9, "color": "black"},
        )

        ax_month.set_title(calendar.month_name[month], fontsize=12)
        ax_month.set_xticks([])
        ax_month.set_yticks([])

    fig.suptitle(f"Productivity Calendar Heatmap - {year}", fontsize=14)


fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(12, 9))

create_calendar_heatmap(year, df, axes)
plt.show()
