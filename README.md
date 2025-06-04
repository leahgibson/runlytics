# heat-economy
 An N=1 analysis of running efficiency before and after heat adaptation, using my personal data to investigate the effects of heat exposure.

## process_fit.py

CLI tool for processing Garmin .fit files into cleaned CSV data.

### Usage

```bash
./process_fit.py <fit_file> [options]
```

#### Arguments

- `fit_file`: Path to the .fit file to process

#### Options

- `--base`: Mark as a base run (saves as `YYYYMMDD_base.csv` instead of `YYYYMMDD.csv`)
- `--filter`: Allows geographic filtering to a specific region
- `--output DIR`: Output directory (default: `./data`)

#### Examples

```bash
# Basic processing
./process_fit.py ./raw_data/activity.fit

# Base run
./process_fit.py ./raw_data/activity.fit --base

# Skip geographic filtering
./process_fit.py ./raw_data/activity.fit --filter

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
