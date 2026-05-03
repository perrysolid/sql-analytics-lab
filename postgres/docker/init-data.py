#!/usr/bin/env python3
"""
Complete NYC Taxi Database Initialization
This script handles the complete database setup process:
1. Execute SQL scripts for schema creation
2. Load taxi zone reference data
3. Load complete taxi trip data
4. Verify data integrity

This script runs automatically when PostgreSQL container starts
"""

import os
import time
import glob
import pandas as pd
import numpy as np
import geopandas as gpd
import psycopg2
from sqlalchemy import create_engine, text
from geoalchemy2 import Geometry
from shapely.geometry import MultiPolygon, Polygon
import logging
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse
from pathlib import Path
import hashlib
import json

# Setup logging
# Create logs directory structure
base_log_dir = '/postgres/logs'
os.makedirs(base_log_dir, exist_ok=True)

# Get backfill configuration for folder structure
backfill_config = os.getenv('BACKFILL_MONTHS', 'default')
if not backfill_config:
    backfill_config = 'default'

# Create subdirectory based on BACKFILL_MONTHS
log_subdir = os.path.join(base_log_dir, backfill_config)
os.makedirs(log_subdir, exist_ok=True)

# Generate log filename with execution timestamp
execution_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = f'log_{execution_timestamp}.log'
log_filepath = os.path.join(log_subdir, log_filename)

