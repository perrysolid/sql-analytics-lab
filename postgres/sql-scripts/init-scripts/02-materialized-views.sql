-- Materialized views: pre-aggregated trip metrics for BigQuery-like response times
-- Compresses ~19M rows into compact summaries queryable in single-digit milliseconds.
--
-- Three views covering all Sample Analytics Queries:
--   trip_hourly_summary   — queries 1, 5, 6, 9, 10, 11, 12
--   trip_location_summary — queries 3, 4
--   trip_distance_summary — query 8
--
-- Refresh all after loading new data:
--   REFRESH MATERIALIZED VIEW CONCURRENTLY nyc_taxi.trip_hourly_summary;
--   REFRESH MATERIALIZED VIEW CONCURRENTLY nyc_taxi.trip_location_summary;
--   REFRESH MATERIALIZED VIEW CONCURRENTLY nyc_taxi.trip_distance_summary;

-- =============================================================================
-- 1. HOURLY SUMMARY — groups by date, hour, day-of-week, payment type
--    Covers: trip volume by hour, basic overview, payment analysis,
--            daily patterns, rush hour, tip analysis, weekend vs weekday
-- =============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS nyc_taxi.trip_hourly_summary AS
SELECT
    DATE(tpep_pickup_datetime) as trip_date,
    EXTRACT(HOUR FROM tpep_pickup_datetime)::int as pickup_hour,
    EXTRACT(DOW FROM tpep_pickup_datetime)::int as day_of_week,
    payment_type,
    COUNT(*) as trip_count,
    SUM(trip_distance) as total_distance,
    SUM(fare_amount) as total_fare,
    SUM(tip_amount) as total_tip,
    SUM(total_amount) as total_amount,
    COUNT(CASE WHEN tip_amount > 0 THEN 1 END) as trips_with_tips,
    MIN(tpep_pickup_datetime) as min_pickup,
    MAX(tpep_pickup_datetime) as max_pickup
FROM nyc_taxi.yellow_taxi_trips
GROUP BY 1, 2, 3, 4;

CREATE UNIQUE INDEX IF NOT EXISTS idx_trip_hourly_summary_pk
    ON nyc_taxi.trip_hourly_summary (trip_date, pickup_hour, day_of_week, payment_type);

-- =============================================================================
-- 2. LOCATION SUMMARY — groups by pickup/dropoff location and payment type
--    Covers: cross-borough trip analysis, payment patterns by borough
-- =============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS nyc_taxi.trip_location_summary AS
SELECT
    pulocationid,
    dolocationid,
    payment_type,
    COUNT(*) as trip_count,
    SUM(fare_amount) as total_fare,
    SUM(total_amount) as total_amount
FROM nyc_taxi.yellow_taxi_trips
GROUP BY 1, 2, 3;

CREATE UNIQUE INDEX IF NOT EXISTS idx_trip_location_summary_pk
    ON nyc_taxi.trip_location_summary (pulocationid, dolocationid, payment_type);

-- =============================================================================
-- 3. DISTANCE SUMMARY — groups by distance bucket
--    Covers: trip distance distribution
-- =============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS nyc_taxi.trip_distance_summary AS
SELECT
    CASE
        WHEN trip_distance <= 1 THEN 1
        WHEN trip_distance <= 3 THEN 2
        WHEN trip_distance <= 5 THEN 3
        WHEN trip_distance <= 10 THEN 4
        WHEN trip_distance <= 20 THEN 5
        ELSE 6
    END as distance_bucket,
    CASE
        WHEN trip_distance <= 1 THEN '0-1 miles'
        WHEN trip_distance <= 3 THEN '1-3 miles'
        WHEN trip_distance <= 5 THEN '3-5 miles'
        WHEN trip_distance <= 10 THEN '5-10 miles'
        WHEN trip_distance <= 20 THEN '10-20 miles'
        ELSE '20+ miles'
    END as distance_range,
    COUNT(*) as trip_count,
    SUM(trip_distance) as total_distance,
    SUM(total_amount) as total_amount
FROM nyc_taxi.yellow_taxi_trips
WHERE trip_distance > 0 AND trip_distance < 500
GROUP BY 1, 2;

CREATE UNIQUE INDEX IF NOT EXISTS idx_trip_distance_summary_pk
    ON nyc_taxi.trip_distance_summary (distance_bucket);
