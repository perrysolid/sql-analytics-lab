-- ================================================================================
-- NYC Yellow Taxi Complete Schema for PostgreSQL
-- Integrated Initial Schema + Star Schema + Partitioning + Performance Indexing
-- Based on actual NYC TLC Trip Record Data (https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
-- This is a real-world big data model with 3.4+ million taxi trips per month
-- ================================================================================

-- Create schema for NYC Taxi data
CREATE SCHEMA IF NOT EXISTS nyc_taxi;
SET search_path = nyc_taxi, public;

-- ================================================================================
-- PART 1: INITIAL NORMALIZED SCHEMA
-- ================================================================================

-- Yellow Taxi Trip Records table
-- This table structure exactly matches the NYC TLC Yellow Taxi data format (20 columns)
CREATE TABLE IF NOT EXISTS yellow_taxi_trips (
    -- Trip identifiers
    vendorid INTEGER,                    -- Provider that provided the record (1= Creative Mobile Technologies, 2= VeriFone Inc.)

    -- Trip timing
    tpep_pickup_datetime TIMESTAMP,      -- Date and time when the meter was engaged
    tpep_dropoff_datetime TIMESTAMP,     -- Date and time when the meter was disengaged

    -- Passenger information
    passenger_count DECIMAL(4,1),        -- Number of passengers in the vehicle (can be fractional)

    -- Trip distance
    trip_distance DECIMAL(12,2),          -- Trip distance in miles

    -- Location and rate information
    ratecodeid DECIMAL(4,1),             -- Rate code in effect at the end of the trip
    store_and_fwd_flag VARCHAR(1),       -- Y= store and forward trip, N= not a store and forward trip
    pulocationid INTEGER,                -- TLC Taxi Zone where the taximeter was engaged
    dolocationid INTEGER,                -- TLC Taxi Zone where the taximeter was disengaged

    -- Payment information
    payment_type BIGINT,                 -- Payment method (1= Credit card, 2= Cash, 3= No charge, 4= Dispute, 5= Unknown, 6= Voided trip)
    fare_amount DECIMAL(10,2),           -- Time-and-distance fare calculated by the meter
    extra DECIMAL(10,2),                 -- Miscellaneous extras and surcharges ($0.50 and $1 rush hour and overnight charges)
    mta_tax DECIMAL(10,2),               -- $0.50 MTA tax that is automatically triggered based on the metered rate in use
    tip_amount DECIMAL(10,2),            -- Tip amount (automatically populated for credit card tips, cash tips not included)
    tolls_amount DECIMAL(10,2),          -- Total amount of all tolls paid in trip
    improvement_surcharge DECIMAL(10,2),  -- $0.30 improvement surcharge assessed trips at the flag drop
    total_amount DECIMAL(12,2),          -- Total amount charged to passengers (does not include cash tips)
    congestion_surcharge DECIMAL(10,2),  -- Total amount collected in trip for NYS congestion surcharge
    airport_fee DECIMAL(10,2),           -- $1.25 for pick up only at LaGuardia and John F. Kennedy Airports
    cbd_congestion_fee DECIMAL(10,2),     -- CBD (Central Business District) congestion fee

    -- Hash-based duplicate prevention (ultimate protection) - now primary key for performance
    row_hash VARCHAR(64) PRIMARY KEY,    -- SHA-256 hash of all row values prevents any duplicate row

    -- Auto-incrementing ID for ordering (no longer primary key)
    id SERIAL UNIQUE
);

-- Invalid Trip Records table - stores rows that failed to insert into yellow_taxi_trips
-- Used for data quality monitoring and debugging during batch ingestion
CREATE TABLE IF NOT EXISTS yellow_taxi_trips_invalid (
    -- Metadata about the failed insertion
    invalid_id BIGSERIAL PRIMARY KEY,
    failed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    error_type VARCHAR(100), -- 'primary_key_violation', 'constraint_violation', 'data_type_error', etc.
    source_file VARCHAR(200),
    chunk_number INTEGER,
    row_number_in_chunk INTEGER,

    -- Original trip data (same structure as yellow_taxi_trips, but all fields nullable)
    vendorid INTEGER,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count DECIMAL(4,1),
    trip_distance DECIMAL(12,2),
    ratecodeid DECIMAL(4,1),
    store_and_fwd_flag VARCHAR(1),
    pulocationid INTEGER,
    dolocationid INTEGER,
    payment_type BIGINT,
    fare_amount DECIMAL(10,2),
    extra DECIMAL(10,2),
    mta_tax DECIMAL(10,2),
    tip_amount DECIMAL(10,2),
    tolls_amount DECIMAL(10,2),
    improvement_surcharge DECIMAL(10,2),
    total_amount DECIMAL(12,2),
    congestion_surcharge DECIMAL(10,2),
    airport_fee DECIMAL(10,2),
    cbd_congestion_fee DECIMAL(10,2),
    row_hash VARCHAR(64),

    -- Additional debugging information
    raw_data_json JSONB -- Store the complete raw row data for debugging
);

-- Indexes for efficient querying of invalid data
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_trips_invalid_failed_at ON yellow_taxi_trips_invalid (failed_at);
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_trips_invalid_error_type ON yellow_taxi_trips_invalid (error_type);
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_trips_invalid_source_file ON yellow_taxi_trips_invalid (source_file);
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_trips_invalid_row_hash ON yellow_taxi_trips_invalid (row_hash);

-- Data Quality Monitoring table - tracks quality metrics for all table insertions
-- Provides comprehensive monitoring of data quality across all tables and operations
CREATE TABLE IF NOT EXISTS data_quality_monitor (
    -- Primary identification
    quality_id BIGSERIAL PRIMARY KEY,
    monitored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Source and operation context
    source_file VARCHAR(200),
    operation_type VARCHAR(50) NOT NULL, -- 'chunk_insert', 'bulk_load', 'dimension_load', etc.
    target_table VARCHAR(100) NOT NULL, -- Table being inserted into
    target_schema VARCHAR(50) DEFAULT 'nyc_taxi',

    -- Chunk/batch identification
    chunk_number INTEGER,
    batch_id VARCHAR(100), -- For grouping related operations
    processing_session_id VARCHAR(100), -- Links to data_processing_log

    -- Volume metrics
    rows_attempted INTEGER NOT NULL DEFAULT 0,
    rows_inserted INTEGER NOT NULL DEFAULT 0,
    rows_updated INTEGER NOT NULL DEFAULT 0,
    rows_deleted INTEGER NOT NULL DEFAULT 0,
    rows_duplicates INTEGER NOT NULL DEFAULT 0,
    rows_invalid INTEGER NOT NULL DEFAULT 0,
    rows_skipped INTEGER NOT NULL DEFAULT 0,

    -- Quality metrics percentages
    success_rate DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN rows_attempted > 0
        THEN (rows_inserted::DECIMAL / rows_attempted::DECIMAL) * 100
        ELSE 0 END
    ) STORED,
    duplicate_rate DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN rows_attempted > 0
        THEN (rows_duplicates::DECIMAL / rows_attempted::DECIMAL) * 100
        ELSE 0 END
    ) STORED,
    error_rate DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN rows_attempted > 0
        THEN (rows_invalid::DECIMAL / rows_attempted::DECIMAL) * 100
        ELSE 0 END
    ) STORED,

    -- Performance metrics
    processing_duration_ms BIGINT, -- Processing time in milliseconds
    rows_per_second DECIMAL(10,2) GENERATED ALWAYS AS (
        CASE WHEN processing_duration_ms > 0
        THEN (rows_inserted::DECIMAL / (processing_duration_ms::DECIMAL / 1000))
        ELSE 0 END
    ) STORED,

    -- Data validation results
    null_count_violations INTEGER DEFAULT 0,
    constraint_violations INTEGER DEFAULT 0,
    data_type_violations INTEGER DEFAULT 0,
    business_rule_violations INTEGER DEFAULT 0,
    referential_integrity_violations INTEGER DEFAULT 0,

    -- Data range and distribution metrics
    min_date_value DATE,
    max_date_value DATE,
    avg_numeric_value DECIMAL(15,4), -- For key numeric fields
    outlier_count INTEGER DEFAULT 0,

    -- Quality flags (calculated from base columns, not generated columns)
    quality_level VARCHAR(20) GENERATED ALWAYS AS (
        CASE
            WHEN (CASE WHEN rows_attempted > 0 THEN (rows_invalid::DECIMAL / rows_attempted::DECIMAL) * 100 ELSE 0 END) <= 1
                AND (CASE WHEN rows_attempted > 0 THEN (rows_duplicates::DECIMAL / rows_attempted::DECIMAL) * 100 ELSE 0 END) <= 5 THEN 'EXCELLENT'
            WHEN (CASE WHEN rows_attempted > 0 THEN (rows_invalid::DECIMAL / rows_attempted::DECIMAL) * 100 ELSE 0 END) <= 3
                AND (CASE WHEN rows_attempted > 0 THEN (rows_duplicates::DECIMAL / rows_attempted::DECIMAL) * 100 ELSE 0 END) <= 10 THEN 'GOOD'
            WHEN (CASE WHEN rows_attempted > 0 THEN (rows_invalid::DECIMAL / rows_attempted::DECIMAL) * 100 ELSE 0 END) <= 5
                AND (CASE WHEN rows_attempted > 0 THEN (rows_duplicates::DECIMAL / rows_attempted::DECIMAL) * 100 ELSE 0 END) <= 15 THEN 'ACCEPTABLE'
            WHEN (CASE WHEN rows_attempted > 0 THEN (rows_invalid::DECIMAL / rows_attempted::DECIMAL) * 100 ELSE 0 END) <= 10
                AND (CASE WHEN rows_attempted > 0 THEN (rows_duplicates::DECIMAL / rows_attempted::DECIMAL) * 100 ELSE 0 END) <= 25 THEN 'POOR'
            ELSE 'CRITICAL'
        END
    ) STORED,

    has_critical_errors BOOLEAN GENERATED ALWAYS AS (
        CASE WHEN referential_integrity_violations > 0 OR
                  business_rule_violations > (rows_attempted * 0.1) OR
                  (CASE WHEN rows_attempted > 0 THEN (rows_invalid::DECIMAL / rows_attempted::DECIMAL) * 100 ELSE 0 END) > 10
        THEN TRUE ELSE FALSE END
    ) STORED,

    -- Error summary
    primary_error_types JSONB, -- Array of most common error types
    error_message_sample TEXT, -- Sample error message for debugging

    -- Additional metadata
    data_hash VARCHAR(64), -- Hash of the processed data chunk for verification
    processing_node VARCHAR(100), -- Which processing node handled this
    metadata JSONB -- Flexible field for additional metrics
);

