# Apache Superset Configuration File
import os

# Secret key for signing cookies - MUST be set before anything else
SECRET_KEY = 'M5QwzH1CORRyE/gLMRIdmNGGyxj+tV0RfoLdSExzNqzZoUf/f+ehg3AS'

# JWT secret for async queries (minimum 32 bytes required)
# JWT_SECRET_KEY = 'jwt-secret-for-async-queries-at-least-32-bytes-long-with-random-characters-2025'

# Explicitly disable the default secret key check
PREVENT_UNSAFE_DEFAULT_SECRET_KEY = False

# Database configuration for Superset metadata - using SQLite for simplicity and persistence
# SQLite-specific options are included in the URI to avoid affecting PostgreSQL connections
SQLALCHEMY_DATABASE_URI = "sqlite:////app/superset_home/superset.db?check_same_thread=false&timeout=30"

# Simplified caching configuration - no Redis required
# Uses Superset's built-in SQLite-based caching and NullCache for optimal simplicity

# Main cache configuration (application caching) - disabled for simplicity
CACHE_CONFIG = {
    'CACHE_TYPE': 'NullCache',
    'CACHE_DEFAULT_TIMEOUT': 300
}

# Data cache configuration - disabled (no query result caching needed for development)
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'NullCache',
    'CACHE_DEFAULT_TIMEOUT': 86400
}

# Query result backend for async query results
# Disabled for development - enables synchronous query execution in SQL Lab
RESULTS_BACKEND = None

# Filter state cache - uses SQLite metadata database (SupersetMetastoreCache)
FILTER_STATE_CACHE_CONFIG = {
    'CACHE_TYPE': 'SupersetMetastoreCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,    # 24 hours
    'REFRESH_TIMEOUT_ON_RETRIEVAL': True
}

# Explore form data cache - uses SQLite metadata database (SupersetMetastoreCache)
EXPLORE_FORM_DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'SupersetMetastoreCache',
    'CACHE_DEFAULT_TIMEOUT': 3600,     # 1 hour
    'REFRESH_TIMEOUT_ON_RETRIEVAL': True
}

# Enhanced feature flags for better functionality
FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,       # Enable native filters
    "DASHBOARD_CROSS_FILTERS": True,        # Enable cross-filtering
    "GLOBAL_ASYNC_QUERIES": False,          # Disable async queries to avoid JWT issues
    "VERSIONED_EXPORT": True,               # Enable versioned exports
    "ENABLE_TEMPLATE_PROCESSING": True,     # Enable Jinja templating
    "DASHBOARD_CACHE": True,                # Enable dashboard caching
    "REMOVE_SLICE_LEVEL_LABEL_COLORS": False,  # Keep slice-level label colors
    "SIP_38_VIZ_REARCHITECTURE": True,      # Enable new viz architecture
    "TAGGING_SYSTEM": True,                 # Enable tagging system for datasets/charts
    "ENABLE_ADVANCED_DATA_TYPES": True,     # Support for advanced data types
    "SQLLAB_BACKEND_PERSISTENCE": False,   # Disable query editor backend persistence to prevent migration popup
}

# Disable example data to avoid transaction conflicts
SUPERSET_LOAD_EXAMPLES = False

# Configure PostgreSQL drivers for better compatibility with Superset
# Both pg8000 and psycopg2-binary are available for use by SQLAlchemy

# Minimal SQLAlchemy configuration to avoid conflicts with data source connections
# Only apply essential settings that work for both SQLite (metadata) and PostgreSQL (data sources)
SQLALCHEMY_ENGINE_OPTIONS = {
    'echo': False,                          # Disable SQL query logging for performance
}

# Suppress SQLAlchemy warnings about SQLite and Decimal objects
import warnings
from sqlalchemy.exc import SAWarning
warnings.filterwarnings('ignore', category=SAWarning, message='.*Dialect sqlite.*does.*not.*support Decimal.*')

# Removed DATABASE_CONNECTIVITY_OPTIONS that were interfering with PostgreSQL connections

# Removed psycopg2 mock - it was interfering with actual PostgreSQL connections
# Superset can handle both pg8000 and psycopg2 drivers naturally without mocking

# Performance monitoring and query optimization
ENABLE_TIME_ROTATE = True
TIME_ROTATE_LOG_LEVEL = 'INFO'

