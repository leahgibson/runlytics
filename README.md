# runlytics
 Started as an N=1 analysis of running efficiency before and after heat adaptation, using my personal data to investigate the effects of heat exposure, ended up as a full-blown analysis of my running data.

## process_fit.py

CLI tool for processing Garmin .fit files into cleaned CSV data.

### Usage

```bash
./process_fit.py <fit_file> [options]
```

#### Arguments

- `fit_file`: Path to the .fit file to process

#### Options

- `--type RUN TYPE`: Type of run (saves as `YYYYMMDD_run_type.csv` instead of `YYYYMMDD.csv`)
- `--filter`: Allows geographic filtering to a specific region
- `--output DIR`: Output directory (default: `./data`)

#### Examples

```bash
# Basic processing
./process_fit.py ./raw_data/activity.fit

# Base run
./process_fit.py ./raw_data/activity.fit --type base

# Tempo run with geographic filtering
./process_fit.py ./raw_data/activity.fit --type tempo --filter

# Custom output directory
./process_fit.py ./raw_data/activity.fit --output ./processed_runs
```

### Setup

1. Make executable: `chmod +x process_fit.py`

2. For geographic filtering, create a `.env` file with bounding box coordinates:
   ```
   minx=your_min_longitude
   miny=your_min_latitude
   maxx=your_max_longitude
   maxy=your_max_latitude
   ```

### Output
- Extracts: timestamp, pace, heart rate, distance
- Date automatically extracted from .fit file metadata
- Filename format: `YYYYMMDD.csv` or `YYYYMMDD_base.csv`
- Geographic filtering removes GPS coordinates from final output for privacy

## data_handling.py

Functions for loading and handling of files generated using the CLI.

## base_analysis.py

Framework for aerobic efficiency analysis of base runs. Code is specific to my analysis but easily adaptable.

## banister_modeling.py

Framework for applying Banister model to running data. Also creates the file 'load.csv' which is necessary for ridge regression. This is a good place to start before getting into other analyses.

## ridge_data_prep.py

Code for organizing data into weekly stats to be used in Ridge Regression.

## ridge_regression.py

Code for applying ridge regression to data. Currently uses LOO CV given the small dataset that I have, but could be changed to a train-test split for larger datasets.

## nn_data_prep.py

Code for organizing data to use to predict my 50k race time.

## race_prediction.py

Using a regression model and a small NN to predict my 50k race time.