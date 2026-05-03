-- ================================================================================
-- Sample Queries for Star Schema + Partitioned Model
-- Demonstrates the power of dimensional modeling with optimized performance
-- ================================================================================

-- Set schema context
SET search_path = nyc_taxi, public;

-- ================================================================================
-- BASIC DIMENSIONAL QUERIES
-- ================================================================================

-- Query 1: Revenue by Borough and Day of Week
-- Shows how dimension tables simplify business queries
SELECT
    dl.borough,
    dd.day_name,
    COUNT(*) as trip_count,
    SUM(ft.total_amount) as total_revenue,
    AVG(ft.total_amount) as avg_fare,
    AVG(ft.tip_percentage) as avg_tip_pct
FROM fact_taxi_trips ft
JOIN dim_locations dl ON ft.pickup_location_key = dl.location_key
JOIN dim_date dd ON ft.pickup_date_key = dd.date_key
WHERE ft.pickup_date >= CURRENT_DATE - 30
GROUP BY dl.borough, dd.day_name, dd.day_of_week
ORDER BY dl.borough, dd.day_of_week;

-- Query 2: Rush Hour Analysis
-- Demonstrates time dimension with business rules
SELECT
    dt.time_period,
    dt.is_rush_hour,
    dl.zone_type,
    COUNT(*) as trips,
    AVG(ft.total_amount) as avg_fare,
    AVG(ft.avg_speed_mph) as avg_speed,
    SUM(CASE WHEN ft.is_cash_trip THEN 1 ELSE 0 END) as cash_trips
FROM fact_taxi_trips ft
JOIN dim_time dt ON ft.pickup_time_key = dt.time_key
JOIN dim_locations dl ON ft.pickup_location_key = dl.location_key
WHERE ft.pickup_date >= CURRENT_DATE - 7
GROUP BY dt.time_period, dt.is_rush_hour, dl.zone_type
ORDER BY dt.time_period;

-- ================================================================================
-- PARTITION PRUNING DEMONSTRATIONS
-- ================================================================================

-- Query 3: Monthly Trends (Shows Partition Elimination)
-- This query will only scan specific monthly partitions
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    dd.year,
    dd.month,
    dd.month_name,
    COUNT(*) as trips,
    SUM(ft.total_amount) as revenue,
    AVG(ft.trip_distance) as avg_distance
FROM fact_taxi_trips ft
JOIN dim_date dd ON ft.pickup_date_key = dd.date_key
WHERE ft.pickup_date BETWEEN '2024-01-01' AND '2024-03-31'  -- Only 3 partitions scanned
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;

-- Query 4: Single Day Analysis (Minimal Partition Scan)
-- Demonstrates how date filtering eliminates most partitions
SELECT
    dt.hour_24,
    COUNT(*) as trips,
    SUM(ft.total_amount) as hourly_revenue,
    AVG(ft.trip_distance) as avg_distance
FROM fact_taxi_trips ft
JOIN dim_time dt ON ft.pickup_time_key = dt.time_key
WHERE ft.pickup_date = '2024-01-15'  -- Only one partition scanned
GROUP BY dt.hour_24
ORDER BY dt.hour_24;

-- ================================================================================
-- COVERING INDEX DEMONSTRATIONS
-- ================================================================================

-- Query 5: Location Performance (Uses Covering Index)
-- Should show "Index Only Scan" in execution plan
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    ft.pickup_location_key,
    ft.dropoff_location_key,
    COUNT(*) as trip_count,
    AVG(ft.trip_distance) as avg_distance,
    AVG(ft.total_amount) as avg_fare,
    AVG(ft.passenger_count) as avg_passengers
FROM fact_taxi_trips ft
WHERE ft.pickup_date >= CURRENT_DATE - 7
GROUP BY ft.pickup_location_key, ft.dropoff_location_key
ORDER BY trip_count DESC
LIMIT 20;

-- Query 6: Vendor Performance Analysis
-- Demonstrates vendor covering index usage
SELECT
    dv.vendor_name,
    ft.pickup_date,
    COUNT(*) as trips,
    AVG(ft.total_amount) as avg_fare,
    AVG(ft.tip_percentage) as avg_tip_pct,
    AVG(ft.avg_speed_mph) as avg_speed
FROM fact_taxi_trips ft
JOIN dim_vendor dv ON ft.vendor_key = dv.vendor_key
WHERE ft.pickup_date >= CURRENT_DATE - 30
GROUP BY dv.vendor_name, ft.pickup_date
ORDER BY ft.pickup_date, dv.vendor_name;

-- ================================================================================
-- PARTIAL INDEX DEMONSTRATIONS
-- ================================================================================

-- Query 7: Airport Trips Analysis (Uses Airport Partial Index)
SELECT
    dl_pickup.zone as pickup_zone,
    dl_dropoff.zone as dropoff_zone,
    COUNT(*) as trip_count,
    AVG(ft.total_amount) as avg_fare,
    AVG(ft.trip_distance) as avg_distance,
    SUM(ft.airport_fee) as total_airport_fees
