# =============================================================================
# Cyclistic Bike-Share Analysis
# Google Data Analytics Professional Certificate — Capstone Case Study
#
# Business Question: How do annual members and casual riders use
#                    Cyclistic bikes differently?
#
# Author : Giacomo
# Date   : April 2026
# Tools  : Python 3.12 | pandas | matplotlib | seaborn | pyarrow
# Data   : Divvy Trip Data, April 2025 – March 2026
#          Source: https://divvy-tripdata.s3.amazonaws.com/index.html
#          License: https://divvybikes.com/data-license-agreement
# =============================================================================

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# If running in a Jupyter Notebook or Google Colab, uncomment the next line:
# %matplotlib inline

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

DATA_DIR   = 'data/raw/'       # folder containing the 12 monthly CSV files
OUTPUT_DIR = 'data/processed/' # folder for the cleaned parquet file
CHARTS_DIR = 'charts/'         # folder for exported visualizations

for folder in [OUTPUT_DIR, CHARTS_DIR]:
    os.makedirs(folder, exist_ok=True)

# Consistent color palette across all charts
MEMBER_COLOR = '#1A73E8'   # blue  — members
CASUAL_COLOR = '#F4A300'   # amber — casual riders
PALETTE      = {'member': MEMBER_COLOR, 'casual': CASUAL_COLOR}

plt.rcParams.update({
    'font.family'        : 'DejaVu Sans',
    'axes.spines.top'    : False,
    'axes.spines.right'  : False,
    'axes.grid'          : True,
    'axes.grid.axis'     : 'y',
    'grid.alpha'         : 0.3,
})


# =============================================================================
# PHASE 1 — PREPARE
# Load and validate the raw data
# =============================================================================

print("=" * 60)
print("PHASE 1 — PREPARE")
print("=" * 60)

files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.csv')])
print(f"Files found: {len(files)}")
for f in files:
    print(f"  {f}")

# Verify schema consistency across all files before loading
print("\nValidating schema consistency...")
schemas = {}
for f in files:
    df_tmp = pd.read_csv(DATA_DIR + f, nrows=1)
    schemas[f] = df_tmp.columns.tolist()

reference_schema = list(schemas.values())[0]
all_match = all(cols == reference_schema for cols in schemas.values())
print(f"Schema consistent across all files: {all_match}")
print(f"Columns: {reference_schema}")

# Load all files
print("\nLoading all files...")
dfs = []
for f in files:
    df_tmp = pd.read_csv(DATA_DIR + f, parse_dates=['started_at', 'ended_at'])
    dfs.append(df_tmp)
    print(f"  {f}: {len(df_tmp):,} rows")

df = pd.concat(dfs, ignore_index=True)
print(f"\nTotal rows loaded: {len(df):,}")

# Initial quality report
print("\n--- Null counts ---")
print(df.isnull().sum())
print(f"\nDuplicate ride_ids: {df['ride_id'].duplicated().sum()}")
print(f"\nmember_casual values:\n{df['member_casual'].value_counts()}")
print(f"\nrideable_type values:\n{df['rideable_type'].value_counts()}")
print(f"\nDate range: {df['started_at'].min()} → {df['started_at'].max()}")


# =============================================================================
# PHASE 2 — PROCESS
# Clean data and engineer features
# =============================================================================

print("\n" + "=" * 60)
print("PHASE 2 — PROCESS")
print("=" * 60)

rows_before = len(df)

# Step 1: Remove rows with null user type (1 row)
df = df[df['member_casual'].notna()].copy()
print(f"After removing null member_casual: {len(df):,} rows")

# Step 2: Calculate ride duration in minutes
df['ride_length_min'] = (
    df['ended_at'] - df['started_at']
).dt.total_seconds() / 60

# Step 3: Remove invalid durations
#   - Negative or zero: system errors (ended_at <= started_at)
#   - Under 1 minute:   likely false starts or accidental docking
#   - Over 24 hours:    likely unreturned or stolen bikes
df = df[(df['ride_length_min'] >= 1) & (df['ride_length_min'] <= 1440)]

rows_after   = len(df)
rows_removed = rows_before - rows_after
print(f"After removing invalid durations: {rows_after:,} rows")
print(f"Rows removed: {rows_removed:,} ({rows_removed / rows_before * 100:.2f}%)")

# Note on station nulls:
# ~21% of trips have null station names. This is expected for electric bikes,
# which can be locked anywhere (not only at docking stations). These rows are
# retained; they are excluded only from station-level analyses.
station_null_pct = df['start_station_name'].isnull().mean() * 100
print(f"\nStation name nulls: {station_null_pct:.1f}% (expected for e-bikes)")

