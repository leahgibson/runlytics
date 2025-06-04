#!/usr/bin/env python3
"""
CLI tool for processing Garmin .fit running files into cleaned CSV data.
"""

import os
import argparse
import pandas as pd
import geopandas as gpd
import fitdecode
from shapely.geometry import Polygon
from dotenv import load_dotenv
from pathlib import Path


def semicircle_to_degrees(semicircle_val):
    return semicircle_val / (2**32 / 360)


def meters_per_sec_to_min_per_mile(pace_m_per_s):
    if pace_m_per_s == 0.0:
        return 0.0

    return 1 / (pace_m_per_s * 60 / 1609)


def process_fit_file(
    fit_file_path, is_base_run=False, filter_run=False, output_dir="~./data"
):
    """
    Process a .fit file and save as cleaned CSV

    Args:
        fit_file_path (str): Path to the .fit file
        is_base_run (bool): Whether this is a base run (affects filename)
        filter_run (bool): Whether to filter run to a specific geographical region
        output_dir (str): Directory to save the output file
    """
    run_df = pd.DataFrame(columns=["timestamp", "lat", "lon", "pace", "hr", "distance"])

    # Load .fit files
    print(f"Processing {fit_file_path}...")
    with fitdecode.FitReader(fit_file_path) as fitfile:
        index = 0
        for frame in fitfile:
            if frame.frame_type == fitdecode.FIT_FRAME_DATA and frame.name == "record":
                data = {field.name: field.value for field in frame.fields}

                if not all(
                    key in data
                    for key in [
                        "timestamp",
                        "position_lat",
                        "position_long",
                        "enhanced_speed",
                        "heart_rate",
                        "distance",
                    ]
                ):
                    continue

                row = {
                    "timestamp": data["timestamp"],
                    "lat": semicircle_to_degrees(data["position_lat"]),
                    "lon": semicircle_to_degrees(data["position_long"]),
                    "pace": meters_per_sec_to_min_per_mile(data["enhanced_speed"]),
                    "hr": data["heart_rate"],
                    "distance": data["distance"] / 1609,
                }
                run_df.loc[index] = row
                index += 1

    if run_df.empty:
        print("Warning: No valid data found in .fit file")
        return

    run_gdf = gpd.GeoDataFrame(
        run_df, geometry=gpd.points_from_xy(run_df.lon, run_df.lat)
    )

    if filter_run:
        # Load environment variables for bounding box
        load_dotenv()
        minx = os.getenv("minx")
        miny = os.getenv("miny")
        maxx = os.getenv("maxx")
        maxy = os.getenv("maxy")

        bbox = Polygon(
            [(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny), (minx, miny)]
        )

        # Filter data to valid running area
        run_gdf = run_gdf[run_gdf.geometry.within(bbox)]

        if run_gdf.empty:
            print("Warning: No data points found within the specified running area")

    df = pd.DataFrame(run_gdf.drop(columns=["lat", "lon", "geometry"]))
    df = df.reset_index(level=0, drop=True)
    date_str = df.loc[0, "timestamp"].strftime("%Y%m%d")

    if is_base_run:
        filename = f"{date_str}_base.csv"
    else:
        filename = f"{date_str}.csv"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    full_path = os.path.join(output_path, filename)
    try:
        df.to_csv(full_path, index=False)
        print(f"Saved to: {full_path}")
    except:  # noqa: E722
        print("Warning: File not saved.")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Process Garmin .fit files into cleaned CSV data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_fit.py data.fit
  python process_fit.py data.fit --base --filter
  python process_fit.py data.fit --output ./processed_data
        """,
    )

    parser.add_argument("fit_file", help="Path to the .fit file to process")

    parser.add_argument(
        "--base",
        action="store_true",
        help="Mark this as a base run (adds '_base' to filename)",
    )

    parser.add_argument(
        "--filter",
        action="store_true",
        help="Filter run to include data within specified region",
    )

    parser.add_argument(
        "--output",
        default="./data",
        help="Output directory for processed files (default: ./data)",
    )

    args = parser.parse_args()

    # Validate inputs
    if not os.path.exists(args.fit_file):
        print(f"Error: File '{args.fit_file}' not found")
        return 1

    if not args.fit_file.lower().endswith(".fit"):
        print("Warning: File doesn't have .fit extension")

    load_dotenv()
    required_env_vars = ["minx", "miny", "maxx", "maxy"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(
            f"Error: Missing required environment variables: {', '.join(missing_vars)}"
        )
        print("Please set these in your .env file")
        return 1

    try:
        process_fit_file(args.fit_file, args.base, args.filter, args.output)
        return 0
    except Exception as e:
        print(f"Error processing file: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