FROM fact_taxi_trips ft
JOIN dim_locations dl_pickup ON ft.pickup_location_key = dl_pickup.location_key
JOIN dim_locations dl_dropoff ON ft.dropoff_location_key = dl_dropoff.location_key
WHERE ft.is_airport_trip = true  -- Uses partial index
AND ft.pickup_date >= CURRENT_DATE - 30
GROUP BY dl_pickup.zone, dl_dropoff.zone
ORDER BY trip_count DESC;

-- Query 8: Cross-Borough Trips (Uses Cross-Borough Partial Index)
SELECT
    dl_pickup.borough as pickup_borough,
    dl_dropoff.borough as dropoff_borough,
    COUNT(*) as trip_count,
    AVG(ft.total_amount) as avg_fare,
    AVG(ft.trip_distance) as avg_distance,
    AVG(ft.trip_duration_minutes) as avg_duration_min
FROM fact_taxi_trips ft
JOIN dim_locations dl_pickup ON ft.pickup_location_key = dl_pickup.location_key
JOIN dim_locations dl_dropoff ON ft.dropoff_location_key = dl_dropoff.location_key
WHERE ft.is_cross_borough_trip = true  -- Uses partial index
AND ft.pickup_date >= CURRENT_DATE - 7
GROUP BY dl_pickup.borough, dl_dropoff.borough
ORDER BY trip_count DESC;

-- ================================================================================
-- MATERIALIZED VIEW QUERIES
-- ================================================================================

-- Query 9: Fast Hourly Dashboard (Uses Materialized View)
-- Lightning fast response compared to raw fact table aggregation
SELECT
    pickup_borough,
    hour_24,
    SUM(trip_count) as total_trips,
    SUM(total_revenue) as total_revenue,
    AVG(avg_fare) as avg_fare,
    AVG(avg_tip_pct) as avg_tip_percentage
FROM mv_hourly_trip_summary
WHERE pickup_date >= CURRENT_DATE - 7
AND is_rush_hour = true
GROUP BY pickup_borough, hour_24
ORDER BY total_revenue DESC;

-- Query 10: Zone Performance Dashboard (Uses Materialized View)
SELECT
    zone,
    borough,
    zone_type,
    SUM(daily_trips) as total_trips,
    SUM(daily_revenue) as total_revenue,
    AVG(avg_trip_value) as avg_trip_value,
    AVG(revenue_per_mile) as avg_revenue_per_mile,
    AVG(trips_per_hour) as avg_trips_per_hour
FROM mv_daily_zone_performance
WHERE pickup_date >= CURRENT_DATE - 30
GROUP BY zone, borough, zone_type
ORDER BY total_revenue DESC
LIMIT 20;

-- ================================================================================
-- ADVANCED ANALYTICAL QUERIES
-- ================================================================================

-- Query 11: Seasonal Patterns Analysis
-- Shows the power of date dimension hierarchies
SELECT
    dd.season,
    dd.year,
    dl.zone_type,
    COUNT(*) as trips,
    AVG(ft.total_amount) as avg_fare,
    AVG(ft.trip_distance) as avg_distance,
    AVG(ft.tip_percentage) as avg_tip_pct
FROM fact_taxi_trips ft
JOIN dim_date dd ON ft.pickup_date_key = dd.date_key
JOIN dim_locations dl ON ft.pickup_location_key = dl.location_key
WHERE dd.year >= 2023
GROUP BY dd.season, dd.year, dl.zone_type
ORDER BY dd.year, dd.season, dl.zone_type;

-- Query 12: Weekend vs Weekday Comparison
SELECT
    dd.is_weekend,
    dt.is_rush_hour,
    dpt.payment_type_desc,
    COUNT(*) as trip_count,
    AVG(ft.total_amount) as avg_fare,
    AVG(ft.tip_percentage) as avg_tip_pct,
    -- Payment mix analysis
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY dd.is_weekend, dt.is_rush_hour) as payment_pct
FROM fact_taxi_trips ft
JOIN dim_date dd ON ft.pickup_date_key = dd.date_key
JOIN dim_time dt ON ft.pickup_time_key = dt.time_key
JOIN dim_payment_type dpt ON ft.payment_type_key = dpt.payment_type_key
WHERE ft.pickup_date >= CURRENT_DATE - 30
GROUP BY dd.is_weekend, dt.is_rush_hour, dpt.payment_type_desc
ORDER BY dd.is_weekend, dt.is_rush_hour, trip_count DESC;

-- ================================================================================
-- PERFORMANCE COMPARISON QUERIES
-- ================================================================================

-- Query 13: Before/After Performance Demo
-- Compare these two equivalent queries:

