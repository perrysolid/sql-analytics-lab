"""
Pytest configuration and shared fixtures
"""
import pytest
import psycopg2
import requests
import time
from pathlib import Path


@pytest.fixture(scope="session")
def postgres_connection():
    """
    Fixture for PostgreSQL database connection
    Returns connection if available, otherwise skips tests
    """
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="playground",
            user="admin",
            password="admin123",
            connect_timeout=5
        )
        yield conn
        conn.close()
    except psycopg2.OperationalError:
        pytest.skip("PostgreSQL container not running")


@pytest.fixture(scope="session")
def wait_for_containers():
    """
    Fixture to wait for containers to be ready before running tests
    """
    max_wait = 60  # seconds
    wait_interval = 5  # seconds

    services = {
        "postgres": ("localhost", 5432),
        "pgadmin": ("http://localhost:8080", None),
        "superset": ("http://localhost:8088", None)
    }

    for service_name, (host, port) in services.items():
        print(f"Waiting for {service_name} to be ready...")

        for attempt in range(max_wait // wait_interval):
            try:
                if port:  # Database service
                    conn = psycopg2.connect(
                        host=host,
                        port=port,
                        database="playground",
                        user="admin",
                        password="admin123",
                        connect_timeout=2
                    )
                    conn.close()
                    print(f"✓ {service_name} is ready")
                    break
                else:  # Web service
                    response = requests.get(host, timeout=2)
                    if response.status_code in [200, 302]:
                        print(f"✓ {service_name} is ready")
                        break
            except (psycopg2.OperationalError, requests.exceptions.RequestException):
                if attempt < (max_wait // wait_interval) - 1:
                    time.sleep(wait_interval)
                else:
                    print(f"⚠ {service_name} not ready after {max_wait}s")


@pytest.fixture
def sample_query_runner(postgres_connection):
    """
    Fixture that provides a function to run sample queries
    """
    def run_query(query, fetch_all=True):
        cursor = postgres_connection.cursor()
        cursor.execute(query)
        if fetch_all:
            return cursor.fetchall()
        else:
            return cursor.fetchone()

    return run_query


@pytest.fixture(scope="session")
def project_root():
    """
    Fixture that returns the project root directory
    """
    return Path(__file__).parent.parent


@pytest.fixture
def config_files(project_root):
    """
    Fixture that provides paths to configuration files
    """
    return {
        'docker_compose': project_root / 'docker-compose.yml',
        'superset_config': project_root / 'superset' / 'config' / 'superset_config.py',
        'env_file': project_root / '.env',
        'claude_md': project_root / 'CLAUDE.md'
    }