-- Quality Assessment Summary table - aggregated quality metrics by table/timeframe
CREATE TABLE IF NOT EXISTS data_quality_summary (
    summary_id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Aggregation context
    target_table VARCHAR(100) NOT NULL,
    target_schema VARCHAR(50) DEFAULT 'nyc_taxi',
    summary_period VARCHAR(20) NOT NULL, -- 'hourly', 'daily', 'weekly', 'monthly'
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,

    -- Aggregated volume metrics
    total_operations INTEGER NOT NULL DEFAULT 0,
    total_rows_attempted BIGINT NOT NULL DEFAULT 0,
    total_rows_inserted BIGINT NOT NULL DEFAULT 0,
    total_rows_invalid BIGINT NOT NULL DEFAULT 0,
    total_rows_duplicates BIGINT NOT NULL DEFAULT 0,

    -- Aggregated quality metrics
    avg_success_rate DECIMAL(5,2),
    avg_error_rate DECIMAL(5,2),
    avg_duplicate_rate DECIMAL(5,2),

    -- Quality trends
    quality_trend VARCHAR(20), -- 'IMPROVING', 'STABLE', 'DEGRADING'
    quality_score DECIMAL(5,2), -- Composite quality score 0-100

    -- Alert flags
    quality_alerts JSONB, -- Array of quality alerts triggered

    -- Performance metrics
    avg_processing_speed DECIMAL(10,2), -- Average rows per second
    total_processing_time_ms BIGINT,

    UNIQUE(target_table, target_schema, summary_period, period_start)
);