-- SLOW VERSION (Original Schema):
/*
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    tzl.borough,
    EXTRACT(HOUR FROM yt.tpep_pickup_datetime) as hour,
    COUNT(*) as trips,
    SUM(yt.total_amount) as revenue
FROM yellow_taxi_trips yt
JOIN taxi_zone_lookup tzl ON yt.pulocationid = tzl.locationid
WHERE yt.tpep_pickup_datetime >= CURRENT_DATE - 7
GROUP BY tzl.borough, EXTRACT(HOUR FROM yt.tpep_pickup_datetime)
ORDER BY tzl.borough, hour;
*/

-- FAST VERSION (Star Schema + Partitioned):
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    pickup_borough,
    hour_24,
    SUM(trip_count) as trips,
    SUM(total_revenue) as revenue
FROM mv_hourly_trip_summary
WHERE pickup_date >= CURRENT_DATE - 7
GROUP BY pickup_borough, hour_24
ORDER BY pickup_borough, hour_24;

-- ================================================================================
-- BUSINESS INTELLIGENCE EXAMPLES
-- ================================================================================

-- Query 14: Top Performing Zones by Revenue
SELECT
    dl.borough,
    dl.zone,
    dl.zone_type,
    COUNT(*) as total_trips,
    SUM(ft.total_amount) as total_revenue,
    AVG(ft.total_amount) as avg_trip_value,
    AVG(ft.tip_percentage) as avg_tip_pct,
    SUM(ft.total_amount) / COUNT(*) as revenue_per_trip,
    -- Ranking within borough
    ROW_NUMBER() OVER (PARTITION BY dl.borough ORDER BY SUM(ft.total_amount) DESC) as borough_rank
FROM fact_taxi_trips ft
JOIN dim_locations dl ON ft.pickup_location_key = dl.location_key
WHERE ft.pickup_date >= CURRENT_DATE - 30
GROUP BY dl.borough, dl.zone, dl.zone_type
ORDER BY total_revenue DESC
LIMIT 25;

-- Query 15: Payment Method Trends
SELECT
    dd.year,
    dd.month,
    dpt.payment_type_desc,
    COUNT(*) as trip_count,
    SUM(ft.total_amount) as total_revenue,
    AVG(ft.tip_percentage) as avg_tip_pct,
    -- Trend calculations
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY dd.year, dd.month) as monthly_share_pct
FROM fact_taxi_trips ft
JOIN dim_date dd ON ft.pickup_date_key = dd.date_key
JOIN dim_payment_type dpt ON ft.payment_type_key = dpt.payment_type_key
WHERE dd.year >= 2023
GROUP BY dd.year, dd.month, dpt.payment_type_desc
ORDER BY dd.year, dd.month, trip_count DESC;

-- ================================================================================
-- INDEX USAGE MONITORING
-- ================================================================================

-- Query 16: Check Which Indexes Are Being Used
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as times_used,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    CASE
        WHEN idx_scan = 0 THEN 'UNUSED'
        WHEN idx_scan < 100 THEN 'LOW_USAGE'
        WHEN idx_scan < 1000 THEN 'MODERATE_USAGE'
        ELSE 'HIGH_USAGE'
    END as usage_level
FROM pg_stat_user_indexes
WHERE schemaname = 'nyc_taxi'
AND tablename LIKE 'fact_taxi_trips_____%%'
ORDER BY idx_scan DESC;

-- Query 17: Partition Elimination Demo
-- Show which partitions are accessed for different date ranges
SELECT
    'Single Day Query' as query_type,
    schemaname,
    tablename as partition_accessed
FROM pg_stat_user_tables
WHERE schemaname = 'nyc_taxi'
AND tablename LIKE 'fact_taxi_trips_____%%'
AND seq_scan > 0;  -- Reset stats first with: SELECT pg_stat_reset();

-- ================================================================================
-- USAGE INSTRUCTIONS
-- ================================================================================

/*
TO USE THESE QUERIES:

1. EXECUTE THE SCHEMA SCRIPTS FIRST:
   \i 01-phase1-star-schema.sql
   \i 02-phase2-partitioning.sql
   \i 03-phase3-performance-indexing.sql

2. MIGRATE YOUR DATA:
   \i 04-data-migration.sql
   SELECT migrate_taxi_data_to_star_schema(50000);

3. RUN THESE SAMPLE QUERIES:
   \i examples/sample-queries.sql

4. COMPARE PERFORMANCE:
   - Enable timing: \timing
   - Run queries and compare execution times
   - Use EXPLAIN ANALYZE to see query plans

5. MONITOR INDEX USAGE:
   - Reset stats: SELECT pg_stat_reset();
   - Run your queries
   - Check index usage with Query 16

EXPECTED PERFORMANCE IMPROVEMENTS:
- 10-100x faster analytical queries
- Partition elimination reduces data scanned
- Covering indexes eliminate table lookups
- Materialized views provide instant aggregations
*/

-- ================================================================================
-- END OF SAMPLE QUERIES
-- ================================================================================

SELECT
    'Sample queries loaded successfully!' as status,
    'Start with Query 1 for basic dimensional analysis' as suggestion;