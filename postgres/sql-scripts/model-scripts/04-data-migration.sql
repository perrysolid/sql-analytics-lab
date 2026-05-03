-- ================================================================================
-- Phase 4: Data Migration Script
-- Migrate data from normalized schema to star schema with partitioning
-- This script transforms and loads data into the new dimensional model
-- ================================================================================

-- Set schema context
SET search_path = nyc_taxi, public;

-- ================================================================================
-- PRE-MIGRATION VALIDATION
-- ================================================================================

-- Function to validate dimension data completeness
CREATE OR REPLACE FUNCTION validate_dimensions()
RETURNS TABLE(dimension_name text, record_count bigint, status text) AS $$
BEGIN
    RETURN QUERY
    SELECT 'dim_date'::text, COUNT(*), 'OK'::text FROM dim_date
    UNION ALL
    SELECT 'dim_time'::text, COUNT(*), 'OK'::text FROM dim_time
    UNION ALL
    SELECT 'dim_locations'::text, COUNT(*), 'OK'::text FROM dim_locations
    UNION ALL
    SELECT 'dim_vendor'::text, COUNT(*), 'OK'::text FROM dim_vendor
    UNION ALL
    SELECT 'dim_payment_type'::text, COUNT(*), 'OK'::text FROM dim_payment_type
    UNION ALL
    SELECT 'dim_rate_code'::text, COUNT(*), 'OK'::text FROM dim_rate_code;
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- DATA MIGRATION FUNCTION
-- ================================================================================

-- Main migration function with chunked processing
CREATE OR REPLACE FUNCTION migrate_taxi_data_to_star_schema(
    chunk_size INTEGER DEFAULT 50000,
    start_date DATE DEFAULT NULL,
    end_date DATE DEFAULT NULL
)
RETURNS TEXT AS $$
DECLARE
    total_rows BIGINT;
    processed_rows BIGINT := 0;
    chunk_start BIGINT := 0;
    migration_start TIMESTAMP;
    chunk_start_time TIMESTAMP;
    progress_msg TEXT;
    date_filter TEXT := '';