# Step 4: Feature engineering
season_map = {
    12: 'Winter', 1: 'Winter',  2: 'Winter',
    3:  'Spring', 4: 'Spring',  5: 'Spring',
    6:  'Summer', 7: 'Summer',  8: 'Summer',
    9:  'Fall',   10: 'Fall',   11: 'Fall'
}

def time_of_day(h):
    if h < 6:  return 'Night'
    if h < 12: return 'Morning'
    if h < 17: return 'Afternoon'
    if h < 21: return 'Evening'
    return 'Night'

df['month']        = df['started_at'].dt.month
df['month_name']   = df['started_at'].dt.strftime('%b %Y')
df['day_of_week']  = df['started_at'].dt.dayofweek   # 0 = Monday
df['day_name']     = df['started_at'].dt.strftime('%a')
df['hour']         = df['started_at'].dt.hour
df['season']       = df['month'].map(season_map)
df['is_weekend']   = df['day_of_week'].isin([5, 6])
df['time_of_day']  = df['hour'].map(time_of_day)
df['station_complete'] = (
    df['start_station_name'].notna() & df['end_station_name'].notna()
)

print(f"\nFeature engineering complete.")
print(f"Final dataset: {len(df):,} rows | {len(df.columns)} columns")

# Save cleaned dataset as Parquet for efficient reuse
df.to_parquet(OUTPUT_DIR + 'cyclistic_clean.parquet', index=False)
print(f"Saved: {OUTPUT_DIR}cyclistic_clean.parquet")


# =============================================================================
# PHASE 3 — ANALYZE
# Compute aggregations used in the visualizations
# =============================================================================

print("\n" + "=" * 60)
print("PHASE 3 — ANALYZE")
print("=" * 60)

# Exclude the 11 stray Mar 2025 rows at the edge of the dataset
df_12 = df[~(
    (df['started_at'].dt.year == 2025) & (df['started_at'].dt.month == 3)
)]

# --- Overall split ---
counts = df['member_casual'].value_counts()
print(f"\nRide split:\n{counts}")
print(f"Casual share: {counts['casual'] / counts.sum() * 100:.1f}%")

# --- Ride duration ---
duration_stats = df.groupby('member_casual')['ride_length_min'].describe(
    percentiles=[.25, .5, .75, .95]
).round(1)
print(f"\nRide duration by user type:\n{duration_stats}")

# --- Day of week ---
dow_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
dow = (df.groupby(['member_casual', 'day_name', 'day_of_week'])
         .size().reset_index(name='rides').sort_values('day_of_week'))
print(f"\nRides by day of week:\n{dow.to_string(index=False)}")

# --- Weekend vs weekday ---
weekend = df.groupby(['member_casual', 'is_weekend']).size().unstack()
weekend.columns = ['Weekday', 'Weekend']
weekend['Weekend %'] = (weekend['Weekend'] / weekend.sum(axis=1) * 100).round(1)
print(f"\nWeekend breakdown:\n{weekend}")

# --- Hourly pattern ---
hourly = df.groupby(['member_casual', 'hour']).size().reset_index(name='rides')

# --- Monthly trend ---
month_order = [
    'Apr 2025', 'May 2025', 'Jun 2025', 'Jul 2025',
    'Aug 2025', 'Sep 2025', 'Oct 2025', 'Nov 2025',
    'Dec 2025', 'Jan 2026', 'Feb 2026', 'Mar 2026'
]
monthly = df_12.groupby(['member_casual', 'month_name']).size().reset_index(name='rides')
monthly['month_name'] = pd.Categorical(
    monthly['month_name'], categories=month_order, ordered=True
)
monthly = monthly.sort_values('month_name')

# --- Average duration by day ---
avg_len_dow = (df.groupby(['member_casual', 'day_name', 'day_of_week'])
                 ['ride_length_min'].mean().reset_index()
                 .sort_values('day_of_week'))

# --- Seasonal ---
season_order = ['Spring', 'Summer', 'Fall', 'Winter']
seasonal = df.groupby(['member_casual', 'season']).size().reset_index(name='rides')
seasonal['season'] = pd.Categorical(
    seasonal['season'], categories=season_order, ordered=True
)
seasonal = seasonal.sort_values('season')

# --- Bike type ---
bike = df.groupby(['member_casual', 'rideable_type']).size().reset_index(name='rides')