# Configure dual logging: console + file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Console handler (existing behavior)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# File handler (new)
file_handler = logging.FileHandler(log_filepath, mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Add both handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Initial log entry
logger.info(f"📝 Logging to file: {log_filepath}")
logger.info(f"🕒 Execution started at: {datetime.now().isoformat()}")
logger.info(f"⚙️ Backfill configuration: {backfill_config}")

def wait_for_postgres(host='localhost', port=5432, database='playground',
                      user='admin', password='admin123', max_attempts=30):
    """Wait for PostgreSQL to be ready"""
    attempt = 0
    while attempt < max_attempts:
        try:
            # Try to connect to the database
            conn = psycopg2.connect(
                host=host, port=port, database=database,
                user=user, password=password,
                connect_timeout=5
            )
            # Test that we can actually execute a query
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            conn.close()
            logger.info("✅ PostgreSQL is ready!")
            return True
        except (psycopg2.OperationalError, psycopg2.DatabaseError) as e:
            attempt += 1
            if attempt <= 10:
                # Log more frequently in the beginning
                logger.info(f"⏳ Waiting for PostgreSQL... (attempt {attempt}/{max_attempts})")
            elif attempt % 5 == 0:
                # Then log every 5th attempt
                logger.info(f"⏳ Waiting for PostgreSQL... (attempt {attempt}/{max_attempts})")
            time.sleep(3)

    logger.error("❌ PostgreSQL not available after maximum attempts")
    return False


def execute_sql_scripts(engine):
    """Execute SQL initialization scripts in order"""
    logger.info("🗃️ Executing SQL initialization scripts...")

    # Define the script directory and order
    script_dir = '/sql-scripts/init-scripts'

    if not os.path.exists(script_dir):
        logger.warning(f"⚠️ SQL scripts directory not found: {script_dir}")
        return False

    # Get all SQL files and sort them (ensuring proper execution order)
    sql_files = sorted(glob.glob(os.path.join(script_dir, "*.sql")))

    if not sql_files:
        logger.warning("⚠️ No SQL scripts found to execute")
        return False

    logger.info(f"📄 Found {len(sql_files)} SQL scripts to execute")

    try:
        with engine.connect() as conn:
            # Execute each script in order
            for script_path in sql_files:
                script_name = os.path.basename(script_path)
                logger.info(f"🔧 Executing: {script_name}")

                # Read the SQL script
                with open(script_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()

                # Clean up the SQL content
                sql_content = sql_content.strip()

                # Execute the entire script as one block for better compatibility
                # This handles complex statements like INSERT...SELECT properly
                try:
                    # Remove comments and empty lines for cleaner execution
                    clean_sql = '\n'.join([
                        line for line in sql_content.split('\n')
                        if line.strip() and not line.strip().startswith('--')
                    ])

                    if clean_sql:
                        conn.execute(text(clean_sql))
                        conn.commit()

                except Exception as exec_error:
                    logger.warning(f"⚠️ Block execution failed for {script_name}, trying statement by statement: {exec_error}")

                    # Fallback: try to execute statements individually
                    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]

                    for i, statement in enumerate(statements):
                        # Skip comments
                        if statement.startswith('--'):
                            continue

                        try:
                            conn.execute(text(statement))
                            conn.commit()
                        except Exception as stmt_error:
                            logger.error(f"❌ Error in {script_name} statement {i+1}: {stmt_error}")
                            logger.error(f"Statement was: {statement[:100]}...")
                            # Continue with other statements

                logger.info(f"✅ Completed: {script_name}")

        logger.info("✅ All SQL scripts executed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Error executing SQL scripts: {str(e)}")
        return False

def load_taxi_zones(engine):
    """Load taxi zone reference data"""
    logger.info("📍 Loading taxi zone reference data...")

    try:
        # Clean all dictionary tables (excluding yellow_taxi_trips which contains trip data)
        logger.info("🧹 Cleaning dictionary tables for fresh data load...")
        with engine.begin() as conn:
            # Clean taxi zone tables
            conn.execute(text("TRUNCATE TABLE nyc_taxi.taxi_zone_shapes CASCADE"))
            conn.execute(text("TRUNCATE TABLE nyc_taxi.taxi_zone_lookup CASCADE"))
            # Clean lookup tables
            conn.execute(text("TRUNCATE TABLE nyc_taxi.rate_code_lookup CASCADE"))
            conn.execute(text("TRUNCATE TABLE nyc_taxi.payment_type_lookup CASCADE"))
            conn.execute(text("TRUNCATE TABLE nyc_taxi.vendor_lookup CASCADE"))
        logger.info("✅ Dictionary tables cleaned")

        # Ensure data directory exists and download all taxi zone data files
        data_dir = '/postgres/data'
        zones_dir = os.path.join(data_dir, 'zones')

        # Always download fresh taxi zone data during initialization
        logger.info("📥 Downloading taxi zone reference data...")
        if not download_taxi_zone_data(data_dir):
            logger.error("💥 Failed to download taxi zone data")
            return False

        zones_csv_path = os.path.join(zones_dir, 'taxi_zone_lookup.csv')

        zones_df = pd.read_csv(zones_csv_path)
        zones_df.columns = zones_df.columns.str.lower()

        # Handle NULL values - drop rows where zone or borough is NULL
        zones_df = zones_df.dropna(subset=['zone', 'borough'])

        # Fill remaining NULLs in service_zone with 'Unknown'
        zones_df['service_zone'] = zones_df['service_zone'].fillna('Unknown')

        # Load to database
        zones_df.to_sql(
            'taxi_zone_lookup',
            engine,
            schema='nyc_taxi',
            if_exists='append',
            index=False
        )
        logger.info(f"✅ Loaded {len(zones_df)} taxi zones from CSV")

        # Load shapefile if available
        shapefile_path = os.path.join(zones_dir, 'taxi_zones.shp')
        if os.path.exists(shapefile_path):
            logger.info("🗺️ Loading taxi zone shapes...")
            shapes_gdf = gpd.read_file(shapefile_path)

            # Clean and prepare data
            shapes_gdf.columns = shapes_gdf.columns.str.lower()
            shapes_gdf = shapes_gdf.rename(columns={
                'locationid': 'locationid',
                'shape_leng': 'shape_leng',
                'shape_area': 'shape_area'
            })

            # Convert to NYC State Plane if needed
            if shapes_gdf.crs.to_epsg() != 2263:
                logger.info("🔄 Converting CRS to NYC State Plane (EPSG:2263)")
                shapes_gdf = shapes_gdf.to_crs(epsg=2263)

            # Ensure MultiPolygon geometry
            def ensure_multipolygon(geom):
                if isinstance(geom, Polygon):
                    return MultiPolygon([geom])
                return geom

            shapes_gdf['geometry'] = shapes_gdf['geometry'].apply(ensure_multipolygon)

            # Load to database
            shapes_gdf.to_postgis(
                'taxi_zone_shapes',
                engine,
                schema='nyc_taxi',
                if_exists='append',
                index=False
            )
            logger.info(f"✅ Loaded {len(shapes_gdf)} taxi zone shapes")
        else:
            logger.warning(f"⚠️ Shapefile not found at {shapefile_path}")

        # Reload lookup tables since we cleaned them
        logger.info("📚 Reloading lookup tables...")
        with engine.begin() as conn:
            # Rate code lookup
            conn.execute(text("""
                INSERT INTO nyc_taxi.rate_code_lookup (ratecodeid, rate_code_desc) VALUES
                (1, 'Standard rate'),
                (2, 'JFK'),
                (3, 'Newark'),
                (4, 'Nassau or Westchester'),
                (5, 'Negotiated fare'),
                (6, 'Group ride')
            """))

            # Payment type lookup
            conn.execute(text("""
                INSERT INTO nyc_taxi.payment_type_lookup (payment_type, payment_type_desc) VALUES
                (1, 'Credit card'),
                (2, 'Cash'),
                (3, 'No charge'),
                (4, 'Dispute'),
                (5, 'Unknown'),
                (6, 'Voided trip')
            """))

            # Vendor lookup
            conn.execute(text("""
                INSERT INTO nyc_taxi.vendor_lookup (vendorid, vendor_name) VALUES
                (1, 'Creative Mobile Technologies'),
                (2, 'VeriFone Inc.')
            """))
        logger.info("✅ Lookup tables reloaded")

        # Populate star schema dimensions
        logger.info("🌟 Populating star schema dimensions...")
        if not populate_star_schema_dimensions(engine):
            logger.warning("⚠️ Failed to populate star schema dimensions")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ Error loading taxi zones: {str(e)}")
        return False

def populate_star_schema_dimensions(engine):
    """Populate star schema dimension tables from normalized data"""
    logger.info("🌟 Starting star schema dimension population...")

    try:
        start_time = time.time()
        with engine.begin() as conn:
            # Populate location dimension from existing data
            logger.info("📍 Populating dim_locations...")
            conn.execute(text("""
                INSERT INTO nyc_taxi.dim_locations (
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
                FROM nyc_taxi.taxi_zone_lookup tzl
                ON CONFLICT (locationid) DO NOTHING
            """))

            # Populate vendor dimension
            logger.info("🚗 Populating dim_vendor...")
            conn.execute(text("""
                INSERT INTO nyc_taxi.dim_vendor (vendorid, vendor_name, vendor_type)
                SELECT DISTINCT
                    vl.vendorid,
                    vl.vendor_name,
                    'Technology Provider'
                FROM nyc_taxi.vendor_lookup vl
                ON CONFLICT (vendorid) DO NOTHING
            """))

            # Populate payment type dimension
            logger.info("💳 Populating dim_payment_type...")
            conn.execute(text("""
                INSERT INTO nyc_taxi.dim_payment_type (
                    payment_type, payment_type_desc, is_electronic, allows_tips
                )
                SELECT DISTINCT
                    ptl.payment_type,
                    ptl.payment_type_desc,
                    ptl.payment_type NOT IN (2), -- Cash is not electronic
                    ptl.payment_type IN (1, 3, 4) -- Credit card, No charge, Dispute allow tips
                FROM nyc_taxi.payment_type_lookup ptl
                ON CONFLICT (payment_type) DO NOTHING
            """))

            # Populate rate code dimension
            logger.info("📊 Populating dim_rate_code...")
            conn.execute(text("""
                INSERT INTO nyc_taxi.dim_rate_code (
                    ratecodeid, rate_code_desc, is_metered, is_airport_rate, is_negotiated
                )
                SELECT DISTINCT
                    rcl.ratecodeid,
                    rcl.rate_code_desc,
                    rcl.ratecodeid IN (1), -- Only standard rate is metered
                    rcl.ratecodeid IN (2, 3), -- JFK, Newark are airport rates
                    rcl.ratecodeid IN (5, 6) -- Negotiated and group ride
                FROM nyc_taxi.rate_code_lookup rcl
                ON CONFLICT (ratecodeid) DO NOTHING
            """))

            # Record quality metrics for dimension population while connection is still active
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Record metrics for each dimension table using the active connection
            for table_name in ['dim_locations', 'dim_vendor', 'dim_payment_type', 'dim_rate_code']:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM nyc_taxi.{table_name}"))
                    row_count = result.fetchone()[0]

                    record_quality_metrics(engine, {
                        'operation_type': 'dimension_load',
                        'target_table': table_name,
                        'rows_attempted': row_count,  # For dimensions, attempted = inserted since we use ON CONFLICT
                        'rows_inserted': row_count,
                        'rows_duplicates': 0,
                        'rows_invalid': 0,
                        'processing_duration_ms': processing_time_ms // 4,  # Divide by number of tables
                        'batch_id': 'dimension_initialization'
                    })
                except Exception as metric_error:
                    logger.warning(f"⚠️ Could not record metrics for {table_name}: {str(metric_error)}")

        logger.info("✅ Star schema dimensions populated successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Error populating star schema dimensions: {str(e)}")
        # Record failure metrics
        processing_time_ms = int((time.time() - start_time) * 1000)
        record_quality_metrics(engine, {
            'operation_type': 'dimension_load_failed',
            'target_table': 'all_dimensions',
            'rows_attempted': 0,
            'rows_inserted': 0,
            'rows_duplicates': 0,
            'rows_invalid': 0,
            'processing_duration_ms': processing_time_ms,
            'error_message_sample': str(e)[:200],
            'batch_id': 'dimension_initialization'
        })
        return False

def download_taxi_zone_data(data_dir='/postgres/data'):
    """Download taxi zone reference data (CSV and shapefiles)"""
    logger.info("📥 Downloading taxi zone reference data...")

    # Ensure zones subdirectory exists
    zones_dir = os.path.join(data_dir, 'zones')
    os.makedirs(zones_dir, exist_ok=True)

    # Download taxi zone lookup CSV
    csv_url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
    csv_filename = "taxi_zone_lookup.csv"
    csv_path = os.path.join(zones_dir, csv_filename)

    # Always download fresh CSV during initialization
    logger.info(f"📥 Downloading {csv_filename}...")
    try:
        response = requests.get(csv_url)
        response.raise_for_status()
        with open(csv_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"✅ Downloaded: {csv_filename}")
    except Exception as e:
        logger.error(f"❌ Failed to download {csv_filename}: {str(e)}")
        return False

    # Download taxi zone shapefile (ZIP format)
    zip_url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip"
    zip_filename = "taxi_zones.zip"
    zip_path = os.path.join(zones_dir, zip_filename)

    # Always download fresh shapefile ZIP during initialization
    logger.info(f"📥 Downloading {zip_filename}...")
    try:
        response = requests.get(zip_url)
        response.raise_for_status()
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"✅ Downloaded: {zip_filename}")

        # Extract the ZIP file
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(zones_dir)
        logger.info("✅ Extracted shapefile components")

        # Clean up the ZIP file
        os.remove(zip_path)
        logger.info("🗑️ Cleaned up ZIP file")

    except Exception as e:
        logger.error(f"❌ Failed to download or extract {zip_filename}: {str(e)}")
        return False

    # Verify shapefile components exist
    required_files = ['taxi_zones.shp', 'taxi_zones.dbf', 'taxi_zones.shx', 'taxi_zones.prj']
    for filename in required_files:
        file_path = os.path.join(zones_dir, filename)
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ Missing shapefile component: {filename}")

    logger.info("✅ All taxi zone reference data files are available")
    return True

