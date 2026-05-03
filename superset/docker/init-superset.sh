#!/bin/bash

# ================================================================================
# Apache Superset Initialization Script
# Handles database setup, admin user creation, and role initialization
# ================================================================================

set -e

echo "🚀 Starting Superset initialization..."

# Create Superset home directory and ensure it's writable
echo "📁 Setting up Superset home directory..."
mkdir -p /app/superset_home
chmod 755 /app/superset_home
echo "✅ Superset home directory ready!"

# Redis is no longer required - using SQLite-based caching
echo "ℹ️ Using SQLite-based caching (no Redis dependency)"

# Load Superset configuration and initialize logging
echo "📋 Loading Superset configuration..."
python -c "
import sys
sys.path.insert(0, '/app')
from superset_config import configure_logging
configure_logging()
print('✅ Superset configuration loaded successfully')
"

# Initialize database schema
echo "🗄️ Initializing Superset database schema..."
superset db upgrade
echo "✅ Database schema initialized"

# Create admin user (handle existing user gracefully)
echo "👤 Creating admin user..."
superset fab create-admin \
    --username "${SUPERSET_ADMIN_USER:-admin}" \
    --firstname "${SUPERSET_ADMIN_FIRSTNAME:-Admin}" \
    --lastname "${SUPERSET_ADMIN_LASTNAME:-User}" \
    --email "${SUPERSET_ADMIN_EMAIL:-admin@admin.com}" \
    --password "${SUPERSET_ADMIN_PASSWORD:-admin123}" \
    2>/dev/null || echo "ℹ️ Admin user already exists, skipping creation"
echo "✅ Admin user ready"

# Initialize default roles and permissions
echo "🔐 Initializing roles and permissions..."
superset init
echo "✅ Roles and permissions initialized"

# Load example data (optional)
if [ "${SUPERSET_LOAD_EXAMPLES:-false}" = "true" ]; then
    echo "📊 Loading example data..."
    superset load-examples
    echo "✅ Example data loaded"
else
    echo "ℹ️ Skipping example data (SUPERSET_LOAD_EXAMPLES not enabled)"
fi

echo "🎉 Superset initialization complete!"
echo "📍 Superset will be available at: http://localhost:8088"
echo "🔑 Login: admin@admin.com / admin123"
echo ""
echo "🚀 Starting Superset server..."