BEGIN
    migration_start := CURRENT_TIMESTAMP;

    -- Set date filter if provided
    IF start_date IS NOT NULL AND end_date IS NOT NULL THEN
        date_filter := format(' WHERE DATE(tpep_pickup_datetime) BETWEEN %L AND %L', start_date, end_date);
    END IF;

    -- Get total count for progress tracking
    EXECUTE format('SELECT COUNT(*) FROM yellow_taxi_trips %s', date_filter) INTO total_rows;

    RAISE NOTICE 'Starting migration of % rows in chunks of %', total_rows, chunk_size;

    -- Process data in chunks
    WHILE processed_rows < total_rows LOOP
        chunk_start_time := CURRENT_TIMESTAMP;

        -- Insert chunk with full transformation
        EXECUTE format('
            INSERT INTO fact_taxi_trips (
                pickup_date_key, pickup_time_key, dropoff_date_key, dropoff_time_key,
                pickup_location_key, dropoff_location_key, vendor_key,
                payment_type_key, rate_code_key, pickup_date,
                trip_distance, trip_duration_minutes, passenger_count,
                fare_amount, extra, mta_tax, tip_amount, tolls_amount,
                improvement_surcharge, total_amount, congestion_surcharge,
                airport_fee, cbd_congestion_fee, base_fare, total_surcharges,
                tip_percentage, avg_speed_mph, revenue_per_mile,
                is_airport_trip, is_cross_borough_trip, is_cash_trip,
                is_long_distance, is_short_trip, original_row_hash
            )
            SELECT
                -- Date and time keys
                TO_CHAR(DATE(yt.tpep_pickup_datetime), ''YYYYMMDD'')::INTEGER as pickup_date_key,
                EXTRACT(HOUR FROM yt.tpep_pickup_datetime)::INTEGER as pickup_time_key,
                TO_CHAR(DATE(yt.tpep_dropoff_datetime), ''YYYYMMDD'')::INTEGER as dropoff_date_key,
                EXTRACT(HOUR FROM yt.tpep_dropoff_datetime)::INTEGER as dropoff_time_key,

                -- Location keys
                dl_pickup.location_key as pickup_location_key,
                dl_dropoff.location_key as dropoff_location_key,

                -- Other dimension keys
                dv.vendor_key,
                dpt.payment_type_key,
                drc.rate_code_key,

                -- Partition key
                DATE(yt.tpep_pickup_datetime) as pickup_date,

                -- Direct measures
                yt.trip_distance,
                EXTRACT(EPOCH FROM (yt.tpep_dropoff_datetime - yt.tpep_pickup_datetime))::INTEGER / 60 as trip_duration_minutes,
                COALESCE(yt.passenger_count::INTEGER, 1) as passenger_count,
                yt.fare_amount,
                yt.extra,
                yt.mta_tax,
                yt.tip_amount,
                yt.tolls_amount,
                yt.improvement_surcharge,
                yt.total_amount,
                yt.congestion_surcharge,
                yt.airport_fee,
                yt.cbd_congestion_fee,

                -- Calculated measures
                yt.fare_amount + yt.extra as base_fare,
                yt.mta_tax + yt.improvement_surcharge + COALESCE(yt.congestion_surcharge, 0) +
                    COALESCE(yt.airport_fee, 0) + COALESCE(yt.cbd_congestion_fee, 0) as total_surcharges,

                -- Tip percentage
                CASE
                    WHEN yt.fare_amount > 0 THEN ROUND(100.0 * yt.tip_amount / yt.fare_amount, 2)
                    ELSE 0
                END as tip_percentage,

                -- Average speed
                CASE
                    WHEN yt.trip_distance > 0 AND
                         EXTRACT(EPOCH FROM (yt.tpep_dropoff_datetime - yt.tpep_pickup_datetime)) > 0
                    THEN ROUND(
                        yt.trip_distance / (EXTRACT(EPOCH FROM (yt.tpep_dropoff_datetime - yt.tpep_pickup_datetime)) / 3600.0),
                        2
                    )
                    ELSE NULL
                END as avg_speed_mph,

                -- Revenue per mile
                CASE
                    WHEN yt.trip_distance > 0 THEN ROUND(yt.total_amount / yt.trip_distance, 2)
                    ELSE NULL
                END as revenue_per_mile,

                -- Business flags
                (dl_pickup.is_airport OR dl_dropoff.is_airport) as is_airport_trip,
                (dl_pickup.borough != dl_dropoff.borough) as is_cross_borough_trip,
                (yt.payment_type = 2) as is_cash_trip,
                (yt.trip_distance > 10) as is_long_distance,
                (yt.trip_distance < 1) as is_short_trip,

                -- Original reference
                yt.row_hash as original_row_hash

            FROM yellow_taxi_trips yt
            LEFT JOIN dim_locations dl_pickup ON yt.pulocationid = dl_pickup.locationid
            LEFT JOIN dim_locations dl_dropoff ON yt.dolocationid = dl_dropoff.locationid
            LEFT JOIN dim_vendor dv ON yt.vendorid = dv.vendorid
            LEFT JOIN dim_payment_type dpt ON yt.payment_type = dpt.payment_type
            LEFT JOIN dim_rate_code drc ON yt.ratecodeid::INTEGER = drc.ratecodeid

            %s  -- date filter placeholder

            ORDER BY yt.tpep_pickup_datetime
            OFFSET %s LIMIT %s
        ', date_filter, processed_rows, chunk_size);

        processed_rows := processed_rows + chunk_size;

        -- Progress reporting
        progress_msg := format(
            'Processed %s/%s rows (%.1f%%) - Chunk time: %s',
            LEAST(processed_rows, total_rows),
            total_rows,
            100.0 * LEAST(processed_rows, total_rows) / total_rows,
            CURRENT_TIMESTAMP - chunk_start_time
        );

        RAISE NOTICE '%', progress_msg;

        -- Commit chunk (if in a transaction block, this would be SAVEPOINT)
        -- COMMIT; -- Uncomment if running outside transaction block
    END LOOP;

    -- Final statistics update
    ANALYZE fact_taxi_trips;

    RETURN format(
        'Migration completed successfully! Processed %s rows in %s',
        total_rows,
        CURRENT_TIMESTAMP - migration_start
    );
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- INCREMENTAL MIGRATION FUNCTION
-- ================================================================================

-- Function for incremental updates (new data only)
CREATE OR REPLACE FUNCTION incremental_migrate_taxi_data(
    target_date DATE DEFAULT CURRENT_DATE - 1
)
RETURNS TEXT AS $$
DECLARE
    new_rows BIGINT;
    start_time TIMESTAMP;
BEGIN
    start_time := CURRENT_TIMESTAMP;

    -- Check if we already have data for this date
    IF EXISTS (
        SELECT 1 FROM fact_taxi_trips
        WHERE pickup_date = target_date
        LIMIT 1
    ) THEN
        RETURN format('Data for %s already exists in fact table', target_date);
    END IF;

    -- Migrate single day
    SELECT migrate_taxi_data_to_star_schema(
        50000,  -- chunk_size
        target_date,
        target_date
    ) INTO new_rows;

    RETURN format(
        'Incremental migration for %s completed in %s',
        target_date,
        CURRENT_TIMESTAMP - start_time
    );
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- DATA QUALITY VALIDATION
-- ================================================================================

-- Function to validate migrated data
CREATE OR REPLACE FUNCTION validate_migration()
RETURNS TABLE(
    check_name TEXT,
    original_value BIGINT,
    migrated_value BIGINT,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    -- Total record count
    WITH counts AS (
        SELECT COUNT(*) as orig_count FROM yellow_taxi_trips
    ), fact_counts AS (
        SELECT COUNT(*) as fact_count FROM fact_taxi_trips
    )
    SELECT
        'Total Records'::TEXT,
        c.orig_count,
        fc.fact_count,
        CASE WHEN c.orig_count = fc.fact_count THEN 'PASS' ELSE 'FAIL' END
    FROM counts c, fact_counts fc

    UNION ALL

    -- Revenue totals
    WITH revenue AS (
        SELECT ROUND(SUM(total_amount)::NUMERIC, 2) as orig_revenue FROM yellow_taxi_trips
    ), fact_revenue AS (
        SELECT ROUND(SUM(total_amount)::NUMERIC, 2) as fact_revenue FROM fact_taxi_trips
    )
    SELECT
        'Total Revenue'::TEXT,
        r.orig_revenue::BIGINT,
        fr.fact_revenue::BIGINT,
        CASE WHEN ABS(r.orig_revenue - fr.fact_revenue) < 1 THEN 'PASS' ELSE 'FAIL' END
    FROM revenue r, fact_revenue fr

    UNION ALL

    -- Trip distance totals
    WITH distance AS (
        SELECT ROUND(SUM(trip_distance)::NUMERIC, 2) as orig_distance FROM yellow_taxi_trips
    ), fact_distance AS (
        SELECT ROUND(SUM(trip_distance)::NUMERIC, 2) as fact_distance FROM fact_taxi_trips
    )
    SELECT
        'Total Distance'::TEXT,
        d.orig_distance::BIGINT,
        fd.fact_distance::BIGINT,
        CASE WHEN ABS(d.orig_distance - fd.fact_distance) < 1 THEN 'PASS' ELSE 'FAIL' END
    FROM distance d, fact_distance fd;

END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- MIGRATION ROLLBACK FUNCTION
-- ================================================================================

-- Function to rollback migration (truncate fact table)
CREATE OR REPLACE FUNCTION rollback_migration()
RETURNS TEXT AS $$
DECLARE
    partition_record RECORD;
    sql_cmd TEXT;
BEGIN
    -- Truncate all partitions
    FOR partition_record IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'nyc_taxi'
        AND tablename LIKE 'fact_taxi_trips_____%%'
    LOOP
        sql_cmd := format('TRUNCATE TABLE nyc_taxi.%I', partition_record.tablename);
        EXECUTE sql_cmd;
    END LOOP;

    -- Reset partition statistics
    DELETE FROM partition_management;

    RETURN 'Migration rollback completed - all fact table partitions truncated';
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- USAGE EXAMPLES AND INSTRUCTIONS
-- ================================================================================

/*
MIGRATION EXECUTION EXAMPLES:

1. VALIDATE DIMENSIONS FIRST:
   SELECT * FROM validate_dimensions();

2. FULL MIGRATION (ALL DATA):
   SELECT migrate_taxi_data_to_star_schema(50000);

3. PARTIAL MIGRATION (SPECIFIC DATE RANGE):
   SELECT migrate_taxi_data_to_star_schema(50000, '2024-01-01', '2024-01-31');

4. INCREMENTAL MIGRATION (DAILY):
   SELECT incremental_migrate_taxi_data('2024-01-15');

5. VALIDATE MIGRATION:
   SELECT * FROM validate_migration();

6. ROLLBACK IF NEEDED:
   SELECT rollback_migration();

PERFORMANCE TIPS:
- Use smaller chunk_size (10000-25000) if experiencing memory issues
- Run migration during off-peak hours
- Monitor disk space during migration
- Consider parallel execution for different date ranges

MONITORING MIGRATION:
- Watch PostgreSQL logs for progress notices
- Monitor partition_management table for statistics
- Check fact_taxi_trips row counts per partition
*/

-- ================================================================================
-- AUTOMATIC MAINTENANCE SETUP
-- ================================================================================

-- Function to set up automatic daily migration (for new data)
CREATE OR REPLACE FUNCTION setup_daily_migration()
RETURNS TEXT AS $$
BEGIN
    -- This would typically be set up as a cron job or scheduled task
    -- Example cron entry: 0 2 * * * psql -d playground -c "SELECT incremental_migrate_taxi_data();"

    RETURN 'Set up daily migration job to run: SELECT incremental_migrate_taxi_data();';
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- INITIAL VALIDATION
-- ================================================================================

-- Show dimension validation results
SELECT * FROM validate_dimensions();

-- ================================================================================
-- COMMENTS
-- ================================================================================

COMMENT ON FUNCTION migrate_taxi_data_to_star_schema(INTEGER, DATE, DATE) IS 'Main migration function with chunked processing and full data transformation';
COMMENT ON FUNCTION incremental_migrate_taxi_data(DATE) IS 'Incremental migration for daily data loads';
COMMENT ON FUNCTION validate_migration() IS 'Validates data consistency between original and migrated data';
COMMENT ON FUNCTION rollback_migration() IS 'Rollback function to truncate all fact table partitions';

-- Show ready status
SELECT
    'Data migration script ready!' as status,
    'Run: SELECT migrate_taxi_data_to_star_schema(50000);' as next_step;