# Query timeout and row limit settings
SQLLAB_TIMEOUT = 300                    # 5 minutes for SQL Lab queries
SQLLAB_ASYNC_TIME_LIMIT_SEC = 600       # 10 minutes for async queries
SQL_MAX_ROW = 100000                    # Maximum rows returned by query
ROW_LIMIT = 5000                        # Default row limit for exploration

# Query result caching
SUPERSET_WEBSERVER_TIMEOUT = 300
SQLLAB_SAVE_WARNING_MESSAGE = "Please save your query before continuing"

# Performance settings
WEBSERVER_THREADS = 4
SQLLAB_DEFAULT_DBID = None

# Enable query result caching globally
CACHE_DEFAULT_TIMEOUT = 3600            # 1 hour default cache
ENABLE_CORS = False

# Query performance optimization
SQLLAB_CTAS_NO_LIMIT = True            # Allow CREATE TABLE AS SELECT without limit

# Security settings - Disable CSRF for development environment
WTF_CSRF_ENABLED = False
TALISMAN_ENABLED = False

# Additional security settings for development
CSRF_ENABLED = False
WTF_CSRF_CHECK_DEFAULT = False
WTF_CSRF_SSL_STRICT = False
SEND_FILE_MAX_AGE_DEFAULT = 60 * 60 * 24 * 365

# API and frontend CSRF handling
SUPERSET_WEBSERVER_TIMEOUT = 300
PUBLIC_ROLE_LIKE_GAMMA = True

# Session configuration for development
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = None  # More permissive for development

# Use filesystem session storage (more reliable than Redis)
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = '/tmp/superset_sessions'
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True

# Alternative Redis cache for other purposes (keep Redis for caching only)
# Note: Redis session storage can cause CSRF issues in some Superset versions

# Additional configuration for SQL Lab stability
SQLLAB_TIMEOUT = 300
SQLLAB_ASYNC_TIME_LIMIT_SEC = 600

# Email configuration (optional)
SMTP_HOST = "localhost"
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_USER = "admin@superset.com"
SMTP_PORT = 25
SMTP_MAIL_FROM = "admin@superset.com"

# Default language
BABEL_DEFAULT_LOCALE = "en"
BABEL_DEFAULT_FOLDER = "superset/translations"
LANGUAGES = {
    "en": {"flag": "us", "name": "English"},
}

# =============================================================================
# SUPERSET NATIVE LOGGING CONFIGURATION - For debugging and monitoring
# =============================================================================
import logging
from datetime import datetime

# Ensure log directory exists
LOG_DIR = '/app/logs'
os.makedirs(LOG_DIR, exist_ok=True)

# Use environment variable for timestamped log filename (set by startup script)
# Falls back to generic name if not set
LOG_FILENAME = os.getenv('SUPERSET_LOG_FILENAME', 'superset.log')

# Superset-native logging configuration (this is what Superset actually uses)
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(asctime)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'superset_file': {
            'class': 'logging.FileHandler',
            'filename': f'{LOG_DIR}/{LOG_FILENAME}',
            'formatter': 'detailed',
            'level': 'INFO'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO'
        }
    },
    'loggers': {
        # Main Superset application logger
        'superset': {
            'handlers': ['superset_file', 'console'],
            'level': 'INFO',
            'propagate': False
        },
        # Superset-specific modules
        'superset.charts': {
            'handlers': ['superset_file'],
            'level': 'INFO',
            'propagate': False
        },
        'superset.dashboards': {
            'handlers': ['superset_file'],
            'level': 'INFO',
            'propagate': False
        },
        'superset.views': {
            'handlers': ['superset_file'],
            'level': 'INFO',
            'propagate': False
        },
        'superset.sql_lab': {
            'handlers': ['superset_file'],
            'level': 'INFO',
            'propagate': False
        },
        'superset.connectors': {
            'handlers': ['superset_file'],
            'level': 'INFO',
            'propagate': False
        },
        # Database and SQLAlchemy logs
        'sqlalchemy.engine': {
            'handlers': ['superset_file'],
            'level': 'WARNING',
            'propagate': False
        },
        'sqlalchemy.pool': {
            'handlers': ['superset_file'],
            'level': 'WARNING',
            'propagate': False
        },
        # Flask and security logs
        'flask': {
            'handlers': ['superset_file'],
            'level': 'WARNING',
            'propagate': False
        },
        'flask_appbuilder': {
            'handlers': ['superset_file'],
            'level': 'INFO',
            'propagate': False
        },
        'flask_appbuilder.security': {
            'handlers': ['superset_file'],
            'level': 'INFO',
            'propagate': False
        },
        # Gunicorn web server logs
        'gunicorn': {
            'handlers': ['superset_file'],
            'level': 'INFO',
            'propagate': False
        },
        'gunicorn.error': {
            'handlers': ['superset_file'],
            'level': 'ERROR',
            'propagate': False
        },
        'gunicorn.access': {
            'handlers': ['superset_file'],
            'level': 'INFO',
            'propagate': False
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING'
    }
}