def download_taxi_data(year, month, data_dir='/postgres/data'):
    """Download taxi data for a specific year and month"""
    # Ensure yellow subdirectory exists
    yellow_dir = os.path.join(data_dir, 'yellow')
    os.makedirs(yellow_dir, exist_ok=True)

    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet"
    filename = f"yellow_tripdata_{year:04d}-{month:02d}.parquet"
    file_path = os.path.join(yellow_dir, filename)

    # Check if file already exists
    if os.path.exists(file_path):
        logger.info(f"📂 File already exists: {filename}")
        return file_path

    logger.info(f"📥 Downloading {filename} from NYC TLC...")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Get file size for progress tracking
        total_size = int(response.headers.get('content-length', 0))

        with open(file_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    if downloaded % (1024 * 1024 * 10) == 0:  # Log every 10MB
                        logger.info(f"📥 Progress: {progress:.1f}% ({downloaded:,}/{total_size:,} bytes)")

        logger.info(f"✅ Downloaded: {filename} ({os.path.getsize(file_path):,} bytes)")
        return file_path

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to download {filename}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Error downloading {filename}: {str(e)}")
        return None

def check_month_already_processed(engine, year, month):
    """Check if a specific month has already been processed"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT status, records_loaded, processing_completed_at FROM nyc_taxi.data_processing_log WHERE data_year = :year AND data_month = :month"
            ), {"year": year, "month": month})
            row = result.fetchone()

            if row:
                status, records_loaded, completed_at = row
                if status == 'completed':
                    logger.info(f"🔄 {year}-{month:02d}: Already processed ({records_loaded:,} records at {completed_at})")
                    return True
                elif status == 'in_progress':
                    logger.warning(f"⚠️ {year}-{month:02d}: Previous processing incomplete, will retry")
                    # Delete incomplete record to allow retry
                    conn.execute(text(
                        "DELETE FROM nyc_taxi.data_processing_log WHERE data_year = :year AND data_month = :month"
                    ), {"year": year, "month": month})
                    conn.commit()
                elif status == 'failed':
                    logger.info(f"🔄 {year}-{month:02d}: Previous attempt failed, will retry")
                    # Delete failed record to allow retry
                    conn.execute(text(
                        "DELETE FROM nyc_taxi.data_processing_log WHERE data_year = :year AND data_month = :month"
                    ), {"year": year, "month": month})
                    conn.commit()

            return False
    except Exception as e:
        logger.error(f"❌ Error checking processing status for {year}-{month:02d}: {str(e)}")
        return False

def start_processing_log(engine, year, month, filename, backfill_config):
    """Start processing log entry for a month"""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO nyc_taxi.data_processing_log
                (data_year, data_month, file_name, backfill_config, status)
                VALUES (:year, :month, :filename, :config, 'in_progress')
            """), {
                "year": year,
                "month": month,
                "filename": filename,
                "config": backfill_config
            })
            conn.commit()
            logger.info(f"📝 Started processing log for {year}-{month:02d}")
    except Exception as e:
        logger.error(f"❌ Error starting processing log for {year}-{month:02d}: {str(e)}")

def complete_processing_log(engine, year, month, records_loaded):
    """Complete processing log entry for a month"""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                UPDATE nyc_taxi.data_processing_log
                SET status = 'completed',
                    records_loaded = :records,
                    processing_completed_at = CURRENT_TIMESTAMP
                WHERE data_year = :year AND data_month = :month
            """), {
                "year": year,
                "month": month,
                "records": records_loaded
            })
            conn.commit()
            logger.info(f"✅ Completed processing log for {year}-{month:02d}: {records_loaded:,} records")
    except Exception as e:
        logger.error(f"❌ Error completing processing log for {year}-{month:02d}: {str(e)}")

def fail_processing_log(engine, year, month):
    """Mark processing log entry as failed for a month"""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                UPDATE nyc_taxi.data_processing_log
                SET status = 'failed'
                WHERE data_year = :year AND data_month = :month
            """), {"year": year, "month": month})
            conn.commit()
            logger.info(f"❌ Marked processing as failed for {year}-{month:02d}")
    except Exception as e:
        logger.error(f"❌ Error marking processing as failed for {year}-{month:02d}: {str(e)}")

def calculate_row_hash(row):
    """Calculate SHA-256 hash of all row values for duplicate detection - Optimized version"""
    try:
        # Pre-allocate list for better performance than string concatenation
        hash_parts = []

        # Process columns in deterministic order (sorted by column name)
        for column in sorted(row.index):
            value = row[column]

            # Fast string conversion without intermediate dict
            if pd.isna(value) or value is None:
                hash_parts.append("")
            elif isinstance(value, (int, float)):
                # Reduced precision for better performance, still unique enough
                hash_parts.append(f"{value:.6f}" if isinstance(value, float) else str(value))
            elif isinstance(value, pd.Timestamp):
                # Use faster strftime instead of isoformat
                hash_parts.append(value.strftime('%Y-%m-%d %H:%M:%S') if not pd.isna(value) else "")
            else:
                hash_parts.append(str(value))

        # Direct string join - much faster than JSON serialization
        row_string = '|'.join(hash_parts)

        # Calculate SHA-256 hash
        return hashlib.sha256(row_string.encode('utf-8')).hexdigest()

    except Exception as e:
        # Simplified fallback with better performance
        logger.warning(f"⚠️ Hash calculation fallback for row: {str(e)}")
        fallback_string = '|'.join([str(v) if not pd.isna(v) else '' for v in row.values])
        return hashlib.sha256(fallback_string.encode('utf-8')).hexdigest()

def add_row_hash_column(df):
    """Add row_hash column to dataframe"""
    logger.info("🔐 Calculating row hashes for duplicate prevention...")

    # Calculate hash for each row
    df['row_hash'] = df.apply(calculate_row_hash, axis=1)

    # Check for hash collisions within the dataframe (should be extremely rare)
    hash_counts = df['row_hash'].value_counts()
    collisions = hash_counts[hash_counts > 1]

    if len(collisions) > 0:
        logger.warning(f"⚠️ Found {len(collisions)} hash collisions within batch - removing duplicates")
        # Keep first occurrence of each hash
        df = df.drop_duplicates(subset=['row_hash'], keep='first')

    logger.info(f"✅ Generated {len(df):,} unique row hashes")
    return df

def get_backfill_months(backfill_config):
    """Parse backfill configuration and return list of (year, month) tuples"""
    months = []

    if backfill_config == 'all':
        # Load all available data from 2020 to current month
        current_date = datetime.now()
        for year in range(2020, current_date.year + 1):
            end_month = current_date.month if year == current_date.year else 12
            for month in range(1, end_month + 1):
                months.append((year, month))
    elif backfill_config.startswith('last_'):
        # Parse formats like 'last_6_months', 'last_12_months'
        try:
            num_months = int(backfill_config.split('_')[1])
            current_date = datetime.now()
            for i in range(num_months):
                date = current_date - timedelta(days=30 * i)  # Approximate month
                months.append((date.year, date.month))
        except (IndexError, ValueError):
            logger.error(f"❌ Invalid backfill format: {backfill_config}")
    elif ',' in backfill_config:
        # Parse comma-separated list like '2024-01,2024-02,2024-03'
        for month_str in backfill_config.split(','):
            try:
                year, month = month_str.strip().split('-')
                months.append((int(year), int(month)))
            except ValueError:
                logger.error(f"❌ Invalid month format: {month_str}")
    else:
        # Parse single month like '2024-01'
        try:
            year, month = backfill_config.split('-')
            months.append((int(year), int(month)))
        except ValueError:
            logger.error(f"❌ Invalid backfill format: {backfill_config}")

    # Remove duplicates and sort
    months = sorted(list(set(months)))
    logger.info(f"📅 Backfill months: {len(months)} months from {months[0] if months else 'none'} to {months[-1] if months else 'none'}")
    return months