# --- Duration samples for boxplot ---
median_len = df.groupby('member_casual')['ride_length_min'].median()
rld_m = df[df['member_casual'] == 'member']['ride_length_min'].clip(
    upper=60).sample(50000, random_state=42).values
rld_c = df[df['member_casual'] == 'casual']['ride_length_min'].clip(
    upper=60).sample(50000, random_state=42).values

# Free memory before plotting
del df, df_12
print("\nAnalysis complete. Generating visualizations...")


# =============================================================================
# PHASE 4 — SHARE
# Generate and export all visualizations
# =============================================================================

def save_chart(name):
    """Save chart to CHARTS_DIR and display inline in notebook."""
    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}{name}.png', dpi=120, bbox_inches='tight')
    plt.show()   # displays inline in Jupyter / Colab
    plt.close()
    print(f"  Saved: {name}.png")

print("\n" + "=" * 60)
print("PHASE 4 — SHARE")
print("=" * 60)

# --- Figure 1: Total rides by user type (donut) ---
total = counts.sum()
fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts, autotexts = ax.pie(
    [counts['member'], counts['casual']],
    labels=['Members', 'Casual Riders'],
    colors=[MEMBER_COLOR, CASUAL_COLOR],
    autopct='%1.1f%%', startangle=90,
    wedgeprops={'width': 0.5, 'edgecolor': 'white', 'linewidth': 2},
    textprops={'fontsize': 13}
)
for at in autotexts:
    at.set_fontsize(13)
    at.set_fontweight('bold')
    at.set_color('white')
ax.set_title(
    'Total Rides by User Type\nApr 2025 – Mar 2026',
    fontsize=15, fontweight='bold', pad=20
)
ax.text(0, 0, f'{total / 1e6:.1f}M\nrides',
        ha='center', va='center', fontsize=14,
        fontweight='bold', color='#333333')
save_chart('01_rides_by_type')

# --- Figure 2: Rides by day of week ---
fig, ax = plt.subplots(figsize=(10, 5))
x = range(7)
w = 0.35
m_data = dow[dow['member_casual'] == 'member'].sort_values('day_of_week')['rides'].values
c_data = dow[dow['member_casual'] == 'casual'].sort_values('day_of_week')['rides'].values
ax.bar([i - w/2 for i in x], m_data, w, label='Members', color=MEMBER_COLOR, alpha=0.9)
ax.bar([i + w/2 for i in x], c_data, w, label='Casual',  color=CASUAL_COLOR, alpha=0.9)
ax.set_xticks(list(x))
ax.set_xticklabels(dow_order, fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1000:.0f}K'))
ax.set_ylabel('Number of Rides', fontsize=12)
ax.set_title('Rides by Day of Week', fontsize=15, fontweight='bold')
ax.legend(fontsize=12)
ax.axvspan(4.5, 6.5, alpha=0.05, color='gray')
ax.text(5.5, max(m_data) * 0.97, 'Weekend', ha='center', fontsize=10, color='gray')
save_chart('02_rides_by_dow')

# --- Figure 3: Average ride duration by day ---
fig, ax = plt.subplots(figsize=(10, 5))
for label, color in PALETTE.items():
    d = avg_len_dow[avg_len_dow['member_casual'] == label].sort_values('day_of_week')
    ax.plot(d['day_name'], d['ride_length_min'],
            marker='o', linewidth=2.5, markersize=8,
            label=label.capitalize(), color=color)
ax.set_ylabel('Avg Ride Duration (min)', fontsize=12)
ax.set_title('Average Ride Duration by Day of Week', fontsize=15, fontweight='bold')
ax.legend(fontsize=12)
ax.set_ylim(0)
save_chart('03_avg_duration_dow')

# --- Figure 4: Rides by hour of day ---
fig, ax = plt.subplots(figsize=(12, 5))
max_rides = 0
for label, color in PALETTE.items():
    d = hourly[hourly['member_casual'] == label].sort_values('hour')
    ax.fill_between(d['hour'], d['rides'], alpha=0.2, color=color)
    ax.plot(d['hour'], d['rides'], linewidth=2.5,
            label=label.capitalize(), color=color)
    max_rides = max(max_rides, d['rides'].max())
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1000:.0f}K'))
ax.set_xlabel('Hour of Day', fontsize=12)
ax.set_ylabel('Number of Rides', fontsize=12)
ax.set_title('Rides by Hour of Day', fontsize=15, fontweight='bold')
ax.set_xticks(range(0, 24, 2))
ax.legend(fontsize=12)
ax.axvspan(7, 9, alpha=0.08, color=MEMBER_COLOR)
ax.axvspan(16, 18, alpha=0.08, color=MEMBER_COLOR)
ax.text(8,  max_rides * 0.88, 'AM\nCommute', ha='center', fontsize=9, color=MEMBER_COLOR)
ax.text(17, max_rides * 0.88, 'PM\nCommute', ha='center', fontsize=9, color=MEMBER_COLOR)
save_chart('04_rides_by_hour')

