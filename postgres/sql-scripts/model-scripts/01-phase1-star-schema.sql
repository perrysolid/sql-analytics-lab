-- ================================================================================
-- Phase 1: Star Schema Implementation
-- Transform normalized schema into dimensional model for analytical queries
-- Based on Interview Question 2: Dimensional Modeling
-- ================================================================================

-- Set schema context
SET search_path = nyc_taxi, public;

-- ================================================================================
-- DIMENSION TABLES
-- ================================================================================

-- Date Dimension - Complete date hierarchy for time-based analysis
CREATE TABLE dim_date (
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
CREATE TABLE dim_time (
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
CREATE TABLE dim_locations (
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
CREATE TABLE dim_vendor (
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
CREATE TABLE dim_payment_type (
    payment_type_key SERIAL PRIMARY KEY,
    payment_type INTEGER NOT NULL,
    payment_type_desc VARCHAR(50) NOT NULL,
    is_electronic BOOLEAN NOT NULL,
    allows_tips BOOLEAN NOT NULL,
    processing_fee_applies BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(payment_type)
);

-- Rate Code Dimension - Enhanced with zone applicability
CREATE TABLE dim_rate_code (
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
-- FACT TABLE
-- ================================================================================

-- Fact table with foreign keys to dimensions and measures
CREATE TABLE fact_taxi_trips (
    trip_key BIGSERIAL PRIMARY KEY,

    -- Foreign Keys to Dimensions
    pickup_date_key INTEGER REFERENCES dim_date(date_key),
    pickup_time_key INTEGER REFERENCES dim_time(time_key),
    dropoff_date_key INTEGER REFERENCES dim_date(date_key),
    dropoff_time_key INTEGER REFERENCES dim_time(time_key),
    pickup_location_key INTEGER REFERENCES dim_locations(location_key),
    dropoff_location_key INTEGER REFERENCES dim_locations(location_key),
    vendor_key INTEGER REFERENCES dim_vendor(vendor_key),
    payment_type_key INTEGER REFERENCES dim_payment_type(payment_type_key),
    rate_code_key INTEGER REFERENCES dim_rate_code(rate_code_key),

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
    base_fare DECIMAL(8,2), -- fare_amount + extra
    total_surcharges DECIMAL(8,2), -- sum of all surcharges
    tip_percentage DECIMAL(5,2), -- tip as % of fare
    avg_speed_mph DECIMAL(5,2), -- trip_distance / (duration_hours)
    revenue_per_mile DECIMAL(8,2), -- total_amount / trip_distance

    -- Flags for Analysis
    is_airport_trip BOOLEAN,
    is_cross_borough_trip BOOLEAN,
    is_cash_trip BOOLEAN,
    is_long_distance BOOLEAN, -- > 10 miles
    is_short_trip BOOLEAN,    -- < 1 mile

    -- Original row reference for traceability
    original_row_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================================================
-- DIMENSION DATA POPULATION FUNCTIONS
-- ================================================================================

-- Function to populate dim_date
CREATE OR REPLACE FUNCTION populate_dim_date(start_date DATE, end_date DATE)
RETURNS void AS $$
DECLARE
    current_date DATE;
    date_record RECORD;
BEGIN
    current_date := start_date;

    WHILE current_date <= end_date LOOP
        -- Calculate all date attributes
        INSERT INTO dim_date (
            date_key, full_date, year, quarter, month, month_name,
            day_of_month, day_of_year, day_of_week, day_name,
            week_of_year, is_weekend, is_holiday, fiscal_year,
            fiscal_quarter, season
        ) VALUES (
            TO_CHAR(current_date, 'YYYYMMDD')::INTEGER,
            current_date,
            EXTRACT(YEAR FROM current_date),
            EXTRACT(QUARTER FROM current_date),
            EXTRACT(MONTH FROM current_date),
            TO_CHAR(current_date, 'Month'),
            EXTRACT(DAY FROM current_date),
            EXTRACT(DOY FROM current_date),
            EXTRACT(DOW FROM current_date) + 1, -- Convert to 1-7 range
            TO_CHAR(current_date, 'Day'),
            EXTRACT(WEEK FROM current_date),
            EXTRACT(DOW FROM current_date) IN (0, 6), -- Weekend
            FALSE, -- Holiday detection can be enhanced
            CASE
                WHEN EXTRACT(MONTH FROM current_date) >= 4 THEN EXTRACT(YEAR FROM current_date)
                ELSE EXTRACT(YEAR FROM current_date) - 1
            END, -- Fiscal year starts in April
            CASE
                WHEN EXTRACT(MONTH FROM current_date) BETWEEN 4 AND 6 THEN 1
                WHEN EXTRACT(MONTH FROM current_date) BETWEEN 7 AND 9 THEN 2
                WHEN EXTRACT(MONTH FROM current_date) BETWEEN 10 AND 12 THEN 3
                ELSE 4
            END,
            CASE
                WHEN EXTRACT(MONTH FROM current_date) IN (12, 1, 2) THEN 'Winter'
                WHEN EXTRACT(MONTH FROM current_date) IN (3, 4, 5) THEN 'Spring'
                WHEN EXTRACT(MONTH FROM current_date) IN (6, 7, 8) THEN 'Summer'
                ELSE 'Fall'
            END
        ) ON CONFLICT (date_key) DO NOTHING;

        current_date := current_date + 1;
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
-- POPULATE INITIAL DIMENSION DATA
-- ================================================================================

-- Populate date dimension for taxi data range (2020-2025)
SELECT populate_dim_date('2020-01-01'::DATE, '2025-12-31'::DATE);

-- Populate time dimension
SELECT populate_dim_time();

-- Populate location dimension from existing data
INSERT INTO dim_locations (
    locationid, zone, borough, service_zone, zone_type,
    is_airport, is_manhattan, is_high_demand, business_district
)
SELECT DISTINCT
    tzl.locationid,
    tzl.zone,
    tzl.borough,
    tzl.service_zone,
    CASE
        WHEN tzl.zone ILIKE '%airport%' OR tzl.service_zone = 'EWR' THEN 'Airport'
        WHEN tzl.borough = 'Manhattan' AND tzl.zone ILIKE '%midtown%' THEN 'Manhattan Core'
        WHEN tzl.borough = 'Manhattan' THEN 'Manhattan'
        ELSE 'Outer Borough'
    END as zone_type,
    (tzl.zone ILIKE '%airport%' OR tzl.service_zone = 'EWR'),
    (tzl.borough = 'Manhattan'),
    FALSE, -- Will be updated based on trip volume analysis
    (tzl.zone ILIKE '%financial%' OR tzl.zone ILIKE '%midtown%' OR tzl.zone ILIKE '%times square%')
FROM taxi_zone_lookup tzl
ORDER BY tzl.locationid;

-- Populate vendor dimension
INSERT INTO dim_vendor (vendorid, vendor_name, vendor_type)
SELECT DISTINCT
    vl.vendorid,
    vl.vendor_name,
    'Technology Provider'
FROM vendor_lookup vl
ORDER BY vl.vendorid;

-- Populate payment type dimension
INSERT INTO dim_payment_type (
    payment_type, payment_type_desc, is_electronic, allows_tips
)
SELECT DISTINCT
    ptl.payment_type,
    ptl.payment_type_desc,
    ptl.payment_type NOT IN (2), -- Cash is not electronic
    ptl.payment_type IN (1, 3, 4) -- Credit card, No charge, Dispute allow tips
FROM payment_type_lookup ptl
ORDER BY ptl.payment_type;

-- Populate rate code dimension
INSERT INTO dim_rate_code (
    ratecodeid, rate_code_desc, is_metered, is_airport_rate, is_negotiated
)
SELECT DISTINCT
    rcl.ratecodeid,
    rcl.rate_code_desc,
    rcl.ratecodeid IN (1), -- Only standard rate is metered
    rcl.ratecodeid IN (2, 3), -- JFK, Newark are airport rates
    rcl.ratecodeid IN (5, 6) -- Negotiated and group ride
FROM rate_code_lookup rcl
ORDER BY rcl.ratecodeid;

-- ================================================================================
-- CREATE INDEXES ON DIMENSIONS
-- ================================================================================

-- Date dimension indexes
CREATE INDEX idx_dim_date_full_date ON dim_date (full_date);
CREATE INDEX idx_dim_date_year_month ON dim_date (year, month);
CREATE INDEX idx_dim_date_is_weekend ON dim_date (is_weekend);
CREATE INDEX idx_dim_date_quarter ON dim_date (year, quarter);

-- Time dimension indexes
CREATE INDEX idx_dim_time_hour ON dim_time (hour_24);
CREATE INDEX idx_dim_time_rush_hour ON dim_time (is_rush_hour);
CREATE INDEX idx_dim_time_business_hours ON dim_time (is_business_hours);

-- Location dimension indexes
CREATE INDEX idx_dim_locations_borough ON dim_locations (borough);
CREATE INDEX idx_dim_locations_zone_type ON dim_locations (zone_type);
CREATE INDEX idx_dim_locations_is_airport ON dim_locations (is_airport);
CREATE INDEX idx_dim_locations_is_manhattan ON dim_locations (is_manhattan);

-- ================================================================================
-- COMMENTS FOR DOCUMENTATION
-- ================================================================================

COMMENT ON TABLE fact_taxi_trips IS 'Star schema fact table containing trip-level metrics and foreign keys to all dimensions';
COMMENT ON TABLE dim_date IS 'Date dimension with complete date hierarchy for time-based analysis';
COMMENT ON TABLE dim_time IS 'Time dimension with hour-level analysis and business rules';
COMMENT ON TABLE dim_locations IS 'Enhanced location dimension with business classifications';
COMMENT ON TABLE dim_vendor IS 'Vendor dimension with performance metrics placeholders';
COMMENT ON TABLE dim_payment_type IS 'Payment type dimension with processing characteristics';
COMMENT ON TABLE dim_rate_code IS 'Rate code dimension with zone applicability flags';

COMMENT ON COLUMN fact_taxi_trips.trip_key IS 'Surrogate key for the fact table';
COMMENT ON COLUMN fact_taxi_trips.avg_speed_mph IS 'Calculated average speed: distance / duration';
COMMENT ON COLUMN fact_taxi_trips.tip_percentage IS 'Tip amount as percentage of fare amount';
COMMENT ON COLUMN fact_taxi_trips.is_cross_borough_trip IS 'Flag indicating pickup and dropoff in different boroughs';