-- Indexes for efficient data quality monitoring queries
CREATE INDEX IF NOT EXISTS idx_data_quality_monitor_monitored_at ON data_quality_monitor (monitored_at);
CREATE INDEX IF NOT EXISTS idx_data_quality_monitor_target_table ON data_quality_monitor (target_table, target_schema);
CREATE INDEX IF NOT EXISTS idx_data_quality_monitor_quality_level ON data_quality_monitor (quality_level);
CREATE INDEX IF NOT EXISTS idx_data_quality_monitor_source_file ON data_quality_monitor (source_file);
CREATE INDEX IF NOT EXISTS idx_data_quality_monitor_batch_id ON data_quality_monitor (batch_id);
CREATE INDEX IF NOT EXISTS idx_data_quality_monitor_critical_errors ON data_quality_monitor (has_critical_errors) WHERE has_critical_errors = true;
CREATE INDEX IF NOT EXISTS idx_data_quality_monitor_session_id ON data_quality_monitor (processing_session_id);

-- Summary table indexes
CREATE INDEX IF NOT EXISTS idx_data_quality_summary_table_period ON data_quality_summary (target_table, summary_period, period_start);
CREATE INDEX IF NOT EXISTS idx_data_quality_summary_quality_score ON data_quality_summary (quality_score);
CREATE INDEX IF NOT EXISTS idx_data_quality_summary_period_range ON data_quality_summary (period_start, period_end);

