"""
Tests for Docker container setup and configuration
"""
import pytest
import requests
import psycopg2
import time
from pathlib import Path


class TestDockerSetup:
    """Test Docker container setup and connectivity"""

    def test_postgres_connection(self):
        """Test PostgreSQL database connectivity"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="playground",
                user="admin",
                password="admin123"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            assert "PostgreSQL" in version[0]
            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("PostgreSQL container not running")

    def test_postgis_extension(self):
        """Test PostGIS extension is available"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="playground",
                user="admin",
                password="admin123"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT PostGIS_Version();")
            version = cursor.fetchone()
            assert version is not None
            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("PostgreSQL container not running")

    def test_pgadmin_web_interface(self):
        """Test PGAdmin web interface accessibility"""
        try:
            response = requests.get("http://localhost:8080", timeout=10)
            assert response.status_code == 200
            assert "pgAdmin" in response.text
        except requests.exceptions.ConnectionError:
            pytest.skip("PGAdmin container not running")

    def test_superset_web_interface(self):
        """Test Superset web interface accessibility"""
        try:
            response = requests.get("http://localhost:8088", timeout=10)
            assert response.status_code in [200, 302]  # 302 for redirect to login
        except requests.exceptions.ConnectionError:
            pytest.skip("Superset container not running")


class TestDataStructure:
    """Test database schema and data structure"""

    def test_nyc_taxi_schema_exists(self):
        """Test that nyc_taxi schema exists"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="playground",
                user="admin",
                password="admin123"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'nyc_taxi';")
            schema = cursor.fetchone()
            assert schema is not None
            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("PostgreSQL container not running")

    def test_taxi_trips_table_exists(self):
        """Test that yellow_taxi_trips table exists with expected structure"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="playground",
                user="admin",
                password="admin123"
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'nyc_taxi'
                AND table_name = 'yellow_taxi_trips'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            assert len(columns) > 0

            # Check for key columns
            column_names = [col[0] for col in columns]
            assert 'row_hash' in column_names
            assert 'vendorid' in column_names
            assert 'pickup_datetime' in column_names
            assert 'dropoff_datetime' in column_names

            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("PostgreSQL container not running")


class TestConfigFiles:
    """Test configuration files and structure"""

    def test_superset_config_exists(self):
        """Test that Superset configuration file exists"""
        config_path = Path("superset/config/superset_config.py")
        assert config_path.exists(), "Superset config file should exist in superset directory"

    def test_docker_compose_structure(self):
        """Test docker-compose.yml has expected services"""
        compose_path = Path("docker-compose.yml")
        assert compose_path.exists(), "docker-compose.yml should exist"

        with open(compose_path, 'r') as f:
            content = f.read()

        # Check for expected services (no Redis)
        assert "postgres:" in content
        assert "pgadmin:" in content
        assert "superset:" in content
        assert "redis:" not in content  # Ensure Redis is removed

    def test_logs_directory_structure(self):
        """Test logs directory exists with expected structure"""
        logs_path = Path("logs")
        assert logs_path.exists(), "Logs directory should exist"

        superset_logs = Path("logs/superset")
        assert superset_logs.exists(), "Superset logs directory should exist"