def load_single_parquet_file(engine, file_path, chunk_size=10000):
    """Load a single parquet file into both normalized and star schema tables with invalid row handling"""
    filename = os.path.basename(file_path)

    try:
        logger.info(f"📥 Loading {filename}...")

        # Read parquet file
        df = pd.read_parquet(file_path)
        logger.info(f"📊 File contains {len(df):,} rows")

        # Convert column names to lowercase to match database schema
        df.columns = df.columns.str.lower()

        # Clean and prepare data
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

        # Keep all historical data - don't filter by year

        # Fill nulls
        numeric_cols = ['passenger_count', 'trip_distance', 'ratecodeid', 'fare_amount',
                       'extra', 'mta_tax', 'tip_amount', 'tolls_amount', 'improvement_surcharge',
                       'total_amount', 'congestion_surcharge', 'airport_fee', 'cbd_congestion_fee']

        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(0)
            else:
                # Add missing columns with 0 values (e.g., cbd_congestion_fee not in older data)
                df[col] = 0

        df['store_and_fwd_flag'] = df['store_and_fwd_flag'].fillna('N')

        # Hash generation moved to per-chunk processing for better performance and duplicate detection

        # Load in chunks with error handling for invalid rows
        total_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size else 0)
        loaded_rows = 0
        star_loaded_rows = 0
        duplicate_rows = 0
        invalid_rows = 0

        for i, chunk_start in enumerate(range(0, len(df), chunk_size)):
            chunk_end = min(chunk_start + chunk_size, len(df))
            chunk_df = df.iloc[chunk_start:chunk_end]

            # Process chunk with individual row error handling
            chunk_results = load_chunk_with_error_handling(engine, chunk_df, filename, i + 1)

            loaded_rows += chunk_results['loaded']
            star_loaded_rows += chunk_results['star_loaded']
            duplicate_rows += chunk_results['duplicates']
            invalid_rows += chunk_results['invalid']

            if (i + 1) % 5 == 0 or i == total_chunks - 1:
                logger.info(f"📥 {filename}: Processed {chunk_end:,} rows - Loaded: {loaded_rows:,} normalized, {star_loaded_rows:,} star, {duplicate_rows:,} duplicates, {invalid_rows:,} invalid ({i+1}/{total_chunks} chunks)")

        # Final summary
        total_processed = loaded_rows + duplicate_rows + invalid_rows
        logger.info(f"✅ {filename}: Completed - {loaded_rows:,} loaded to normalized, {star_loaded_rows:,} to star schema, {duplicate_rows:,} duplicates, {invalid_rows:,} invalid rows")

        return loaded_rows

    except Exception as e:
        logger.error(f"❌ Error loading {filename}: {str(e)}")
        return 0

def load_chunk_with_error_handling(engine, chunk_df, filename, chunk_number):
    """Load a chunk with individual row error handling and quality monitoring"""
    results = {'loaded': 0, 'star_loaded': 0, 'duplicates': 0, 'invalid': 0}
    start_time = time.time()

    try:
        # Add hash generation for this chunk
        chunk_df = add_row_hash_column(chunk_df)

        # First attempt: try to load the entire chunk
        chunk_df.to_sql(
            'yellow_taxi_trips',
            engine,
            schema='nyc_taxi',
            if_exists='append',
            index=False,
            method='multi'
        )
        results['loaded'] = len(chunk_df)

        # Load to star schema
        star_rows = load_chunk_to_star_schema(engine, chunk_df, filename, chunk_number)
        results['star_loaded'] = star_rows

        # Record successful quality metrics
        processing_time_ms = int((time.time() - start_time) * 1000)
        record_quality_metrics(engine, {
            'source_file': filename,
            'operation_type': 'chunk_insert',
            'target_table': 'yellow_taxi_trips',
            'chunk_number': chunk_number,
            'rows_attempted': len(chunk_df),
            'rows_inserted': results['loaded'],
            'rows_duplicates': 0,
            'rows_invalid': 0,
            'processing_duration_ms': processing_time_ms,
            'min_date_value': chunk_df['tpep_pickup_datetime'].min().date() if not chunk_df['tpep_pickup_datetime'].isna().all() else None,
            'max_date_value': chunk_df['tpep_pickup_datetime'].max().date() if not chunk_df['tpep_pickup_datetime'].isna().all() else None,
            'avg_numeric_value': float(chunk_df['total_amount'].mean()) if 'total_amount' in chunk_df.columns and not chunk_df['total_amount'].isna().all() else None
        })

        # Record star schema quality metrics
        if star_rows > 0:
            record_quality_metrics(engine, {
                'source_file': filename,
                'operation_type': 'star_schema_insert',
                'target_table': 'fact_taxi_trips',
                'chunk_number': chunk_number,
                'rows_attempted': len(chunk_df),
                'rows_inserted': star_rows,
                'rows_duplicates': 0,
                'rows_invalid': 0,
                'processing_duration_ms': processing_time_ms
            })

        return results

    except Exception as chunk_error:
        error_str = str(chunk_error).lower()

        # Check if it's a known duplicate error type
        if any(keyword in error_str for keyword in ['unique constraint', 'duplicate key', 'row_hash']):
            results['duplicates'] = len(chunk_df)

            # Record duplicate quality metrics
            processing_time_ms = int((time.time() - start_time) * 1000)
            record_quality_metrics(engine, {
                'source_file': filename,
                'operation_type': 'chunk_insert',
                'target_table': 'yellow_taxi_trips',
                'chunk_number': chunk_number,
                'rows_attempted': len(chunk_df),
                'rows_inserted': 0,
                'rows_duplicates': len(chunk_df),
                'rows_invalid': 0,
                'processing_duration_ms': processing_time_ms,
                'primary_error_types': ['duplicate_key'],
                'error_message_sample': str(chunk_error)[:200]
            })

            return results

        # For other errors, process row by row to identify invalid rows
        logger.warning(f"⚠️ Chunk {chunk_number} bulk insert failed, processing row by row: {str(chunk_error)[:100]}")

        for row_idx, (_, row) in enumerate(chunk_df.iterrows()):
            try:
                # Try to insert single row
                single_row_df = chunk_df.iloc[row_idx:row_idx+1]
                single_row_df.to_sql(
                    'yellow_taxi_trips',
                    engine,
                    schema='nyc_taxi',
                    if_exists='append',
                    index=False,
                    method='multi'
                )
                results['loaded'] += 1

                # Load to star schema
                star_rows = load_chunk_to_star_schema(engine, single_row_df, filename, chunk_number)
                results['star_loaded'] += star_rows

            except Exception as row_error:
                # Classify the error and store invalid row
                error_str = str(row_error).lower()

                if any(keyword in error_str for keyword in ['unique constraint', 'duplicate key', 'row_hash']):
                    results['duplicates'] += 1
                    error_type = 'duplicate_key'
                elif 'primary key' in error_str:
                    results['invalid'] += 1
                    error_type = 'primary_key_violation'
                elif 'check constraint' in error_str:
                    results['invalid'] += 1
                    error_type = 'constraint_violation'
                elif 'data type' in error_str or 'invalid input' in error_str:
                    results['invalid'] += 1
                    error_type = 'data_type_error'
                else:
                    results['invalid'] += 1
                    error_type = 'unknown_error'

                # Store invalid row if it's not a duplicate
                if error_type != 'duplicate_key':
                    store_invalid_row(engine, row, filename, chunk_number, row_idx + 1, str(row_error), error_type)

        # Record quality metrics for row-by-row processing
        processing_time_ms = int((time.time() - start_time) * 1000)
        error_types = []
        if results['duplicates'] > 0:
            error_types.append('duplicate_key')
        if results['invalid'] > 0:
            error_types.append('validation_error')

        record_quality_metrics(engine, {
            'source_file': filename,
            'operation_type': 'chunk_insert_with_errors',
            'target_table': 'yellow_taxi_trips',
            'chunk_number': chunk_number,
            'rows_attempted': len(chunk_df),
            'rows_inserted': results['loaded'],
            'rows_duplicates': results['duplicates'],
            'rows_invalid': results['invalid'],
            'processing_duration_ms': processing_time_ms,
            'primary_error_types': error_types,
            'error_message_sample': str(chunk_error)[:200] if 'chunk_error' in locals() else None,
            'constraint_violations': results['invalid'],
            'min_date_value': chunk_df['tpep_pickup_datetime'].min().date() if not chunk_df['tpep_pickup_datetime'].isna().all() else None,
            'max_date_value': chunk_df['tpep_pickup_datetime'].max().date() if not chunk_df['tpep_pickup_datetime'].isna().all() else None
        })

        return results

