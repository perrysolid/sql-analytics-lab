-- NYC Yellow Taxi Data Analytics Queries
-- Sample queries to explore the NYC taxi dataset

-- 1. Basic Data Overview
SELECT 'Total Trips' as metric, COUNT(*)::text as value
FROM nyc_taxi.yellow_taxi_trips

UNION ALL

SELECT 'Date Range' as metric,
       MIN(tpep_pickup_datetime)::text || ' to ' || MAX(tpep_pickup_datetime)::text as value
FROM nyc_taxi.yellow_taxi_trips

UNION ALL

SELECT 'Total Revenue' as metric, '$' || ROUND(SUM(total_amount), 2)::text as value
FROM nyc_taxi.yellow_taxi_trips;

-- 2. Trip Volume by Hour of Day
SELECT
    EXTRACT(HOUR FROM tpep_pickup_datetime) as pickup_hour,
    COUNT(*) as trip_count,
    ROUND(AVG(trip_distance), 2) as avg_distance,
    ROUND(AVG(total_amount), 2) as avg_fare
FROM nyc_taxi.yellow_taxi_trips
GROUP BY EXTRACT(HOUR FROM tpep_pickup_datetime)
ORDER BY pickup_hour;

-- 3. Payment Method Analysis
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

-- 4. Top Revenue Generating Trips - possible erroneous data inputs 
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

-- 5. Trip Distance Distribution
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
    ROUND(AVG(total_amount), 2) as avg_fare,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM nyc_taxi.yellow_taxi_trips
WHERE trip_distance > 0
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

-- 6. Daily Trip Patterns
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

-- 7. Rush Hour Analysis
SELECT
    CASE
        WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 7 AND 9 THEN 'Morning Rush (7-9 AM)'
        WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 17 AND 19 THEN 'Evening Rush (5-7 PM)'
        WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 22 AND 23 OR
             EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 0 AND 5 THEN 'Night (10 PM - 5 AM)'
        ELSE 'Regular Hours'
    END as time_period,
    COUNT(*) as trip_count,
    ROUND(AVG(trip_distance), 2) as avg_distance,
    ROUND(AVG(total_amount), 2) as avg_fare,
    ROUND(AVG(tip_amount), 2) as avg_tip
FROM nyc_taxi.yellow_taxi_trips
GROUP BY
    CASE
        WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 7 AND 9 THEN 'Morning Rush (7-9 AM)'
        WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 17 AND 19 THEN 'Evening Rush (5-7 PM)'
        WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 22 AND 23 OR
             EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 0 AND 5 THEN 'Night (10 PM - 5 AM)'
        ELSE 'Regular Hours'
    END
ORDER BY trip_count DESC;

-- 8. Tip Analysis by Payment Type
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

-- 9. Weekend vs Weekday Analysis
SELECT
    CASE
        WHEN EXTRACT(DOW FROM tpep_pickup_datetime) IN (0, 6) THEN 'Weekend'
        ELSE 'Weekday'
    END as day_type,
    COUNT(*) as trip_count,
    ROUND(AVG(trip_distance), 2) as avg_distance,
    ROUND(AVG(total_amount), 2) as avg_fare,
    ROUND(SUM(total_amount), 2) as total_revenue
FROM nyc_taxi.yellow_taxi_trips
GROUP BY
    CASE
        WHEN EXTRACT(DOW FROM tpep_pickup_datetime) IN (0, 6) THEN 'Weekend'
        ELSE 'Weekday'
    END
ORDER BY trip_count DESC;

-- 10. Long Distance Trips (Over 20 miles) - possible erroneous data inputs 
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