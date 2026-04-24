# Cyclistic Bike-Share Analysis: How Do Members and Casual Riders Differ?

**Google Data Analytics Professional Certificate — Capstone Case Study**
**Author:** Giacomo | **Date:** April 2026 | **Tools:** Python, pandas, matplotlib, seaborn

---

## Introduction & Business Context

Cyclistic is a Chicago-based bike-share company operating a fleet of over 5,800 bicycles across 692 docking stations throughout the city. Since its launch in 2016, Cyclistic has offered flexible pricing plans to attract a broad user base: single-ride passes, full-day passes, and annual memberships. Riders who purchase annual memberships are referred to as **members**; those who use single-ride or day passes are referred to as **casual riders**.

Cyclistic's finance team has determined that annual members are significantly more profitable than casual riders. The director of marketing, Lily Moreno, believes the company's growth strategy should focus on converting existing casual riders into members rather than acquiring entirely new customers — a more cost-efficient path to revenue growth.

This analysis addresses the first of three strategic questions assigned to the marketing analytics team:

> **How do annual members and casual riders use Cyclistic bikes differently?**

Understanding these behavioral differences is the foundation for designing a targeted conversion campaign. The insights derived from this analysis informed the three recommendations presented in the Act section of this report.

> **Note on data currency:** While the course suggests using 2019–2020 data for this case study, this analysis uses the most recent 12 months available (April 2025 – March 2026), sourced directly from Divvy's public trip data repository. This decision ensures that findings reflect current rider behavior and post-pandemic usage patterns, making the recommendations more actionable for today's business context.

---

## Ask — Business Task & Stakeholders

### Business Task

Analyze 12 months of Cyclistic trip data to identify behavioral differences between casual riders and annual members, and use those differences to inform a marketing strategy aimed at converting casual riders into members.

### Guiding Questions

- How do annual members and casual riders use Cyclistic bikes differently?
- What patterns in ride frequency, duration, timing, and seasonality distinguish the two groups?
- How can these behavioral differences guide targeted marketing decisions?

### Stakeholders

| Stakeholder | Role | Interest in this analysis |
|---|---|---|
| Lily Moreno | Director of Marketing | Needs behavioral insights to design a conversion campaign |
| Cyclistic Executive Team | Decision-makers | Must approve the proposed marketing strategy based on data |
| Cyclistic Marketing Analytics Team | Peers | Will use findings to inform campaign tactics and messaging |

---

## Prepare — Data Sources & Credibility

### Data Source

The data used in this analysis consists of 12 monthly CSV files covering **April 2025 through March 2026**, downloaded from Divvy's public trip data repository, hosted by Motivate International Inc. under a [public license](https://divvybikes.com/data-license-agreement). The dataset is made available for non-commercial analysis and does not require additional authorization.

| Attribute | Detail |
|---|---|
| Source | Divvy Bikes / Motivate International Inc. |
| Period | April 2025 – March 2026 |
| Files | 12 monthly CSV files |
| Total rows (raw) | 5,242,349 trips |
| Format | CSV, consistent 13-column schema across all files |

### Data Structure

Each row represents one individual trip. The 13 columns include:

- **ride_id** — unique trip identifier
- **rideable_type** — bike type (classic_bike, electric_bike)
- **started_at / ended_at** — trip start and end timestamps
- **start_station_name/id / end_station_name/id** — station identifiers
- **start_lat/lng / end_lat/lng** — GPS coordinates
- **member_casual** — user type (member or casual)

### Credibility Assessment (ROCCC)

| Criterion | Assessment |
|---|---|
| **Reliable** | Data is collected automatically by Divvy's docking system — not self-reported |
| **Original** | First-party data from the operator of the bike-share system |
| **Comprehensive** | Covers all trips system-wide for the full 12-month period |
| **Current** | Most recent 12 months available as of April 2026 |
| **Cited** | Publicly attributed to Motivate International Inc. under open license |

### Privacy & Limitations

The dataset contains no personally identifiable information (PII). Rider identity, payment details, and demographic data are not included, which means it is not possible to determine whether a casual rider has purchased multiple passes or to link trips across sessions. Analysis is limited to aggregate behavioral patterns.

---

## Process — Data Cleaning & Transformation

### Tools

