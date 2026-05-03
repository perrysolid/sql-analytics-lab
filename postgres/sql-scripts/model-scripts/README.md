# SQL Playground Advanced Model Scripts

Implementation of Phases 1-3 from the SQL Playground Development Plan, transforming our NYC Taxi database from basic normalized schema to enterprise-grade analytical platform.

## 📁 Files Overview

- **`01-phase1-star-schema.sql`** - Dimensional model implementation
- **`02-phase2-partitioning.sql`** - Monthly partitioning with automation
- **`03-phase3-performance-indexing.sql`** - Advanced indexing and optimization
- **`04-data-migration.sql`** - Data migration from original to star schema (created separately)
- **`examples/`** - Query examples and performance comparisons

## 🚀 Implementation Order

**⚠️ Important**: Execute these scripts in order. Each phase builds upon the previous one.

### Phase 1: Star Schema Implementation
```bash
# Connect to your database
docker exec -it sql-playground-postgres psql -U admin -d playground

# Execute Phase 1
\i /sql-scripts/model-scripts/01-phase1-star-schema.sql
```

**What it creates:**
- 6 dimension tables with business-friendly hierarchies
- Fact table structure with foreign keys and measures
- Automated dimension population functions
- Basic dimensional indexes

### Phase 2: Partitioning Implementation
```bash
# Execute Phase 2
\i /sql-scripts/model-scripts/02-phase2-partitioning.sql
```

**What it creates:**
- Monthly range partitions (2020-2025)
- Automated partition creation/maintenance functions
- Partition management tracking table
- Constraint exclusion optimization

### Phase 3: Performance & Indexing
```bash
# Execute Phase 3
\i /sql-scripts/model-scripts/03-phase3-performance-indexing.sql
```

**What it creates:**
- Partition-local indexes for optimal performance
- Covering indexes with INCLUDE clauses
- Partial indexes for filtered queries
- Expression indexes for calculated fields
- Materialized views for common aggregations

## 📊 Architecture Transformation

### Before (Normalized Schema)
```
yellow_taxi_trips (3.4M+ rows/month)
├── All data in single table
├── Basic indexes on individual columns
└── No partitioning
```

### After (Star Schema + Partitioned)
```
fact_taxi_trips (partitioned by month)
├── Monthly partitions (2020_01, 2020_02, ...)
├── Partition-local indexes
└── Materialized views for aggregations

Dimension Tables:
├── dim_date (2,191 rows - 6 years of dates)
├── dim_time (24 rows - hourly granularity)
├── dim_locations (263 rows - NYC taxi zones)
├── dim_vendor (2 rows - taxi companies)
├── dim_payment_type (6 rows - payment methods)
└── dim_rate_code (6 rows - fare types)
```

## 🔧 Key Features Implemented

### 1. Star Schema Benefits
- **Faster analytical queries** via dimensional model
- **Business-friendly** attribute names and hierarchies
- **Pre-calculated measures** (tip_percentage, avg_speed_mph, etc.)
- **Simplified joins** for reporting tools

### 2. Partitioning Advantages
- **Partition elimination** for date-range queries
- **Parallel processing** across partitions
- **Easier maintenance** (backup, analyze, vacuum per partition)
- **Automatic partition creation** for future months

### 3. Advanced Indexing
- **Partition-local indexes** for better performance
- **Covering indexes** to avoid table lookups
- **Partial indexes** for filtered queries (airport trips, cross-borough, etc.)
- **Expression indexes** for calculated patterns

## 📈 Performance Improvements

### Query Performance Examples

#### Before (Normalized Schema)
```sql
-- Slow: Full table scan across 40M+ records
SELECT
    tzl.borough,
    EXTRACT(HOUR FROM yt.tpep_pickup_datetime) as hour,
    COUNT(*), SUM(yt.total_amount)
FROM yellow_taxi_trips yt
JOIN taxi_zone_lookup tzl ON yt.pulocationid = tzl.locationid
WHERE yt.tpep_pickup_datetime >= '2024-01-01'
GROUP BY tzl.borough, EXTRACT(HOUR FROM yt.tpep_pickup_datetime);
```

