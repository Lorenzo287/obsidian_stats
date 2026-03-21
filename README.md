# Obsidian Productivity Tracker

A Python-based productivity tracking system that parses daily journal entries from an Obsidian vault to generate insights, heatmaps, and trend analysis.

## Features

- **Data Extraction**: Parses daily markdown files for specific metrics (tasks, sleep, study deficit, etc.).
- **Productivity Scoring**: Calculates a weighted daily productivity score with rolling averages.
- **Visualizations**: Generates calendar heatmaps and trend plots.
- **Analysis**: Detects anomalies and identifies most/least productive days/weeks.

## Repository Structure

- `0_data_import.py`: Extracts raw data from Obsidian markdown files into a CSV.
- `1_prod_score.py`: Computes productivity scores and generates the daily score plot.
- `2_heatmap.py`: Creates a calendar heatmap of productivity throughout the year.
- `3_anomalies.py`: Identifies unusual productivity dips or peaks using Isolation Forest.
- `4_week_trend.py`: Analyzes productivity trends across different weeks and weekdays.
- `5_correlations.py`: Calculates correlations between different habits (e.g., sleep vs. productivity).
- `settings.py`: Centralized configuration for file paths and environment variables.
- `sleep_function.py`: Helper script for visualizing the sleep bonus algorithm.

## Setup

1. **Clone the repository.**
2. **Create a virtual environment and install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install pandas numpy matplotlib seaborn scikit-learn
   ```
3. **Configure Environment Variables**:
   Copy `.env.example` to a new file named `.env` and update the paths to point to your Obsidian vault and preferred output locations:
   ```bash
   OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/daily/journal
   DATA_OUTPUT_CSV=data_output.csv
   PROD_OUTPUT_CSV=prod_output.csv
   ```

## Usage

Run the scripts in order to update your data and view insights:

1. `python 0_data_import.py`
2. `python 1_prod_score.py`
3. Any of the other analysis scripts (`2_heatmap.py`, etc.).
