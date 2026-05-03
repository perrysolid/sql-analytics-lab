"""Capture PGAdmin screenshots for all Sample Analytics Queries."""
import subprocess
import time
import json

QUERIES = {
    "query-04-payment-borough": """SELECT pz.borough || ' - ' || ptl.payment_type_desc AS borough_payment_type,
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
ORDER BY avg_total DESC;""",

    "query-05-basic-overview": """SELECT unnest(ARRAY['Total Trips', 'Date Range', 'Total Revenue']) as metric,
       unnest(ARRAY[
           COUNT(*)::text,
           MIN(tpep_pickup_datetime)::text || ' to ' || MAX(tpep_pickup_datetime)::text,
           '$' || ROUND(SUM(total_amount), 2)::text
       ]) as value
FROM nyc_taxi.yellow_taxi_trips;""",

    "query-06-payment-method": """SELECT
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
ORDER BY trip_count DESC;""",

    "query-07-top-revenue": """SELECT
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
LIMIT 20;""",

    "query-08-distance-distribution": """SELECT
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
ORDER BY MIN(trip_distance);""",

    "query-09-daily-patterns": """SELECT
    DATE(tpep_pickup_datetime) as trip_date,
    COUNT(*) as total_trips,
    ROUND(AVG(total_amount), 2) as avg_fare,
    ROUND(SUM(total_amount), 2) as daily_revenue,
    COUNT(CASE WHEN payment_type = 1 THEN 1 END) as credit_card_trips,
    COUNT(CASE WHEN payment_type = 2 THEN 1 END) as cash_trips
FROM nyc_taxi.yellow_taxi_trips
GROUP BY DATE(tpep_pickup_datetime)
ORDER BY trip_date;""",

    "query-10-rush-hour": """SELECT
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
ORDER BY trip_count DESC;""",

    "query-11-tip-analysis": """SELECT
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
ORDER BY avg_tip DESC;""",

    "query-12-weekend-weekday": """SELECT
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
ORDER BY trip_count DESC;""",

    "query-13-long-distance": """SELECT
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
LIMIT 20;""",

    # Materialized View queries
    "mv-01-trip-volume": """SELECT h.pickup_hour as hour,
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
ORDER BY h.pickup_hour;""",

    "mv-03-cross-borough": """SELECT pz.borough || ' -> ' || dz.borough AS trip_route,
       SUM(ls.trip_count) AS trip_count,
       ROUND((SUM(ls.total_fare) / SUM(ls.trip_count))::numeric, 2) AS avg_fare
FROM nyc_taxi.trip_location_summary ls
JOIN nyc_taxi.taxi_zone_lookup pz ON ls.pulocationid = pz.locationid
JOIN nyc_taxi.taxi_zone_lookup dz ON ls.dolocationid = dz.locationid
GROUP BY pz.borough, dz.borough
ORDER BY trip_count DESC;""",

    "mv-04-payment-borough": """SELECT pz.borough || ' - ' || ptl.payment_type_desc AS borough_payment_type,
       SUM(ls.trip_count) AS trips,
       ROUND((SUM(ls.total_amount) / SUM(ls.trip_count))::numeric, 2) AS avg_total
FROM nyc_taxi.trip_location_summary ls
JOIN nyc_taxi.taxi_zone_lookup pz ON ls.pulocationid = pz.locationid
JOIN nyc_taxi.payment_type_lookup ptl ON ls.payment_type = ptl.payment_type
GROUP BY pz.borough, ptl.payment_type_desc
ORDER BY avg_total DESC;""",

    "mv-05-basic-overview": """SELECT unnest(ARRAY['Total Trips', 'Date Range', 'Total Revenue']) as metric,
       unnest(ARRAY[
           SUM(trip_count)::text,
           MIN(min_pickup)::text || ' to ' || MAX(max_pickup)::text,
           '$' || ROUND(SUM(total_amount)::numeric, 2)::text
       ]) as value
FROM nyc_taxi.trip_hourly_summary;""",

    "mv-06-payment-method": """SELECT
    CASE payment_type
        WHEN 1 THEN 'Credit Card' WHEN 2 THEN 'Cash' WHEN 3 THEN 'No Charge'
        WHEN 4 THEN 'Dispute' WHEN 5 THEN 'Unknown' WHEN 6 THEN 'Voided'
        ELSE 'Other'
    END as payment_method,
    SUM(trip_count) as trip_count,
    ROUND((SUM(total_amount) / SUM(trip_count))::numeric, 2) as avg_fare,
    ROUND((SUM(total_tip) / SUM(trip_count))::numeric, 2) as avg_tip,
    ROUND(SUM(total_amount)::numeric, 2) as total_revenue,
    ROUND(100.0 * SUM(trip_count) / SUM(SUM(trip_count)) OVER(), 2) as percentage
FROM nyc_taxi.trip_hourly_summary
GROUP BY payment_type
ORDER BY trip_count DESC;""",

    "mv-08-distance-distribution": """SELECT distance_range,
       trip_count,
       ROUND((total_distance / trip_count)::numeric, 2) as avg_distance,
       ROUND((total_amount / trip_count)::numeric, 2) as avg_fare,
       ROUND(100.0 * trip_count / SUM(trip_count) OVER(), 2) as percentage
FROM nyc_taxi.trip_distance_summary
ORDER BY distance_bucket;""",

    "mv-09-daily-patterns": """SELECT trip_date,
       SUM(trip_count) as total_trips,
       ROUND((SUM(total_amount) / SUM(trip_count))::numeric, 2) as avg_fare,
       ROUND(SUM(total_amount)::numeric, 2) as daily_revenue,
       SUM(CASE WHEN payment_type = 1 THEN trip_count ELSE 0 END) as credit_card_trips,
       SUM(CASE WHEN payment_type = 2 THEN trip_count ELSE 0 END) as cash_trips
FROM nyc_taxi.trip_hourly_summary
GROUP BY trip_date
ORDER BY trip_date;""",

    "mv-10-rush-hour": """SELECT
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
GROUP BY 1
ORDER BY trip_count DESC;""",

    "mv-11-tip-analysis": """SELECT
    CASE payment_type WHEN 1 THEN 'Credit Card' WHEN 2 THEN 'Cash' ELSE 'Other' END as payment_method,
    SUM(trip_count) as trip_count,
    ROUND((SUM(total_tip) / SUM(trip_count))::numeric, 2) as avg_tip,
    ROUND((SUM(total_fare) / SUM(trip_count))::numeric, 2) as avg_fare,
    ROUND((SUM(total_tip) / NULLIF(SUM(total_fare), 0) * 100)::numeric, 2) as avg_tip_percentage,
    SUM(trips_with_tips) as trips_with_tips
FROM nyc_taxi.trip_hourly_summary
WHERE total_fare > 0 AND payment_type IN (1, 2)
GROUP BY payment_type
ORDER BY avg_tip DESC;""",

    "mv-12-weekend-weekday": """SELECT
    CASE WHEN day_of_week IN (0, 6) THEN 'Weekend' ELSE 'Weekday' END as day_type,
    SUM(trip_count) as trip_count,
    ROUND((SUM(total_distance) / SUM(trip_count))::numeric, 2) as avg_distance,
    ROUND((SUM(total_amount) / SUM(trip_count))::numeric, 2) as avg_fare,
    ROUND(SUM(total_amount)::numeric, 2) as total_revenue
FROM nyc_taxi.trip_hourly_summary
GROUP BY CASE WHEN day_of_week IN (0, 6) THEN 'Weekend' ELSE 'Weekday' END
ORDER BY trip_count DESC;""",
}

# Estimate wait times based on query type
SLOW_QUERIES = {"query-05", "query-06", "query-08", "query-09", "query-10", "query-11", "query-12"}

for name, sql in QUERIES.items():
    wait = 20 if any(name.startswith(s) for s in SLOW_QUERIES) else 5
    print(f"Ready: {name} (wait={wait}s)")
    print(f"SQL length: {len(sql)} chars")
    print()

print(f"Total queries: {len(QUERIES)}")