#### After (Star Schema + Partitioned)
```sql
-- Fast: Partition elimination + materialized view
SELECT
    pickup_borough,
    hour_24,
    SUM(trip_count), SUM(total_revenue)
FROM mv_hourly_trip_summary
WHERE pickup_date >= '2024-01-01'
GROUP BY pickup_borough, hour_24;
```

### Performance Monitoring
```sql
-- Check partition pruning
SELECT * FROM explain_partition_pruning('2024-01-01', '2024-01-31');

-- Monitor index usage
SELECT * FROM index_usage_stats WHERE usage_category = 'UNUSED';

-- Identify slow queries
SELECT * FROM identify_slow_queries();
```

## 🛠 Maintenance Operations

### Daily Maintenance
```sql
-- Run daily partition maintenance
SELECT daily_partition_maintenance();

-- Update partition statistics
SELECT update_partition_stats();

-- Refresh materialized views
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_hourly_trip_summary;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_zone_performance;
```

### Monthly Maintenance
```sql
-- Create next month's partition
SELECT create_monthly_partition(CURRENT_DATE + INTERVAL '1 month');

-- Analyze new partitions
ANALYZE fact_taxi_trips;

-- Check index usage and cleanup unused indexes
SELECT * FROM index_usage_stats WHERE usage_category = 'UNUSED';
```

## 🔍 Monitoring & Analysis

### Partition Information
```sql
-- View all partitions and their data
SELECT
    partition_name,
    start_date,
    end_date,
    row_count,
    pg_size_pretty(pg_total_relation_size('nyc_taxi.' || partition_name)) as size
FROM partition_management
ORDER BY start_date;
```

### Index Usage Analysis
```sql
-- Check which indexes are being used
SELECT
    tablename,
    indexname,
    idx_scan,
    usage_category,
    index_size
FROM index_usage_stats
ORDER BY idx_scan DESC;
```

### Query Performance Analysis
```sql
-- Analyze specific query performance
SELECT * FROM analyze_query_performance('
    SELECT pickup_borough, COUNT(*)
    FROM mv_hourly_trip_summary
    WHERE pickup_date >= CURRENT_DATE - 7
    GROUP BY pickup_borough
', true);
```

## 📋 Data Migration

After implementing the schema, you'll need to migrate data from the original `yellow_taxi_trips` table to the new star schema. This involves:

1. **Dimension lookups** to get foreign keys
2. **Calculated measures** (tip_percentage, avg_speed_mph, etc.)
3. **Flag calculations** (is_airport_trip, is_cross_borough_trip, etc.)
4. **Partition routing** based on pickup_date

A separate migration script will handle this transformation.

## 🎯 Usage Examples

### Business Intelligence Queries
```sql
-- Top 10 most profitable taxi zones by borough
SELECT
    dl.borough,
    dl.zone,
    SUM(ft.total_amount) as total_revenue,
    COUNT(*) as trip_count,
    AVG(ft.tip_percentage) as avg_tip_pct
FROM fact_taxi_trips ft
JOIN dim_locations dl ON ft.pickup_location_key = dl.location_key
WHERE ft.pickup_date >= CURRENT_DATE - 30
GROUP BY dl.borough, dl.zone
ORDER BY total_revenue DESC
LIMIT 10;

-- Rush hour vs non-rush hour comparison
SELECT
    dt.is_rush_hour,
    COUNT(*) as trips,
    AVG(ft.total_amount) as avg_fare,
    AVG(ft.trip_distance) as avg_distance
FROM fact_taxi_trips ft
JOIN dim_time dt ON ft.pickup_time_key = dt.time_key
WHERE ft.pickup_date >= CURRENT_DATE - 7
GROUP BY dt.is_rush_hour;
```