Python was chosen for this analysis given the dataset size (~5.2M rows, ~1 GB across 12 files). The following libraries were used:

- **pandas** — data loading, cleaning, aggregation, and feature engineering
- **matplotlib / seaborn** — data visualization
- **pyarrow** — efficient storage of the cleaned dataset in Parquet format

### Schema Validation

Before loading the full dataset, the column schema was verified across all 12 files. All files share an identical 13-column structure with consistent data types, confirming no schema drift across the annual period.

### Cleaning Steps

| Step | Action | Rows affected |
|---|---|---|
| Null user type | Removed 1 row where `member_casual` was null | −1 |
| Negative/zero duration | Removed trips where `ended_at ≤ started_at` | −29 |
| Rides under 1 minute | Removed likely false starts and docking errors | −134,162 |
| Rides over 24 hours | Removed likely unreturned or stolen bikes | −5,047 |
| **Total removed** | | **−139,239 (2.66%)** |
| **Final dataset** | | **5,103,110 trips** |

### Notes on Station Nulls

Approximately 21% of trips have null values in the station name and ID columns. This is expected behavior for electric bikes, which can be locked anywhere within the service area rather than at a fixed docking station. These rows were retained for all analyses that do not depend on station-level data.

### Feature Engineering

The following columns were derived from the raw data to enable temporal and behavioral analysis:

| New column | Derived from | Description |
|---|---|---|
| `ride_length_min` | `ended_at − started_at` | Trip duration in minutes |
| `month` | `started_at` | Month number (1–12) |
| `month_name` | `started_at` | Month label (e.g., "Apr 2025") |
| `day_of_week` | `started_at` | Day number (0 = Monday) |
| `day_name` | `started_at` | Day label (e.g., "Sat") |
| `hour` | `started_at` | Hour of day (0–23) |
| `season` | `month` | Spring / Summer / Fall / Winter |
| `is_weekend` | `day_of_week` | Boolean flag for Saturday and Sunday |
| `time_of_day` | `hour` | Night / Morning / Afternoon / Evening |

---

## Analyze — Key Findings

### Overall Ride Distribution

Of the 5,103,110 trips analyzed, **65.2% were taken by members** and **34.8% by casual riders**. While members dominate by volume, casual riders represent a substantial and commercially significant segment.

### Finding 1: Members Commute, Casual Riders Explore

The hourly distribution of rides reveals the most fundamental behavioral difference between the two groups. Members show a clear **bimodal pattern** with peaks at 8 AM and 5 PM — the classic commute signature. Casual riders, by contrast, display a **unimodal curve** that builds gradually through the morning and peaks in the mid-to-late afternoon (~3–5 PM), consistent with leisure and recreational use.

This distinction is reinforced by the weekly pattern: members ride most on Tuesday through Thursday, while casual riders peak on **Saturday and Sunday**, generating 37.7% of their total trips on weekends vs. 23.4% for members.

### Finding 2: Casual Riders Take Longer Trips

Despite taking fewer trips overall, casual riders spend significantly more time on bikes per ride:

| Metric | Members | Casual Riders |
|---|---|---|
| Median ride duration | 8.7 min | 11.8 min |
| Difference | — | +36% longer |

This gap holds across every day of the week and widens further on weekends, when casual riders average their longest rides. The pattern is consistent with leisure use: casual riders are less focused on getting from A to B efficiently and more likely to ride for the experience itself.

### Finding 3: Casual Riders Are Highly Seasonal

Both groups show reduced activity in winter, but the drop is far more pronounced for casual riders. In summer (June–August), casual riders account for approximately **42% of all trips** — their highest share of the year. By January, that share falls to roughly **17%**. Members maintain a more stable year-round presence, suggesting their bike use is integrated into daily routines regardless of weather.

This seasonal concentration has direct implications for campaign timing: the window of maximum casual rider engagement is narrow and predictable.

### Finding 4: Bike Type Preference Is Similar

Both members and casual riders show a preference for electric bikes over classic bikes, with no meaningful difference in the ratio between groups. Bike type does not appear to be a differentiating factor in usage behavior.

---

## Share — Visualizations & Insights

