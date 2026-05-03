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