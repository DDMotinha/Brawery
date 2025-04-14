import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# API configuration
API_BASE_URL = "https://api.openbrewerydb.org/v1/breweries"
API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "10"))  # Requests per minute

# Data lake paths
DATA_LAKE_BASE_PATH = os.getenv("DATA_LAKE_BASE_PATH", "/opt/airflow/data")
BRONZE_LAYER_PATH = os.path.join(DATA_LAKE_BASE_PATH, "bronze")
SILVER_LAYER_PATH = os.path.join(DATA_LAKE_BASE_PATH, "silver")
GOLD_LAYER_PATH = os.path.join(DATA_LAKE_BASE_PATH, "gold")

# Monitoring configuration
ENABLE_MONITORING = os.getenv("ENABLE_MONITORING", "true").lower() == "true"
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "admin@example.com")