The following visualizations were produced in Python using matplotlib and seaborn. All charts use a consistent color scheme: **blue (#1A73E8) for members** and **amber (#F4A300) for casual riders**.

---

**Figure 1 — Total Rides by User Type**
Members account for 65.2% of all trips (3.3M), casual riders for 34.8% (1.8M). Despite the volume gap, casual riders represent a large and engaged base — roughly 1 in 3 rides.

---

**Figure 2 — Rides by Day of Week**
Members ride most on weekdays (peak: Tuesday–Thursday). Casual riders shift significantly toward the weekend, with Saturday being their highest-volume day. The weekend shaded area highlights the divergence clearly.

---

**Figure 3 — Average Ride Duration by Day of Week**
Casual riders consistently average longer rides than members across all days. The gap widens on weekends, when casual riders reach their longest average durations (~23 min on Saturday vs. ~13 min for members).

---

**Figure 4 — Rides by Hour of Day**
The commute signature of members (twin peaks at 8 AM and 5 PM) contrasts sharply with the smooth afternoon curve of casual riders. This single chart is the clearest visual evidence of the commute vs. leisure divide.

---

**Figure 5 — Monthly Ride Volume (Apr 2025 – Mar 2026)**
Both groups peak in summer and decline in winter. Casual ridership is far more volatile: the gap between their summer peak and winter trough is proportionally much larger than for members.

---

**Figure 6 — Ride Duration Distribution**
Boxplots confirm the duration difference at the distributional level. Casual riders have a higher median and a wider spread, indicating more variable trip lengths consistent with exploratory riding.

---

**Figure 7 — Rides by Season**
Summer is the dominant season for both groups, but the casual-to-member ratio shifts most favorably toward casuals in summer and most unfavorably in winter. Fall shows a steeper drop for casuals than members.

---

**Figure 8 — Bike Type Preference**
Both groups prefer electric bikes, with similar proportions of classic vs. electric use. Bike type is not a differentiating behavioral variable between members and casual riders.

---

## Act — Recommendations

Based on the analysis, three data-driven recommendations are proposed to guide Cyclistic's marketing strategy for converting casual riders into annual members.

---

**Recommendation 1: Launch a Weekend Membership Tier**

Casual riders generate 37.7% of their trips on weekends, compared to only 23.4% for members. This signals that a significant share of casual riders uses Cyclistic primarily for leisure on Saturdays and Sundays — a usage pattern that a standard annual membership may not feel relevant to.

*Recommended action:* Introduce a weekend-focused membership option (e.g., "Weekend Pass") at a lower annual price point than the full membership. This lowers the commitment barrier for casual riders whose primary use case is recreational. Pair the offer with messaging that emphasizes savings per ride: casual riders average 11.8 minutes per trip vs. 8.7 minutes for members, meaning they spend more time on bikes per ride and have more to gain from a flat-rate plan.

---

**Recommendation 2: Concentrate Conversion Campaigns in Summer**

Summer (June–August) represents the peak season for casual ridership. During this period, casual riders account for approximately 42% of all trips — their highest share of the year. By contrast, in January that share drops to roughly 17%. Casual riders are highly seasonal, and their engagement window is concentrated.

*Recommended action:* Allocate the majority of the conversion marketing budget to a summer campaign (June–August). This is when casual riders are most active, most engaged with the product, and most likely to perceive value in a membership. Campaigns launched outside this window face a structurally smaller and less receptive audience. Messaging should emphasize the cost advantage of membership over single-ride or day-pass pricing across an entire season of frequent use.

---

**Recommendation 3: Activate Conversion at High-Casual Stations**

The dataset includes GPS coordinates for every trip's start and end station. Spatial analysis reveals that casual ridership is not uniformly distributed across the city — it concentrates around specific areas, likely near lakefront parks, tourist destinations, and recreational zones. These locations represent high-intent touchpoints where casual riders are already engaged with the product.

*Recommended action:* Deploy targeted in-person and digital activation at the top stations by casual ride volume. Tactics may include QR-code membership sign-up displays at docking stations, geo-targeted mobile ads within proximity of these locations, and promotional staff during summer weekends. Concentrating acquisition efforts where casual riders already are maximizes conversion efficiency and reduces wasted spend on audiences less likely to convert.

---

*This case study was completed as part of the Google Data Analytics Professional Certificate. Data provided by Motivate International Inc. under public license.*
