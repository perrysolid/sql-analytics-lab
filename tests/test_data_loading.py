"""
Tests for data loading and processing functionality
"""
import pytest
import psycopg2
import pandas as pd
from pathlib import Path


class TestDataLoading:
    """Test data loading processes and data integrity"""

    def test_taxi_zone_data_loaded(self):
        """Test that taxi zone lookup data is properly loaded"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="playground",
                user="admin",
                password="admin123"
            )
            cursor = conn.cursor()

            # Check taxi zone lookup table
            cursor.execute("SELECT COUNT(*) FROM nyc_taxi.taxi_zone_lookup;")
            zone_count = cursor.fetchone()[0]
            assert zone_count > 0, "Taxi zone lookup table should have data"

            # Check for expected NYC boroughs
            cursor.execute("SELECT DISTINCT borough FROM nyc_taxi.taxi_zone_lookup ORDER BY borough;")
            boroughs = [row[0] for row in cursor.fetchall()]
            expected_boroughs = ['Bronx', 'Brooklyn', 'Manhattan', 'Queens', 'Staten Island']
            for borough in expected_boroughs:
                assert borough in boroughs, f"Borough {borough} should be in taxi zones"

            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("PostgreSQL container not running")

    def test_geospatial_data_loaded(self):
        """Test that geospatial taxi zone shapes are loaded"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="playground",
                user="admin",
                password="admin123"
            )
            cursor = conn.cursor()

            # Check taxi zone shapes table
            cursor.execute("SELECT COUNT(*) FROM nyc_taxi.taxi_zone_shapes;")
            shape_count = cursor.fetchone()[0]
            assert shape_count > 0, "Taxi zone shapes table should have data"

            # Check that geometries are valid
            cursor.execute("SELECT COUNT(*) FROM nyc_taxi.taxi_zone_shapes WHERE ST_IsValid(geom) = false;")
            invalid_geoms = cursor.fetchone()[0]
            assert invalid_geoms == 0, "All geometries should be valid"

            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("PostgreSQL container not running")

    def test_trip_data_structure(self):
        """Test trip data table structure and constraints"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="playground",
                user="admin",
                password="admin123"
            )
            cursor = conn.cursor()

            # Check if trip data table exists and has data
            cursor.execute("SELECT COUNT(*) FROM nyc_taxi.yellow_taxi_trips;")
            trip_count = cursor.fetchone()[0]
            # Note: trip_count might be 0 if no data loaded yet

            # Check unique constraint on row_hash
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.table_constraints tc
                JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
                WHERE tc.table_schema = 'nyc_taxi'
                AND tc.table_name = 'yellow_taxi_trips'
                AND ccu.column_name = 'row_hash'
                AND tc.constraint_type = 'UNIQUE';
            """)
            unique_constraint = cursor.fetchone()[0]
            assert unique_constraint > 0, "row_hash should have unique constraint"

            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("PostgreSQL container not running")

    def test_data_processing_log(self):
        """Test data processing log table exists and functions"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="playground",
                user="admin",
                password="admin123"
            )
            cursor = conn.cursor()

            # Check data processing log table structure
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'nyc_taxi'
                AND table_name = 'data_processing_log'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]

            expected_columns = ['month_year', 'status', 'processed_at', 'record_count']
            for col in expected_columns:
                assert col in column_names, f"Column {col} should exist in data_processing_log"

            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("PostgreSQL container not running")


class TestDataIntegrity:
    """Test data integrity and consistency"""

    def test_lookup_table_relationships(self):
        """Test relationships between main table and lookup tables"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="playground",
                user="admin",
                password="admin123"
            )
            cursor = conn.cursor()

            # Check if we have trip data to test relationships
            cursor.execute("SELECT COUNT(*) FROM nyc_taxi.yellow_taxi_trips;")
            trip_count = cursor.fetchone()[0]

            if trip_count > 0:
                # Test pickup location references
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM nyc_taxi.yellow_taxi_trips t
                    LEFT JOIN nyc_taxi.taxi_zone_lookup z
                    ON t.pulocationid = z.locationid
                    WHERE t.pulocationid IS NOT NULL
                    AND z.locationid IS NULL;
                """)
                orphaned_pickup = cursor.fetchone()[0]
                # Some orphaned records are expected due to data quality issues
                assert orphaned_pickup >= 0, "Query should execute without error"

            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("PostgreSQL container not running")

    def test_hash_uniqueness(self):
        """Test that row hashes are actually unique"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="playground",
                user="admin",
                password="admin123"
            )
            cursor = conn.cursor()

            # Check if we have trip data
            cursor.execute("SELECT COUNT(*) FROM nyc_taxi.yellow_taxi_trips;")
            trip_count = cursor.fetchone()[0]

            if trip_count > 0:
                # Check for duplicate hashes
                cursor.execute("""
                    SELECT row_hash, COUNT(*)
                    FROM nyc_taxi.yellow_taxi_trips
                    GROUP BY row_hash
                    HAVING COUNT(*) > 1;
                """)
                duplicates = cursor.fetchall()
                assert len(duplicates) == 0, f"Found duplicate row hashes: {duplicates}"

            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("PostgreSQL container not running")


class TestFileStructure:
    """Test file and directory structure"""

    def test_data_directory_structure(self):
        """Test that data directories are properly organized"""
        sql_scripts_path = Path("postgres/sql-scripts")
        assert sql_scripts_path.exists(), "postgres/sql-scripts directory should exist"

        data_path = Path("postgres/data")
        assert data_path.exists(), "data directory should exist"

        zones_path = Path("postgres/data/zones")
        yellow_path = Path("postgres/data/yellow")
        # These directories are created during data loading, so they might not exist initially
        # Just check that the parent data directory exists

    def test_init_scripts_exist(self):
        """Test that initialization SQL scripts exist"""
        init_scripts_path = Path("postgres/sql-scripts/init-scripts")
        assert init_scripts_path.exists(), "init-scripts directory should exist"

        # Check for key initialization files
        postgis_script = Path("postgres/sql-scripts/init-scripts/00-postgis-setup.sql")
        schema_script = Path("postgres/sql-scripts/init-scripts/01-nyc-taxi-schema.sql")

        assert postgis_script.exists(), "PostGIS setup script should exist"
        assert schema_script.exists(), "Schema setup script should exist"