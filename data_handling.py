"""
Functions or loading and handling running data processed using process_fit.py
"""

import os
import pandas as pd
from datetime import datetime


def load_runs(start_date=None, end_date=None, type=None):
    """
    Loads running data from the 'data' folder.

    Parameters
    ----------
    start_date: str, optional
        Start date in 'yyyymmdd' format. Only loads runs on or after this date.
    end_date: str, optional
        End date in 'yyyymmdd' format. Only loads runs on or before this date.
    type: str, optional
        Type of run (e.g., 'base', 'sprint'). Only loads runs with that flag.

    Returns
    -------
    dict
        Dictionary of runs wehre keys are filenames and values are DataFrames.
    """

    runs = {}
    folder = "data"

    if start_date:
        start_dt = datetime.strptime(start_date, "%Y%m%d")
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y%m%d")

    for filename in os.listdir(folder):
        parts = filename.split("_")
        date_str = parts[0]
        if type or start_date or end_date:
            file_dt = datetime.strptime(date_str, "%Y%m%d")

            if type and not filename.endswith(f"{type}.csv"):
                continue

            if start_date and file_dt < start_dt:
                continue

            if end_date and file_dt > end_dt:
                continue

        filepath = os.path.join(folder, filename)
        df = pd.read_csv(filepath)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        runs[date_str] = df

    return runs


def add_elapsed_time(df):
    """
    Adds 'elapsed_time' col to df
    """

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    start_time = df["timestamp"].iloc[0]

    elapsed_seconds = (df["timestamp"] - start_time).dt.total_seconds()

    df["elapsed_time"] = pd.to_timedelta(elapsed_seconds, unit="s")

    return df


def clean_base_runs(df):
    """
    Performs basic QC/cleaning on base runs data, including
    - Removing first 5 min of data
    - Nan'ing data where pace = 0
    """

    df = df[df["elapsed_time"] > pd.Timedelta(minutes=5)]
    df.loc[df["pace"] == 0.0, ["pace", "hr"]] = pd.NA
    df.loc[df["pace"] > 11.0, ["pace", "hr"]] = pd.NA

    return df