# --- Figure 5: Monthly ride volume ---
fig, ax = plt.subplots(figsize=(13, 5))
for label, color in PALETTE.items():
    d = monthly[monthly['member_casual'] == label].sort_values('month_name')
    ax.fill_between(range(12), d['rides'].values, alpha=0.15, color=color)
    ax.plot(range(12), d['rides'].values, marker='o', linewidth=2.5,
            markersize=7, label=label.capitalize(), color=color)
ax.set_xticks(range(12))
ax.set_xticklabels([m.replace(' ', '\n') for m in month_order], fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1000:.0f}K'))
ax.set_ylabel('Number of Rides', fontsize=12)
ax.set_title('Monthly Ride Volume — Apr 2025 to Mar 2026', fontsize=15, fontweight='bold')
ax.legend(fontsize=12)
save_chart('05_monthly_trend')

# --- Figure 6: Ride duration distribution (boxplot) ---
# Uses a 50K sample per group for performance; capped at 60 min for readability
fig, ax = plt.subplots(figsize=(8, 5))
plot_df = pd.DataFrame({
    'ride_length_min': list(rld_m) + list(rld_c),
    'member_casual':   ['member'] * 50000 + ['casual'] * 50000
})
sns.boxplot(
    data=plot_df, x='member_casual', y='ride_length_min',
    hue='member_casual', palette=PALETTE, width=0.4, ax=ax,
    order=['member', 'casual'], legend=False,
    medianprops={'color': 'white', 'linewidth': 2.5}
)
ax.set_xticks([0, 1])
ax.set_xticklabels(['Members', 'Casual Riders'], fontsize=13)
ax.set_xlabel('')
ax.set_ylabel('Ride Duration (min)', fontsize=12)
ax.set_title(
    'Ride Duration Distribution\n(50K sample per group, capped at 60 min)',
    fontsize=14, fontweight='bold'
)
ax.text(0, median_len['member'] + 0.5,
        f"Median: {median_len['member']:.1f} min",
        ha='center', fontsize=10, color=MEMBER_COLOR, fontweight='bold')
ax.text(1, median_len['casual'] + 0.5,
        f"Median: {median_len['casual']:.1f} min",
        ha='center', fontsize=10, color=CASUAL_COLOR, fontweight='bold')
save_chart('06_ride_length_boxplot')

# --- Figure 7: Rides by season ---
fig, ax = plt.subplots(figsize=(9, 5))
x = range(4)
w = 0.35
m_s = seasonal[seasonal['member_casual'] == 'member']['rides'].values
c_s = seasonal[seasonal['member_casual'] == 'casual']['rides'].values
ax.bar([i - w/2 for i in x], m_s, w, label='Members', color=MEMBER_COLOR, alpha=0.9)
ax.bar([i + w/2 for i in x], c_s, w, label='Casual',  color=CASUAL_COLOR, alpha=0.9)
ax.set_xticks(list(x))
ax.set_xticklabels(season_order, fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1000:.0f}K'))
ax.set_ylabel('Number of Rides', fontsize=12)
ax.set_title('Rides by Season', fontsize=15, fontweight='bold')
ax.legend(fontsize=12)
save_chart('07_rides_by_season')

# --- Figure 8: Bike type preference ---
pivot = bike.pivot(index='member_casual', columns='rideable_type', values='rides')
pivot.index = ['Casual', 'Members']
pivot.columns = ['Classic Bike', 'Electric Bike']
fig, ax = plt.subplots(figsize=(8, 5))
pivot.plot(kind='bar', ax=ax, color=['#4CAF50', '#FF7043'], alpha=0.9, width=0.5)
ax.set_xticklabels(['Casual', 'Members'], rotation=0, fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1e6:.1f}M'))
ax.set_xlabel('')
ax.set_ylabel('Number of Rides', fontsize=12)
ax.set_title('Bike Type Preference by User Type', fontsize=15, fontweight='bold')
ax.legend(fontsize=12)
save_chart('08_bike_type')

print("\nAll visualizations saved to:", CHARTS_DIR)
print("\nAnalysis complete.")