-- Data Quality Alert Thresholds Configuration table
CREATE TABLE IF NOT EXISTS data_quality_thresholds (
    threshold_id SERIAL PRIMARY KEY,
    target_table VARCHAR(100) NOT NULL,
    target_schema VARCHAR(50) DEFAULT 'nyc_taxi',

    -- Threshold definitions
    max_error_rate DECIMAL(5,2) DEFAULT 5.0,
    max_duplicate_rate DECIMAL(5,2) DEFAULT 15.0,
    min_success_rate DECIMAL(5,2) DEFAULT 95.0,
    max_processing_time_ms BIGINT DEFAULT 300000, -- 5 minutes

    -- Alert configuration
    alert_enabled BOOLEAN DEFAULT TRUE,
    alert_email_recipients TEXT[],
    alert_webhook_url VARCHAR(500),

    -- Threshold metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',

    UNIQUE(target_table, target_schema)
);

-- Insert default thresholds for key tables
INSERT INTO data_quality_thresholds (target_table, max_error_rate, max_duplicate_rate, min_success_rate) VALUES
('yellow_taxi_trips', 2.0, 5.0, 98.0),
('fact_taxi_trips', 1.0, 3.0, 99.0),
('taxi_zone_lookup', 0.0, 0.0, 100.0),
('taxi_zone_shapes', 0.0, 0.0, 100.0)
ON CONFLICT (target_table, target_schema) DO UPDATE SET
    max_error_rate = EXCLUDED.max_error_rate,
    max_duplicate_rate = EXCLUDED.max_duplicate_rate,
    min_success_rate = EXCLUDED.min_success_rate,
    updated_at = CURRENT_TIMESTAMP;

-- Taxi Zone Lookup table (complete reference data from NYC TLC)
CREATE TABLE IF NOT EXISTS taxi_zone_lookup (
    locationid INTEGER PRIMARY KEY,
    borough VARCHAR(50) NOT NULL,
    zone VARCHAR(100) NOT NULL,
    service_zone VARCHAR(50) NOT NULL
);

-- Taxi Zone Shapes table (geospatial data from NYC TLC)
-- Contains polygon geometries for each taxi zone
CREATE TABLE IF NOT EXISTS taxi_zone_shapes (
    objectid INTEGER PRIMARY KEY,
    locationid INTEGER NOT NULL,
    zone VARCHAR(100) NOT NULL,
    borough VARCHAR(50) NOT NULL,
    shape_leng DECIMAL(15,6),
    shape_area DECIMAL(15,6),
    geometry GEOMETRY(MULTIPOLYGON, 2263), -- NYC State Plane coordinate system
    FOREIGN KEY (locationid) REFERENCES taxi_zone_lookup(locationid)
);

-- Create spatial index for efficient geospatial queries
CREATE INDEX IF NOT EXISTS idx_taxi_zone_shapes_geometry ON taxi_zone_shapes USING GIST (geometry);

-- Rate Code Lookup table
CREATE TABLE IF NOT EXISTS rate_code_lookup (
    ratecodeid INTEGER PRIMARY KEY,
    rate_code_desc VARCHAR(50)
);

-- Payment Type Lookup table
CREATE TABLE IF NOT EXISTS payment_type_lookup (
    payment_type INTEGER PRIMARY KEY,
    payment_type_desc VARCHAR(50)
);

-- Vendor Lookup table
CREATE TABLE IF NOT EXISTS vendor_lookup (
    vendorid INTEGER PRIMARY KEY,
    vendor_name VARCHAR(100)
);

-- Data Processing Tracking table
-- Tracks which months have been successfully processed to prevent duplicates
CREATE TABLE IF NOT EXISTS data_processing_log (
    id SERIAL PRIMARY KEY,
    data_year INTEGER NOT NULL,
    data_month INTEGER NOT NULL,
    file_name VARCHAR(200) NOT NULL,
    records_loaded BIGINT NOT NULL DEFAULT 0,
    processing_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_completed_at TIMESTAMP,
    backfill_config VARCHAR(100),
    status VARCHAR(20) DEFAULT 'in_progress',
    CONSTRAINT unique_month_processing UNIQUE (data_year, data_month),
    CONSTRAINT valid_month CHECK (data_month BETWEEN 1 AND 12),
    CONSTRAINT valid_status CHECK (status IN ('in_progress', 'completed', 'failed'))
);