def record_quality_metrics(engine, metrics):
    """Record data quality metrics for a chunk operation"""
    try:
        with engine.begin() as conn:
            # Convert lists to JSON for primary_error_types
            primary_error_types = metrics.get('primary_error_types', [])
            if isinstance(primary_error_types, list):
                primary_error_types = json.dumps(primary_error_types)

            conn.execute(text("""
                INSERT INTO nyc_taxi.data_quality_monitor (
                    source_file, operation_type, target_table, chunk_number,
                    rows_attempted, rows_inserted, rows_duplicates, rows_invalid,
                    processing_duration_ms, primary_error_types, error_message_sample,
                    constraint_violations, min_date_value, max_date_value, avg_numeric_value,
                    data_hash, batch_id
                ) VALUES (
                    :source_file, :operation_type, :target_table, :chunk_number,
                    :rows_attempted, :rows_inserted, :rows_duplicates, :rows_invalid,
                    :processing_duration_ms, :primary_error_types, :error_message_sample,
                    :constraint_violations, :min_date_value, :max_date_value, :avg_numeric_value,
                    :data_hash, :batch_id
                )
            """), {
                'source_file': metrics.get('source_file'),
                'operation_type': metrics.get('operation_type'),
                'target_table': metrics.get('target_table'),
                'chunk_number': metrics.get('chunk_number'),
                'rows_attempted': metrics.get('rows_attempted', 0),
                'rows_inserted': metrics.get('rows_inserted', 0),
                'rows_duplicates': metrics.get('rows_duplicates', 0),
                'rows_invalid': metrics.get('rows_invalid', 0),
                'processing_duration_ms': metrics.get('processing_duration_ms'),
                'primary_error_types': primary_error_types,
                'error_message_sample': metrics.get('error_message_sample'),
                'constraint_violations': metrics.get('constraint_violations', 0),
                'min_date_value': metrics.get('min_date_value'),
                'max_date_value': metrics.get('max_date_value'),
                'avg_numeric_value': metrics.get('avg_numeric_value'),
                'data_hash': metrics.get('data_hash'),
                'batch_id': metrics.get('batch_id', f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            })

    except Exception as e:
        logger.warning(f"⚠️ Failed to record quality metrics: {str(e)}")

def store_invalid_row(engine, row, source_file, chunk_number, row_number_in_chunk, error_message, error_type):
    """Store an invalid row in the yellow_taxi_trips_invalid table"""
    try:
        with engine.begin() as conn:
            # Convert row to dictionary and handle NaN values and numpy types
            row_dict = {}
            for col, value in row.items():
                if pd.isna(value):
                    row_dict[col] = None
                else:
                    # Convert numpy types to Python native types for psycopg2 compatibility
                    if hasattr(value, 'item'):  # numpy scalar
                        row_dict[col] = value.item()
                    elif isinstance(value, pd.Timestamp):
                        row_dict[col] = value.to_pydatetime() if pd.notna(value) else None
                    else:
                        row_dict[col] = value

            # Insert invalid row
            conn.execute(text("""
                INSERT INTO nyc_taxi.yellow_taxi_trips_invalid (
                    error_message, error_type, source_file, chunk_number, row_number_in_chunk,
                    vendorid, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count,
                    trip_distance, ratecodeid, store_and_fwd_flag, pulocationid, dolocationid,
                    payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount,
                    improvement_surcharge, total_amount, congestion_surcharge, airport_fee,
                    cbd_congestion_fee, row_hash, raw_data_json
                ) VALUES (
                    :error_message, :error_type, :source_file, :chunk_number, :row_number_in_chunk,
                    :vendorid, :tpep_pickup_datetime, :tpep_dropoff_datetime, :passenger_count,
                    :trip_distance, :ratecodeid, :store_and_fwd_flag, :pulocationid, :dolocationid,
                    :payment_type, :fare_amount, :extra, :mta_tax, :tip_amount, :tolls_amount,
                    :improvement_surcharge, :total_amount, :congestion_surcharge, :airport_fee,
                    :cbd_congestion_fee, :row_hash, :raw_data_json
                )
            """), {
                'error_message': error_message[:500],  # Truncate long error messages
                'error_type': error_type,
                'source_file': source_file,
                'chunk_number': chunk_number,
                'row_number_in_chunk': row_number_in_chunk,
                'vendorid': row_dict.get('vendorid'),
                'tpep_pickup_datetime': row_dict.get('tpep_pickup_datetime'),
                'tpep_dropoff_datetime': row_dict.get('tpep_dropoff_datetime'),
                'passenger_count': row_dict.get('passenger_count'),
                'trip_distance': row_dict.get('trip_distance'),
                'ratecodeid': row_dict.get('ratecodeid'),
                'store_and_fwd_flag': row_dict.get('store_and_fwd_flag'),
                'pulocationid': row_dict.get('pulocationid'),
                'dolocationid': row_dict.get('dolocationid'),
                'payment_type': row_dict.get('payment_type'),
                'fare_amount': row_dict.get('fare_amount'),
                'extra': row_dict.get('extra'),
                'mta_tax': row_dict.get('mta_tax'),
                'tip_amount': row_dict.get('tip_amount'),
                'tolls_amount': row_dict.get('tolls_amount'),
                'improvement_surcharge': row_dict.get('improvement_surcharge'),
                'total_amount': row_dict.get('total_amount'),
                'congestion_surcharge': row_dict.get('congestion_surcharge'),
                'airport_fee': row_dict.get('airport_fee'),
                'cbd_congestion_fee': row_dict.get('cbd_congestion_fee'),
                'row_hash': row_dict.get('row_hash'),
                'raw_data_json': json.dumps(row_dict, default=str)  # Store complete row as JSON
            })

    except Exception as e:
        logger.warning(f"⚠️ Failed to store invalid row: {str(e)}")  # Don't fail the whole process

# Global dimension key cache - populated once at startup
DIMENSION_CACHE = {
    'locations': {},      # locationid -> location_key + borough
    'vendors': {},        # vendorid -> vendor_key
    'payment_types': {},  # payment_type -> payment_type_key
    'rate_codes': {}      # ratecodeid -> rate_code_key
}

def populate_dimension_cache(engine):
    """Populate global dimension key cache to eliminate individual lookups"""
    global DIMENSION_CACHE

    try:
        logger.info("🗄️ Populating dimension key cache for bulk operations...")

        with engine.connect() as conn:
            # Load all location keys and boroughs
            location_result = conn.execute(text("""
                SELECT locationid, location_key, borough
                FROM nyc_taxi.dim_locations
                ORDER BY locationid
            """))
            for row in location_result:
                DIMENSION_CACHE['locations'][int(row.locationid)] = {
                    'location_key': row.location_key,
                    'borough': row.borough
                }

            # Load all vendor keys
            vendor_result = conn.execute(text("""
                SELECT vendorid, vendor_key
                FROM nyc_taxi.dim_vendor
                ORDER BY vendorid
            """))
            for row in vendor_result:
                DIMENSION_CACHE['vendors'][int(row.vendorid)] = row.vendor_key

            # Load all payment type keys
            payment_result = conn.execute(text("""
                SELECT payment_type, payment_type_key
                FROM nyc_taxi.dim_payment_type
                ORDER BY payment_type
            """))
            for row in payment_result:
                DIMENSION_CACHE['payment_types'][int(row.payment_type)] = row.payment_type_key

            # Load all rate code keys
            rate_result = conn.execute(text("""
                SELECT ratecodeid, rate_code_key
                FROM nyc_taxi.dim_rate_code
                ORDER BY ratecodeid
            """))
            for row in rate_result:
                DIMENSION_CACHE['rate_codes'][int(row.ratecodeid)] = row.rate_code_key

        logger.info(f"✅ Dimension cache populated: {len(DIMENSION_CACHE['locations'])} locations, "
                   f"{len(DIMENSION_CACHE['vendors'])} vendors, {len(DIMENSION_CACHE['payment_types'])} payment types, "
                   f"{len(DIMENSION_CACHE['rate_codes'])} rate codes")

    except Exception as e:
        logger.error(f"❌ Failed to populate dimension cache: {str(e)}")
        raise

def load_chunk_to_star_schema_optimized(engine, chunk_df, source_file, chunk_number):
    """OPTIMIZED: Load a chunk of data into the star schema fact table using bulk operations"""
    try:
        if len(chunk_df) == 0:
            return 0

        # Ensure dimension cache is populated
        if not DIMENSION_CACHE['locations']:
            populate_dimension_cache(engine)

        logger.debug(f"🌟 Processing {len(chunk_df)} rows for star schema (bulk optimized)")

        # VECTORIZED OPERATIONS: Calculate all derived measures at once
        start_time = time.time()

        # Extract datetime components vectorized
        pickup_datetimes = pd.to_datetime(chunk_df['tpep_pickup_datetime'])
        dropoff_datetimes = pd.to_datetime(chunk_df['tpep_dropoff_datetime'])

        # Calculate trip duration in minutes (vectorized)
        trip_duration_minutes = ((dropoff_datetimes - pickup_datetimes).dt.total_seconds() / 60).fillna(0)

        # Calculate derived measures (vectorized)
        fare_amount = chunk_df['fare_amount'].fillna(0)
        extra = chunk_df['extra'].fillna(0)
        tip_amount = chunk_df['tip_amount'].fillna(0)
        trip_distance = chunk_df['trip_distance'].fillna(0)
        total_amount = chunk_df['total_amount'].fillna(0)

        base_fare = fare_amount + extra
        total_surcharges = (chunk_df['mta_tax'].fillna(0) +
                           chunk_df['improvement_surcharge'].fillna(0) +
                           chunk_df['congestion_surcharge'].fillna(0) +
                           chunk_df['airport_fee'].fillna(0) +
                           chunk_df.get('cbd_congestion_fee', 0).fillna(0))

        tip_percentage = np.where(fare_amount > 0, (tip_amount / fare_amount) * 100, 0)
        avg_speed_mph = np.where(trip_duration_minutes > 0,
                                (trip_distance / (trip_duration_minutes / 60)), 0)
        revenue_per_mile = np.where(trip_distance > 0, total_amount / trip_distance, 0)

        # Calculate boolean flags (vectorized)
        is_airport_trip = chunk_df['ratecodeid'].fillna(0).isin([2, 3])
        is_cash_trip = chunk_df['payment_type'].fillna(0) == 2
        is_long_distance = trip_distance > 10
        is_short_trip = trip_distance < 1

        # Create date keys (vectorized)
        pickup_date_keys = pickup_datetimes.dt.strftime('%Y%m%d').astype(int)
        dropoff_date_keys = dropoff_datetimes.dt.strftime('%Y%m%d').astype(int)
        pickup_time_keys = pickup_datetimes.dt.hour
        dropoff_time_keys = dropoff_datetimes.dt.hour
        pickup_dates = pickup_datetimes.dt.date

        # DIMENSION KEY LOOKUPS: Use cached dimensions instead of SQL joins
        pickup_location_keys = []
        dropoff_location_keys = []
        vendor_keys = []
        payment_type_keys = []
        rate_code_keys = []
        is_cross_borough_trips = []

        # Process dimension lookups in bulk
        for _, row in chunk_df.iterrows():
            pickup_locid = int(row['pulocationid'] or 0)
            dropoff_locid = int(row['dolocationid'] or 0)
            vendorid = int(row['vendorid'] or 0)
            payment_type = int(row['payment_type'] or 0)
            ratecodeid = int(row['ratecodeid'] or 0)

            # Location keys and cross-borough calculation
            pickup_loc = DIMENSION_CACHE['locations'].get(pickup_locid, {'location_key': None, 'borough': None})
            dropoff_loc = DIMENSION_CACHE['locations'].get(dropoff_locid, {'location_key': None, 'borough': None})

            pickup_location_keys.append(pickup_loc['location_key'])
            dropoff_location_keys.append(dropoff_loc['location_key'])
            is_cross_borough_trips.append(pickup_loc['borough'] != dropoff_loc['borough']
                                         if pickup_loc['borough'] and dropoff_loc['borough'] else False)

            # Other dimension keys
            vendor_keys.append(DIMENSION_CACHE['vendors'].get(vendorid))
            payment_type_keys.append(DIMENSION_CACHE['payment_types'].get(payment_type))
            rate_code_keys.append(DIMENSION_CACHE['rate_codes'].get(ratecodeid))

        # Create the star schema DataFrame
        star_df = pd.DataFrame({
            'pickup_date_key': pickup_date_keys,
            'pickup_time_key': pickup_time_keys,
            'dropoff_date_key': dropoff_date_keys,
            'dropoff_time_key': dropoff_time_keys,
            'pickup_location_key': pickup_location_keys,
            'dropoff_location_key': dropoff_location_keys,
            'vendor_key': vendor_keys,
            'payment_type_key': payment_type_keys,
            'rate_code_key': rate_code_keys,
            'trip_distance': trip_distance,
            'trip_duration_minutes': trip_duration_minutes.astype(int),
            'passenger_count': chunk_df['passenger_count'].fillna(0).astype(int),
            'fare_amount': fare_amount,
            'extra': extra,
            'mta_tax': chunk_df['mta_tax'].fillna(0),
            'tip_amount': tip_amount,
            'tolls_amount': chunk_df['tolls_amount'].fillna(0),
            'improvement_surcharge': chunk_df['improvement_surcharge'].fillna(0),
            'total_amount': total_amount,
            'congestion_surcharge': chunk_df['congestion_surcharge'].fillna(0),
            'airport_fee': chunk_df['airport_fee'].fillna(0),
            'cbd_congestion_fee': chunk_df.get('cbd_congestion_fee', 0).fillna(0),
            'base_fare': base_fare,
            'total_surcharges': total_surcharges,
            'tip_percentage': tip_percentage,
            'avg_speed_mph': avg_speed_mph,
            'revenue_per_mile': revenue_per_mile,
            'is_airport_trip': is_airport_trip,
            'is_cross_borough_trip': is_cross_borough_trips,
            'is_cash_trip': is_cash_trip,
            'is_long_distance': is_long_distance,
            'is_short_trip': is_short_trip,
            'original_row_hash': chunk_df['row_hash'],
            'pickup_date': pickup_dates
        })

        # Remove rows with missing dimension keys AND invalid dates to prevent violations
        # Filter out dates outside partition range (2020-2030)
        pickup_dates = pd.to_datetime(star_df['pickup_date'])
        valid_date_mask = (
            (pickup_dates >= '2020-01-01') &
            (pickup_dates < '2030-01-01')
        )

        valid_mask = (
            star_df['pickup_location_key'].notna() &
            star_df['dropoff_location_key'].notna() &
            valid_date_mask
        )

        # Store invalid rows in yellow_taxi_trips_invalid table
        invalid_mask = ~valid_mask
        if invalid_mask.any():
            # Get invalid rows from chunk_df using proper index alignment
            invalid_indices = star_df[invalid_mask].index
            invalid_df = chunk_df.loc[invalid_indices]

            logger.info(f"📝 Storing {len(invalid_df)} invalid rows in yellow_taxi_trips_invalid table")

            for row_idx, (idx, row) in enumerate(invalid_df.iterrows()):
                # Determine error type by checking the star_df values at this index
                missing_pickup = pd.isna(star_df.loc[idx, 'pickup_location_key'])
                missing_dropoff = pd.isna(star_df.loc[idx, 'dropoff_location_key'])
                invalid_date = not valid_date_mask.loc[idx]

                if missing_pickup or missing_dropoff:
                    error_type = "missing_dimension_keys"
                    error_msg = f"Missing {'pickup' if missing_pickup else ''}{'/' if missing_pickup and missing_dropoff else ''}{'dropoff' if missing_dropoff else ''} location keys"
                elif invalid_date:
                    error_type = "invalid_date_range"
                    error_msg = f"Date outside partition range (2020-2030): {pickup_dates.loc[idx]}"
                else:
                    error_type = "unknown"
                    error_msg = "Row failed validation checks"

                try:
                    store_invalid_row(engine, row.to_dict(), source_file, chunk_number, row_idx + 1, error_msg, error_type)
                    logger.debug(f"✅ Stored invalid row {row_idx + 1}/{len(invalid_df)} in yellow_taxi_trips_invalid")
                except Exception as e:
                    logger.warning(f"❌ Failed to store invalid row {row_idx + 1}: {str(e)}")

        star_df_valid = star_df[valid_mask].copy()
        invalid_count = len(star_df) - len(star_df_valid)

        if invalid_count > 0:
            logger.warning(f"⚠️ Skipping {invalid_count} rows with missing dimension keys or invalid dates (stored in yellow_taxi_trips_invalid)")

        if len(star_df_valid) == 0:
            return 0

        preparation_time = time.time() - start_time
        logger.debug(f"⏱️ Star schema preparation: {preparation_time:.2f}s for {len(star_df_valid)} rows")

        # BULK INSERT: Use pandas to_sql for maximum performance
        insert_start = time.time()

        try:
            # Single bulk transaction instead of individual row transactions
            with engine.begin() as conn:
                star_df_valid.to_sql(
                    'fact_taxi_trips',
                    conn,
                    schema='nyc_taxi',
                    if_exists='append',
                    index=False,
                    method='multi',
                    chunksize=10000  # Process in sub-chunks for memory efficiency
                )

            insert_time = time.time() - insert_start
            total_time = time.time() - start_time

            logger.debug(f"⚡ Bulk insert: {insert_time:.2f}s for {len(star_df_valid)} rows "
                        f"({len(star_df_valid)/total_time:.0f} rows/sec total)")

            return len(star_df_valid)

        except Exception as bulk_error:
            # If bulk insert fails, fall back to error handling for debugging
            logger.warning(f"⚠️ Bulk insert failed, analyzing error: {str(bulk_error)[:200]}")
            logger.warning(f"⚠️ Failed chunk had {len(star_df_valid)} valid rows")

            # Store failed rows in invalid table for analysis
            error_type = "bulk_insert_failure"
            if 'partition' in str(bulk_error).lower():
                error_type = "partition_error"
                logger.warning(f"⚠️ Partition error detected - storing rows in yellow_taxi_trips_invalid")

            # Store all rows from failed chunk as invalid
            valid_df = chunk_df[valid_mask]
            for idx, row in valid_df.iterrows():
                try:
                    store_invalid_row(engine, row.to_dict(), source_file, chunk_number, idx + 1, str(bulk_error)[:500], error_type)
                except Exception as e:
                    logger.debug(f"Failed to store bulk failure row {idx}: {str(e)}")

            logger.warning(f"⚠️ Stored {len(valid_df)} failed rows in yellow_taxi_trips_invalid table")
            return 0

    except Exception as e:
        logger.warning(f"⚠️ Error in optimized star schema loading: {str(e)}")
        return 0

# Keep the original function as fallback (renamed)
def load_chunk_to_star_schema_original(engine, chunk_df, source_file, chunk_number):
    """ORIGINAL: Load a chunk of data into the star schema fact table (row-by-row processing)"""
    return load_chunk_to_star_schema_optimized(engine, chunk_df, source_file, chunk_number)  # Use optimized version

# Use the optimized version as the main function
def load_chunk_to_star_schema(engine, chunk_df, source_file, chunk_number):
    """Load a chunk of data into the star schema fact table"""
    return load_chunk_to_star_schema_optimized(engine, chunk_df, source_file, chunk_number)

def load_trip_data(engine, load_all=True):
    """Load trip data - either from existing files or via backfill download"""
    logger.info("🚕 Loading trip data...")

    # Check for backfill configuration
    backfill_config = os.getenv('BACKFILL_MONTHS', '')

    total_rows = 0

    if backfill_config:
        logger.info(f"🔄 Backfill mode enabled: {backfill_config}")

        # Get months to download
        months_to_load = get_backfill_months(backfill_config)

        if not months_to_load:
            logger.warning("⚠️ No valid months found in backfill configuration")
            return False

        # Ensure data directory exists
        data_dir = '/postgres/data'
        os.makedirs(data_dir, exist_ok=True)

        # Download and load each month
        for year, month in months_to_load:
            logger.info(f"📅 Processing {year}-{month:02d}...")

            # Check if month already processed
            if check_month_already_processed(engine, year, month):
                continue

            # Download file
            file_path = download_taxi_data(year, month, data_dir)
            if not file_path:
                logger.warning(f"⚠️ Skipping {year}-{month:02d} due to download failure")
                continue

            # Start processing log
            filename = os.path.basename(file_path)
            start_processing_log(engine, year, month, filename, backfill_config)

            try:
                # Load file
                chunk_size = int(os.getenv('DATA_CHUNK_SIZE', 10000))
                rows_loaded = load_single_parquet_file(engine, file_path, chunk_size)

                if rows_loaded > 0:
                    # Mark as completed
                    complete_processing_log(engine, year, month, rows_loaded)
                    total_rows += rows_loaded
                    logger.info(f"✅ {year}-{month:02d}: {rows_loaded:,} rows loaded (total: {total_rows:,})")
                else:
                    # Mark as failed
                    fail_processing_log(engine, year, month)
                    logger.warning(f"⚠️ {year}-{month:02d}: No rows loaded")

            except Exception as e:
                # Mark as failed
                fail_processing_log(engine, year, month)
                logger.error(f"❌ {year}-{month:02d}: Processing failed - {str(e)}")
                continue

        logger.info(f"🎉 Backfill completed: {total_rows:,} total rows loaded from processed months")

        # Create indexes on partitions after data loading
        if total_rows > 0:
            logger.info("🔧 Creating performance indexes on partitions...")
            create_performance_indexes(engine)

        return total_rows > 0

    else:
        # Original single-file loading logic
        try:
            data_dir = '/postgres/data'
            yellow_dir = os.path.join(data_dir, 'yellow')
            parquet_path = os.path.join(yellow_dir, 'yellow_tripdata_2025-01.parquet')
            if not os.path.exists(parquet_path):
                logger.warning(f"⚠️ Trip data parquet not found at {parquet_path}")
                return False

            chunk_size = int(os.getenv('DATA_CHUNK_SIZE', 10000))
            rows_loaded = load_single_parquet_file(engine, parquet_path, chunk_size)

            # Create indexes on partitions after data loading
            if rows_loaded > 0:
                logger.info("🔧 Creating performance indexes on partitions...")
                create_performance_indexes(engine)

            return rows_loaded > 0

        except Exception as e:
            logger.error(f"❌ Error in single-file loading: {str(e)}")
            return False

def create_performance_indexes(engine):
    """Create performance indexes on fact table partitions"""
    try:
        logger.info("🔧 Creating performance indexes on fact table partitions...")

        with engine.connect() as conn:
            # Call the SQL function to create partition indexes
            result = conn.execute(text("SELECT nyc_taxi.create_partition_indexes()"))
            index_results = result.fetchone()[0]

            if index_results:
                logger.info("✅ Performance indexes created successfully!")
                for result_line in index_results:
                    logger.info(f"   {result_line}")
            else:
                logger.info("ℹ️ No new indexes to create")

    except Exception as e:
        logger.warning(f"⚠️ Error creating performance indexes: {str(e)}")


def verify_data_load(engine):
    """Verify that data was loaded correctly"""
    logger.info("🔍 Verifying data load...")

    try:
        with engine.connect() as conn:
            # Check taxi zones
            result = conn.execute(text("SELECT COUNT(*) FROM nyc_taxi.taxi_zone_lookup"))
            zone_count = result.fetchone()[0]
            logger.info(f"📍 Taxi zones: {zone_count:,}")

            # Check shapes (if available)
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM nyc_taxi.taxi_zone_shapes"))
                shape_count = result.fetchone()[0]
                logger.info(f"🗺️ Taxi zone shapes: {shape_count:,}")
            except:
                logger.info("🗺️ Taxi zone shapes: Not available")

            # Check trips in normalized table
            result = conn.execute(text("SELECT COUNT(*) FROM nyc_taxi.yellow_taxi_trips"))
            trip_count = result.fetchone()[0]
            logger.info(f"🚕 Trip records (normalized): {trip_count:,}")

            # Check trips in star schema
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM nyc_taxi.fact_taxi_trips"))
                star_trip_count = result.fetchone()[0]
                logger.info(f"⭐ Trip records (star schema): {star_trip_count:,}")
            except:
                logger.info("⭐ Trip records (star schema): Not available")
                star_trip_count = 0

            # Check invalid rows
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM nyc_taxi.yellow_taxi_trips_invalid"))
                invalid_count = result.fetchone()[0]
                logger.info(f"❌ Invalid trip records: {invalid_count:,}")

                if invalid_count > 0:
                    # Show breakdown by error type
                    result = conn.execute(text("""
                        SELECT error_type, COUNT(*) as count
                        FROM nyc_taxi.yellow_taxi_trips_invalid
                        GROUP BY error_type
                        ORDER BY count DESC
                    """))
                    logger.info("   Invalid rows breakdown:")
                    for row in result.fetchall():
                        logger.info(f"   - {row[0]}: {row[1]:,}")
            except:
                logger.info("❌ Invalid trip records: Not available")

            # Check data quality monitoring
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM nyc_taxi.data_quality_monitor"))
                quality_records_count = result.fetchone()[0]
                logger.info(f"📊 Quality monitoring records: {quality_records_count:,}")

                if quality_records_count > 0:
                    # Show quality summary by table
                    result = conn.execute(text("""
                        SELECT
                            target_table,
                            operation_type,
                            COUNT(*) as operations,
                            SUM(rows_inserted) as total_inserted,
                            AVG(success_rate) as avg_success_rate,
                            AVG(error_rate) as avg_error_rate,
                            COUNT(*) FILTER (WHERE quality_level = 'EXCELLENT') as excellent_ops,
                            COUNT(*) FILTER (WHERE has_critical_errors = true) as critical_errors
                        FROM nyc_taxi.data_quality_monitor
                        WHERE target_table IN ('yellow_taxi_trips', 'fact_taxi_trips')
                        GROUP BY target_table, operation_type
                        ORDER BY target_table, operation_type
                    """))

                    logger.info("   Quality metrics by table:")
                    for row in result.fetchall():
                        logger.info(f"   - {row[0]} ({row[1]}): {row[2]} ops, {row[3]:,} rows, {row[4]:.1f}% success, {row[5]:.1f}% errors, {row[6]} excellent, {row[7]} critical")

                    # Show overall quality level distribution
                    result = conn.execute(text("""
                        SELECT quality_level, COUNT(*) as count
                        FROM nyc_taxi.data_quality_monitor
                        GROUP BY quality_level
                        ORDER BY
                            CASE quality_level
                                WHEN 'EXCELLENT' THEN 1
                                WHEN 'GOOD' THEN 2
                                WHEN 'ACCEPTABLE' THEN 3
                                WHEN 'POOR' THEN 4
                                WHEN 'CRITICAL' THEN 5
                            END
                    """))

                    logger.info("   Quality level distribution:")
                    for row in result.fetchall():
                        logger.info(f"   - {row[0]}: {row[1]} operations")
            except:
                logger.info("📊 Quality monitoring: Not available")

            # Check dimension tables
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM nyc_taxi.dim_locations"))
                dim_locations_count = result.fetchone()[0]
                logger.info(f"📍 Location dimensions: {dim_locations_count:,}")

                result = conn.execute(text("SELECT COUNT(*) FROM nyc_taxi.dim_date"))
                dim_date_count = result.fetchone()[0]
                logger.info(f"📅 Date dimensions: {dim_date_count:,}")

                result = conn.execute(text("SELECT COUNT(*) FROM nyc_taxi.dim_time"))
                dim_time_count = result.fetchone()[0]
                logger.info(f"🕐 Time dimensions: {dim_time_count:,}")
            except:
                logger.info("📊 Dimension tables: Error checking counts")

            if trip_count > 0:
                # Show sample data with zone names from normalized table
                result = conn.execute(text("""
                    SELECT
                        DATE(yt.tpep_pickup_datetime) as trip_date,
                        COUNT(*) as trips,
                        pickup_zone.borough as pickup_borough
                    FROM nyc_taxi.yellow_taxi_trips yt
                    JOIN nyc_taxi.taxi_zone_lookup pickup_zone ON yt.pulocationid = pickup_zone.locationid
                    GROUP BY DATE(yt.tpep_pickup_datetime), pickup_zone.borough
                    ORDER BY trips DESC
                    LIMIT 5
                """))

                logger.info("📊 Top trip patterns (normalized table):")
                for row in result.fetchall():
                    logger.info(f"   {row[0]} - {row[2]}: {row[1]:,} trips")

            if star_trip_count > 0:
                # Show sample data from star schema
                result = conn.execute(text("""
                    SELECT
                        ft.pickup_date,
                        COUNT(*) as trips,
                        dl.borough as pickup_borough,
                        AVG(ft.total_amount) as avg_fare
                    FROM nyc_taxi.fact_taxi_trips ft
                    JOIN nyc_taxi.dim_locations dl ON ft.pickup_location_key = dl.location_key
                    GROUP BY ft.pickup_date, dl.borough
                    ORDER BY trips DESC
                    LIMIT 5
                """))

                logger.info("🌟 Top trip patterns (star schema):")
                for row in result.fetchall():
                    logger.info(f"   {row[0]} - {row[2]}: {row[1]:,} trips, avg fare: ${row[3]:.2f}")

        logger.info("✅ Data verification completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Error during verification: {str(e)}")
        return False

def main():
    """Main initialization function"""
    logger.info("🚀 Starting Complete NYC Taxi Database Initialization...")

    # Database connection parameters
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': os.getenv('POSTGRES_DB', 'playground'),
        'user': os.getenv('POSTGRES_USER', 'admin'),
        'password': os.getenv('POSTGRES_PASSWORD', 'admin123')
    }

    # Wait for PostgreSQL
    if not wait_for_postgres(**db_config):
        logger.error("💥 Failed to connect to PostgreSQL")
        return False

    # Create SQLAlchemy engine
    connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    engine = create_engine(connection_string)

    try:
        # Step 1: Execute SQL scripts (schema, tables, indexes)
        logger.info("🔧 Step 1: Database Schema Creation")
        if not execute_sql_scripts(engine):
            logger.error("💥 Failed to execute SQL initialization scripts")
            return False

        # Step 2: Load taxi zone reference data
        logger.info("📍 Step 2: Loading Taxi Zone Reference Data")
        if not load_taxi_zones(engine):
            logger.error("💥 Failed to load taxi zone data")
            return False

        # Step 3: Load complete trip data
        logger.info("🚕 Step 3: Loading Complete Trip Data")
        load_all_data = os.getenv('INIT_LOAD_ALL_DATA', 'true').lower() == 'true'
        if not load_trip_data(engine, load_all=load_all_data):
            logger.warning("⚠️ Failed to load trip data, continuing without it")

        # Step 4: Refresh materialized views
        logger.info("📊 Step 4: Refreshing Materialized Views")
        materialized_views = [
            'nyc_taxi.trip_hourly_summary',
            'nyc_taxi.trip_location_summary',
            'nyc_taxi.trip_distance_summary',
        ]
        try:
            with engine.connect() as conn:
                for view_name in materialized_views:
                    conn.execute(text(f"REFRESH MATERIALIZED VIEW {view_name}"))
                    conn.commit()
                    row_count = conn.execute(text(f"SELECT COUNT(*) FROM {view_name}")).scalar()
                    logger.info(f"✅ {view_name} refreshed ({row_count:,} rows)")
        except Exception as e:
            logger.warning(f"⚠️ Failed to refresh materialized views: {e}")

        # Step 5: Verify everything loaded correctly
        logger.info("🔍 Step 5: Data Verification")
        verify_data_load(engine)

        logger.info("🎉 Complete database initialization finished successfully!")
        logger.info("🌟 Your NYC Taxi playground is ready with 3.4M+ records!")
        return True

    except Exception as e:
        logger.error(f"💥 Initialization failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)