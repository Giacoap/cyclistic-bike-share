# Cyclistic Bike-Share Analysis

**Google Data Analytics Professional Certificate — Capstone Case Study**

> How do annual members and casual riders use Cyclistic bikes differently?

---

## Overview

This project analyzes 12 months of real bike-share trip data (April 2025 – March 2026) from Divvy Bikes in Chicago to identify behavioral differences between casual riders and annual members. The goal is to inform a marketing strategy aimed at converting casual riders into annual members.

This analysis was completed as the capstone project for the [Google Data Analytics Professional Certificate](https://grow.google/certificates/data-analytics/). Unlike the course's suggested dataset (2019–2020), this project uses the most recent data available to ensure findings reflect current rider behavior.

---

## Key Findings

| Finding | Members | Casual Riders |
|---|---|---|
| Primary use case | Commuting | Leisure / recreation |
| Peak days | Tue – Thu | Saturday – Sunday |
| Peak hours | 8 AM and 5 PM (bimodal) | 3 – 5 PM (gradual curve) |
| Median ride duration | 8.7 min | 11.8 min (+36%) |
| Weekend share of rides | 23.4% | 37.7% |
| Summer share of annual rides | ~33% | ~42% |

**Top 3 recommendations:**
1. Launch a weekend-focused membership tier to lower the conversion barrier for leisure riders
2. Concentrate conversion campaigns in summer, when casual ridership peaks
3. Deploy targeted activation at high-casual stations (lakefront, parks, tourist areas)

---

## Repository Structure

```
cyclistic-bike-share/
│
├── data/
│   ├── raw/                  # Monthly CSV files (not included — see Data section)
│   └── processed/            # Cleaned dataset (cyclistic_clean.parquet)
│
├── charts/                   # All exported visualizations (PNG)
│   ├── 01_rides_by_type.png
│   ├── 02_rides_by_dow.png
│   ├── 03_avg_duration_dow.png
│   ├── 04_rides_by_hour.png
│   ├── 05_monthly_trend.png
│   ├── 06_ride_length_boxplot.png
│   ├── 07_rides_by_season.png
│   └── 08_bike_type.png
│
├── analysis.py               # Full analysis script (Prepare → Share)
├── writeup.md                # Case study write-up (Ask → Act)
└── README.md
```

---

## Data

**Source:** [Divvy Trip Data](https://divvy-tripdata.s3.amazonaws.com/index.html), provided by Motivate International Inc.  
**License:** [Divvy Data License Agreement](https://divvybikes.com/data-license-agreement)  
**Period:** April 2025 – March 2026 (12 monthly CSV files)  
**Raw size:** ~1 GB, 5,242,349 trips  
**After cleaning:** 5,103,110 trips (2.66% removed)

The raw CSV files are not included in this repository due to size. To reproduce the analysis, download the monthly files from the link above and place them in `data/raw/`.

---

## How to Reproduce

### Requirements

```
python >= 3.10
pandas
matplotlib
seaborn
pyarrow
```

Install dependencies:

```bash
pip install pandas matplotlib seaborn pyarrow
```

### Run the analysis

```bash
git clone https://github.com/your-username/cyclistic-bike-share.git
cd cyclistic-bike-share

# Download and place CSV files in data/raw/ (see Data section above)

python analysis.py
```

The script will:
1. Load and validate all 12 CSV files
2. Clean the data and engineer features
3. Compute all aggregations
4. Generate and export 8 visualizations to `charts/`
5. Save the cleaned dataset to `data/processed/cyclistic_clean.parquet`

---

## Methodology

This analysis follows the **Google Data Analytics six-phase process**:

| Phase | Description |
|---|---|
| **Ask** | Defined the business task and stakeholders |
| **Prepare** | Downloaded, validated, and documented the data source |
| **Process** | Cleaned data, removed invalid trips, engineered features |
| **Analyze** | Identified behavioral patterns by user type across time, duration, and geography |
| **Share** | Created 8 visualizations communicating key findings |
| **Act** | Formulated 3 actionable recommendations for the marketing team |

Full documentation is in [`writeup.md`](writeup.md).

---

## Tools

| Tool | Use |
|---|---|
| Python 3.12 | Primary analysis language |
| pandas | Data loading, cleaning, and aggregation |
| matplotlib | Chart generation |
| seaborn | Statistical visualizations |
| pyarrow | Efficient Parquet storage |

---

## Author

**Giacomo**  
Google Data Analytics Professional Certificate — April 2026  
[LinkedIn](#) · [Portfolio](#)
