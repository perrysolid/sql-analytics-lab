# SQL Playgrounds with NYC Taxi Data

## 🎯 **Perfect for SQL Technical Interviews & Learning**

This playground is an **ideal resource for SQL technical interviews and database skill development**. It features **real-world production data** (3-5 million records per month) and **comprehensive technical interview questions** covering all levels from mid to senior database engineering roles.

### 📚 **Complete Technical Interview Guide**
- **15 detailed interview questions** with full answers covering data modeling, ETL, performance optimization, complex analytics, geospatial analysis, data quality, and system architecture
- **Production-ready scenarios** based on real NYC taxi data challenges
- **Multi-level difficulty** suitable for mid to senior SQL developers
- **Complete documentation**: [`docs/interviews/sql-interview-questions.md`](docs/interviews/sql-interview-questions.md)

### 🚀 **Interview Question Categories**
- **Data Modeling & Schema Design**: Normalization, dimensional modeling, partitioning strategies
- **Data Ingestion & ETL**: Duplicate prevention, pipeline design, error handling
- **Performance & Optimization**: Index strategies, query optimization, execution plans
- **Complex Queries & Analytics**: Window functions, time series analysis, business intelligence
- **Geospatial & PostGIS**: Spatial analysis, geometric operations, location-based queries
- **Data Quality & Integrity**: Data validation, anomaly detection, cleaning strategies
- **System Architecture & Scalability**: High availability, monitoring, production deployment

### 💡 **Why This Playground for Interviews?**
- **Real Production Data**: authentic NYC taxi records, not synthetic datasets
- **Complex Schema**: 21-column fact table with geospatial dimensions and lookup tables
- **Production Challenges**: Data quality issues, performance optimization, scale considerations
- **Complete ETL Pipeline**: Hash-based duplicate prevention, chunked processing, error recovery
- **Advanced Features**: PostGIS spatial analysis, time-series data, multi-borough analytics
- **🎯 Business Intelligence**: Apache Superset for creating professional dashboards and data visualizations
- **📈 Data Storytelling**: Transform SQL queries into compelling visual narratives and interactive reports

---

A production-ready Docker-based SQL playground featuring PostgreSQL 17 + PostGIS 3.5, PGAdmin, and **Apache Superset** for business intelligence with authentic NYC Yellow Taxi trip data. Query millions of records through **interactive dashboards, SQL Lab, and custom visualizations** while leveraging automated data backfill system that can load multiple months (3-5 million records per month) with single-command deployment.

## Features

- **PostgreSQL 17 + PostGIS 3.5** with geospatial support and custom Python environment
- **PGAdmin 4** (latest) for web-based database management and query execution
- **🚀 Apache Superset** modern business intelligence platform with interactive dashboards, SQL Lab, and advanced visualizations
- **📊 Visual Analytics** - Create charts, graphs, and dashboards from millions of NYC taxi records
- **🔍 SQL Lab Integration** - Write complex queries with autocomplete and export results directly from Superset
- **📱 Interactive Dashboards** - Cross-filtering, drill-down capabilities, and real-time data exploration
- **Automated Backfill System** - Download and load multiple months of authentic NYC taxi data
- **Flexible Data Loading** - Load specific months, last 6/12 months, or all available data (2009-2025)
- **Complete Geospatial Data** - 263 official NYC taxi zones with polygon boundaries (auto-downloaded)
- **Unified Data Management** - Single location for all data with automatic downloads from official sources
- **Dictionary Table Cleaning** - Fresh reference data loaded with each backfill for consistency
- **Production-Scale Performance** - Optimized schema with spatial indexes for big data analytics
- **Memory-Efficient Loading** - Chunked processing handles large datasets safely
- **Persistent Logging** - Organized logs by configuration with full traceability
- **Hash-Based Duplicate Prevention** - Ultimate protection against duplicate data with SHA-256 row hashing
- **Star Schema Support** - Dimensional modeling with fact and dimension tables for advanced analytics
- **Historical Data Support** - Complete NYC TLC data coverage from 2009 to present

## 📚 Table of Contents