### Geospatial Analysis
```sql
-- Airport trips analysis
SELECT
    dl_pickup.zone as pickup_zone,
    dl_dropoff.zone as dropoff_zone,
    COUNT(*) as trip_count,
    AVG(ft.total_amount) as avg_fare
FROM fact_taxi_trips ft
JOIN dim_locations dl_pickup ON ft.pickup_location_key = dl_pickup.location_key
JOIN dim_locations dl_dropoff ON ft.dropoff_location_key = dl_dropoff.location_key
WHERE ft.is_airport_trip = true
AND ft.pickup_date >= CURRENT_DATE - 30
GROUP BY dl_pickup.zone, dl_dropoff.zone
ORDER BY trip_count DESC;
```

## 🚨 Important Notes

1. **Backup First**: Always backup your data before running these scripts
2. **Test Environment**: Run on a copy of production data first
3. **Downtime**: Phase 2 recreates the fact table - plan for downtime
4. **Disk Space**: Indexes and materialized views require additional storage
5. **Maintenance**: Set up automated maintenance for optimal performance

## 🎓 Learning Outcomes

This implementation demonstrates:
- **Dimensional modeling** principles
- **Partitioning strategies** for large datasets
- **Advanced indexing** techniques
- **Query optimization** methods
- **Performance monitoring** practices
- **Maintenance automation** procedures

Perfect for SQL interview preparation and real-world data warehouse scenarios!

---
Perfect! I've successfully implemented Phases 1, 2, and 3 of the SQL Playground development plan. Here's what's been     
  created in ./sql-scripts/model-scripts/:

  📁 Implementation Complete

  Core Scripts

  - 01-phase1-star-schema.sql - Complete dimensional model with 6 dimension tables and fact table structure
  - 02-phase2-partitioning.sql - Monthly range partitioning with automated maintenance functions
  - 03-phase3-performance-indexing.sql - Advanced indexing strategy with partition-local, covering, and partial indexes    
  - 04-data-migration.sql - Data transformation and migration from normalized to star schema

  Documentation & Examples

  - README.md - Comprehensive implementation guide with usage examples
  - examples/sample-queries.sql - 17 demonstration queries showing performance benefits

  🚀 Key Features Implemented

  Phase 1: Star Schema

  - Date dimension with complete hierarchy (2,191 dates)
  - Time dimension with business rules (rush hour, business hours)
  - Enhanced location dimension with zone classifications
  - Vendor, payment type, and rate code dimensions
  - Fact table with calculated measures and business flags

  Phase 2: Partitioning

  - Monthly range partitions (2020-2025)
  - Automated partition creation/maintenance functions
  - Partition management tracking
  - Constraint exclusion optimization

  Phase 3: Performance

  - Partition-local indexes for optimal performance
  - Covering indexes with INCLUDE clauses
  - Partial indexes for filtered queries (airport trips, cross-borough)
  - Expression indexes for time patterns
  - Materialized views for common aggregations

  🎯 Next Steps

  1. Execute the scripts in your Docker environment:
  docker exec -it sql-playground-postgres psql -U admin -d playground
  \i /sql-scripts/model-scripts/01-phase1-star-schema.sql
  \i /sql-scripts/model-scripts/02-phase2-partitioning.sql
  \i /sql-scripts/model-scripts/03-phase3-performance-indexing.sql
  2. Migrate your data:
  \i /sql-scripts/model-scripts/04-data-migration.sql
  SELECT migrate_taxi_data_to_star_schema(50000);
  3. Test the performance:
  \i /sql-scripts/model-scripts/examples/sample-queries.sql

  The implementation transforms your playground from a basic normalized schema into an enterprise-grade analytical
  platform that demonstrates advanced SQL concepts perfect for interview preparation and real-world data engineering       
  scenarios!