-- Insert reference data
INSERT INTO rate_code_lookup (ratecodeid, rate_code_desc) VALUES
(1, 'Standard rate'),
(2, 'JFK'),
(3, 'Newark'),
(4, 'Nassau or Westchester'),
(5, 'Negotiated fare'),
(6, 'Group ride')
ON CONFLICT (ratecodeid) DO UPDATE SET
    rate_code_desc = EXCLUDED.rate_code_desc;

INSERT INTO payment_type_lookup (payment_type, payment_type_desc) VALUES
(1, 'Credit card'),
(2, 'Cash'),
(3, 'No charge'),
(4, 'Dispute'),
(5, 'Unknown'),
(6, 'Voided trip')
ON CONFLICT (payment_type) DO UPDATE SET
    payment_type_desc = EXCLUDED.payment_type_desc;

INSERT INTO vendor_lookup (vendorid, vendor_name) VALUES
(1, 'Creative Mobile Technologies'),
(2, 'VeriFone Inc.')
ON CONFLICT (vendorid) DO UPDATE SET
    vendor_name = EXCLUDED.vendor_name;

-- Taxi zone data will be loaded from CSV and shapefile via Python script

-- Indexes for performance optimization on real NYC taxi data
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_pickup_datetime ON yellow_taxi_trips (tpep_pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_dropoff_datetime ON yellow_taxi_trips (tpep_dropoff_datetime);
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_pickup_location ON yellow_taxi_trips (pulocationid);
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_dropoff_location ON yellow_taxi_trips (dolocationid);
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_payment_type ON yellow_taxi_trips (payment_type);
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_vendor ON yellow_taxi_trips (vendorid);
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_trip_distance ON yellow_taxi_trips (trip_distance);
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_total_amount ON yellow_taxi_trips (total_amount);

-- Composite indexes for common analytical queries
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_datetime_vendor ON yellow_taxi_trips (tpep_pickup_datetime, vendorid);
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_location_datetime ON yellow_taxi_trips (pulocationid, tpep_pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_yellow_taxi_date_payment ON yellow_taxi_trips (DATE(tpep_pickup_datetime), payment_type);

-- Partitioning by month for better performance (if using PostgreSQL 10+)
-- This would be implemented when loading actual data by month

-- ================================================================================
-- PART 2: STAR SCHEMA DIMENSIONAL MODEL
-- ================================================================================

-- Date Dimension - Complete date hierarchy for time-based analysis
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_year INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,  -- 1=Sunday, 7=Saturday
    day_name VARCHAR(10) NOT NULL,
    week_of_year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER NOT NULL,
    season VARCHAR(10) NOT NULL
);

-- Time Dimension - Hour-level analysis with business rules
CREATE TABLE IF NOT EXISTS dim_time (
    time_key INTEGER PRIMARY KEY,
    hour_24 INTEGER NOT NULL,
    hour_12 INTEGER NOT NULL,
    am_pm VARCHAR(2) NOT NULL,
    hour_name VARCHAR(20) NOT NULL,
    is_rush_hour BOOLEAN NOT NULL,
    is_business_hours BOOLEAN NOT NULL,
    time_period VARCHAR(20) NOT NULL, -- Early Morning, Morning Rush, etc.
    minute INTEGER NOT NULL DEFAULT 0
);

-- Enhanced Location Dimension - Enriched with business classifications
CREATE TABLE IF NOT EXISTS dim_locations (
    location_key SERIAL PRIMARY KEY,
    locationid INTEGER NOT NULL,
    zone VARCHAR(100) NOT NULL,
    borough VARCHAR(50) NOT NULL,
    service_zone VARCHAR(50) NOT NULL,
    zone_type VARCHAR(20) NOT NULL, -- Airport, Manhattan Core, Outer Borough, etc.
    is_airport BOOLEAN NOT NULL DEFAULT FALSE,
    is_manhattan BOOLEAN NOT NULL DEFAULT FALSE,
    is_high_demand BOOLEAN NOT NULL DEFAULT FALSE,
    population_density VARCHAR(10), -- High, Medium, Low
    business_district BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(locationid)
);

-- Vendor Dimension - Enhanced with performance metrics placeholders
CREATE TABLE IF NOT EXISTS dim_vendor (
    vendor_key SERIAL PRIMARY KEY,
    vendorid INTEGER NOT NULL,
    vendor_name VARCHAR(100) NOT NULL,
    vendor_type VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    market_share_pct DECIMAL(5,2),
    avg_trip_rating DECIMAL(3,2),
    UNIQUE(vendorid)
);

-- Payment Type Dimension - Enhanced with processing characteristics
CREATE TABLE IF NOT EXISTS dim_payment_type (
    payment_type_key SERIAL PRIMARY KEY,
    payment_type INTEGER NOT NULL,
    payment_type_desc VARCHAR(50) NOT NULL,
    is_electronic BOOLEAN NOT NULL,
    allows_tips BOOLEAN NOT NULL,
    processing_fee_applies BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(payment_type)
);

-- Rate Code Dimension - Enhanced with zone applicability
CREATE TABLE IF NOT EXISTS dim_rate_code (
    rate_code_key SERIAL PRIMARY KEY,
    ratecodeid INTEGER NOT NULL,
    rate_code_desc VARCHAR(50) NOT NULL,
    is_metered BOOLEAN NOT NULL,
    is_airport_rate BOOLEAN NOT NULL DEFAULT FALSE,
    is_negotiated BOOLEAN NOT NULL DEFAULT FALSE,
    applies_to_all_zones BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE(ratecodeid)
);

-- ================================================================================
-- PARTITIONED FACT TABLE WITH STAR SCHEMA DESIGN
-- ================================================================================

-- Partitioned fact table by pickup date
CREATE TABLE IF NOT EXISTS fact_taxi_trips (
    trip_key BIGSERIAL,

    -- Foreign Keys to Dimensions
    pickup_date_key INTEGER,
    pickup_time_key INTEGER,
    dropoff_date_key INTEGER,
    dropoff_time_key INTEGER,
    pickup_location_key INTEGER,
    dropoff_location_key INTEGER,
    vendor_key INTEGER,
    payment_type_key INTEGER,
    rate_code_key INTEGER,

    -- Measures (Facts) - Updated precision to handle outliers
    trip_distance DECIMAL(12,2),
    trip_duration_minutes INTEGER,
    passenger_count INTEGER,
    fare_amount DECIMAL(10,2),
    extra DECIMAL(10,2),
    mta_tax DECIMAL(10,2),
    tip_amount DECIMAL(10,2),
    tolls_amount DECIMAL(10,2),
    improvement_surcharge DECIMAL(10,2),
    total_amount DECIMAL(12,2),
    congestion_surcharge DECIMAL(10,2),
    airport_fee DECIMAL(10,2),
    cbd_congestion_fee DECIMAL(10,2),

    -- Derived Measures
    base_fare DECIMAL(10,2),
    total_surcharges DECIMAL(10,2),
    tip_percentage DECIMAL(10,2),
    avg_speed_mph DECIMAL(10,2),
    revenue_per_mile DECIMAL(10,2),

    -- Flags for Analysis
    is_airport_trip BOOLEAN,
    is_cross_borough_trip BOOLEAN,
    is_cash_trip BOOLEAN,
    is_long_distance BOOLEAN,
    is_short_trip BOOLEAN,

    -- Original row reference
    original_row_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Partition key (must be included in primary key for partitioned tables)
    pickup_date DATE NOT NULL,

    -- Primary key including partition key
    PRIMARY KEY (trip_key, pickup_date)

) PARTITION BY RANGE (pickup_date);

-- ================================================================================
-- DIMENSION DATA POPULATION FUNCTIONS
-- ================================================================================

-- Function to populate dim_date
CREATE OR REPLACE FUNCTION populate_dim_date(start_date DATE, end_date DATE)
RETURNS void AS $$
DECLARE
    current_dt DATE;
    date_record RECORD;
BEGIN
    current_dt := start_date;

    WHILE current_dt <= end_date LOOP
        -- Calculate all date attributes
        INSERT INTO dim_date (
            date_key, full_date, year, quarter, month, month_name,
            day_of_month, day_of_year, day_of_week, day_name,
            week_of_year, is_weekend, is_holiday, fiscal_year,
            fiscal_quarter, season
        ) VALUES (
            TO_CHAR(current_dt, 'YYYYMMDD')::INTEGER,
            current_dt,
            EXTRACT(YEAR FROM current_dt),
            EXTRACT(QUARTER FROM current_dt),
            EXTRACT(MONTH FROM current_dt),
            TRIM(TO_CHAR(current_dt, 'Month')),
            EXTRACT(DAY FROM current_dt),
            EXTRACT(DOY FROM current_dt),
            EXTRACT(DOW FROM current_dt) + 1, -- Convert to 1-7 range
            TRIM(TO_CHAR(current_dt, 'Day')),
            EXTRACT(WEEK FROM current_dt),
            EXTRACT(DOW FROM current_dt) IN (0, 6), -- Weekend
            FALSE, -- Holiday detection can be enhanced
            CASE
                WHEN EXTRACT(MONTH FROM current_dt) >= 4 THEN EXTRACT(YEAR FROM current_dt)
                ELSE EXTRACT(YEAR FROM current_dt) - 1
            END, -- Fiscal year starts in April
            CASE
                WHEN EXTRACT(MONTH FROM current_dt) BETWEEN 4 AND 6 THEN 1
                WHEN EXTRACT(MONTH FROM current_dt) BETWEEN 7 AND 9 THEN 2
                WHEN EXTRACT(MONTH FROM current_dt) BETWEEN 10 AND 12 THEN 3
                ELSE 4
            END,
            CASE
                WHEN EXTRACT(MONTH FROM current_dt) IN (12, 1, 2) THEN 'Winter'
                WHEN EXTRACT(MONTH FROM current_dt) IN (3, 4, 5) THEN 'Spring'
                WHEN EXTRACT(MONTH FROM current_dt) IN (6, 7, 8) THEN 'Summer'
                ELSE 'Fall'
            END
        ) ON CONFLICT (date_key) DO NOTHING;

        current_dt := current_dt + 1;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function to populate dim_time
CREATE OR REPLACE FUNCTION populate_dim_time()
RETURNS void AS $$
DECLARE
    hour_val INTEGER;
BEGIN
    FOR hour_val IN 0..23 LOOP
        INSERT INTO dim_time (
            time_key, hour_24, hour_12, am_pm, hour_name,
            is_rush_hour, is_business_hours, time_period
        ) VALUES (
            hour_val,
            hour_val,
            CASE WHEN hour_val = 0 THEN 12
                 WHEN hour_val <= 12 THEN hour_val
                 ELSE hour_val - 12 END,
            CASE WHEN hour_val < 12 THEN 'AM' ELSE 'PM' END,
            CASE
                WHEN hour_val = 0 THEN 'Midnight'
                WHEN hour_val = 12 THEN 'Noon'
                WHEN hour_val < 12 THEN hour_val || ' AM'
                ELSE (hour_val - 12) || ' PM'
            END,
            hour_val IN (7, 8, 9, 17, 18, 19), -- Rush hours
            hour_val BETWEEN 9 AND 17, -- Business hours
            CASE
                WHEN hour_val BETWEEN 0 AND 5 THEN 'Late Night'
                WHEN hour_val BETWEEN 6 AND 9 THEN 'Morning Rush'
                WHEN hour_val BETWEEN 10 AND 16 THEN 'Midday'
                WHEN hour_val BETWEEN 17 AND 19 THEN 'Evening Rush'
                WHEN hour_val BETWEEN 20 AND 23 THEN 'Evening'
            END
        ) ON CONFLICT (time_key) DO NOTHING;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- AUTOMATED PARTITION CREATION FUNCTIONS
-- ================================================================================

-- Function to create a monthly partition
CREATE OR REPLACE FUNCTION create_monthly_partition(target_date DATE)
RETURNS text AS $$
DECLARE
    partition_name text;
    start_date date;
    end_date date;
    sql_cmd text;
BEGIN
    -- Calculate partition boundaries
    start_date := date_trunc('month', target_date);
    end_date := start_date + interval '1 month';
    partition_name := 'fact_taxi_trips_' || to_char(start_date, 'YYYY_MM');

    -- Check if partition already exists
    IF EXISTS (
        SELECT 1 FROM pg_tables
        WHERE schemaname = 'nyc_taxi'
        AND tablename = partition_name
    ) THEN
        RETURN 'Partition ' || partition_name || ' already exists';
    END IF;

    -- Create partition
    sql_cmd := format(
        'CREATE TABLE nyc_taxi.%I PARTITION OF nyc_taxi.fact_taxi_trips
         FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date
    );

    EXECUTE sql_cmd;

    -- Add check constraint for better query planning
    sql_cmd := format(
        'ALTER TABLE nyc_taxi.%I ADD CONSTRAINT %I_pickup_date_check
         CHECK (pickup_date >= %L AND pickup_date < %L)',
        partition_name, partition_name, start_date, end_date
    );

    EXECUTE sql_cmd;

    RETURN 'Created partition: ' || partition_name;
END;
$$ LANGUAGE plpgsql;

-- Function to create partitions for a date range
CREATE OR REPLACE FUNCTION create_partitions_for_range(
    start_date DATE,
    end_date DATE
)
RETURNS text[] AS $$
DECLARE
    current_dt DATE;
    results text[] := ARRAY[]::text[];
    result_msg text;
BEGIN
    current_dt := date_trunc('month', start_date);

    WHILE current_dt <= end_date LOOP
        SELECT create_monthly_partition(current_dt) INTO result_msg;
        results := results || result_msg;
        current_dt := current_dt + interval '1 month';
    END LOOP;

    RETURN results;
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- PERFORMANCE INDEXING FUNCTIONS
-- ================================================================================

-- Function to create indexes on all existing partitions
CREATE OR REPLACE FUNCTION create_partition_indexes()
RETURNS text[] AS $$
DECLARE
    partition_record RECORD;
    results text[] := ARRAY[]::text[];
    sql_cmd text;
    index_name text;
BEGIN
    -- Loop through all fact table partitions
    FOR partition_record IN
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname = 'nyc_taxi'
        AND tablename LIKE 'fact_taxi_trips_____%%'
    LOOP
        -- 1. Primary performance index: pickup_date + location
        index_name := partition_record.tablename || '_pickup_date_location_idx';
        sql_cmd := format('CREATE INDEX IF NOT EXISTS %I ON nyc_taxi.%I (pickup_date, pickup_location_key)',
                         index_name, partition_record.tablename);
        EXECUTE sql_cmd;
        results := results || ('Created: ' || index_name);

        -- 2. Time-based analysis index
        index_name := partition_record.tablename || '_pickup_time_idx';
        sql_cmd := format('CREATE INDEX IF NOT EXISTS %I ON nyc_taxi.%I (pickup_time_key)',
                         index_name, partition_record.tablename);
        EXECUTE sql_cmd;
        results := results || ('Created: ' || index_name);

        -- 3. Revenue analysis covering index
        index_name := partition_record.tablename || '_revenue_covering_idx';
        sql_cmd := format('CREATE INDEX IF NOT EXISTS %I ON nyc_taxi.%I (pickup_location_key, payment_type_key) INCLUDE (total_amount, tip_amount, trip_distance)',
                         index_name, partition_record.tablename);
        EXECUTE sql_cmd;
        results := results || ('Created: ' || index_name);

        -- 4. Location analytics covering index
        index_name := partition_record.tablename || '_location_analytics_covering_idx';
        sql_cmd := format('CREATE INDEX IF NOT EXISTS %I ON nyc_taxi.%I (pickup_location_key, dropoff_location_key)
                          INCLUDE (trip_distance, total_amount, tip_amount, passenger_count, trip_duration_minutes)',
                         index_name, partition_record.tablename);
        EXECUTE sql_cmd;
        results := results || ('Created: ' || index_name);

    END LOOP;

    RETURN results;
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- INITIALIZATION AND SETUP
-- ================================================================================

-- Populate date dimension for taxi data range (2009-2025)
SELECT populate_dim_date('2009-01-01'::DATE, '2025-12-31'::DATE);

-- Populate time dimension
SELECT populate_dim_time();

-- Create partitions for the full historical data range (2009-2025)
SELECT create_partitions_for_range('2009-01-01'::DATE, '2025-12-31'::DATE);

-- Enable constraint exclusion for better partition pruning
SET constraint_exclusion = partition;

-- ================================================================================
-- COMMENTS AND DOCUMENTATION
-- ================================================================================

COMMENT ON TABLE fact_taxi_trips IS 'Partitioned star schema fact table with foreign keys to all dimensions and comprehensive measures';
COMMENT ON TABLE dim_date IS 'Date dimension with complete date hierarchy for time-based analysis';
COMMENT ON TABLE dim_time IS 'Time dimension with hour-level analysis and business rules';
COMMENT ON TABLE dim_locations IS 'Enhanced location dimension with business classifications';
COMMENT ON TABLE dim_vendor IS 'Vendor dimension with performance metrics placeholders';
COMMENT ON TABLE dim_payment_type IS 'Payment type dimension with processing characteristics';
COMMENT ON TABLE dim_rate_code IS 'Rate code dimension with zone applicability flags';
COMMENT ON TABLE yellow_taxi_trips_invalid IS 'Stores rows that failed validation during batch ingestion for data quality monitoring and debugging';
COMMENT ON TABLE data_quality_monitor IS 'Comprehensive data quality monitoring for all table operations with real-time metrics and automated quality scoring';
COMMENT ON TABLE data_quality_summary IS 'Aggregated quality metrics by table and time period for trend analysis and reporting';
COMMENT ON TABLE data_quality_thresholds IS 'Configurable quality thresholds and alerting rules for each table';