import requests
import json
import os
import time
from typing import Dict, List, Any, Optional
from src.utils.logging_utils import setup_logger

logger = setup_logger()

def extract_breweries(output_path: str, per_page: int = 50, max_pages: int = 10) -> None:
    """
    Extract brewery data from the OpenBreweryDB API and save it to the bronze layer.
    
    Args:
        output_path: Path where the raw data will be saved
        per_page: Number of breweries per API request
        max_pages: Maximum number of pages to request
    """
    logger.info(f"Starting extraction of brewery data to {output_path}")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    base_url = "https://api.openbrewerydb.org/v1/breweries"
    all_breweries = []
    
    for page in range(1, max_pages + 1):
        try:
            logger.info(f"Fetching page {page} of brewery data")
            params = {
                "page": page,
                "per_page": per_page
            }
            
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            breweries = response.json()
            
            # If we get fewer breweries than requested, we've reached the end
            if len(breweries) == 0:
                logger.info(f"No more breweries to fetch after page {page-1}")
                break
                
            all_breweries.extend(breweries)
            logger.info(f"Successfully fetched {len(breweries)} breweries from page {page}")
            
            # Add a small delay to avoid hitting API rate limits
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching brewery data: {str(e)}")
            # Re-raise the exception to trigger Airflow retry mechanism
            raise
    
    # Save the raw data to the bronze layer
    try:
        with open(output_path, 'w') as f:
            json.dump(all_breweries, f)
        logger.info(f"Successfully saved {len(all_breweries)} breweries to {output_path}")
    except Exception as e:
        logger.error(f"Error saving brewery data: {str(e)}")
        raise
        
    return len(all_breweries)
