#!/usr/bin/env python3
"""
Simple script to create PostgreSQL database connection in Superset after startup
"""
import time
import requests
import json
import sys

def create_database_connection():
    """Create PostgreSQL database connection via API after Superset is ready"""
    base_url = "http://localhost:8088"
    max_attempts = 10

    # Wait for Superset to be ready
    print("🔄 Waiting for Superset to be ready...")
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Superset is ready!")
                break
        except:
            pass

        if attempt < max_attempts - 1:
            print(f"⏳ Attempt {attempt + 1}/{max_attempts}, waiting 10 seconds...")
            time.sleep(10)
    else:
        print("❌ Superset not ready after maximum attempts")
        return False

    # Get CSRF token
    try:
        session = requests.Session()
        csrf_response = session.get(f"{base_url}/api/v1/security/csrf_token/")
        csrf_token = csrf_response.json()["result"]
        print("✅ CSRF token obtained")
    except Exception as e:
        print(f"❌ Failed to get CSRF token: {e}")
        return False

    # Authenticate
    try:
        auth_data = {
            "username": "admin",
            "password": "admin123",
            "provider": "db"
        }
        auth_response = session.post(
            f"{base_url}/api/v1/security/login",
            json=auth_data,
            headers={"X-CSRFToken": csrf_token}
        )
        access_token = auth_response.json()["access_token"]
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

    # Create database connection
    try:
        db_data = {
            "database_name": "PostgreSQL Playground",
            "engine": "postgresql+pg8000",
            "sqlalchemy_uri": "postgresql+pg8000://admin:admin123@postgres:5432/playground",
            "expose_in_sqllab": True,
            "allow_run_async": True,
            "allow_ctas": True,
            "allow_cvas": True,
            "allow_dml": True,
            "allow_file_upload": True,
            "extra": json.dumps({
                "metadata_params": {},
                "engine_params": {},
                "schemas_allowed_for_file_upload": ["nyc_taxi"]
            })
        }

        db_response = session.post(
            f"{base_url}/api/v1/database/",
            json=db_data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-CSRFToken": csrf_token,
                "Content-Type": "application/json"
            }
        )

        if db_response.status_code in [200, 201]:
            print("✅ PostgreSQL database connection created successfully!")
            return True
        else:
            print(f"⚠️ Database connection response: {db_response.status_code} - {db_response.text}")
            return False

    except Exception as e:
        print(f"❌ Failed to create database connection: {e}")
        return False

if __name__ == "__main__":
    success = create_database_connection()
    sys.exit(0 if success else 1)