# Enable logging and application insights
ENABLE_PROXY_FIX = True

# Log level for Flask-appbuilder
FAB_LOG_LEVEL = "INFO"

# Enable Flask debugging in development
FLASK_ENV = 'development'

# Startup logging function (called by Superset during initialization)
import logging.config
def configure_logging():
    """Configure Superset logging on startup"""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('superset.config')
    logger.info("=" * 80)
    logger.info("🚀 SUPERSET PERSISTENT LOGGING CONFIGURED")
    logger.info("=" * 80)
    logger.info(f"📁 Log Directory: {LOG_DIR}")
    logger.info(f"🗄️ Database: SQLite (/app/superset_home/superset.db)")
    logger.info("🔑 Caching: SQLite-based (No Redis required)")
    logger.info(f"🔒 CSRF Protection: {'❌ DISABLED (Development Mode)' if not WTF_CSRF_ENABLED else '✅ ENABLED'}")
    logger.info(f"🛡️ Talisman Security: {'❌ DISABLED (Development Mode)' if not TALISMAN_ENABLED else '✅ ENABLED'}")
    logger.info(f"📊 Row Limit: {ROW_LIMIT} (Max: {SQL_MAX_ROW})")
    logger.info(f"⏱️ Query Timeouts: SQL Lab={SQLLAB_TIMEOUT}s, Async={SQLLAB_ASYNC_TIME_LIMIT_SEC}s")
    logger.info(f"📁 Session Storage: {SESSION_TYPE} ({'Filesystem' if SESSION_TYPE == 'filesystem' else 'Other'})")
    logger.info("🗂️ Cache Configuration:")
    logger.info("  • Application Cache: NullCache (disabled)")
    logger.info("  • Data Cache: NullCache (no query result caching)")
    logger.info("  • Filter State: SupersetMetastoreCache (SQLite)")
    logger.info("  • Explore Form Data: SupersetMetastoreCache (SQLite)")
    logger.info("📋 Log Files:")
    logger.info(f"  • Application: superset.log")
    logger.info(f"  • Errors: superset_errors.log")
    logger.info("🚩 Enhanced Feature Flags:")
    key_features = ["DASHBOARD_NATIVE_FILTERS", "DASHBOARD_CROSS_FILTERS", "GLOBAL_ASYNC_QUERIES", "DASHBOARD_CACHE", "TAGGING_SYSTEM", "SQLLAB_BACKEND_PERSISTENCE"]
    for flag in key_features:
        if flag in FEATURE_FLAGS:
            logger.info(f"  • {flag}: {'✅' if FEATURE_FLAGS[flag] else '❌'}")
    logger.info(f"  • Plus {len(FEATURE_FLAGS) - len(key_features)} additional features enabled")
    logger.info("🔧 Performance Optimizations:")
    logger.info("  • Metadata DB: SQLite (persistent, no connection pooling)")
    logger.info(f"  • SQLite Timeout: {SQLALCHEMY_ENGINE_OPTIONS.get('connect_args', {}).get('timeout', 'N/A')}s")
    logger.info("  • Data Sources: PostgreSQL with optimized connection pooling")
    logger.info(f"  • SQLAlchemy Warnings: Suppressed for SQLite/Decimal compatibility")
    logger.info("  • Caching Strategy: Simplified (SQLite-based, no Redis)")
    logger.info(f"  • Time Rotate Logging: {'✅' if ENABLE_TIME_ROTATE else '❌'}")
    logger.info("=" * 80)

# Configure logging immediately
configure_logging()