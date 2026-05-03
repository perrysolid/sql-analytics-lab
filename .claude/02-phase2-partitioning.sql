-- ================================================================================
-- Phase 2: Partitioning Implementation
-- Create scalable architecture foundation with automated monthly partitioning
-- Based on Interview Question 13: Database Partitioning Strategy
-- ================================================================================

-- Set schema context
SET search_path = nyc_taxi, public;

-- ================================================================================
-- PARTITIONED FACT TABLE
-- ================================================================================

-- Drop the existing fact table if it exists (for clean implementation)
-- In production, you would migrate data instead
DROP TABLE IF EXISTS fact_taxi_trips CASCADE;

-- Create partitioned fact table by pickup date
CREATE TABLE fact_taxi_trips (
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

    -- Measures (Facts)
    trip_distance DECIMAL(8,2),
    trip_duration_minutes INTEGER,
    passenger_count INTEGER,
    fare_amount DECIMAL(8,2),
    extra DECIMAL(8,2),
    mta_tax DECIMAL(8,2),
    tip_amount DECIMAL(8,2),
    tolls_amount DECIMAL(8,2),
    improvement_surcharge DECIMAL(8,2),
    total_amount DECIMAL(8,2),
    congestion_surcharge DECIMAL(8,2),
    airport_fee DECIMAL(8,2),
    cbd_congestion_fee DECIMAL(8,2),

    -- Derived Measures
    base_fare DECIMAL(8,2),
    total_surcharges DECIMAL(8,2),
    tip_percentage DECIMAL(5,2),
    avg_speed_mph DECIMAL(5,2),
    revenue_per_mile DECIMAL(8,2),

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
    current_date DATE;
    results text[] := ARRAY[]::text[];
    result_msg text;
BEGIN
    current_date := date_trunc('month', start_date);

    WHILE current_date <= end_date LOOP
        SELECT create_monthly_partition(current_date) INTO result_msg;
        results := results || result_msg;
        current_date := current_date + interval '1 month';
    END LOOP;

    RETURN results;
END;
$$ LANGUAGE plpgsql;

-- Function to drop old partitions (for maintenance)
CREATE OR REPLACE FUNCTION drop_old_partitions(months_to_keep INTEGER DEFAULT 24)
RETURNS text[] AS $$
DECLARE
    partition_record RECORD;
    cutoff_date DATE;
    results text[] := ARRAY[]::text[];
    sql_cmd text;
BEGIN
    cutoff_date := date_trunc('month', CURRENT_DATE) - (months_to_keep || ' months')::interval;

    FOR partition_record IN
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname = 'nyc_taxi'
        AND tablename LIKE 'fact_taxi_trips_____%%'
        AND tablename < 'fact_taxi_trips_' || to_char(cutoff_date, 'YYYY_MM')
    LOOP
        sql_cmd := format('DROP TABLE %I.%I',
                         partition_record.schemaname,
                         partition_record.tablename);
        EXECUTE sql_cmd;
        results := results || ('Dropped partition: ' || partition_record.tablename);
    END LOOP;

    RETURN results;
END;
$$ LANGUAGE plpgsql;

-- Function for automatic partition maintenance
CREATE OR REPLACE FUNCTION maintain_partitions()
RETURNS text AS $$
DECLARE
    results text[] := ARRAY[]::text[];
    future_results text[];
    cleanup_results text[];
BEGIN
    -- Create partitions for next 3 months
    SELECT create_partitions_for_range(
        CURRENT_DATE,
        CURRENT_DATE + interval '3 months'
    ) INTO future_results;

    results := results || future_results;

    -- Optional: Clean up old partitions (commented out for safety)
    -- Uncomment and adjust retention policy as needed
    -- SELECT drop_old_partitions(24) INTO cleanup_results;
    -- results := results || cleanup_results;

    RETURN array_to_string(results, E'\n');
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- PARTITION MANAGEMENT TABLE
-- ================================================================================

-- Table to track partition information and maintenance
CREATE TABLE partition_management (
    id SERIAL PRIMARY KEY,
    partition_name VARCHAR(100) NOT NULL,
    partition_schema VARCHAR(50) NOT NULL DEFAULT 'nyc_taxi',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    row_count BIGINT DEFAULT 0,
    last_analyzed TIMESTAMP,
    notes TEXT,
    UNIQUE(partition_name, partition_schema)
);

-- Function to update partition statistics
CREATE OR REPLACE FUNCTION update_partition_stats()
RETURNS void AS $$
DECLARE
    partition_record RECORD;
    row_count BIGINT;
    sql_cmd text;
BEGIN
    FOR partition_record IN
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname = 'nyc_taxi'
        AND tablename LIKE 'fact_taxi_trips_____%%'
    LOOP
        -- Get row count
        sql_cmd := format('SELECT COUNT(*) FROM %I.%I',
                         partition_record.schemaname,
                         partition_record.tablename);
        EXECUTE sql_cmd INTO row_count;

        -- Update or insert partition stats
        INSERT INTO partition_management (
            partition_name, partition_schema, start_date, end_date, row_count, last_analyzed
        )
        SELECT
            partition_record.tablename,
            partition_record.schemaname,
            -- Extract dates from partition name
            to_date(substring(partition_record.tablename from 'fact_taxi_trips_(\d{4}_\d{2})'), 'YYYY_MM'),
            to_date(substring(partition_record.tablename from 'fact_taxi_trips_(\d{4}_\d{2})'), 'YYYY_MM') + interval '1 month',
            row_count,
            CURRENT_TIMESTAMP
        ON CONFLICT (partition_name, partition_schema)
        DO UPDATE SET
            row_count = EXCLUDED.row_count,
            last_analyzed = EXCLUDED.last_analyzed;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- CREATE INITIAL PARTITIONS
-- ================================================================================

-- Create partitions for the data range we have (2020-2025)
SELECT create_partitions_for_range('2020-01-01'::DATE, '2025-12-31'::DATE);

-- ================================================================================
-- PARTITION-AWARE FOREIGN KEY CONSTRAINTS
-- ================================================================================

-- Note: PostgreSQL doesn't support foreign keys on partitioned tables directly
-- We'll add these constraints to individual partitions via a function

CREATE OR REPLACE FUNCTION add_constraints_to_partition(partition_name text)
RETURNS void AS $$
DECLARE
    sql_cmd text;
BEGIN
    -- Add foreign key constraints to the partition
    sql_cmd := format('
        ALTER TABLE nyc_taxi.%I
        ADD CONSTRAINT %I_pickup_date_key_fk
            FOREIGN KEY (pickup_date_key) REFERENCES nyc_taxi.dim_date(date_key),
        ADD CONSTRAINT %I_pickup_time_key_fk
            FOREIGN KEY (pickup_time_key) REFERENCES nyc_taxi.dim_time(time_key),
        ADD CONSTRAINT %I_pickup_location_key_fk
            FOREIGN KEY (pickup_location_key) REFERENCES nyc_taxi.dim_locations(location_key),
        ADD CONSTRAINT %I_dropoff_location_key_fk
            FOREIGN KEY (dropoff_location_key) REFERENCES nyc_taxi.dim_locations(location_key),
        ADD CONSTRAINT %I_vendor_key_fk
            FOREIGN KEY (vendor_key) REFERENCES nyc_taxi.dim_vendor(vendor_key),
        ADD CONSTRAINT %I_payment_type_key_fk
            FOREIGN KEY (payment_type_key) REFERENCES nyc_taxi.dim_payment_type(payment_type_key),
        ADD CONSTRAINT %I_rate_code_key_fk
            FOREIGN KEY (rate_code_key) REFERENCES nyc_taxi.dim_rate_code(rate_code_key)',
        partition_name, partition_name, partition_name, partition_name,
        partition_name, partition_name, partition_name, partition_name
    );

    EXECUTE sql_cmd;
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- PARTITION PRUNING OPTIMIZATION
-- ================================================================================

-- Enable constraint exclusion for better partition pruning
SET constraint_exclusion = partition;

-- Create a view that demonstrates partition pruning
CREATE OR REPLACE VIEW partition_pruning_demo AS
SELECT
    schemaname,
    tablename as partition_name,
    -- Extract date from partition name for demonstration
    to_date(substring(tablename from 'fact_taxi_trips_(\d{4}_\d{2})'), 'YYYY_MM') as partition_month
FROM pg_tables
WHERE schemaname = 'nyc_taxi'
AND tablename LIKE 'fact_taxi_trips_____%%'
ORDER BY partition_month;

-- ================================================================================
-- EXAMPLE QUERIES FOR PARTITION TESTING
-- ================================================================================

-- Function to demonstrate partition pruning
CREATE OR REPLACE FUNCTION explain_partition_pruning(
    start_date DATE,
    end_date DATE
)
RETURNS TABLE(query_plan text) AS $$
DECLARE
    sql_cmd text;
BEGIN
    sql_cmd := format('
        EXPLAIN (FORMAT TEXT, BUFFERS, ANALYZE FALSE)
        SELECT COUNT(*), AVG(total_amount)
        FROM fact_taxi_trips
        WHERE pickup_date BETWEEN %L AND %L',
        start_date, end_date
    );

    RETURN QUERY EXECUTE sql_cmd;
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- MAINTENANCE PROCEDURES
-- ================================================================================

-- Create a procedure for daily partition maintenance
CREATE OR REPLACE FUNCTION daily_partition_maintenance()
RETURNS text AS $$
DECLARE
    maintenance_result text;
    stats_result text;
BEGIN
    -- Maintain partitions (create future ones)
    SELECT maintain_partitions() INTO maintenance_result;

    -- Update partition statistics
    PERFORM update_partition_stats();

    -- Return summary
    RETURN 'Partition maintenance completed: ' || E'\n' || maintenance_result;
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- COMMENTS AND DOCUMENTATION
-- ================================================================================

COMMENT ON TABLE fact_taxi_trips IS 'Partitioned fact table using range partitioning by pickup_date for optimal performance on time-based queries';
COMMENT ON TABLE partition_management IS 'Tracks partition metadata, statistics, and maintenance history';

COMMENT ON FUNCTION create_monthly_partition(DATE) IS 'Creates a monthly partition for the specified date';
COMMENT ON FUNCTION maintain_partitions() IS 'Automated partition maintenance - creates future partitions and optionally cleans old ones';
COMMENT ON FUNCTION update_partition_stats() IS 'Updates row counts and analysis timestamps for all partitions';
COMMENT ON FUNCTION explain_partition_pruning(DATE, DATE) IS 'Demonstrates partition pruning with EXPLAIN for a date range query';

-- ================================================================================
-- INITIAL SETUP COMPLETION
-- ================================================================================

-- Run initial partition statistics update
SELECT update_partition_stats();

-- Display created partitions
SELECT
    partition_name,
    start_date,
    end_date,
    'Ready for data loading' as status
FROM partition_management
ORDER BY start_date;