- [📝 SQL Technical Interview Questions](#-sql-technical-interview-questions)
- [🚀 Quick Start](#quick-start)
- [🏗️ Data Pipeline Architecture](#data-pipeline-architecture)
- [🔧 Architecture & Data Loading](#architecture--data-loading)
  - [Automated Backfill System](#automated-backfill-system)
  - [Complete Initialization Process](#complete-initialization-process)
  - [Architecture Benefits](#architecture-benefits)
- [📁 Project Structure](#project-structure)
- [🐳 Container Architecture](#container-architecture)
  - [Custom PostgreSQL Container](#custom-postgresql-container)
  - [Apache Superset Container](#apache-superset-container)
  - [Volume Strategy](#volume-strategy)
  - [Memory & Performance](#memory--performance)
- [⏸️ Pause and Resume Capability](#pause-and-resume-capability)
  - [Safe Interruption and Continuation](#safe-interruption-and-continuation)
  - [Intelligent Resume System](#intelligent-resume-system)
- [⚙️ Configuration & Development](#configuration--development)
  - [Environment Variables](#environment-variables-env)
  - [System Requirements](#system-requirements)
  - [Development Commands](#development-commands)
- [🗄️ Database Schema & Analytics](#database-schema--analytics)
  - [NYC Taxi Data Structure](#nyc-taxi-data-structure)
  - [Performance Optimizations](#performance-optimizations)
    - [Database Indexes](#database-indexes)
    - [Materialized Views](#materialized-views)
    - [PostgreSQL Runtime Tuning](#postgresql-runtime-tuning)
    - [PostgreSQL vs BigQuery: Architectural Differences](#postgresql-vs-bigquery-architectural-differences)
- [📈 Data Sources & Authenticity](#data-sources--authenticity)
- [🚀 Apache Superset Business Intelligence Features](#-apache-superset-business-intelligence-features)
  - [📊 Rich Visualization Gallery](#-rich-visualization-gallery)
  - [⚡ Advanced SQL Lab](#-advanced-sql-lab)
  - [🎛️ Interactive Dashboard Features](#️-interactive-dashboard-features)
  - [📈 Perfect for Data Presentations](#-perfect-for-data-presentations)
  - [🔧 Enterprise-Ready Configuration](#-enterprise-ready-configuration)
  - [Sample Dashboard Ideas](#sample-dashboard-ideas)
- [📊 Sample Analytics Queries](#sample-analytics-queries)
  - [1. Trip Volume by Hour](#1-trip-volume-by-hour)
  - [2. Largest Taxi Zones by Area (PostGIS)](#2-largest-taxi-zones-by-area-postgis)
  - [3. Cross-Borough Trip Analysis](#3-cross-borough-trip-analysis)
  - [4. Payment Patterns by Borough](#4-payment-patterns-by-borough)
  - [Why Pre-Aggregation Helps: Hash Join Explained](#why-pre-aggregation-helps-hash-join-explained)
  - [5. Basic Data Overview](#5-basic-data-overview)
  - [6. Payment Method Analysis](#6-payment-method-analysis)
  - [7. Top Revenue Generating Trips](#7-top-revenue-generating-trips)
  - [8. Trip Distance Distribution](#8-trip-distance-distribution)
  - [9. Daily Trip Patterns](#9-daily-trip-patterns)
  - [10. Rush Hour Analysis](#10-rush-hour-analysis)
  - [11. Tip Analysis by Payment Type](#11-tip-analysis-by-payment-type)
  - [12. Weekend vs Weekday Analysis](#12-weekend-vs-weekday-analysis)
  - [13. Long Distance Trips (Over 20 Miles)](#13-long-distance-trips-over-20-miles)
- [📊 Materialized View Queries](#sample-analytics-queries--materialized-view-versions)

## 📝 SQL Technical Interview Questions

**SQL Technical Interview Questions** — 19 questions with answers and implementation references

<details>
<summary><strong>Click to expand full interview questions guide</strong></summary>

# SQL Technical Interview Questions
## NYC Taxi Database - Mid to Senior Level

*Based on the NYC Yellow Taxi Trip Records database with 3-6 M records per month, PostGIS spatial data, and production-level data ingestion pipeline.*

---

## Table of Contents
1. [Data Modeling & Schema Design](#data-modeling--schema-design)
   - [Question 1: Schema Analysis](#question-1-schema-analysis)
   - [Question 2: Dimensional Modeling](#question-2-dimensional-modeling)
2. [Data Ingestion & ETL](#data-ingestion--etl)
   - [Question 3: Duplicate Prevention Strategy](#question-3-duplicate-prevention-strategy)
   - [Question 4: ETL Pipeline Design](#question-4-etl-pipeline-design)
3. [Performance & Optimization](#performance--optimization)
   - [Question 5: Index Strategy](#question-5-index-strategy)
   - [Question 6: Query Optimization](#question-6-query-optimization)
4. [Complex Queries & Analytics](#complex-queries--analytics)
   - [Question 7: Window Functions](#question-7-window-functions)
   - [Question 8: Time Series Analysis](#question-8-time-series-analysis)
5. [Geospatial & PostGIS](#geospatial--postgis)
   - [Question 9: Spatial Analysis](#question-9-spatial-analysis)
   - [Question 10: Complex Geospatial Query](#question-10-complex-geospatial-query)
6. [Data Quality & Integrity](#data-quality--integrity)
   - [Question 11: Data Quality Assessment](#question-11-data-quality-assessment)
   - [Question 12: Data Cleaning Strategy](#question-12-data-cleaning-strategy)
7. [System Architecture & Scalability](#system-architecture--scalability)
   - [Question 13: Database Partitioning Strategy](#question-13-database-partitioning-strategy)
   - [Question 14: High Availability Architecture](#question-14-high-availability-architecture)
   - [Question 15: Monitoring and Alerting](#question-15-monitoring-and-alerting)
8. [Advanced Star Schema & ETL Engineering](#advanced-star-schema--etl-engineering)
   - [Question 16: Star Schema Migration Strategy](#question-16-star-schema-migration-strategy)
   - [Question 17: Hash-Based Duplicate Prevention at Scale](#question-17-hash-based-duplicate-prevention-at-scale)
   - [Question 18: Advanced Dimensional Analytics](#question-18-advanced-dimensional-analytics)
   - [Question 19: ETL Pipeline Error Recovery and Data Quality Assurance](#question-19-etl-pipeline-error-recovery-and-data-quality-assurance)

---

## Data Modeling & Schema Design

### Question 1: Schema Analysis
**Question:** Looking at this NYC taxi schema, identify potential issues and suggest improvements:
```sql
CREATE TABLE nyc_taxi.yellow_taxi_trips (
    vendorid INTEGER,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count DECIMAL(4,1),
    trip_distance DECIMAL(8,2),
    -- ... 20+ columns total
    row_hash VARCHAR(64) UNIQUE
);
```

**Answer:**
1. **Missing Primary Key**: No explicit PK leads to potential issues with replication, referential integrity
2. **Normalization Opportunities**: `vendorid` should reference `vendor_lookup` table with proper FK constraints
3. **Partitioning Strategy**: 3.4M+ records/month suggests monthly/yearly partitioning by `tpep_pickup_datetime`
4. **Index Strategy**: Missing composite indexes for common query patterns. For example, analytical queries that filter trips by pickup location within a date range benefit from a composite index that leads with location and includes the timestamp:
   ```sql
   CREATE INDEX idx_yellow_taxi_location_datetime
       ON yellow_taxi_trips (pulocationid, tpep_pickup_datetime);
   ```
   This lets PostgreSQL satisfy `WHERE pulocationid = 132 AND tpep_pickup_datetime BETWEEN '2024-01-01' AND '2024-01-31'` with a single index range scan instead of scanning the full table or intersecting two separate single-column indexes
5. **Data Types**: Consider if `DECIMAL(4,1)` for passenger_count is appropriate vs INTEGER

**Improved Design:**
```sql
CREATE TABLE nyc_taxi.yellow_taxi_trips (
    trip_id BIGSERIAL PRIMARY KEY,
    vendorid INTEGER REFERENCES vendor_lookup(vendorid),
    tpep_pickup_datetime TIMESTAMP NOT NULL,
    tpep_dropoff_datetime TIMESTAMP NOT NULL,
    -- ... other columns
    row_hash VARCHAR(64) UNIQUE NOT NULL,
    CONSTRAINT valid_trip_duration CHECK (tpep_dropoff_datetime > tpep_pickup_datetime)
) PARTITION BY RANGE (tpep_pickup_datetime);

-- The PARTITION BY clause only declares the strategy.
-- You must create child partitions — without them, INSERTs will fail
-- with "no partition of relation found for row".

-- Create monthly partitions:
CREATE TABLE yellow_taxi_trips_2024_01
    PARTITION OF nyc_taxi.yellow_taxi_trips
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE yellow_taxi_trips_2024_02
    PARTITION OF nyc_taxi.yellow_taxi_trips
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- In production, automate partition creation with a maintenance function
-- or pg_partman extension rather than creating them manually.
```

> **Our implementation:** Schema definition in [01-nyc-taxi-schema.sql (L18–L58)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L18-L58) — main table with `row_hash` primary key and composite indexes [(L388–L390)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L388-L390). Automated partition management in [02-phase2-partitioning.sql](../../postgres/sql-scripts/model-scripts/02-phase2-partitioning.sql) — `create_monthly_partition()` [(L79)](../../postgres/sql-scripts/model-scripts/02-phase2-partitioning.sql#L79), `maintain_partitions()` [(L176)](../../postgres/sql-scripts/model-scripts/02-phase2-partitioning.sql#L176), and `daily_partition_maintenance()` [(L351)](../../postgres/sql-scripts/model-scripts/02-phase2-partitioning.sql#L351).

### Question 2: Dimensional Modeling
**Question:** Design a star schema for taxi trip analytics. What would be your fact table and dimension tables?

**Answer:**
```sql
-- Fact Table
CREATE TABLE nyc_taxi.fact_taxi_trips (
    trip_id BIGSERIAL PRIMARY KEY,
    pickup_location_key INTEGER REFERENCES dim_locations(location_key),
    dropoff_location_key INTEGER REFERENCES dim_locations(location_key),
    pickup_date_key INTEGER REFERENCES dim_date(date_key),
    pickup_time_key INTEGER REFERENCES dim_time(time_key),
    vendor_key INTEGER REFERENCES dim_vendor(vendor_key),
    rate_code_key INTEGER REFERENCES dim_rate_code(rate_code_key),
    payment_type_key INTEGER REFERENCES dim_payment_type(payment_type_key),

    -- Measures
    trip_distance DECIMAL(8,2),
    fare_amount DECIMAL(8,2),
    tip_amount DECIMAL(8,2),
    total_amount DECIMAL(8,2),
    passenger_count INTEGER
);

-- Dimension Tables
CREATE TABLE nyc_taxi.dim_locations (
    location_key SERIAL PRIMARY KEY,
    locationid INTEGER,
    zone VARCHAR(100),
    borough VARCHAR(50),
    service_zone VARCHAR(50),
    geometry GEOMETRY(MULTIPOLYGON, 2263)
);

CREATE TABLE nyc_taxi.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    day_of_week INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);
```

> **Our implementation:** [01-phase1-star-schema.sql](../../postgres/sql-scripts/model-scripts/01-phase1-star-schema.sql) — `fact_taxi_trips` [(L103)](../../postgres/sql-scripts/model-scripts/01-phase1-star-schema.sql#L103) with 6 dimension tables: `dim_date` [(L15)](../../postgres/sql-scripts/model-scripts/01-phase1-star-schema.sql#L15), `dim_time` [(L35)](../../postgres/sql-scripts/model-scripts/01-phase1-star-schema.sql#L35), `dim_locations` [(L48)](../../postgres/sql-scripts/model-scripts/01-phase1-star-schema.sql#L48), `dim_vendor` [(L64)](../../postgres/sql-scripts/model-scripts/01-phase1-star-schema.sql#L64), `dim_payment_type` [(L76)](../../postgres/sql-scripts/model-scripts/01-phase1-star-schema.sql#L76), `dim_rate_code` [(L87)](../../postgres/sql-scripts/model-scripts/01-phase1-star-schema.sql#L87). Data migration in [04-data-migration.sql — `migrate_taxi_data_to_star_schema()` (L38)](../../postgres/sql-scripts/model-scripts/04-data-migration.sql#L38).

---

## Data Ingestion & ETL

### Question 3: Duplicate Prevention Strategy
**Question:** You're loading 3.4M records monthly. How would you prevent duplicates in a production environment?

**Answer:**
Based on the existing system's approach:

1. **Hash-Based Deduplication**:
```python
def calculate_row_hash(row):
    row_dict = {}
    for column, value in row.items():
        if pd.isna(value) or value is None:
            row_dict[column] = ""
        elif isinstance(value, float):
            row_dict[column] = f"{value:.10f}"  # Consistent precision
        else:
            row_dict[column] = str(value)

    row_json = json.dumps(row_dict, sort_keys=True)
    return hashlib.sha256(row_json.encode('utf-8')).hexdigest()
```

2. **Processing State Tracking**:
```sql
CREATE TABLE nyc_taxi.data_processing_log (
    data_year INTEGER,
    data_month INTEGER,
    status VARCHAR(20) CHECK (status IN ('in_progress', 'completed', 'failed')),
    records_loaded BIGINT,
    UNIQUE(data_year, data_month)
);
```

3. **Upsert Pattern**:
```sql
INSERT INTO nyc_taxi.yellow_taxi_trips (...)
VALUES (...)
ON CONFLICT (row_hash) UPDATE;
```

> **Our implementation:** [init-data.py](../../postgres/docker/init-data.py) — `calculate_row_hash()` [(L627)](../../postgres/docker/init-data.py#L627) with SHA-256 hashing, `add_row_hash_column()` [(L661)](../../postgres/docker/init-data.py#L661) for batch hash generation, and hash collision detection [(L668–L675)](../../postgres/docker/init-data.py#L668-L675). Processing log tracked in [01-nyc-taxi-schema.sql — `data_processing_log` (L333)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L333).

### Question 4: ETL Pipeline Design
**Question:** Design an ETL pipeline to process monthly taxi data files. Consider error handling, monitoring, and recovery.

**Answer:**
```python
class TaxiDataETLPipeline:
    def __init__(self, engine, chunk_size=10000):
        self.engine = engine
        self.chunk_size = chunk_size

    def extract(self, year, month):
        url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet"
        return self.download_with_retry(url)

    def transform(self, df):
        # Data cleaning and validation
        df.columns = df.columns.str.lower()
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        df = self.add_row_hash_column(df)
        return self.validate_data_quality(df)

    def load(self, df, year, month):
        self.start_processing_log(year, month)
        try:
            loaded_rows = self.chunked_upsert(df)
            self.complete_processing_log(year, month, loaded_rows)
            return loaded_rows
        except Exception as e:
            self.fail_processing_log(year, month)
            raise

    def validate_data_quality(self, df):
        # Check for required fields
        required_fields = ['tpep_pickup_datetime', 'tpep_dropoff_datetime']
        for field in required_fields:
            if df[field].isna().sum() > df.shape[0] * 0.01:  # >1% nulls
                raise ValueError(f"Too many nulls in {field}")

        # Check for reasonable trip distances
        if (df['trip_distance'] > 200).sum() > 0:
            logger.warning(f"Found {(df['trip_distance'] > 200).sum()} trips >200 miles")

        return df
```

> **Our implementation:** [init-data.py](../../postgres/docker/init-data.py) — `load_trip_data()` [(L1360)](../../postgres/docker/init-data.py#L1360) with chunked loading [(L722, L765–L778)](../../postgres/docker/init-data.py#L722), `download_taxi_data()` [(L496)](../../postgres/docker/init-data.py#L496) with retry logic, and `verify_data_load()` [(L1476)](../../postgres/docker/init-data.py#L1476) for post-load validation.

---

## Performance & Optimization

### Question 5: Index Strategy
**Question:** Given these common queries, design an optimal indexing strategy:
1. Trips by hour of day
2. Revenue by location and date
3. Cross-borough trip analysis
4. Payment method trends over time

**Answer:**
```sql
-- Time-based queries (Question 1)
CREATE INDEX idx_pickup_hour ON yellow_taxi_trips
(EXTRACT(HOUR FROM tpep_pickup_datetime));

-- Location + Date queries (Question 2)
CREATE INDEX idx_location_date ON yellow_taxi_trips
(pulocationid, DATE(tpep_pickup_datetime));

CREATE INDEX idx_location_revenue ON yellow_taxi_trips
(pulocationid, dolocationid) INCLUDE (total_amount);

-- Cross-borough analysis (Question 3)
CREATE INDEX idx_cross_borough ON yellow_taxi_trips
(pulocationid, dolocationid) WHERE pulocationid != dolocationid;

-- Payment trends (Question 4)
CREATE INDEX idx_payment_time ON yellow_taxi_trips
(payment_type, DATE(tpep_pickup_datetime)) INCLUDE (total_amount);

-- Partial indexes for data quality
CREATE INDEX idx_valid_trips ON yellow_taxi_trips (tpep_pickup_datetime)
WHERE trip_distance > 0 AND total_amount > 0;
```

> **Our implementation:** Composite indexes in [01-nyc-taxi-schema.sql (L388–L390)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L388-L390) — `idx_yellow_taxi_datetime_vendor`, `idx_yellow_taxi_location_datetime`, `idx_yellow_taxi_date_payment`. Advanced indexing with covering indexes (INCLUDE), partial indexes (WHERE), and expression indexes in [03-phase3-performance-indexing.sql (L46–L127)](../../postgres/sql-scripts/model-scripts/03-phase3-performance-indexing.sql#L46-L127).

### Question 6: Query Optimization
**Question:** Optimize this slow query that finds peak hour revenue by borough:

```sql
-- Original slow query
SELECT
    b.borough,
    EXTRACT(HOUR FROM yt.tpep_pickup_datetime) as hour,
    SUM(yt.total_amount) as revenue
FROM nyc_taxi.yellow_taxi_trips yt
JOIN nyc_taxi.taxi_zone_lookup b ON yt.pulocationid = b.locationid
GROUP BY b.borough, EXTRACT(HOUR FROM yt.tpep_pickup_datetime)
ORDER BY revenue DESC;
```

**Answer:**
```sql
-- Optimized version
WITH hourly_stats AS (
    SELECT
        yt.pulocationid,
        EXTRACT(HOUR FROM yt.tpep_pickup_datetime) as pickup_hour,
        SUM(yt.total_amount) as total_revenue,
        COUNT(*) as trip_count
    FROM nyc_taxi.yellow_taxi_trips yt
    WHERE yt.tpep_pickup_datetime >= CURRENT_DATE - INTERVAL '30 days'  -- Limit time range
      AND yt.total_amount > 0  -- Filter invalid records
    GROUP BY yt.pulocationid, EXTRACT(HOUR FROM yt.tpep_pickup_datetime)
)
SELECT
    tzl.borough,
    h.pickup_hour,
    SUM(h.total_revenue) as revenue,
    SUM(h.trip_count) as trips
FROM hourly_stats h
JOIN nyc_taxi.taxi_zone_lookup tzl ON h.pulocationid = tzl.locationid
GROUP BY tzl.borough, h.pickup_hour
ORDER BY revenue DESC;

-- Supporting indexes
CREATE INDEX idx_trips_recent_valid ON yellow_taxi_trips
(tpep_pickup_datetime, pulocationid)
WHERE
-- tpep_pickup_datetime >= CURRENT_DATE - INTERVAL '30 days'AND
total_amount > 0;
```

> **Our implementation:** Analytical queries using these optimization patterns in [nyc-taxi-analytics.sql](../../postgres/sql-scripts/report-scripts/nyc-taxi-analytics.sql) — borough-level revenue analysis with CTE pre-aggregation and zone lookups. Star schema optimized queries in [sample-queries.sql](../../postgres/sql-scripts/report-scripts/sample-queries.sql) demonstrating partition pruning and dimension join performance.

---

## Complex Queries & Analytics

### Question 7: Window Functions
**Question:** Write a query to find the top 3 most profitable taxi zones for each borough, including their rank and percentage of borough total revenue.

**Answer:**
```sql
WITH zone_revenue AS (
    SELECT
        tzl.borough,
        tzl.zone,
        tzl.locationid,
        SUM(yt.total_amount) as total_revenue,
        COUNT(*) as trip_count,
        AVG(yt.total_amount) as avg_trip_value
    FROM nyc_taxi.yellow_taxi_trips yt
    JOIN nyc_taxi.taxi_zone_lookup tzl ON yt.pulocationid = tzl.locationid
    WHERE yt.total_amount > 0
    GROUP BY tzl.borough, tzl.zone, tzl.locationid
),
borough_totals AS (
    SELECT
        borough,
        SUM(total_revenue) as borough_total_revenue
    FROM zone_revenue
    GROUP BY borough
),
ranked_zones AS (
    SELECT
        zr.*,
        bt.borough_total_revenue,
        ROW_NUMBER() OVER (PARTITION BY zr.borough ORDER BY zr.total_revenue DESC) as revenue_rank,
        ROUND(100.0 * zr.total_revenue / bt.borough_total_revenue, 2) as pct_of_borough_revenue
    FROM zone_revenue zr
    JOIN borough_totals bt ON zr.borough = bt.borough
)
SELECT
    borough,
    zone,
    revenue_rank,
    total_revenue,
    trip_count,
    avg_trip_value,
    pct_of_borough_revenue
FROM ranked_zones
WHERE revenue_rank <= 3
ORDER BY borough, revenue_rank;
```

> **Our implementation:** Zone revenue ranking queries in [nyc-taxi-analytics.sql](../../postgres/sql-scripts/report-scripts/nyc-taxi-analytics.sql) — borough-level aggregations joining `yellow_taxi_trips` with `taxi_zone_lookup` [(schema at L290)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L290). Star schema version with pre-joined dimensions in [sample-queries.sql](../../postgres/sql-scripts/report-scripts/sample-queries.sql).

### Question 8: Time Series Analysis
**Question:** Identify unusual patterns in daily taxi usage. Flag days where trip volume is more than 2 standard deviations from the 30-day rolling average.

**Answer:**
```sql
WITH daily_trips AS (
    SELECT
        DATE(tpep_pickup_datetime) as trip_date,
        COUNT(*) as daily_trips,
        SUM(total_amount) as daily_revenue,
        EXTRACT(DOW FROM tpep_pickup_datetime) as day_of_week
    FROM nyc_taxi.yellow_taxi_trips
    WHERE tpep_pickup_datetime >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY DATE(tpep_pickup_datetime),
    EXTRACT(DOW FROM tpep_pickup_datetime)
),
rolling_stats AS (
    SELECT
        *,
        AVG(daily_trips) OVER (
            ORDER BY trip_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) as rolling_avg_30d,
        STDDEV(daily_trips) OVER (
            ORDER BY trip_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) as rolling_stddev_30d,
        LAG(daily_trips, 7) OVER (ORDER BY trip_date) as same_weekday_last_week
    FROM daily_trips
)
SELECT
    trip_date,
    daily_trips,
    rolling_avg_30d,
    rolling_stddev_30d,
    ROUND(ABS(daily_trips - rolling_avg_30d) / NULLIF(rolling_stddev_30d, 0), 2) as z_score,
    CASE
        WHEN ABS(daily_trips - rolling_avg_30d) > 2 * rolling_stddev_30d THEN 'ANOMALY'
        WHEN ABS(daily_trips - rolling_avg_30d) > 1.5 * rolling_stddev_30d THEN 'UNUSUAL'
        ELSE 'NORMAL'
    END as pattern_flag,
    CASE WHEN day_of_week = 0 THEN 'Sunday'
         WHEN day_of_week = 1 THEN 'Monday'
         WHEN day_of_week = 2 THEN 'Tuesday'
         WHEN day_of_week = 3 THEN 'Wednesday'
         WHEN day_of_week = 4 THEN 'Thursday'
         WHEN day_of_week = 5 THEN 'Friday'
         WHEN day_of_week = 6 THEN 'Saturday'
    END as weekday,
    ROUND(100.0 * (daily_trips - same_weekday_last_week) / NULLIF(same_weekday_last_week, 0), 1) as pct_change_vs_last_week
FROM rolling_stats
WHERE rolling_stddev_30d IS NOT NULL
ORDER BY trip_date DESC;
```

> **Our implementation:** Time-series pickup datetime index in [01-nyc-taxi-schema.sql — `idx_yellow_taxi_pickup_datetime` (L378)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L378) supports rolling window queries. Date-based expression index `idx_yellow_taxi_date_payment` [(L390)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L390) optimizes `DATE()` grouping.

---

## Geospatial & PostGIS

### Question 9: Spatial Analysis
**Question:** Find all taxi zones within 1 mile of airports and calculate the average trip distance originating from these zones.

**Answer:**
```sql
WITH airport_zones AS (
    SELECT locationid, zone, geometry
    FROM nyc_taxi.taxi_zone_shapes tzs
    JOIN nyc_taxi.taxi_zone_lookup tzl USING (locationid)
    WHERE tzl.zone ILIKE '%airport%'
       OR tzl.service_zone = 'EWR'
),
nearby_zones AS (
    SELECT DISTINCT
        tzs.locationid,
        tzl.zone,
        tzl.borough,
        MIN(ST_Distance(tzs.geometry, az.geometry)) as min_distance_to_airport
    FROM nyc_taxi.taxi_zone_shapes tzs
    JOIN nyc_taxi.taxi_zone_lookup tzl ON tzs.locationid = tzl.locationid
    CROSS JOIN airport_zones az
    WHERE ST_DWithin(tzs.geometry, az.geometry, 5280)  -- 5280 feet = 1 mile
    GROUP BY tzs.locationid, tzl.zone, tzl.borough
)
SELECT
    nz.zone,
    nz.borough,
    ROUND(nz.min_distance_to_airport::numeric, 0) as distance_to_airport_feet,
    COUNT(yt.trip_distance) as trip_count,
    ROUND(AVG(yt.trip_distance), 2) as avg_trip_distance,
    ROUND(AVG(yt.total_amount), 2) as avg_fare
FROM nearby_zones nz
JOIN nyc_taxi.yellow_taxi_trips yt ON nz.locationid = yt.pulocationid
WHERE yt.trip_distance > 0
GROUP BY nz.locationid, nz.zone, nz.borough, nz.min_distance_to_airport
ORDER BY min_distance_to_airport_feet;
```

> **Our implementation:** Spatial data loaded by `load_taxi_zones()` in [init-data.py (L183)](../../postgres/docker/init-data.py#L183) — downloads shapefiles and converts to PostGIS geometries. `taxi_zone_shapes` table with GIST spatial index in [01-nyc-taxi-schema.sql (L299, L311)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L299). Geospatial analytical queries in [geospatial-taxi-analytics.sql](../../postgres/sql-scripts/report-scripts/geospatial-taxi-analytics.sql).

### Question 10: Complex Geospatial Query
**Question:** Create a "heat map" query that identifies 500m x 500m grid cells with the highest concentration of taxi pickups.

**Answer:**
```sql
-- Create a grid and count pickups per cell
WITH grid AS (
    SELECT
        generate_series(
            floor(ST_XMin(envelope))::integer,
            ceil(ST_XMax(envelope))::integer,
            1640  -- 500m in feet (NYC State Plane)
        ) as x,
        generate_series(
            floor(ST_YMin(envelope))::integer,
            ceil(ST_YMax(envelope))::integer,
            1640
        ) as y
    FROM (
        SELECT ST_Envelope(ST_Union(geometry)) as envelope
        FROM nyc_taxi.taxi_zone_shapes
        WHERE borough = 'Manhattan'  -- Focus on Manhattan for performance
    ) bounds
),
grid_cells AS (
    SELECT
        x, y,
        ST_MakeEnvelope(x, y, x+1640, y+1640, 2263) as cell_geom,
        ROW_NUMBER() OVER () as grid_id
    FROM grid
),
pickup_counts AS (
    SELECT
        gc.grid_id,
        gc.x, gc.y,
        COUNT(*) as pickup_count,
        COUNT(DISTINCT DATE(yt.tpep_pickup_datetime)) as active_days
    FROM grid_cells gc
    JOIN nyc_taxi.taxi_zone_shapes tzs ON ST_Intersects(gc.cell_geom, tzs.geometry)
    JOIN nyc_taxi.yellow_taxi_trips yt ON tzs.locationid = yt.pulocationid
    WHERE yt.tpep_pickup_datetime >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY gc.grid_id, gc.x, gc.y
    HAVING COUNT(*) > 50  -- Filter low-activity cells
)
SELECT
    grid_id,
    x, y,
    pickup_count,
    active_days,
    ROUND(pickup_count::numeric / active_days, 1) as avg_pickups_per_day,
    ST_AsText(ST_MakeEnvelope(x, y, x+1640, y+1640, 2263)) as cell_boundary
FROM pickup_counts
ORDER BY pickup_count DESC
LIMIT 20;
```

> **Our implementation:** Same spatial infrastructure as Q9. PostGIS setup with EPSG:2263 (NYC State Plane, feet-based) coordinate system in [00-postgis-setup.sql](../../postgres/sql-scripts/init-scripts/00-postgis-setup.sql). Grid-based geospatial queries in [geospatial-taxi-analytics.sql](../../postgres/sql-scripts/report-scripts/geospatial-taxi-analytics.sql).

---

## Data Quality & Integrity

### Question 11: Data Quality Assessment
**Question:** Write comprehensive data quality checks for the taxi dataset. Identify and quantify various data anomalies.

**Answer:**
```sql
-- Comprehensive data quality report
WITH quality_metrics AS (
    SELECT
        COUNT(*) as total_records,

        -- Temporal anomalies
        COUNT(CASE WHEN tpep_pickup_datetime > tpep_dropoff_datetime THEN 1 END) as negative_duration_trips,
        COUNT(CASE WHEN tpep_dropoff_datetime - tpep_pickup_datetime > INTERVAL '24 hours' THEN 1 END) as extremely_long_trips,
        COUNT(CASE WHEN tpep_pickup_datetime > CURRENT_TIMESTAMP THEN 1 END) as future_pickup_times,

        -- Distance anomalies
        COUNT(CASE WHEN trip_distance = 0 THEN 1 END) as zero_distance_trips,
        COUNT(CASE WHEN trip_distance > 100 THEN 1 END) as extremely_long_distances,
        COUNT(CASE WHEN trip_distance < 0 THEN 1 END) as negative_distances,

        -- Financial anomalies
        COUNT(CASE WHEN total_amount <= 0 THEN 1 END) as non_positive_fares,
        COUNT(CASE WHEN total_amount > 1000 THEN 1 END) as extremely_high_fares,
        COUNT(CASE WHEN tip_amount < 0 THEN 1 END) as negative_tips,
        COUNT(CASE WHEN fare_amount > total_amount THEN 1 END) as fare_exceeds_total,

        -- Location anomalies
        COUNT(CASE WHEN pulocationid IS NULL THEN 1 END) as null_pickup_locations,
        COUNT(CASE WHEN dolocationid IS NULL THEN 1 END) as null_dropoff_locations,
        COUNT(CASE WHEN pulocationid = dolocationid AND trip_distance > 5 THEN 1 END) as same_zone_long_trips,

        -- Passenger count anomalies
        COUNT(CASE WHEN passenger_count = 0 THEN 1 END) as zero_passenger_trips,
        COUNT(CASE WHEN passenger_count > 6 THEN 1 END) as high_passenger_count,

        -- Payment anomalies
        COUNT(CASE WHEN payment_type = 2 AND tip_amount > 0 THEN 1 END) as cash_trips_with_tips

    FROM nyc_taxi.yellow_taxi_trips
    WHERE tpep_pickup_datetime >= CURRENT_DATE - INTERVAL '30 days'
),
location_quality AS (
    SELECT
        COUNT(DISTINCT yt.pulocationid) as distinct_pickup_zones,
        COUNT(DISTINCT yt.dolocationid) as distinct_dropoff_zones,
        COUNT(CASE WHEN pz.locationid IS NULL THEN 1 END) as invalid_pickup_zones,
        COUNT(CASE WHEN dz.locationid IS NULL THEN 1 END) as invalid_dropoff_zones
    FROM nyc_taxi.yellow_taxi_trips yt
    LEFT JOIN nyc_taxi.taxi_zone_lookup pz ON yt.pulocationid = pz.locationid
    LEFT JOIN nyc_taxi.taxi_zone_lookup dz ON yt.dolocationid = dz.locationid
    WHERE yt.tpep_pickup_datetime >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT
    -- Basic counts
    'Total Records' as metric, qm.total_records::text as value,
    '0' as threshold, 'INFO' as severity
FROM quality_metrics qm
UNION ALL
SELECT 'Negative Duration Trips', qm.negative_duration_trips::text, '0',
    CASE WHEN qm.negative_duration_trips = 0 THEN 'GOOD' ELSE 'ERROR' END
FROM quality_metrics qm
UNION ALL
SELECT 'Zero Distance Trips', qm.zero_distance_trips::text,
    ROUND(qm.total_records * 0.01)::text,  -- 1% threshold
    CASE WHEN qm.zero_distance_trips < qm.total_records * 0.01 THEN 'GOOD' ELSE 'WARNING' END
FROM quality_metrics qm
UNION ALL
SELECT 'Extremely High Fares (>$1000)', qm.extremely_high_fares::text, '10',
    CASE WHEN qm.extremely_high_fares <= 10 THEN 'GOOD' ELSE 'WARNING' END
FROM quality_metrics qm
UNION ALL
SELECT 'Invalid Pickup Zones', lq.invalid_pickup_zones::text, '0',
    CASE WHEN lq.invalid_pickup_zones = 0 THEN 'GOOD' ELSE 'ERROR' END
FROM location_quality lq;
```

> **Our implementation:** `data_quality_monitor` table in [01-nyc-taxi-schema.sql (L105)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L105) with severity tracking, quality scores, and batch correlation. Invalid rows captured in `yellow_taxi_trips_invalid` [(L60)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L60) with error classification indexes [(L98–L101)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L98-L101).

### Question 12: Data Cleaning Strategy
**Question:** Design a data cleaning process that handles common taxi data issues while preserving data integrity.

**Answer:**
```sql
-- Create cleaned view with business rules applied
CREATE OR REPLACE VIEW nyc_taxi.yellow_taxi_trips_clean AS
SELECT
    *,
    -- Flag records for different types of cleaning
    CASE
        WHEN tpep_pickup_datetime > tpep_dropoff_datetime THEN 'INVALID_DURATION'
        WHEN trip_distance = 0 AND total_amount > 10 THEN 'ZERO_DISTANCE_HIGH_FARE'
        WHEN total_amount <= 0 THEN 'INVALID_FARE'
        WHEN passenger_count = 0 THEN 'NO_PASSENGERS'
        WHEN pulocationid NOT IN (SELECT locationid FROM nyc_taxi.taxi_zone_lookup) THEN 'INVALID_PICKUP_ZONE'
        ELSE 'VALID'
    END as data_quality_flag,

    -- Cleaned columns with business logic
    CASE
        WHEN passenger_count = 0 THEN 1  -- Assume 1 passenger if 0 reported
        WHEN passenger_count > 6 THEN 6  -- Cap at reasonable maximum
        ELSE passenger_count
    END as passenger_count_clean,

    CASE
        WHEN trip_distance < 0 THEN 0
        WHEN trip_distance = 0 AND
             EXTRACT(EPOCH FROM (tpep_dropoff_datetime - tpep_pickup_datetime))/60 > 5
        THEN 0.1  -- Estimate minimum distance for time-based trips
        ELSE trip_distance
    END as trip_distance_clean,

    CASE
        WHEN total_amount <= 0 THEN NULL  -- Mark invalid fares as NULL
        WHEN total_amount > 1000 THEN NULL  -- Flag extremely high fares for review
        ELSE total_amount
    END as total_amount_clean,

    -- Calculate derived metrics
    EXTRACT(EPOCH FROM (tpep_dropoff_datetime - tpep_pickup_datetime))/60 as trip_duration_minutes,
    CASE
        WHEN trip_distance > 0 AND
             EXTRACT(EPOCH FROM (tpep_dropoff_datetime - tpep_pickup_datetime))/3600 > 0
        THEN trip_distance / (EXTRACT(EPOCH FROM (tpep_dropoff_datetime - tpep_pickup_datetime))/3600)
        ELSE NULL
    END as avg_speed_mph

FROM nyc_taxi.yellow_taxi_trips
WHERE tpep_pickup_datetime IS NOT NULL
  AND tpep_dropoff_datetime IS NOT NULL
  AND tpep_pickup_datetime <= tpep_dropoff_datetime
  AND tpep_pickup_datetime >= DATE '2020-01-01'  -- Reasonable date range
  AND tpep_pickup_datetime <= CURRENT_TIMESTAMP + INTERVAL '1 day';

-- Create summary of cleaning actions
CREATE OR REPLACE VIEW data_cleaning_summary AS
SELECT
    data_quality_flag,
    COUNT(*) as record_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage,
    MIN(tpep_pickup_datetime) as earliest_date,
    MAX(tpep_pickup_datetime) as latest_date
FROM nyc_taxi.yellow_taxi_trips_clean
GROUP BY data_quality_flag
ORDER BY record_count DESC;
```

> **Our implementation:** Data cleaning during ETL in [init-data.py](../../postgres/docker/init-data.py) — NULL handling, column case normalization (`df.columns.str.lower()`), and invalid record filtering. Invalid rows routed to `yellow_taxi_trips_invalid` table [(schema at L60)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L60) with error type classification for post-load analysis.

---

## System Architecture & Scalability

### Question 13: Database Partitioning Strategy
**Question:** Design a partitioning strategy for the taxi trips table considering 3.4M records per month and query patterns focusing on time-based analysis.

**Answer:**
```sql
-- Monthly range partitioning with automatic partition creation
CREATE TABLE nyc_taxi.yellow_taxi_trips_partitioned (
    trip_id BIGSERIAL,
    vendorid INTEGER,
    tpep_pickup_datetime TIMESTAMP NOT NULL,
    tpep_dropoff_datetime TIMESTAMP,
    -- ... other columns
    row_hash VARCHAR(64) UNIQUE
) PARTITION BY RANGE (tpep_pickup_datetime);

-- Create partitions for current and future months
CREATE TABLE yellow_taxi_trips_2024_01 PARTITION OF nyc_taxi.yellow_taxi_trips_partitioned
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE yellow_taxi_trips_2024_02 PARTITION OF nyc_taxi.yellow_taxi_trips_partitioned
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Indexes on each partition
CREATE INDEX idx_trips_2024_01_pickup ON yellow_taxi_trips_2024_01 (tpep_pickup_datetime);
CREATE INDEX idx_trips_2024_01_location ON yellow_taxi_trips_2024_01 (pulocationid, dolocationid);

-- Function to automatically create monthly partitions
CREATE OR REPLACE FUNCTION create_monthly_partition(target_date DATE)
RETURNS void AS $$
DECLARE
    partition_name text;
    start_date date;
    end_date date;
BEGIN
    start_date := date_trunc('month', target_date);
    end_date := start_date + interval '1 month';
    partition_name := 'yellow_taxi_trips_' || to_char(start_date, 'YYYY_MM');

    EXECUTE format('CREATE TABLE %I PARTITION OF nyc_taxi.yellow_taxi_trips_partitioned
                   FOR VALUES FROM (%L) TO (%L)',
                   partition_name, start_date, end_date);

    EXECUTE format('CREATE INDEX idx_%s_pickup ON %I (tpep_pickup_datetime)',
                   partition_name, partition_name);
    EXECUTE format('CREATE INDEX idx_%s_location ON %I (pulocationid, dolocationid)',
                   partition_name, partition_name);
END;
$$ LANGUAGE plpgsql;

-- Automated partition maintenance procedure
CREATE OR REPLACE FUNCTION maintain_partitions()
RETURNS void AS $$
BEGIN
    -- Create next 3 months of partitions
    PERFORM create_monthly_partition(CURRENT_DATE + interval '1 month');
    PERFORM create_monthly_partition(CURRENT_DATE + interval '2 months');
    PERFORM create_monthly_partition(CURRENT_DATE + interval '3 months');

    -- Drop partitions older than 2 years
    PERFORM drop_old_partitions(CURRENT_DATE - interval '2 years');
END;
$$ LANGUAGE plpgsql;
```

> **Our implementation:** Full partitioning system in [02-phase2-partitioning.sql](../../postgres/sql-scripts/model-scripts/02-phase2-partitioning.sql) — `create_monthly_partition()` [(L79)](../../postgres/sql-scripts/model-scripts/02-phase2-partitioning.sql#L79), `create_partitions_for_range()` [(L124)](../../postgres/sql-scripts/model-scripts/02-phase2-partitioning.sql#L124), `drop_old_partitions()` [(L147)](../../postgres/sql-scripts/model-scripts/02-phase2-partitioning.sql#L147), `maintain_partitions()` [(L176)](../../postgres/sql-scripts/model-scripts/02-phase2-partitioning.sql#L176), partition stats tracking with `update_partition_stats()` [(L219)](../../postgres/sql-scripts/model-scripts/02-phase2-partitioning.sql#L219), and `explain_partition_pruning()` [(L326)](../../postgres/sql-scripts/model-scripts/02-phase2-partitioning.sql#L326) for verifying partition elimination.

### Question 14: High Availability Architecture
**Question:** Design a database architecture for handling 100M+ taxi records with high availability requirements and read-heavy workload.

**Answer:**
```sql
-- Master-Slave replication with read replicas
-- Architecture diagram:
-- [Load Balancer] -> [Write Master] -> [Sync Replica] -> [Async Read Replicas]
--                                   -> [Analytics DB (Columnar)]

-- 1. Connection pooling configuration
CREATE DATABASE taxi_analytics_db;

-- 2. Read-only user for analytics queries
CREATE ROLE analytics_reader WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE playground TO analytics_reader;
GRANT USAGE ON SCHEMA nyc_taxi TO analytics_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA nyc_taxi TO analytics_reader;

-- 3. Materialized views for common aggregations
CREATE MATERIALIZED VIEW nyc_taxi.mv_daily_trip_summary AS
SELECT
    DATE(tpep_pickup_datetime) as trip_date,
    pulocationid,
    COUNT(*) as trip_count,
    SUM(total_amount) as total_revenue,
    AVG(trip_distance) as avg_distance,
    AVG(total_amount) as avg_fare
FROM nyc_taxi.yellow_taxi_trips
GROUP BY DATE(tpep_pickup_datetime), pulocationid;

CREATE UNIQUE INDEX idx_mv_daily_summary_unique
ON mv_daily_trip_summary (trip_date, pulocationid);

-- 4. Refresh schedule for materialized views
CREATE OR REPLACE FUNCTION refresh_trip_summaries()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_trip_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_hourly_zone_stats;
    -- Update statistics
    ANALYZE nyc_taxi.yellow_taxi_trips;
END;
$$ LANGUAGE plpgsql;

-- 5. Connection routing logic (application level)
-- Example in Python/SQLAlchemy:
/*
class DatabaseRouter:
    def __init__(self):
        self.write_engine = create_engine(MASTER_DB_URL, pool_size=20)
        self.read_engines = [
            create_engine(REPLICA_1_URL, pool_size=50),
            create_engine(REPLICA_2_URL, pool_size=50),
        ]
        self.analytics_engine = create_engine(ANALYTICS_DB_URL, pool_size=10)

    def get_engine(self, operation_type='read'):
        if operation_type == 'write':
            return self.write_engine
        elif operation_type == 'analytics':
            return self.analytics_engine
        else:
            return random.choice(self.read_engines)
*/
```

> **Our implementation:** Connection pooling configured in [superset_config.py](../../superset/config/superset_config.py) — 20 core + 30 overflow connections. Materialized views for pre-aggregated analytics in [sample-queries.sql](../../postgres/sql-scripts/report-scripts/sample-queries.sql). PostgreSQL tuning parameters (shared_buffers, work_mem, parallel workers) set in [Dockerfile.postgres](../../postgres/docker/Dockerfile.postgres).

### Question 15: Monitoring and Alerting
**Question:** Create a monitoring system for the taxi database that tracks data quality, performance, and operational metrics.

**Answer:**
```sql
-- 1. Performance monitoring table
CREATE TABLE nyc_taxi.database_metrics (
    metric_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    metric_unit VARCHAR(20),
    additional_info JSONB
);

-- 2. Data quality monitoring function
CREATE OR REPLACE FUNCTION monitor_data_quality()
RETURNS TABLE(
    check_name text,
    status text,
    current_value numeric,
    threshold_value numeric,
    severity text
) AS $$
BEGIN
    RETURN QUERY
    WITH checks AS (
        SELECT
            'Daily Trip Count' as check_name,
            COUNT(*)::numeric as current_value,
            50000::numeric as threshold_value,
            CASE WHEN COUNT(*) < 50000 THEN 'LOW_VOLUME' ELSE 'OK' END as status,
            CASE WHEN COUNT(*) < 50000 THEN 'WARNING' ELSE 'INFO' END as severity
        FROM nyc_taxi.yellow_taxi_trips
        WHERE DATE(tpep_pickup_datetime) = CURRENT_DATE - 1

        UNION ALL

        SELECT
            'Data Quality Score',
            (100.0 * COUNT(CASE WHEN data_quality_flag = 'VALID' THEN 1 END) / COUNT(*))::numeric,
            95.0::numeric,
            CASE WHEN (100.0 * COUNT(CASE WHEN data_quality_flag = 'VALID' THEN 1 END) / COUNT(*)) < 95
                 THEN 'QUALITY_DEGRADED' ELSE 'OK' END,
            CASE WHEN (100.0 * COUNT(CASE WHEN data_quality_flag = 'VALID' THEN 1 END) / COUNT(*)) < 95
                 THEN 'ERROR' ELSE 'INFO' END
        FROM nyc_taxi.yellow_taxi_trips_clean
        WHERE DATE(tpep_pickup_datetime) = CURRENT_DATE - 1

        UNION ALL

        SELECT
            'Average Query Response Time (ms)',
            (SELECT avg_exec_time FROM pg_stat_statements
             WHERE query ILIKE '%yellow_taxi_trips%' LIMIT 1),
            1000.0::numeric,
            CASE WHEN (SELECT avg_exec_time FROM pg_stat_statements
                      WHERE query ILIKE '%yellow_taxi_trips%' LIMIT 1) > 1000
                 THEN 'SLOW_QUERIES' ELSE 'OK' END,
            CASE WHEN (SELECT avg_exec_time FROM pg_stat_statements
                      WHERE query ILIKE '%yellow_taxi_trips%' LIMIT 1) > 1000
                 THEN 'WARNING' ELSE 'INFO' END
    )
    SELECT * FROM checks;
END;
$$ LANGUAGE plpgsql;

-- 3. Alerting procedure
CREATE OR REPLACE FUNCTION check_and_alert()
RETURNS void AS $$
DECLARE
    alert_record RECORD;
    alert_message TEXT;
BEGIN
    FOR alert_record IN
        SELECT * FROM monitor_data_quality() WHERE severity IN ('ERROR', 'WARNING')
    LOOP
        alert_message := format('ALERT: %s - Status: %s, Current: %s, Threshold: %s',
            alert_record.check_name,
            alert_record.status,
            alert_record.current_value,
            alert_record.threshold_value);

        -- Log alert
        INSERT INTO nyc_taxi.database_metrics (metric_name, metric_value, metric_unit, additional_info)
        VALUES ('alert', 1, 'count',
                jsonb_build_object('message', alert_message, 'severity', alert_record.severity));

        -- In production, this would integrate with monitoring systems like:
        -- PERFORM pg_notify('database_alerts', alert_message);
        -- Or call external webhook/API

        RAISE NOTICE '%', alert_message;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 4. Performance metrics collection
CREATE OR REPLACE FUNCTION collect_performance_metrics()
RETURNS void AS $$
BEGIN
    -- Table sizes
    INSERT INTO nyc_taxi.database_metrics (metric_name, metric_value, metric_unit)
    SELECT 'table_size_mb', pg_total_relation_size('nyc_taxi.yellow_taxi_trips')/1024/1024, 'MB';

    -- Active connections
    INSERT INTO nyc_taxi.database_metrics (metric_name, metric_value, metric_unit)
    SELECT 'active_connections', COUNT(*), 'connections'
    FROM pg_stat_activity WHERE state = 'active';

    -- Index usage
    INSERT INTO nyc_taxi.database_metrics (metric_name, metric_value, metric_unit, additional_info)
    SELECT 'index_usage', ROUND(100.0 * idx_scan / (seq_scan + idx_scan), 2), 'percent',
           jsonb_build_object('table_name', schemaname||'.'||tablename)
    FROM pg_stat_user_tables
    WHERE schemaname = 'nyc_taxi' AND (seq_scan + idx_scan) > 0;
END;
$$ LANGUAGE plpgsql;
```

> **Our implementation:** `data_quality_monitor` table in [01-nyc-taxi-schema.sql (L105)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L105) — tracks operations with severity levels, quality scores, batch IDs, and critical error flags. Quality summary aggregation in `data_quality_summary` [(L248–L250)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L248-L250) with period-based indexes. Dual logging (console + file) in [init-data.py](../../postgres/docker/init-data.py) with organized log directories per backfill configuration.

---

## Advanced Star Schema & ETL Engineering

### Question 16: Star Schema Migration Strategy
**Question:** You have a normalized OLTP schema with 3.4M monthly records. Design a strategy to implement a star schema for analytics while maintaining the operational system. How would you handle the dual-schema approach?

**Answer:**
```sql
-- 1. Incremental star schema population strategy
CREATE OR REPLACE FUNCTION populate_star_schema_incremental(
    start_date DATE DEFAULT CURRENT_DATE - 1,
    end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE(processed_rows BIGINT, star_rows BIGINT, dimension_updates INTEGER) AS $$
DECLARE
    processed_count BIGINT := 0;
    star_count BIGINT := 0;
    dim_updates INTEGER := 0;
BEGIN
    -- 1. Refresh dimension tables first
    REFRESH MATERIALIZED VIEW CONCURRENTLY dim_locations;
    REFRESH MATERIALIZED VIEW CONCURRENTLY dim_vendor;
    dim_updates := dim_updates + 2;

    -- 2. Process normalized data in chunks
    WITH new_trips AS (
        SELECT *
        FROM nyc_taxi.yellow_taxi_trips
        WHERE DATE(tpep_pickup_datetime) BETWEEN start_date AND end_date
          AND row_hash NOT IN (
              SELECT DISTINCT source_trip_hash
              FROM nyc_taxi.fact_taxi_trips
              WHERE pickup_date BETWEEN start_date AND end_date
          )
    ),
    enriched_trips AS (
        SELECT
            nt.*,
            -- Dimension key lookups
            dl_pickup.location_key as pickup_location_key,
            dl_dropoff.location_key as dropoff_location_key,
            dv.vendor_key,
            dpt.payment_type_key,
            drc.rate_code_key,
            -- Date/time dimension keys
            to_char(nt.tpep_pickup_datetime, 'YYYYMMDD')::INTEGER as pickup_date_key,
            EXTRACT(HOUR FROM nt.tpep_pickup_datetime)::INTEGER as pickup_time_key,
            -- Calculated measures
            EXTRACT(EPOCH FROM (nt.tpep_dropoff_datetime - nt.tpep_pickup_datetime))/60 as trip_duration_minutes,
            CASE
                WHEN nt.trip_distance > 0 AND
                     EXTRACT(EPOCH FROM (nt.tpep_dropoff_datetime - nt.tpep_pickup_datetime))/3600 > 0
                THEN nt.trip_distance / (EXTRACT(EPOCH FROM (nt.tpep_dropoff_datetime - nt.tpep_pickup_datetime))/3600)
                ELSE 0
            END as avg_speed_mph
        FROM new_trips nt
        LEFT JOIN nyc_taxi.dim_locations dl_pickup ON nt.pulocationid = dl_pickup.locationid
        LEFT JOIN nyc_taxi.dim_locations dl_dropoff ON nt.dolocationid = dl_dropoff.locationid
        LEFT JOIN nyc_taxi.dim_vendor dv ON nt.vendorid = dv.vendorid
        LEFT JOIN nyc_taxi.dim_payment_type dpt ON nt.payment_type = dpt.payment_type
        LEFT JOIN nyc_taxi.dim_rate_code drc ON nt.ratecodeid = drc.ratecodeid
    )
    INSERT INTO nyc_taxi.fact_taxi_trips (
        pickup_date_key, pickup_time_key, pickup_location_key, dropoff_location_key,
        vendor_key, payment_type_key, rate_code_key,
        trip_distance, trip_duration_minutes, passenger_count,
        fare_amount, tip_amount, total_amount, avg_speed_mph,
        source_trip_hash, created_at
    )
    SELECT
        pickup_date_key, pickup_time_key, pickup_location_key, dropoff_location_key,
        vendor_key, payment_type_key, rate_code_key,
        trip_distance, trip_duration_minutes, passenger_count::INTEGER,
        fare_amount, tip_amount, total_amount, avg_speed_mph,
        row_hash, CURRENT_TIMESTAMP
    FROM enriched_trips
    WHERE pickup_location_key IS NOT NULL AND dropoff_location_key IS NOT NULL;

    GET DIAGNOSTICS star_count = ROW_COUNT;

    SELECT COUNT(*) INTO processed_count
    FROM nyc_taxi.yellow_taxi_trips
    WHERE DATE(tpep_pickup_datetime) BETWEEN start_date AND end_date;

    RETURN QUERY SELECT processed_count, star_count, dim_updates;
END;
$$ LANGUAGE plpgsql;

-- 2. Data consistency monitoring
CREATE VIEW star_schema_consistency_check AS
WITH normalized_summary AS (
    SELECT
        COUNT(*) as norm_total_trips,
        SUM(total_amount) as norm_total_revenue,
        MIN(tpep_pickup_datetime) as norm_min_date,
        MAX(tpep_pickup_datetime) as norm_max_date
    FROM nyc_taxi.yellow_taxi_trips
    WHERE tpep_pickup_datetime >= CURRENT_DATE - INTERVAL '30 days'
),
star_summary AS (
    SELECT
        COUNT(*) as star_total_trips,
        SUM(total_amount) as star_total_revenue,
        MIN(dd.full_date) as star_min_date,
        MAX(dd.full_date) as star_max_date
    FROM nyc_taxi.fact_taxi_trips ft
    JOIN nyc_taxi.dim_date dd ON ft.pickup_date_key = dd.date_key
    WHERE dd.full_date >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT
    ns.norm_total_trips,
    ss.star_total_trips,
    ns.norm_total_trips - ss.star_total_trips as trip_count_diff,
    ROUND(100.0 * ss.star_total_trips / ns.norm_total_trips, 2) as coverage_percentage,
    ABS(ns.norm_total_revenue - ss.star_total_revenue) as revenue_diff,
    CASE
        WHEN ABS(ns.norm_total_trips - ss.star_total_trips) < ns.norm_total_trips * 0.01
        THEN 'GOOD'
        ELSE 'ATTENTION_NEEDED'
    END as consistency_status
FROM normalized_summary ns, star_summary ss;
```

> **Our implementation:** `migrate_taxi_data_to_star_schema()` in [04-data-migration.sql (L38)](../../postgres/sql-scripts/model-scripts/04-data-migration.sql#L38) — bulk migration with dimension key lookups. Incremental migration via `incremental_migrate_taxi_data()` [(L201)](../../postgres/sql-scripts/model-scripts/04-data-migration.sql#L201). Rollback capability with `rollback_migration()` [(L300)](../../postgres/sql-scripts/model-scripts/04-data-migration.sql#L300). Star schema definition in [01-phase1-star-schema.sql](../../postgres/sql-scripts/model-scripts/01-phase1-star-schema.sql) with fact table [(L103)](../../postgres/sql-scripts/model-scripts/01-phase1-star-schema.sql#L103) and 6 dimension tables.

### Question 17: Hash-Based Duplicate Prevention at Scale
**Question:** Explain the trade-offs of using SHA-256 row hashing for duplicate prevention in a high-volume ETL pipeline. How would you optimize hash generation for 3.4M records per month?

**Answer:**
```python
# Optimized hash generation strategy implemented in the current system

class OptimizedHashGenerator:
    def __init__(self, chunk_size=10000):
        self.chunk_size = chunk_size

    def generate_row_hash_vectorized(self, df_chunk):
        """
        Vectorized hash generation for better performance
        Process 10K rows at a time to balance memory vs speed
        """
        def hash_row_optimized(row):
            # Create deterministic string representation
            row_dict = {}
            for column, value in row.items():
                if pd.isna(value) or value is None:
                    row_dict[column] = ""
                elif isinstance(value, float):
                    row_dict[column] = f"{value:.10f}"  # Consistent precision
                elif isinstance(value, pd.Timestamp):
                    row_dict[column] = value.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    row_dict[column] = str(value)

            # Create sorted JSON for deterministic hashing
            row_json = json.dumps(row_dict, sort_keys=True, ensure_ascii=True)
            return hashlib.sha256(row_json.encode('utf-8')).hexdigest()

        # Apply hash generation row by row (vectorization limited by JSON serialization)
        return df_chunk.apply(hash_row_optimized, axis=1)

    def process_with_collision_detection(self, df):
        """
        Process chunks with collision detection and performance monitoring
        """
        results = {
            'total_rows': len(df),
            'unique_hashes': 0,
            'collisions': 0,
            'processing_time_ms': 0
        }

        start_time = time.time()

        # Process in chunks for memory efficiency
        hash_series_list = []
        seen_hashes = set()

        for chunk_start in range(0, len(df), self.chunk_size):
            chunk_end = min(chunk_start + self.chunk_size, len(df))
            chunk_df = df.iloc[chunk_start:chunk_end].copy()

            # Generate hashes for chunk
            chunk_hashes = self.generate_row_hash_vectorized(chunk_df)

            # Collision detection within chunk
            chunk_unique = len(chunk_hashes.unique())
            chunk_total = len(chunk_hashes)

            if chunk_unique < chunk_total:
                results['collisions'] += (chunk_total - chunk_unique)
                logger.warning(f"Hash collisions detected in chunk: {chunk_total - chunk_unique}")

            # Global collision detection
            new_hashes = set(chunk_hashes) - seen_hashes
            if len(new_hashes) < chunk_unique:
                results['collisions'] += (chunk_unique - len(new_hashes))

            seen_hashes.update(chunk_hashes)
            hash_series_list.append(chunk_hashes)

        # Combine all hash series
        final_hashes = pd.concat(hash_series_list, ignore_index=True)
        results['unique_hashes'] = len(set(final_hashes))
        results['processing_time_ms'] = int((time.time() - start_time) * 1000)

        return final_hashes, results

# Database-level duplicate prevention strategy
CREATE TABLE nyc_taxi.data_quality_monitor (
    monitor_id BIGSERIAL PRIMARY KEY,
    monitored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operation_type VARCHAR(50),
    target_table VARCHAR(100),
    rows_attempted BIGINT,
    rows_inserted BIGINT,
    rows_duplicates BIGINT,
    hash_collisions INTEGER DEFAULT 0,
    processing_duration_ms BIGINT,
    quality_score DECIMAL(5,2)
);

-- Monitoring query for hash effectiveness
SELECT
    DATE(monitored_at) as monitoring_date,
    COUNT(*) as total_operations,
    SUM(rows_attempted) as total_rows_processed,
    SUM(rows_duplicates) as total_duplicates_prevented,
    SUM(hash_collisions) as total_hash_collisions,
    ROUND(100.0 * SUM(rows_duplicates) / SUM(rows_attempted), 2) as duplicate_rate_percent,
    AVG(processing_duration_ms) as avg_processing_time_ms
FROM nyc_taxi.data_quality_monitor
WHERE operation_type = 'chunk_insert'
  AND monitored_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(monitored_at)
ORDER BY monitoring_date DESC;
```

> **Our implementation:** `calculate_row_hash()` in [init-data.py (L627)](../../postgres/docker/init-data.py#L627) — SHA-256 with deterministic JSON serialization and consistent float precision. `add_row_hash_column()` [(L661)](../../postgres/docker/init-data.py#L661) for batch generation with within-chunk collision detection [(L668–L675)](../../postgres/docker/init-data.py#L668-L675). `row_hash` UNIQUE constraint in [01-nyc-taxi-schema.sql (L52)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L52). Monitoring via `data_quality_monitor` [(L105)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L105) tracking duplicate counts and hash collisions per batch.

### Question 18: Advanced Dimensional Analytics
**Question:** Using the star schema, write a query to identify the most profitable pickup-dropoff location pairs by time of day, including their rank within each borough combination and seasonal trends.

**Answer:**
```sql
WITH location_pairs AS (
    SELECT
        dl_pickup.borough as pickup_borough,
        dl_dropoff.borough as dropoff_borough,
        dl_pickup.zone as pickup_zone,
        dl_dropoff.zone as dropoff_zone,
        dt.hour_24 as pickup_hour,
        dd.quarter as pickup_quarter,
        ft.pickup_location_key,
        ft.dropoff_location_key,
        COUNT(*) as trip_count,
        SUM(ft.total_amount) as total_revenue,
        AVG(ft.total_amount) as avg_trip_value,
        AVG(ft.trip_distance) as avg_trip_distance,
        SUM(ft.tip_amount) as total_tips
    FROM nyc_taxi.fact_taxi_trips ft
    JOIN nyc_taxi.dim_locations dl_pickup ON ft.pickup_location_key = dl_pickup.location_key
    JOIN nyc_taxi.dim_locations dl_dropoff ON ft.dropoff_location_key = dl_dropoff.location_key
    JOIN nyc_taxi.dim_time dt ON ft.pickup_time_key = dt.time_key
    JOIN nyc_taxi.dim_date dd ON ft.pickup_date_key = dd.date_key
    WHERE dd.full_date >= CURRENT_DATE - INTERVAL '365 days'
    GROUP BY
        dl_pickup.borough, dl_dropoff.borough, dl_pickup.zone, dl_dropoff.zone,
        dt.hour_24, dd.quarter, ft.pickup_location_key, ft.dropoff_location_key
    HAVING COUNT(*) >= 10  -- Filter low-volume pairs
),
seasonal_comparison AS (
    SELECT
        *,
        -- Time-based rankings
        ROW_NUMBER() OVER (
            PARTITION BY pickup_borough, dropoff_borough, pickup_hour
            ORDER BY total_revenue DESC
        ) as revenue_rank_by_hour,

        ROW_NUMBER() OVER (
            PARTITION BY pickup_borough, dropoff_borough, pickup_quarter
            ORDER BY total_revenue DESC
        ) as revenue_rank_by_quarter,

        -- Calculate seasonal variance
        AVG(total_revenue) OVER (
            PARTITION BY pickup_zone, dropoff_zone, pickup_hour
        ) as avg_revenue_this_hour_all_quarters,

        STDDEV(total_revenue) OVER (
            PARTITION BY pickup_zone, dropoff_zone, pickup_hour
        ) as revenue_stddev_seasonal,

        -- Profitability metrics
        total_revenue / NULLIF(trip_count, 0) as revenue_per_trip,
        total_tips / NULLIF(total_revenue, 0) * 100 as tip_percentage
    FROM location_pairs
),
enriched_analysis AS (
    SELECT
        *,
        CASE
            WHEN pickup_hour BETWEEN 7 AND 9 THEN 'Morning Rush'
            WHEN pickup_hour BETWEEN 17 AND 19 THEN 'Evening Rush'
            WHEN pickup_hour BETWEEN 22 AND 5 THEN 'Night Hours'
            ELSE 'Regular Hours'
        END as time_category,

        CASE pickup_quarter
            WHEN 1 THEN 'Q1 (Winter)'
            WHEN 2 THEN 'Q2 (Spring)'
            WHEN 3 THEN 'Q3 (Summer)'
            WHEN 4 THEN 'Q4 (Fall)'
        END as season,

        -- Seasonal volatility flag
        CASE
            WHEN revenue_stddev_seasonal / NULLIF(avg_revenue_this_hour_all_quarters, 0) > 0.3
            THEN 'HIGH_SEASONAL_VARIANCE'
            ELSE 'STABLE'
        END as seasonal_stability,

        -- Cross-borough premium
        CASE
            WHEN pickup_borough != dropoff_borough THEN 'Cross-Borough'
            ELSE 'Intra-Borough'
        END as trip_type
    FROM seasonal_comparison
)
SELECT
    pickup_borough,
    dropoff_borough,
    pickup_zone,
    dropoff_zone,
    time_category,
    season,
    trip_count,
    ROUND(total_revenue, 2) as total_revenue,
    ROUND(revenue_per_trip, 2) as revenue_per_trip,
    ROUND(tip_percentage, 1) as tip_percentage,
    revenue_rank_by_hour,
    revenue_rank_by_quarter,
    trip_type,
    seasonal_stability,
    -- Performance indicators
    CASE
        WHEN revenue_rank_by_hour <= 3 AND revenue_rank_by_quarter <= 5 THEN 'TOP_PERFORMER'
        WHEN revenue_rank_by_hour <= 10 AND revenue_rank_by_quarter <= 15 THEN 'STRONG_PERFORMER'
        ELSE 'AVERAGE_PERFORMER'
    END as performance_category
FROM enriched_analysis
WHERE revenue_rank_by_hour <= 20  -- Top 20 pairs per borough/hour combination
ORDER BY
    pickup_borough, dropoff_borough, time_category, total_revenue DESC;

-- Supporting materialized view for faster queries
CREATE MATERIALIZED VIEW nyc_taxi.mv_location_pair_metrics AS
SELECT
    ft.pickup_location_key,
    ft.dropoff_location_key,
    dl_pickup.borough as pickup_borough,
    dl_dropoff.borough as dropoff_borough,
    COUNT(*) as total_trips,
    SUM(ft.total_amount) as total_revenue,
    AVG(ft.trip_distance) as avg_distance,
    AVG(ft.trip_duration_minutes) as avg_duration,
    MIN(dd.full_date) as first_trip_date,
    MAX(dd.full_date) as last_trip_date
FROM nyc_taxi.fact_taxi_trips ft
JOIN nyc_taxi.dim_locations dl_pickup ON ft.pickup_location_key = dl_pickup.location_key
JOIN nyc_taxi.dim_locations dl_dropoff ON ft.dropoff_location_key = dl_dropoff.location_key
JOIN nyc_taxi.dim_date dd ON ft.pickup_date_key = dd.date_key
GROUP BY
    ft.pickup_location_key, ft.dropoff_location_key,
    dl_pickup.borough, dl_dropoff.borough;

CREATE UNIQUE INDEX idx_mv_location_pairs
ON mv_location_pair_metrics (pickup_location_key, dropoff_location_key);
```

> **Our implementation:** Star schema queries with dimension joins in [sample-queries.sql](../../postgres/sql-scripts/report-scripts/sample-queries.sql) — location pair analysis, time-of-day breakdowns, and borough-level aggregations. Covering indexes for index-only scans on location+payment dimensions in [03-phase3-performance-indexing.sql (L46, L159–L176)](../../postgres/sql-scripts/model-scripts/03-phase3-performance-indexing.sql#L46). `dim_locations` with PostGIS geometry [(L48)](../../postgres/sql-scripts/model-scripts/01-phase1-star-schema.sql#L48) enables spatial joins within the star schema.

### Question 19: ETL Pipeline Error Recovery and Data Quality Assurance
**Question:** Design an ETL error recovery system that can handle partial failures, data quality issues, and ensure consistent state between normalized and star schemas during high-volume processing.

**Answer:**
```sql
-- 1. ETL State Management System
CREATE TYPE etl_status AS ENUM ('pending', 'in_progress', 'completed', 'failed', 'recovering');

CREATE TABLE nyc_taxi.etl_batch_control (
    batch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_type VARCHAR(50) NOT NULL, -- 'monthly_load', 'incremental', 'recovery'
    source_identifier VARCHAR(200) NOT NULL, -- file path, date range, etc.
    target_tables TEXT[], -- array of affected tables
    batch_status etl_status DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_details JSONB,
    recovery_attempts INTEGER DEFAULT 0,
    rows_processed BIGINT DEFAULT 0,
    rows_succeeded BIGINT DEFAULT 0,
    rows_failed BIGINT DEFAULT 0,
    checksum_normalized VARCHAR(64), -- hash of normalized data
    checksum_star VARCHAR(64), -- hash of star schema data
    parent_batch_id UUID REFERENCES etl_batch_control(batch_id)
);

-- 2. Transactional ETL with Rollback Capability
CREATE OR REPLACE FUNCTION process_batch_with_recovery(
    p_source_identifier VARCHAR(200),
    p_batch_type VARCHAR(50) DEFAULT 'monthly_load'
)
RETURNS TABLE(
    batch_id UUID,
    final_status etl_status,
    rows_processed BIGINT,
    error_summary TEXT
) AS $$
DECLARE
    v_batch_id UUID;
    v_savepoint_name TEXT;
    v_error_msg TEXT;
    v_recovery_attempt INTEGER := 0;
    v_max_recovery_attempts INTEGER := 3;
BEGIN
    -- Create batch record
    INSERT INTO nyc_taxi.etl_batch_control (batch_type, source_identifier, batch_status, started_at)
    VALUES (p_batch_type, p_source_identifier, 'in_progress', CURRENT_TIMESTAMP)
    RETURNING etl_batch_control.batch_id INTO v_batch_id;

    <<recovery_loop>>
    LOOP
        BEGIN
            v_savepoint_name := 'batch_savepoint_' || v_recovery_attempt;
            EXECUTE 'SAVEPOINT ' || v_savepoint_name;

            -- Main ETL processing logic
            PERFORM process_normalized_data(v_batch_id, p_source_identifier);
            PERFORM process_star_schema_data(v_batch_id);
            PERFORM validate_data_consistency(v_batch_id);

            -- Success - update batch status
            UPDATE nyc_taxi.etl_batch_control
            SET batch_status = 'completed',
                completed_at = CURRENT_TIMESTAMP,
                checksum_normalized = calculate_batch_checksum('normalized', v_batch_id),
                checksum_star = calculate_batch_checksum('star', v_batch_id)
            WHERE etl_batch_control.batch_id = v_batch_id;

            RETURN QUERY
            SELECT v_batch_id, 'completed'::etl_status,
                   (SELECT rows_processed FROM nyc_taxi.etl_batch_control WHERE batch_id = v_batch_id),
                   'Success'::TEXT;
            RETURN;

        EXCEPTION
            WHEN OTHERS THEN
                v_error_msg := SQLERRM;
                v_recovery_attempt := v_recovery_attempt + 1;

                -- Log the error
                UPDATE nyc_taxi.etl_batch_control
                SET error_details = COALESCE(error_details, '[]'::jsonb) ||
                    jsonb_build_object(
                        'attempt', v_recovery_attempt,
                        'error', v_error_msg,
                        'timestamp', CURRENT_TIMESTAMP
                    ),
                    recovery_attempts = v_recovery_attempt
                WHERE batch_id = v_batch_id;

                -- Rollback to savepoint
                EXECUTE 'ROLLBACK TO SAVEPOINT ' || v_savepoint_name;

                -- Check if we should retry
                IF v_recovery_attempt >= v_max_recovery_attempts THEN
                    -- Mark as failed
                    UPDATE nyc_taxi.etl_batch_control
                    SET batch_status = 'failed', completed_at = CURRENT_TIMESTAMP
                    WHERE batch_id = v_batch_id;

                    RETURN QUERY
                    SELECT v_batch_id, 'failed'::etl_status, 0::BIGINT, v_error_msg;
                    RETURN;
                END IF;

                -- Wait before retry (exponential backoff)
                PERFORM pg_sleep(POWER(2, v_recovery_attempt));
        END;
    END LOOP recovery_loop;
END;
$$ LANGUAGE plpgsql;

-- 3. Data Quality Validation Framework
CREATE OR REPLACE FUNCTION validate_data_consistency(p_batch_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_norm_count BIGINT;
    v_star_count BIGINT;
    v_norm_revenue NUMERIC;
    v_star_revenue NUMERIC;
    v_variance_threshold NUMERIC := 0.01; -- 1% tolerance
    v_batch_date_range daterange;
BEGIN
    -- Get batch date range
    SELECT daterange(
        MIN(DATE(tpep_pickup_datetime)),
        MAX(DATE(tpep_pickup_datetime)), '[]'
    ) INTO v_batch_date_range
    FROM nyc_taxi.yellow_taxi_trips yt
    JOIN nyc_taxi.etl_batch_control ebc ON ebc.batch_id = p_batch_id
    WHERE yt.created_at >= ebc.started_at;

    -- Validate record counts
    SELECT COUNT(*), SUM(total_amount) INTO v_norm_count, v_norm_revenue
    FROM nyc_taxi.yellow_taxi_trips
    WHERE DATE(tpep_pickup_datetime) <@ v_batch_date_range;

    SELECT COUNT(*), SUM(total_amount) INTO v_star_count, v_star_revenue
    FROM nyc_taxi.fact_taxi_trips ft
    JOIN nyc_taxi.dim_date dd ON ft.pickup_date_key = dd.date_key
    WHERE dd.full_date <@ v_batch_date_range;

    -- Check variance
    IF ABS(v_norm_count - v_star_count) > v_norm_count * v_variance_threshold THEN
        RAISE EXCEPTION 'Record count mismatch: Normalized=%, Star=%, Variance=%',
            v_norm_count, v_star_count,
            ABS(v_norm_count - v_star_count)::NUMERIC / v_norm_count;
    END IF;

    IF ABS(v_norm_revenue - v_star_revenue) > v_norm_revenue * v_variance_threshold THEN
        RAISE EXCEPTION 'Revenue mismatch: Normalized=%, Star=%, Variance=%',
            v_norm_revenue, v_star_revenue,
            ABS(v_norm_revenue - v_star_revenue) / v_norm_revenue;
    END IF;

    -- Log validation success
    INSERT INTO nyc_taxi.data_quality_monitor (
        operation_type, target_table, rows_attempted, rows_inserted,
        additional_info
    ) VALUES (
        'consistency_check', 'normalized_vs_star', v_norm_count, v_star_count,
        jsonb_build_object(
            'batch_id', p_batch_id,
            'norm_revenue', v_norm_revenue,
            'star_revenue', v_star_revenue,
            'validation_status', 'PASSED'
        )
    );

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 4. Automated Recovery Monitoring
CREATE OR REPLACE VIEW etl_health_dashboard AS
SELECT
    DATE(started_at) as processing_date,
    batch_type,
    COUNT(*) as total_batches,
    COUNT(*) FILTER (WHERE batch_status = 'completed') as successful_batches,
    COUNT(*) FILTER (WHERE batch_status = 'failed') as failed_batches,
    COUNT(*) FILTER (WHERE batch_status = 'in_progress') as in_progress_batches,
    AVG(recovery_attempts) as avg_recovery_attempts,
    SUM(rows_processed) as total_rows_processed,
    ROUND(100.0 * COUNT(*) FILTER (WHERE batch_status = 'completed') / COUNT(*), 2) as success_rate,
    MAX(completed_at - started_at) as max_processing_duration,
    AVG(completed_at - started_at) FILTER (WHERE batch_status = 'completed') as avg_processing_duration
FROM nyc_taxi.etl_batch_control
WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(started_at), batch_type
ORDER BY processing_date DESC, batch_type;
```

> **Our implementation:** ETL state tracking via `data_processing_log` in [01-nyc-taxi-schema.sql (L333)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L333) — tracks status (`in_progress`, `completed`, `failed`) per month. Error recovery with chunked loading in [init-data.py — `load_trip_data()` (L1360)](../../postgres/docker/init-data.py#L1360) — individual chunk failures are logged as warnings without aborting the batch [(L851–L898)](../../postgres/docker/init-data.py#L851-L898). Post-load validation via `verify_data_load()` [(L1476)](../../postgres/docker/init-data.py#L1476). Quality monitoring in `data_quality_monitor` [(L105)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L105) with `data_quality_summary` [(L248)](../../postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql#L248) for period-based aggregation.

---

## Conclusion

These questions cover the full spectrum of SQL engineering skills needed for working with large-scale, real-world datasets. They test:

- **Technical Depth**: Complex queries, performance optimization, system architecture
- **Practical Experience**: Data quality issues, ETL processes, monitoring
- **Problem-Solving**: Geospatial analysis, anomaly detection, business intelligence
- **Production Readiness**: Scalability, reliability, maintainability

The NYC Taxi dataset provides an excellent foundation because it represents real-world challenges: messy data, performance requirements, business intelligence needs, and operational complexity that candidates will encounter in production environments.

---

*This document is based on a production-ready NYC Taxi database with 3.4M+ monthly records, PostGIS spatial extensions, and a complete ETL pipeline. All queries have been tested against real data.*

</details>

## Quick Start

<details>
<summary><strong>Click to expand</strong></summary>


1. **Copy environment configuration:**
   ```bash
   cp env .env
   ```

2. **Start the complete SQL playground:**
   ```bash
   ./start.sh
   ```

   The `start.sh` script automatically detects port conflicts and falls back to alternative ports:

   | Service    | Default | Fallbacks   |
   |------------|---------|-------------|
   | PostgreSQL | 5432    | 5433, 5434  |
   | PGAdmin    | 8080    | 8081, 8082  |
   | Superset   | 8088    | 8089, 8090  |

   The actual ports are printed at startup so you always know where to connect. You can still override defaults via `.env` (e.g. `POSTGRES_PORT=5555`).

   > **Alternative**: You can still use `docker-compose up -d --build` directly if you prefer fixed ports.

   ⏱️ **Default configuration loads last 12 months of data** (configure via `.env` file). First startup takes time based on data volume selected.

3. **Configure data backfill (optional):**
   Edit `.env` file to customize data loading:
   ```bash
   # Load last 12 months (default)
   BACKFILL_MONTHS=last_12_months

   # Load specific months
   BACKFILL_MONTHS=2024-01,2024-02,2024-03

   # Load all available data (2009-2025, WARNING: Very large!)
   BACKFILL_MONTHS=all
   ```

4. **Monitor the initialization progress:**
   ```bash
   docker logs -f sql-playground-postgres
   ```

   You'll see real-time progress updates as the system:
   - Creates PostGIS-enabled database schema
   - Downloads and loads 263 NYC taxi zones with geospatial boundaries
   - Downloads and processes trip data in chunks (10K rows each)
   - Performs data integrity verification

5. **Access PGAdmin Web Interface:**
   - **URL**: http://localhost:8080
   - **Login**: admin@admin.com / admin123

6. **Connect to PostgreSQL in PGAdmin:**
   - **Host**: postgres
   - **Port**: 5432
   - **Database**: playground
   - **Username**: admin
   - **Password**: admin123
   - **Schema**: nyc_taxi

7. **🚀 Access Apache Superset for Advanced Business Intelligence:**
   - **URL**: http://localhost:8088
   - **Login**: admin / admin123
   - **🎨 Create Professional Dashboards**: Build interactive visualizations from millions of taxi records
   - **⚡ SQL Lab**: Advanced SQL editor with autocomplete, query history, and result exports
   - **📊 Chart Gallery**: 50+ visualization types including maps, time series, and statistical plots
   - **🔄 Real-time Filtering**: Cross-dashboard filtering and drill-down capabilities
   - **Auto-connected**: Pre-configured PostgreSQL connection to playground database
   - **Persistent**: All dashboards and charts saved in SQLite backend
   - **Connection string**: postgresql+pg8000://admin:admin123@postgres:5432/playground


</details>

## Data Pipeline Architecture

<details>
<summary><strong>Click to expand</strong></summary>


```mermaid
flowchart TD
    %% Data Sources
    A[NYC TLC Data Sources] --> B[yellow_tripdata_*.parquet]
    A --> C[taxi_zone_lookup.csv]
    A --> D[taxi_zones.zip]

    %% ETL Process
    B --> E[Python ETL Process]
    C --> E
    D --> E

    %% Normalized Schema
    E --> F[(yellow_taxi_trips)]
    E --> G[(yellow_taxi_trips_invalid)]
    E --> H[(taxi_zone_lookup)]
    E --> I[(taxi_zone_shapes)]
    E --> J[(vendor_lookup)]
    E --> K[(payment_type_lookup)]
    E --> L[(rate_code_lookup)]

    %% Star Schema Dimensions
    H --> M[(dim_locations)]
    J --> N[(dim_vendor)]
    K --> O[(dim_payment_type)]
    L --> P[(dim_rate_code)]
    E --> Q[(dim_date)]
    E --> R[(dim_time)]

    %% Star Schema Fact Table
    F --> S[(fact_taxi_trips)]
    M --> S
    N --> S
    O --> S
    P --> S
    Q --> S
    R --> S

    %% Data Quality Monitoring
    E --> T[(data_quality_monitor)]
    E --> U[(data_processing_log)]

    %% Table Details (Schema Information)
    F -.-> F1["yellow_taxi_trips
    ---
    row_hash VARCHAR(64) PK
    vendorid INTEGER
    tpep_pickup_datetime TIMESTAMP
    tpep_dropoff_datetime TIMESTAMP
    passenger_count DECIMAL
    trip_distance DECIMAL
    pulocationid INTEGER FK
    dolocationid INTEGER FK
    payment_type BIGINT FK
    fare_amount DECIMAL
    total_amount DECIMAL
    + 12 more columns"]

    G -.-> G1["yellow_taxi_trips_invalid
    ---
    invalid_id BIGSERIAL PK
    error_message TEXT
    error_type VARCHAR
    source_file VARCHAR
    + all yellow_taxi_trips columns
    raw_data_json JSONB"]

    H -.-> H1["taxi_zone_lookup
    ---
    locationid INTEGER PK
    borough VARCHAR
    zone VARCHAR
    service_zone VARCHAR"]

    I -.-> I1["taxi_zone_shapes
    ---
    objectid INTEGER PK
    locationid INTEGER FK
    zone VARCHAR
    borough VARCHAR
    geometry GEOMETRY"]

    M -.-> M1["dim_locations
    ---
    location_key SERIAL PK
    locationid INTEGER UNIQUE
    zone VARCHAR
    borough VARCHAR
    zone_type VARCHAR
    is_airport BOOLEAN
    is_manhattan BOOLEAN
    business_district BOOLEAN"]

    N -.-> N1["dim_vendor
    ---
    vendor_key SERIAL PK
    vendorid INTEGER UNIQUE
    vendor_name VARCHAR
    vendor_type VARCHAR
    is_active BOOLEAN"]

    O -.-> O1["dim_payment_type
    ---
    payment_type_key SERIAL PK
    payment_type INTEGER UNIQUE
    payment_type_desc VARCHAR
    is_electronic BOOLEAN
    allows_tips BOOLEAN"]

    P -.-> P1["dim_rate_code
    ---
    rate_code_key SERIAL PK
    ratecodeid INTEGER UNIQUE
    rate_code_desc VARCHAR
    is_metered BOOLEAN
    is_airport_rate BOOLEAN"]

    Q -.-> Q1["dim_date
    ---
    date_key INTEGER PK
    date_actual DATE
    year INTEGER
    month INTEGER
    day INTEGER
    quarter INTEGER
    is_weekend BOOLEAN
    is_holiday BOOLEAN"]

    R -.-> R1["dim_time
    ---
    time_key INTEGER PK
    hour_24 INTEGER
    hour_12 INTEGER
    is_rush_hour BOOLEAN
    is_business_hours BOOLEAN
    time_period VARCHAR"]

    S -.-> S1["fact_taxi_trips
    ---
    trip_key BIGSERIAL PK
    pickup_date_key INTEGER FK
    pickup_time_key INTEGER FK
    dropoff_date_key INTEGER FK
    dropoff_time_key INTEGER FK
    pickup_location_key INTEGER FK
    dropoff_location_key INTEGER FK
    vendor_key INTEGER FK
    payment_type_key INTEGER FK
    rate_code_key INTEGER FK
    trip_distance DECIMAL
    trip_duration_minutes INTEGER
    fare_amount DECIMAL
    tip_amount DECIMAL
    total_amount DECIMAL
    + calculated measures"]

    T -.-> T1["data_quality_monitor
    ---
    monitor_id BIGSERIAL PK
    monitored_at TIMESTAMP
    source_file VARCHAR
    target_table VARCHAR
    rows_attempted BIGINT
    rows_inserted BIGINT
    rows_duplicates BIGINT
    rows_invalid BIGINT
    quality_level VARCHAR
    processing_duration_ms BIGINT"]

    U -.-> U1["data_processing_log
    ---
    log_id BIGSERIAL PK
    data_year INTEGER
    data_month INTEGER
    status VARCHAR
    processing_started_at TIMESTAMP
    processing_completed_at TIMESTAMP
    total_records_loaded BIGINT
    source_file_path VARCHAR"]

    %% Styling
    classDef source fill:#e1f5fe
    classDef normalized fill:#f3e5f5
    classDef star fill:#e8f5e8
    classDef quality fill:#fff3e0
    classDef details fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5

    class A,B,C,D source
    class F,G,H,I,J,K,L normalized
    class M,N,O,P,Q,R,S star
    class T,U quality
    class F1,G1,H1,I1,M1,N1,O1,P1,Q1,R1,S1,T1,U1 details
```

### Data Flow Legend
- **🔵 Blue (Source)**: NYC TLC official data sources
- **🟣 Purple (Normalized)**: OLTP-style normalized tables for data integrity
- **🟢 Green (Star Schema)**: OLAP-style dimensional model for analytics
- **🟠 Orange (Quality)**: Data quality monitoring and processing logs
- **Solid Lines**: Data transformation flow
- **Dotted Lines**: Table schema details with PK/FK indicators

### Key Relationships
- **yellow_taxi_trips**: Main fact table with hash-based primary key for duplicate prevention
- **Foreign Key Relationships**:
  - `pulocationid/dolocationid` → `taxi_zone_lookup.locationid`
  - `vendorid` → `vendor_lookup.vendorid`
  - `payment_type` → `payment_type_lookup.payment_type`
  - `ratecodeid` → `rate_code_lookup.ratecodeid`
- **Star Schema**: Dimensional model with `fact_taxi_trips` as central fact table
- **Data Quality**: Comprehensive monitoring with invalid row tracking and metrics


</details>

## Architecture & Data Loading

<details>
<summary><strong>Click to expand</strong></summary>


### Automated Backfill System
The system features a **flexible backfill system** that automatically downloads and loads data from official NYC TLC sources:

**Data Sources:**
- **Trip Data**: NYC Yellow Taxi records (2009-2025, 3-5 M records per month)
- **Zone Data**: 263 official NYC TLC taxi zones with lookup table and PostGIS geometries
- **Reference Data**: Vendors, payment types, rate codes with proper relationships

### Complete Initialization Process
The `postgres/docker/init-data.py` script orchestrates the entire process:

1. **PostgreSQL Readiness**: Waits for database to be fully operational
2. **Idempotent Schema Creation**: Executes SQL scripts with `IF NOT EXISTS` clauses for safe restarts
   - **Schema Resilience**: All CREATE TABLE and CREATE INDEX statements use `IF NOT EXISTS`
   - **Data Conflict Resolution**: INSERT statements use `ON CONFLICT ... DO UPDATE` for data consistency
   - **PostGIS Extensions**: Spatial extensions enabled with proper error handling
3. **Dictionary Table Cleaning**: Cleans all reference tables for fresh data loading
4. **Zone Data Processing**:
   - Downloads CSV lookup table and shapefile ZIP from official sources
   - Extracts shapefiles and loads with NULL value cleanup (263 valid zones)
   - Processes geometries with CRS conversion to NYC State Plane (EPSG:2263)
   - Reloads all lookup tables (rate codes, payment types, vendors)
5. **Optimized Trip Data Backfill**:
   - Downloads parquet files for configured months automatically (2009-2025 coverage)
   - Converts column names to lowercase for schema compatibility
   - Handles missing columns (e.g., cbd_congestion_fee in older data)
   - Handles numeric precision issues and NULL values
   - **Performance-Optimized Loading**: 100K row chunks with dimension caching and vectorized operations
   - **Bulk Transaction Processing**: Pandas `to_sql()` with `method='multi'` for maximum performance
   - **Enhanced Error Handling**: Bulk validation with comprehensive error classification
   - **Star Schema Population**: Optimized fact table loading with cached dimension lookups
6. **Data Verification**: Performs integrity checks with sample analytical queries

### Architecture Benefits
- **Zero Manual Data Management**: All data downloaded automatically from official sources
- **Flexible Backfill**: Load specific months, last N months, or all available data
- **Clean State Management**: Dictionary tables refreshed with each backfill for consistency
- **Production-Ready**: Handles real-world data challenges (case sensitivity, precision, memory)
- **Idempotent Operations**: Safe container restarts with `IF NOT EXISTS` schema creation
- **Error Recovery**: `docker-compose down -v` provides clean slate for troubleshooting
- **Persistent Storage**: Data persists between container restarts via Docker volumes
- **Organized Logging**: Logs organized by configuration with full traceability
- **Resumable Processing**: Safe pause/resume capability with automatic continuation from interruption point
- **High-Performance Processing**: 67-100x faster data loading with optimized algorithms


</details>

## Project Structure

<details>
<summary><strong>Click to expand</strong></summary>


```
sql-playgrounds/
├── docker-compose.yml              # Multi-service configuration (PostgreSQL + PGAdmin + Superset)
├── .env                            # Environment variables (credentials, ports, backfill config)
├── CLAUDE.md                       # Detailed architecture guide for Claude Code
├── postgres/                       # PostgreSQL-related files
│   ├── data/                       # NYC taxi data storage (auto-populated during initialization)
│   │   ├── zones/                  # NYC taxi zone reference data (auto-downloaded)
│   │   │   ├── taxi_zone_lookup.csv # 263 official taxi zones
│   │   │   └── taxi_zones.* (shp/dbf/shx/prj/sbn/sbx) # Extracted shapefiles
│   │   └── yellow/                 # NYC Yellow taxi trip data (auto-downloaded)
│   │       └── yellow_tripdata_*.parquet # Trip data files based on backfill config
│   └── logs/                       # PostgreSQL persistent logging
│   └── sql-scripts/                # SQL scripts
│       ├── init-scripts/           # Database schema creation (executed automatically)
│       │   ├── 00-postgis-setup.sql # PostGIS extensions and spatial references
│       │   └── 01-nyc-taxi-schema.sql # Complete NYC taxi schema (lowercase columns)
│       └── reports-scripts/        # Pre-built analytical queries (available in PGAdmin)
│           ├── nyc-taxi-analytics.sql # Trip volume, financial, and temporal analysis
│           └── geospatial-taxi-analytics.sql # PostGIS spatial queries and zone analysis
│   └── docker/                       # PostgreSQL Docker files
│       ├── Dockerfile.postgres       # Custom image: PostgreSQL + PostGIS + Python environment
│       └── init-data.py              # Comprehensive initialization script with backfill system
├── superset/                         # Apache Superset business intelligence platform
│   ├── config/                       # Superset configuration files
│   │   └── superset_config.py        # SQLite-based config (no Redis dependency)
│   ├── logs/                         # Superset application logs
│   └── docker/                       # Superset Docker files
│       ├── Dockerfile.superset       # Superset with PostgreSQL drivers
│       ├── create-db-connection.py   # Database connection script
│       └── init-superset.sh          # Superset initialization
# Note: Python dependencies embedded in Docker containers - no local setup required
```


</details>

## Container Architecture

<details>
<summary><strong>Click to expand</strong></summary>


### Custom PostgreSQL Container
- **Base**: `postgis/postgis:17-3.5` (PostgreSQL 17 + PostGIS 3.5)
- **Python Environment**: Virtual environment with data processing packages
- **Custom Entrypoint**: Starts PostgreSQL, waits for readiness, runs initialization
- **Embedded Dependencies**: pandas, geopandas, pyarrow, psycopg2, sqlalchemy

### Apache Superset Container
- **Base**: `apache/superset:latest` with custom PostgreSQL drivers
- **Metadata Database**: SQLite for persistent dashboard/chart storage
- **Caching Strategy**: SQLite-based using SupersetMetastoreCache (no Redis required)
- **Auto-initialization**: Pre-configured database connection and admin setup
- **Features**: Interactive dashboards, SQL Lab, chart creation, native filters

### Volume Strategy
- **Database Persistence**: `postgres_data` volume (survives container restarts)
- **PGAdmin Configuration**: `pgadmin_data` volume (settings, connections)
- **Superset Configuration**: `superset_data` volume (dashboards, charts, user settings)
- **SQL Scripts**: `./postgres/sql-scripts:/sql-scripts` (database schema and reports)
- **NYC Taxi Data**: `./postgres/data:/postgres/data` (auto-downloaded data files)
- **PostgreSQL Persistent Logging**: `./postgres/logs:/postgres/logs` (organized by backfill configuration)
- **Superset Configuration**: `./superset/config:/app/config` (SQLite-based setup files)
- **Superset Logging**: `./superset/logs:/app/logs` (application logs)
- **Script Access**: SQL scripts available both for initialization and PGAdmin queries

### Memory & Performance
- **Optimized Chunked Loading**: 100K rows per chunk (10x improvement) with memory-efficient processing
- **Progress Tracking**: Real-time logging with execution time tracking and performance metrics
- **Advanced Bulk Operations**: Dimension caching and vectorized calculations for 67-100x performance improvement
- **Optimized Indexes**: Spatial GIST, temporal, location, and composite indexes
- **Production Scale**: Handles millions of records efficiently with sub-30-minute processing times
- **Ultimate Duplicate Prevention**: SHA-256 hash-based system prevents any duplicate rows across backfills
- **Enhanced Error Handling**: Bulk validation with comprehensive error classification and invalid row storage


</details>

## Pause and Resume Capability

<details>
<summary><strong>Click to expand</strong></summary>


### Safe Interruption and Continuation
The system is designed to handle interruptions gracefully with automatic resume capability:

**Pause Processing:**
```bash
# Safely stop containers (preserves all data and progress)
docker-compose stop

# System can be safely interrupted at any point during backfill
```

**Resume Processing:**
```bash
# Automatically continues from where it left off
docker-compose up -d

# Monitor continuation progress
docker logs -f sql-playground-postgres
```

### Intelligent Resume System
When restarted, the system automatically:
- **🔍 Detects Completed Months**: Checks `data_processing_log` table for already-processed data
- **⏭️ Skips Finished Data**: Already loaded months show as "Already processed (X records)"
- **▶️ Continues From Interruption**: Resumes with the next unprocessed month
- **🛡️ Prevents Duplicates**: Hash-based system prevents duplicate rows during resume
- **📁 Reuses Downloads**: Existing parquet files are reused, no re-downloading needed

### Example Resume Behavior
From logs (`logs/last_12_months/log_20250924_215426.log`):
```
🔄 2024-10: Already processed (3,833,769 records)  ✅ Skipped
🔄 2024-11: Already processed (3,646,369 records)  ✅ Skipped
🔄 2024-12: Already processed (3,668,371 records)  ✅ Skipped
🔄 2025-01: Already processed (3,475,226 records)  ✅ Skipped
⚠️ 2025-02: Previous processing incomplete, will retry  🔄 Resumes here

📥 Loading yellow_tripdata_2025-02.parquet...
⚠️ Chunk 5/358 - 10000 duplicates skipped (hash-based)  🛡️ Duplicate protection
⚠️ Chunk 10/358 - 10000 duplicates skipped (hash-based) 🛡️ Working as expected
```

The hash-based duplicate prevention ensures that even if processing was interrupted mid-file, no duplicate records are inserted when resuming.


</details>

## Configuration & Development

<details>
<summary><strong>Click to expand</strong></summary>


### Environment Variables (`.env`)
```env
# PostgreSQL Configuration
POSTGRES_DB=playground
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123
POSTGRES_PORT=5432

# PGAdmin Configuration
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=admin123
PGADMIN_PORT=8080

# Apache Superset Configuration
SUPERSET_PORT=8088
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_EMAIL=admin@admin.com
SUPERSET_ADMIN_PASSWORD=admin123
SUPERSET_LOAD_EXAMPLES=false

# Data Loading Control
DATA_CHUNK_SIZE=100000
INIT_LOAD_ALL_DATA=true

# Backfill Configuration (controls which months to load)
BACKFILL_MONTHS=last_12_months
```

### System Requirements
- **Docker & Docker Compose** (only requirement for deployment)
- **Python 3.12+ with uv** (optional, for local development only)
- **Available Memory**: 4GB+ recommended for data loading process
- **Available Storage**: ~2GB for complete dataset and indexes

### Development Commands
```bash
# Full deployment (production-ready)
docker-compose up -d --build

# Development with clean rebuild (removes all data)
docker-compose down -v && docker-compose up -d --build

# Check data loading status
docker exec sql-playground-postgres psql -U admin -d playground -c "SELECT COUNT(*) FROM nyc_taxi.yellow_taxi_trips;"

# Check backfill progress
docker exec sql-playground-postgres psql -U admin -d playground -c "SELECT * FROM nyc_taxi.data_processing_log ORDER BY data_year, data_month;"

# Direct database access
docker exec -it sql-playground-postgres psql -U admin -d playground

# Monitor initialization progress
docker logs -f sql-playground-postgres

# Monitor persistent logs (organized by configuration)
tail -f logs/last_12_months/log_*.log
```

### Local Python Development (Optional)
```bash
# Install dependencies for local scripts
uv sync

# Add new dependencies
uv add package-name
```

**Note**: Python environment is embedded in Docker container. Local Python setup only needed for custom script development.


</details>

## Database Schema & Analytics

<details>
<summary><strong>Click to expand</strong></summary>


### NYC Taxi Data Structure

Schema defined in [`01-nyc-taxi-schema.sql`](postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql).

**Main Table**: `nyc_taxi.yellow_taxi_trips` (variable records based on backfill configuration, 21 columns)
- **Primary Key**: row_hash (SHA-256 hash of all row values for ultimate duplicate prevention)
- **Trip Identifiers**: vendorid, pickup/dropoff timestamps
- **Location Data**: pulocationid, dolocationid (references taxi zones)
- **Financial Data**: fare_amount, tip_amount, total_amount, taxes, fees
- **Trip Metrics**: passenger_count, trip_distance, payment_type
- **Missing Column Handling**: cbd_congestion_fee (handled gracefully for older data), airport_fee

**Star Schema Tables**:
- `fact_taxi_trips`: Dimensional fact table with calculated measures and foreign keys
- `dim_locations`, `dim_vendor`, `dim_payment_type`, `dim_rate_code`: Dimension tables for analytics
- `dim_date`: Date dimension with partition support (2009-2025)

**Geospatial Tables**:
- `taxi_zone_lookup`: 263 official NYC taxi zones with borough and service zone info
- `taxi_zone_shapes`: PostGIS MULTIPOLYGON geometries in NYC State Plane coordinates

**Reference Tables**: vendor_lookup, payment_type_lookup, rate_code_lookup

### Performance Optimizations

#### Phase 1: ETL Pipeline Optimization (Completed ✅)
- **Enhanced Chunk Processing**: Increased chunk size from 10K to 100K rows (10x improvement)
- **Optimized Hash Generation**: Improved duplicate detection performance by 10x (30K rows/second)
- **Memory-Efficient Processing**: Chunked loading prevents memory overflow while maximizing throughput
- **Overall ETL Improvement**: 6.7x faster data loading pipeline

#### Phase 2A: Database Optimization (Completed ✅)
- **Dimension Key Caching**: In-memory cache eliminates 18M individual SQL dimension lookups
  - **Before**: 5 SQL joins per row × 3.6M rows = 18M database queries
  - **After**: 4 one-time cache population queries + instant dictionary lookups (1000x faster)
- **Vectorized Operations**: Pandas/NumPy vectorized calculations replace row-by-row processing
  - **Trip duration calculations**: Vectorized datetime operations across entire DataFrames
  - **Derived measures**: Tip percentages, average speeds calculated in bulk (~100x faster)
- **Bulk Transaction Strategy**: Single bulk transactions replace individual row transactions
  - **Before**: 3.6M individual `engine.begin()` transactions
  - **After**: ~37 bulk transactions using `pandas.to_sql()` with `method='multi'`
- **Enhanced Error Handling**: Bulk validation with comprehensive error classification

#### Performance Results
- **Total Improvement**: **67-100x performance improvement**
  - **Before**: ~3.3 hours for 3.6M records
  - **After**: ~22 minutes for 3.6M records
- **Star Schema Processing**: <3 minutes (vs 95% of original processing time)
- **Hash Generation**: Maintains 30K rows/second with larger chunks

#### Database Indexes

The `yellow_taxi_trips` table carries 13 indexes totaling more storage than the data itself:

| Component | Size |
|-----------|------|
| Table data | 6.8 GB |
| Indexes (13 total) | 11 GB |
| **Combined** | **17 GB** |

**Index breakdown by size:**

| Index | Size | Purpose |
|-------|------|---------|
| `yellow_taxi_trips_pkey` (row_hash) | 3.9 GB | SHA-256 primary key for duplicate prevention |
| `idx_yellow_taxi_location_datetime` | 1.5 GB | Composite: location + datetime queries |
| `idx_yellow_taxi_datetime_vendor` | 990 MB | Composite: datetime + vendor queries |
| `yellow_taxi_trips_id_key` | 702 MB | Unique constraint |
| `idx_yellow_taxi_total_amount` | 696 MB | Top revenue queries (12ms vs ~2s without) |
| `idx_yellow_taxi_pickup_datetime` | 689 MB | Time-series lookups, hourly analysis |
| `idx_yellow_taxi_dropoff_datetime` | 686 MB | Dropoff time lookups |
| `idx_yellow_taxi_trip_distance` | 669 MB | Distance filtering (12ms vs ~2s without) |
| 5 smaller indexes | ~1 GB | Payment type, locations, vendor, date+payment |

**The tradeoff**: indexes make data loading ~2x slower (every INSERT must update all 13 indexes) but turn specific lookups from seconds to milliseconds. For a read-heavy playground that loads data once and queries many times, this is the right balance.

#### Materialized Views

Three pre-aggregated materialized views compress the full trips table for BigQuery-like response times on analytical queries (see [`02-materialized-views.sql`](postgres/sql-scripts/init-scripts/02-materialized-views.sql)):

| View | Source rows | Materialized rows | Size | Compression |
|------|-------------|-------------------|------|-------------|
| `trip_hourly_summary` | ~32M | ~25K | 4 MB | 1,280x |
| `trip_location_summary` | ~32M | ~121K | 12 MB | 264x |
| `trip_distance_summary` | ~32M | 6 | 40 KB | 5,300,000x |

**Sample speedups (raw table vs materialized view):**

| Query | Raw table | Materialized view | Speedup |
|-------|-----------|-------------------|---------|
| Cross-Borough Analysis | 1.78s | 32ms | 56x |
| Distance Distribution | 2.22s | 0.07ms | 31,700x |
| Weekend vs Weekday | 1.5s | 5ms | 300x |
| Payment Method Analysis | 1.5s | 4ms | 380x |

Views are refreshed automatically after each data load (Step 4 in init pipeline). For ad-hoc refresh:
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY nyc_taxi.trip_hourly_summary;
REFRESH MATERIALIZED VIEW CONCURRENTLY nyc_taxi.trip_location_summary;
REFRESH MATERIALIZED VIEW CONCURRENTLY nyc_taxi.trip_distance_summary;
```

#### PostgreSQL Runtime Tuning

PostgreSQL ships with conservative defaults designed to run on a 512MB shared hosting server from 2005. On a modern machine with 32 CPUs and 31 GB RAM, these defaults leave most of the hardware idle. The container is tuned at startup via command-line flags to fully utilize available resources.

**Memory settings — telling PostgreSQL how much RAM it can use:**

| Setting | PostgreSQL default | Our configuration | What changes |
|---------|-------------------|-------------------|--------------|
| `shared_buffers` | 128 MB | **8 GB** | PostgreSQL's own data cache — hot table pages stay in memory instead of being re-read from disk on every query |
| `effective_cache_size` | 4 GB | **24 GB** | Tells the query planner how much total cache (PostgreSQL + OS) is available — higher values make it prefer index scans over sequential scans |
| `work_mem` | 4 MB | **256 MB** | Memory for sorts and hash tables per operation — eliminates disk spill (our queries were spilling 267MB-1.4GB to disk at default) |
| `maintenance_work_mem` | 64 MB | **512 MB** | Memory for `CREATE INDEX`, `VACUUM`, bulk loading — speeds up data initialization |

**Parallelism settings — using all available CPU cores:**

| Setting | PostgreSQL default | Our configuration | What changes |
|---------|-------------------|-------------------|--------------|
| `max_worker_processes` | 8 | **24** | Total background workers PostgreSQL can spawn |
| `max_parallel_workers` | 8 | **20** | Workers available for parallel query execution |
| `max_parallel_workers_per_gather` | 2 | **16** | Workers per individual query — a full-table scan of 32M rows splits across 16 cores instead of 2 |

**The impact is cumulative.** A query that previously ran with 2 workers sorting 267MB to disk because `work_mem` was 4MB now runs with 16 workers keeping everything in RAM. The theoretical improvement for full-table scans is ~8x from parallelism alone, plus elimination of disk I/O from memory tuning.

**Before tuning (PostgreSQL defaults):**
```
Query: Trip volume by hour
Plan:  2 workers -> seq scan -> 267MB disk sort -> GroupAggregate
Time:  6.9 seconds
```

**After tuning (current configuration):**
```
Query: Trip volume by hour
Plan:  16 workers -> parallel seq scan -> in-memory HashAggregate
Time:  <1 second
```

#### PostgreSQL vs BigQuery: Architectural Differences

This playground uses PostgreSQL — a traditional row-oriented database designed for transactional workloads. Cloud analytical engines like BigQuery were built from the ground up for a different purpose: scanning terabytes of data across thousands of machines. Understanding these differences explains why certain optimizations are needed here but not there — and what we can borrow from BigQuery's playbook.

| Aspect | PostgreSQL (this project) | BigQuery |
|--------|--------------------------|----------|
| **Storage format** | Row-based — reads entire rows even if query needs 2 columns | Columnar — reads only the columns used in the query |
| **Parallelism** | Up to 16 workers on a single machine | Thousands of workers across a cluster |
| **Indexes** | Must be manually created; cost storage + write speed (our indexes are 1.6x the data size) | No traditional indexes — relies on partitioning + clustering |
| **Materialized views** | Must be manually created and refreshed | Has materialized views, plus automatic caching layers |
| **Memory model** | Shared buffers (8 GB) + OS page cache | Distributed memory across cluster, effectively unlimited |
| **Cost model** | Fixed infrastructure cost (your Docker container) | Pay-per-query based on bytes scanned |
| **Best for** | OLTP + moderate analytics, full SQL control | Large-scale analytics, ad-hoc exploration |

**What we replicate from BigQuery's approach:**
- **Materialized views** — pre-aggregated summaries compress 32M rows to 25K, giving sub-millisecond response times (up to 31,700x speedup)
- **Aggressive parallelism** — 16 workers instead of the default 2, similar in spirit to BigQuery splitting work across many machines
- **Memory-first processing** — 8GB shared buffers + 256MB work_mem keeps hot data and intermediate results in RAM, avoiding disk I/O like BigQuery's in-memory processing

**What we can't replicate:**
- **Columnar storage** — PostgreSQL reads full rows; a query needing just `trip_distance` still reads all 21 columns from disk (BigQuery would read only that one column, ~5% of the data)
- **Elastic parallelism** — we're capped at one machine's cores; BigQuery can throw 10,000 workers at a query
- **Separation of storage and compute** — BigQuery scales compute independently per query; our storage and compute share the same Docker container


</details>

## Data Sources & Authenticity

<details>
<summary><strong>Click to expand</strong></summary>


### NYC Yellow Taxi Trip Records
**Source**: [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- **Format**: Official parquet files (updated monthly by NYC TLC)
- **Available Data**: 2009-2025 (monthly files, ~60MB/3-5 M records per month)
- **Auto-Download**: System automatically downloads configured months from official sources
- **Coverage**: Complete historical coverage of taxi trip data from NYC Taxi & Limousine Commission
- **Data Quality**: Handles missing columns across different data periods with graceful fallbacks

### NYC Taxi Zone Reference Data
**Source**: [NYC TLC Taxi Zone Maps and Lookup Tables](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- **Lookup Table**: `taxi_zone_lookup.csv` - 263 official taxi zones (automatically downloaded)
- **Geospatial Data**: Complete shapefile ZIP with polygon boundaries (automatically downloaded and extracted)
- **Coordinate System**: Converted to NYC State Plane (EPSG:2263) for optimal spatial analysis
- **Components**: `.shp`, `.dbf`, `.shx`, `.prj`, `.sbn`, `.sbx` files extracted automatically

### Data Authenticity & Scale
This is **production-scale real-world data** from New York City's official transportation authority:
- ✅ **Authentic NYC taxi trips** - every record represents a real taxi ride
- ✅ **Flexible temporal coverage** - load specific months, last N months, or all available data
- ✅ **Official geospatial boundaries** - precise NYC taxi zone polygons
- ✅ **Rich analytical dimensions** - financial, temporal, spatial, and operational data
- ✅ **Always current** - downloads latest data directly from official NYC TLC sources

Perfect for learning advanced SQL, big data analytics, and geospatial analysis with realistic datasets that mirror production database challenges. The flexible backfill system allows you to work with datasets ranging from a single month to 16+ years of historical data (2009-2025).


</details>

## 🚀 Apache Superset Business Intelligence Features

<details>
<summary><strong>Click to expand</strong></summary>


### Transform Raw Data into Visual Stories
The playground includes a fully configured Apache Superset instance that transforms your NYC taxi data analysis into professional business intelligence:

#### 📊 **Rich Visualization Gallery**
- **Geospatial Maps**: Visualize pickup/dropoff patterns across NYC boroughs with PostGIS integration
- **Time Series Charts**: Track taxi demand patterns, revenue trends, and seasonal variations
- **Statistical Distributions**: Payment type breakdowns, trip distance histograms, fare analysis
- **Cross-Tab Tables**: Multi-dimensional analysis with drill-down capabilities
- **Custom Metrics**: Calculate KPIs like average trip duration, revenue per mile, tip percentages

#### ⚡ **Advanced SQL Lab**
- **Intelligent Autocomplete**: Schema-aware query suggestions for all tables and columns
- **Query History**: Save and reuse complex analytical queries
- **Result Visualization**: Instantly convert query results into charts and graphs
- **Data Export**: Download results in CSV, Excel, or JSON formats
- **Query Performance**: Built-in query optimization and execution plan analysis

#### 🎛️ **Interactive Dashboard Features**
- **Real-time Filtering**: Apply filters across multiple charts simultaneously
- **Cross-Dashboard Navigation**: Link related dashboards for comprehensive analysis
- **Responsive Design**: Dashboards work seamlessly on desktop and mobile devices
- **Scheduled Reports**: Automate dashboard delivery via email
- **Public Sharing**: Share dashboards with stakeholders via secure URLs

#### 📈 **Perfect for Data Presentations**
- **Executive Dashboards**: High-level KPIs and trends for decision makers
- **Operational Reports**: Daily/weekly performance monitoring and alerts
- **Analytical Deep-Dives**: Detailed exploration of taxi industry patterns
- **Geographic Analysis**: Borough-by-borough performance comparisons
- **Financial Insights**: Revenue analysis, payment pattern trends, profitability metrics

#### 🔧 **Enterprise-Ready Configuration**
- **SQLite Metadata Backend**: No Redis dependency, simplified deployment
- **Persistent Storage**: All dashboards, charts, and user settings preserved
- **Security Features**: Role-based access control, user management
- **Performance Optimized**: Efficient caching and query optimization
- **Scalable Architecture**: Ready for production deployment

### Sample Dashboard Ideas
Get started with these dashboard concepts using your NYC taxi data:
1. **📍 Geographic Performance**: Map visualizations showing hotspot areas and trip flows
2. **⏰ Temporal Analysis**: Hourly, daily, and seasonal demand patterns
3. **💰 Financial Dashboard**: Revenue trends, payment type analysis, profitability metrics
4. **🚗 Operations Monitor**: Trip volume, average duration, distance distributions
5. **🏙️ Borough Comparison**: Cross-borough analytics and performance benchmarks

Transform your SQL skills into compelling data stories with Superset's powerful visualization engine!


</details>

## 📊 Sample Analytics Queries

<details>
<summary><strong>Click to expand Sample Analytics Queries (13 queries + materialized view versions)</strong></summary>

### Sample Analytics Queries

#### 1. Trip Volume by Hour

Counts trips per hour with average distance, average fare, and a list of all boroughs. Optimized with CROSS JOIN LATERAL — aggregates trips first, then attaches the borough list separately instead of joining 11M rows to the lookup table before grouping (~3x faster).

```sql
SELECT h.hour, h.trips, h.avg_distance, h.avg_fare, b.pickup_boroughs
FROM (
    SELECT EXTRACT(HOUR FROM tpep_pickup_datetime) as hour,
           COUNT(*) as trips,
           ROUND(AVG(trip_distance), 2) as avg_distance,
           ROUND(AVG(total_amount), 2) as avg_fare
    FROM nyc_taxi.yellow_taxi_trips
    GROUP BY 1
) h
CROSS JOIN LATERAL (
    SELECT STRING_AGG(DISTINCT tz.borough, ', ') as pickup_boroughs
    FROM nyc_taxi.taxi_zone_lookup tz
) b
ORDER BY h.hour;

-- Original version (slower — joins 11M rows to lookup before grouping, causing 267MB disk sort):
-- SELECT EXTRACT(HOUR FROM yt.tpep_pickup_datetime) as hour,
--        COUNT(*) as trips,
--        STRING_AGG(DISTINCT pickup_zone.borough, ', ') as pickup_boroughs
-- FROM nyc_taxi.yellow_taxi_trips yt
-- JOIN nyc_taxi.taxi_zone_lookup pickup_zone ON yt.pulocationid = pickup_zone.locationid
-- GROUP BY hour ORDER BY hour;
```

<!-- ![Trip Volume by Hour - Query Results](docs/pictures/query-01-trip-volume-by-hour.png) -->

#### 2. Largest Taxi Zones by Area (PostGIS)

Uses `ST_Area()` on PostGIS geometries to find the 10 largest taxi zones in acres. Fast by nature — only 263 rows in the shapes table.

```sql
SELECT tzl.zone, tzl.borough,
       ROUND((ST_Area(geometry) / 43560)::numeric, 2) as area_acres
FROM nyc_taxi.taxi_zone_shapes tzs
JOIN nyc_taxi.taxi_zone_lookup tzl ON tzs.locationid = tzl.locationid
ORDER BY ST_Area(geometry) DESC LIMIT 10;
```

<!-- ![Largest Taxi Zones - Query Results](docs/pictures/query-02-largest-taxi-zones.png) -->

#### 3. Cross-Borough Trip Analysis

Shows trip counts and average fares between borough pairs. Optimized by pre-aggregating by location ID pair (~43K groups) before joining to the lookup table, so hash joins operate on 43K rows instead of 11M (~37% faster).

```sql
SELECT pz.borough || ' -> ' || dz.borough AS trip_route,
       SUM(agg.trip_count) AS trip_count,
       SUM(agg.avg_fare * agg.trip_count) / SUM(agg.trip_count) AS avg_fare
FROM (
    SELECT pulocationid, dolocationid,
           COUNT(*) AS trip_count,
           AVG(fare_amount) AS avg_fare
    FROM nyc_taxi.yellow_taxi_trips
    GROUP BY pulocationid, dolocationid
) agg
JOIN nyc_taxi.taxi_zone_lookup pz ON agg.pulocationid = pz.locationid
JOIN nyc_taxi.taxi_zone_lookup dz ON agg.dolocationid = dz.locationid
GROUP BY pz.borough, dz.borough
ORDER BY trip_count DESC;

-- Original version (slower — joins 11M rows to lookup twice before grouping by borough):
-- SELECT
--        pickup_zone.borough || ' -> ' || dropoff_zone.borough AS trip_route,
--        COUNT(*) AS trip_count,
--        AVG(yt.fare_amount) AS avg_fare
-- FROM nyc_taxi.yellow_taxi_trips yt
-- JOIN nyc_taxi.taxi_zone_lookup pickup_zone
--      ON yt.pulocationid = pickup_zone.locationid
-- JOIN nyc_taxi.taxi_zone_lookup dropoff_zone
--      ON yt.dolocationid = dropoff_zone.locationid
-- GROUP BY pickup_zone.borough, dropoff_zone.borough
-- ORDER BY trip_count DESC;
```

<!-- ![Cross-Borough Trip Analysis - Query Results](docs/pictures/query-03-cross-borough.png) -->

#### 4. Payment Patterns by Borough

Financial breakdown of payment types per borough. Same pre-aggregation optimization as query 3 — groups by raw IDs first (~1.2K groups), then joins to lookup tables for display names (~38% faster).

```sql
SELECT pz.borough || ' - ' || ptl.payment_type_desc AS borough_payment_type,
       SUM(agg.trips) AS trips,
       SUM(agg.avg_total * agg.trips) / SUM(agg.trips) AS avg_total
FROM (
    SELECT pulocationid, payment_type,
           COUNT(*) AS trips,
           AVG(total_amount) AS avg_total
    FROM nyc_taxi.yellow_taxi_trips
    GROUP BY pulocationid, payment_type
) agg
JOIN nyc_taxi.taxi_zone_lookup pz ON agg.pulocationid = pz.locationid
JOIN nyc_taxi.payment_type_lookup ptl ON agg.payment_type = ptl.payment_type
GROUP BY pz.borough, ptl.payment_type_desc
ORDER BY avg_total DESC;

-- Original version (slower — joins 11M rows to two lookups before grouping):
-- SELECT
--        pickup_zone.borough || ' - ' || ptl.payment_type_desc AS borough_payment_type,
--        COUNT(*) AS trips,
--        AVG(yt.total_amount) AS avg_total
-- FROM nyc_taxi.yellow_taxi_trips yt
-- JOIN nyc_taxi.taxi_zone_lookup pickup_zone
--      ON yt.pulocationid = pickup_zone.locationid
-- JOIN nyc_taxi.payment_type_lookup ptl
--      ON yt.payment_type = ptl.payment_type
-- GROUP BY pickup_zone.borough, ptl.payment_type_desc
-- ORDER BY avg_total DESC;
```

<!-- ![Payment Patterns by Borough - Query Results](docs/pictures/query-04-payment-borough.png) -->

#### Why Pre-Aggregation Helps: Hash Join Explained

Queries 3 and 4 use the same optimization pattern — **pre-aggregate by raw IDs, then join to lookup tables**. The key to understanding why this is faster lies in how PostgreSQL's hash join works.

**Hash join** is PostgreSQL's strategy when joining a large table to a small one. It works in two phases:

1. **Build phase** — scan the small table (e.g., `taxi_zone_lookup`, 263 rows) and build an in-memory hash table keyed on the join column (`locationid`). This takes ~20KB of memory.

2. **Probe phase** — scan the large table and for each row, hash the join column and look it up in the hash table. Each lookup is O(1).

The hash join itself is fast — the cost per probe is negligible. The problem is **what flows through it**. In the original queries, the full 11M-row trips table is probed against the lookup, producing 11M joined rows that then need to be aggregated by borough. In the optimized version, the trips are first grouped by location ID (~1-43K groups depending on the query), and only those groups are probed — reducing the downstream aggregation work by orders of magnitude.

```
Original:  11M trips --hash join--> 11M joined rows --GROUP BY borough--> 24-35 results
Optimized: 11M trips --GROUP BY id--> 1-43K groups --hash join--> 1-43K rows --GROUP BY borough--> 24-35 results
```

The sequential scan on the 11M-row table is unavoidable either way — but the join and final aggregation operate on dramatically fewer rows.

#### 5. Basic Data Overview

Quick summary of total trips, date range, and total revenue. Optimized to compute all aggregates in a single table scan using `unnest(ARRAY[...])` instead of 3 separate scans with `UNION ALL` (~2.8x faster).

```sql
SELECT unnest(ARRAY['Total Trips', 'Date Range', 'Total Revenue']) as metric,
       unnest(ARRAY[
           COUNT(*)::text,
           MIN(tpep_pickup_datetime)::text || ' to ' || MAX(tpep_pickup_datetime)::text,
           '$' || ROUND(SUM(total_amount), 2)::text
       ]) as value
FROM nyc_taxi.yellow_taxi_trips;

-- Original version (slower — 3 separate full table scans via UNION ALL):
-- SELECT 'Total Trips' as metric, COUNT(*)::text as value
-- FROM nyc_taxi.yellow_taxi_trips
-- UNION ALL
-- SELECT 'Date Range' as metric,
--        MIN(tpep_pickup_datetime)::text || ' to ' || MAX(tpep_pickup_datetime)::text as value
-- FROM nyc_taxi.yellow_taxi_trips
-- UNION ALL
-- SELECT 'Total Revenue' as metric, '$' || ROUND(SUM(total_amount), 2)::text as value
-- FROM nyc_taxi.yellow_taxi_trips;
```

<!-- ![Basic Data Overview - Query Results](docs/pictures/query-05-basic-overview.png) -->

#### 6. Payment Method Analysis

Breakdown by payment type with trip counts, averages, totals, and percentage share using a window function.

```sql
SELECT
    CASE payment_type
        WHEN 1 THEN 'Credit Card'
        WHEN 2 THEN 'Cash'
        WHEN 3 THEN 'No Charge'
        WHEN 4 THEN 'Dispute'
        WHEN 5 THEN 'Unknown'
        WHEN 6 THEN 'Voided'
        ELSE 'Other'
    END as payment_method,
    COUNT(*) as trip_count,
    ROUND(AVG(total_amount), 2) as avg_fare,
    ROUND(AVG(tip_amount), 2) as avg_tip,
    ROUND(SUM(total_amount), 2) as total_revenue,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM nyc_taxi.yellow_taxi_trips
GROUP BY payment_type
ORDER BY trip_count DESC;
```

<!-- ![Payment Method Analysis - Query Results](docs/pictures/query-06-payment-method.png) -->

#### 7. Top Revenue Generating Trips

Highest-value trips — useful for spotting possible erroneous data inputs (e.g., $900+ fares).

```sql
SELECT
    tpep_pickup_datetime,
    trip_distance,
    total_amount,
    tip_amount,
    PULocationID as pickup_zone,
    DOLocationID as dropoff_zone,
    EXTRACT(HOUR FROM tpep_pickup_datetime) as pickup_hour
FROM nyc_taxi.yellow_taxi_trips
WHERE total_amount > 100
ORDER BY total_amount DESC
LIMIT 20;
```

<!-- ![Top Revenue Generating Trips - Query Results](docs/pictures/query-07-top-revenue.png) -->

#### 8. Trip Distance Distribution

Bucketed distance ranges with trip counts, averages, and percentage distribution. Filters out zero-distance and extreme outliers.

```sql
SELECT
    CASE
        WHEN trip_distance <= 1 THEN '0-1 miles'
        WHEN trip_distance <= 3 THEN '1-3 miles'
        WHEN trip_distance <= 5 THEN '3-5 miles'
        WHEN trip_distance <= 10 THEN '5-10 miles'
        WHEN trip_distance <= 20 THEN '10-20 miles'
        ELSE '20+ miles'
    END as distance_range,
    COUNT(*) as trip_count,
    ROUND(AVG(trip_distance),2) AS avg_distance,
    ROUND(AVG(total_amount), 2) as avg_fare,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM nyc_taxi.yellow_taxi_trips
WHERE trip_distance > 0 AND trip_distance < 500
GROUP BY
    CASE
        WHEN trip_distance <= 1 THEN '0-1 miles'
        WHEN trip_distance <= 3 THEN '1-3 miles'
        WHEN trip_distance <= 5 THEN '3-5 miles'
        WHEN trip_distance <= 10 THEN '5-10 miles'
        WHEN trip_distance <= 20 THEN '10-20 miles'
        ELSE '20+ miles'
    END
ORDER BY MIN(trip_distance);
```

<!-- ![Trip Distance Distribution - Query Results](docs/pictures/query-08-distance-distribution.png) -->

#### 9. Daily Trip Patterns

Day-by-day totals with revenue and payment method split — good for time-series visualization in Superset.

```sql
SELECT
    DATE(tpep_pickup_datetime) as trip_date,
    COUNT(*) as total_trips,
    ROUND(AVG(total_amount), 2) as avg_fare,
    ROUND(SUM(total_amount), 2) as daily_revenue,
    COUNT(CASE WHEN payment_type = 1 THEN 1 END) as credit_card_trips,
    COUNT(CASE WHEN payment_type = 2 THEN 1 END) as cash_trips
FROM nyc_taxi.yellow_taxi_trips
GROUP BY DATE(tpep_pickup_datetime)
ORDER BY trip_date;
```

<!-- ![Daily Trip Patterns - Query Results](docs/pictures/query-09-daily-patterns.png) -->

#### 10. Rush Hour Analysis

Groups trips into four time-of-day buckets (morning rush, evening rush, night, regular) with distance and fare averages. Optimized with two-stage aggregation: groups by hour first (24 groups), then maps to time periods — avoids 1.2GB disk sort caused by grouping on the CASE text expression directly (~18% faster).

```sql
SELECT
    CASE
        WHEN h BETWEEN 7 AND 9 THEN 'Morning Rush (7-9 AM)'
        WHEN h BETWEEN 17 AND 19 THEN 'Evening Rush (5-7 PM)'
        WHEN h >= 22 OR h <= 5 THEN 'Night (10 PM - 5 AM)'
        ELSE 'Regular Hours'
    END as time_period,
    SUM(cnt) as trip_count,
    ROUND((SUM(dist) / SUM(cnt))::numeric, 2) as avg_distance,
    ROUND((SUM(amt) / SUM(cnt))::numeric, 2) as avg_fare,
    ROUND((SUM(tip) / SUM(cnt))::numeric, 2) as avg_tip
FROM (
    SELECT EXTRACT(HOUR FROM tpep_pickup_datetime)::int as h,
           COUNT(*) as cnt, SUM(trip_distance) as dist,
           SUM(total_amount) as amt, SUM(tip_amount) as tip
    FROM nyc_taxi.yellow_taxi_trips
    GROUP BY 1
) sub
GROUP BY 1
ORDER BY trip_count DESC;

-- Original version (slower — groups on CASE text expression, causing 1.2GB disk sort):
-- SELECT
--     CASE
--         WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 7 AND 9 THEN 'Morning Rush (7-9 AM)'
--         WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 17 AND 19 THEN 'Evening Rush (5-7 PM)'
--         WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 22 AND 23 OR
--              EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 0 AND 5 THEN 'Night (10 PM - 5 AM)'
--         ELSE 'Regular Hours'
--     END as time_period,
--     COUNT(*) as trip_count,
--     ROUND(AVG(trip_distance), 2) as avg_distance,
--     ROUND(AVG(total_amount), 2) as avg_fare,
--     ROUND(AVG(tip_amount), 2) as avg_tip
-- FROM nyc_taxi.yellow_taxi_trips
-- GROUP BY 1
-- ORDER BY trip_count DESC;
```

<!-- ![Rush Hour Analysis - Query Results](docs/pictures/query-10-rush-hour.png) -->

#### 11. Tip Analysis by Payment Type

Compares tipping behavior between credit card and cash payments — tip percentage, average tip, and how many trips include a tip.

```sql
SELECT
    CASE payment_type
        WHEN 1 THEN 'Credit Card'
        WHEN 2 THEN 'Cash'
        ELSE 'Other'
    END as payment_method,
    COUNT(*) as trip_count,
    ROUND(AVG(tip_amount), 2) as avg_tip,
    ROUND(AVG(fare_amount), 2) as avg_fare,
    ROUND(AVG(tip_amount / NULLIF(fare_amount, 0) * 100), 2) as avg_tip_percentage,
    COUNT(CASE WHEN tip_amount > 0 THEN 1 END) as trips_with_tips
FROM nyc_taxi.yellow_taxi_trips
WHERE fare_amount > 0 AND payment_type IN (1, 2)
GROUP BY payment_type
ORDER BY avg_tip DESC;
```

<!-- ![Tip Analysis - Query Results](docs/pictures/query-11-tip-analysis.png) -->

#### 12. Weekend vs Weekday Analysis

Compares trip volume, distance, fare, and revenue between weekdays and weekends. Optimized with two-stage aggregation: groups by day-of-week first (7 groups), then maps to weekend/weekday — avoids planner overestimating CASE expression cardinality.

```sql
SELECT
    CASE WHEN dow IN (0, 6) THEN 'Weekend' ELSE 'Weekday' END as day_type,
    SUM(cnt) as trip_count,
    ROUND((SUM(dist) / SUM(cnt))::numeric, 2) as avg_distance,
    ROUND((SUM(amt) / SUM(cnt))::numeric, 2) as avg_fare,
    ROUND(SUM(amt)::numeric, 2) as total_revenue
FROM (
    SELECT EXTRACT(DOW FROM tpep_pickup_datetime)::int as dow,
           COUNT(*) as cnt, SUM(trip_distance) as dist,
           SUM(total_amount) as amt
    FROM nyc_taxi.yellow_taxi_trips
    GROUP BY 1
) sub
GROUP BY 1
ORDER BY trip_count DESC;

-- Original version (slower — groups on CASE text expression, planner loses parallelism):
-- SELECT
--     CASE
--         WHEN EXTRACT(DOW FROM tpep_pickup_datetime) IN (0, 6) THEN 'Weekend'
--         ELSE 'Weekday'
--     END as day_type,
--     COUNT(*) as trip_count,
--     ROUND(AVG(trip_distance), 2) as avg_distance,
--     ROUND(AVG(total_amount), 2) as avg_fare,
--     ROUND(SUM(total_amount), 2) as total_revenue
-- FROM nyc_taxi.yellow_taxi_trips
-- GROUP BY
--     CASE
--         WHEN EXTRACT(DOW FROM tpep_pickup_datetime) IN (0, 6) THEN 'Weekend'
--         ELSE 'Weekday'
--     END
-- ORDER BY trip_count DESC;
```

<!-- ![Weekend vs Weekday - Query Results](docs/pictures/query-12-weekend-weekday.png) -->

#### 13. Long Distance Trips (Over 20 Miles)

Identifies unusually long trips with fare-per-mile calculation — useful for spotting possible erroneous data inputs or airport runs.

```sql
SELECT
    tpep_pickup_datetime,
    trip_distance,
    total_amount,
    ROUND(total_amount / trip_distance, 2) as fare_per_mile,
    PULocationID,
    DOLocationID,
    passenger_count
FROM nyc_taxi.yellow_taxi_trips
WHERE trip_distance > 20
ORDER BY trip_distance DESC
LIMIT 4000;
```

<!-- ![Long Distance Trips - Query Results](docs/pictures/query-13-long-distance.png) -->

### Sample Analytics Queries — Materialized View Versions

The queries below produce the same results as the Sample Analytics Queries above but run against pre-aggregated materialized views instead of scanning the full 19M-row trips table. Response times drop from seconds to single-digit milliseconds.

Three materialized views are created automatically during initialization (see [`02-materialized-views.sql`](postgres/sql-scripts/init-scripts/02-materialized-views.sql)):

| View | Rows | Covers queries |
|------|------|----------------|
| `nyc_taxi.trip_hourly_summary` | ~25K | 1, 5, 6, 9, 10, 11, 12 |
| `nyc_taxi.trip_location_summary` | ~121K | 3, 4 |
| `nyc_taxi.trip_distance_summary` | 6 | 8 |

Queries 2 (PostGIS zones), 7 (top revenue trips), and 13 (long distance trips) are already fast and don't benefit from materialized views — they either operate on small tables or use index scans.

Refresh all views after loading new data:
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY nyc_taxi.trip_hourly_summary;
REFRESH MATERIALIZED VIEW CONCURRENTLY nyc_taxi.trip_location_summary;
REFRESH MATERIALIZED VIEW CONCURRENTLY nyc_taxi.trip_distance_summary;
```

#### MV-1. Trip Volume by Hour

Uses `trip_hourly_summary`. Boroughs are still attached via CROSS JOIN LATERAL from the lookup table. **~6ms** (vs ~2.3s on raw table).

```sql
SELECT h.pickup_hour as hour,
       SUM(h.trip_count) as trips,
       ROUND((SUM(h.total_distance) / SUM(h.trip_count))::numeric, 2) as avg_distance,
       ROUND((SUM(h.total_amount) / SUM(h.trip_count))::numeric, 2) as avg_fare,
       b.pickup_boroughs
FROM nyc_taxi.trip_hourly_summary h
CROSS JOIN LATERAL (
    SELECT STRING_AGG(DISTINCT tz.borough, ', ') as pickup_boroughs
    FROM nyc_taxi.taxi_zone_lookup tz
) b
GROUP BY h.pickup_hour, b.pickup_boroughs
ORDER BY h.pickup_hour;
```

![MV Trip Volume by Hour - Query Results](docs/pictures/mv-01-trip-volume.png)

#### MV-3. Cross-Borough Trip Analysis

Uses `trip_location_summary`. Joins 121K pre-aggregated rows to lookup tables instead of 19M. **~22ms** (vs ~1.1s on raw table).

```sql
SELECT pz.borough || ' -> ' || dz.borough AS trip_route,
       SUM(ls.trip_count) AS trip_count,
       ROUND((SUM(ls.total_fare) / SUM(ls.trip_count))::numeric, 2) AS avg_fare
FROM nyc_taxi.trip_location_summary ls
JOIN nyc_taxi.taxi_zone_lookup pz ON ls.pulocationid = pz.locationid
JOIN nyc_taxi.taxi_zone_lookup dz ON ls.dolocationid = dz.locationid
GROUP BY pz.borough, dz.borough
ORDER BY trip_count DESC;
```

![MV Cross-Borough - Query Results](docs/pictures/mv-03-cross-borough.png)

#### MV-4. Payment Patterns by Borough

Uses `trip_location_summary`. Joins to both zone lookup and payment type lookup. **~20ms** (vs ~1.2s on raw table).

```sql
SELECT pz.borough || ' - ' || ptl.payment_type_desc AS borough_payment_type,
       SUM(ls.trip_count) AS trips,
       ROUND((SUM(ls.total_amount) / SUM(ls.trip_count))::numeric, 2) AS avg_total
FROM nyc_taxi.trip_location_summary ls
JOIN nyc_taxi.taxi_zone_lookup pz ON ls.pulocationid = pz.locationid
JOIN nyc_taxi.payment_type_lookup ptl ON ls.payment_type = ptl.payment_type
GROUP BY pz.borough, ptl.payment_type_desc
ORDER BY avg_total DESC;
```

![MV Payment Patterns - Query Results](docs/pictures/mv-04-payment-borough.png)

#### MV-5. Basic Data Overview

Uses `trip_hourly_summary`. Single scan of 25K rows instead of 19M. **~3ms** (vs ~0.9s on raw table).

```sql
SELECT unnest(ARRAY['Total Trips', 'Date Range', 'Total Revenue']) as metric,
       unnest(ARRAY[
           SUM(trip_count)::text,
           MIN(min_pickup)::text || ' to ' || MAX(max_pickup)::text,
           '$' || ROUND(SUM(total_amount)::numeric, 2)::text
       ]) as value
FROM nyc_taxi.trip_hourly_summary;
```

![MV Basic Overview - Query Results](docs/pictures/mv-05-basic-overview.png)

#### MV-6. Payment Method Analysis

Uses `trip_hourly_summary`. Aggregates 25K rows by payment type instead of 19M. **~4ms** (vs ~1.6s on raw table).

```sql
SELECT
    CASE payment_type
        WHEN 1 THEN 'Credit Card'
        WHEN 2 THEN 'Cash'
        WHEN 3 THEN 'No Charge'
        WHEN 4 THEN 'Dispute'
        WHEN 5 THEN 'Unknown'
        WHEN 6 THEN 'Voided'
        ELSE 'Other'
    END as payment_method,
    SUM(trip_count) as trip_count,
    ROUND((SUM(total_amount) / SUM(trip_count))::numeric, 2) as avg_fare,
    ROUND((SUM(total_tip) / SUM(trip_count))::numeric, 2) as avg_tip,
    ROUND(SUM(total_amount)::numeric, 2) as total_revenue,
    ROUND(100.0 * SUM(trip_count) / SUM(SUM(trip_count)) OVER(), 2) as percentage
FROM nyc_taxi.trip_hourly_summary
GROUP BY payment_type
ORDER BY trip_count DESC;
```

![MV Payment Method - Query Results](docs/pictures/mv-06-payment-method.png)

#### MV-8. Trip Distance Distribution

Uses `trip_distance_summary`. Reads 6 pre-computed rows — effectively instant. **~0.06ms** (vs ~2.2s on raw table).

```sql
SELECT distance_range,
       trip_count,
       ROUND((total_distance / trip_count)::numeric, 2) as avg_distance,
       ROUND((total_amount / trip_count)::numeric, 2) as avg_fare,
       ROUND(100.0 * trip_count / SUM(trip_count) OVER(), 2) as percentage
FROM nyc_taxi.trip_distance_summary
ORDER BY distance_bucket;
```

![MV Distance Distribution - Query Results](docs/pictures/mv-08-distance-distribution.png)

#### MV-9. Daily Trip Patterns

Uses `trip_hourly_summary`. Groups by date across 25K rows instead of 19M. **~5ms** (vs ~1s on raw table).

```sql
SELECT trip_date,
       SUM(trip_count) as total_trips,
       ROUND((SUM(total_amount) / SUM(trip_count))::numeric, 2) as avg_fare,
       ROUND(SUM(total_amount)::numeric, 2) as daily_revenue,
       SUM(CASE WHEN payment_type = 1 THEN trip_count ELSE 0 END) as credit_card_trips,
       SUM(CASE WHEN payment_type = 2 THEN trip_count ELSE 0 END) as cash_trips
FROM nyc_taxi.trip_hourly_summary
GROUP BY trip_date
ORDER BY trip_date;
```

![MV Daily Patterns - Query Results](docs/pictures/mv-09-daily-patterns.png)

#### MV-10. Rush Hour Analysis

Uses `trip_hourly_summary`. Groups by hour bucket across 25K rows instead of 19M. **~6ms** (vs ~7.1s on raw table).

```sql
SELECT
    CASE
        WHEN pickup_hour BETWEEN 7 AND 9 THEN 'Morning Rush (7-9 AM)'
        WHEN pickup_hour BETWEEN 17 AND 19 THEN 'Evening Rush (5-7 PM)'
        WHEN pickup_hour >= 22 OR pickup_hour <= 5 THEN 'Night (10 PM - 5 AM)'
        ELSE 'Regular Hours'
    END as time_period,
    SUM(trip_count) as trip_count,
    ROUND((SUM(total_distance) / SUM(trip_count))::numeric, 2) as avg_distance,
    ROUND((SUM(total_amount) / SUM(trip_count))::numeric, 2) as avg_fare,
    ROUND((SUM(total_tip) / SUM(trip_count))::numeric, 2) as avg_tip
FROM nyc_taxi.trip_hourly_summary
GROUP BY
    CASE
        WHEN pickup_hour BETWEEN 7 AND 9 THEN 'Morning Rush (7-9 AM)'
        WHEN pickup_hour BETWEEN 17 AND 19 THEN 'Evening Rush (5-7 PM)'
        WHEN pickup_hour >= 22 OR pickup_hour <= 5 THEN 'Night (10 PM - 5 AM)'
        ELSE 'Regular Hours'
    END
ORDER BY trip_count DESC;
```

![MV Rush Hour - Query Results](docs/pictures/mv-10-rush-hour.png)

#### MV-11. Tip Analysis by Payment Type

Uses `trip_hourly_summary`. **~3ms** (vs ~1.8s on raw table). Note: `avg_tip_percentage` is approximated as the ratio of total tip to total fare (not the average of per-row percentages), which is more statistically meaningful for large datasets.

```sql
SELECT
    CASE payment_type
        WHEN 1 THEN 'Credit Card'
        WHEN 2 THEN 'Cash'
        ELSE 'Other'
    END as payment_method,
    SUM(trip_count) as trip_count,
    ROUND((SUM(total_tip) / SUM(trip_count))::numeric, 2) as avg_tip,
    ROUND((SUM(total_fare) / SUM(trip_count))::numeric, 2) as avg_fare,
    ROUND((SUM(total_tip) / NULLIF(SUM(total_fare), 0) * 100)::numeric, 2) as avg_tip_percentage,
    SUM(trips_with_tips) as trips_with_tips
FROM nyc_taxi.trip_hourly_summary
WHERE total_fare > 0 AND payment_type IN (1, 2)
GROUP BY payment_type
ORDER BY avg_tip DESC;
```

![MV Tip Analysis - Query Results](docs/pictures/mv-11-tip-analysis.png)

#### MV-12. Weekend vs Weekday Analysis

Uses `trip_hourly_summary`. Groups by pre-computed `day_of_week` column across 25K rows. **~5ms** (vs ~7.1s on raw table).

```sql
SELECT
    CASE WHEN day_of_week IN (0, 6) THEN 'Weekend' ELSE 'Weekday' END as day_type,
    SUM(trip_count) as trip_count,
    ROUND((SUM(total_distance) / SUM(trip_count))::numeric, 2) as avg_distance,
    ROUND((SUM(total_amount) / SUM(trip_count))::numeric, 2) as avg_fare,
    ROUND(SUM(total_amount)::numeric, 2) as total_revenue
FROM nyc_taxi.trip_hourly_summary
GROUP BY CASE WHEN day_of_week IN (0, 6) THEN 'Weekend' ELSE 'Weekday' END
ORDER BY trip_count DESC;
```

![MV Weekend vs Weekday - Query Results](docs/pictures/mv-12-weekend-weekday.png)

</details>

