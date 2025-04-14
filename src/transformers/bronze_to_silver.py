import json
import os
import pandas as pd
from typing import Dict, List, Any
from src.utils.logging_utils import setup_logger

logger = setup_logger()

def transform_bronze_to_silver(input_path: str, output_base_path: str, execution_date: str) -> None:
    """
    Transform raw brewery data from the bronze layer to the silver layer.
    Data is cleaned, transformed to Parquet format, and partitioned by state.
    
    Args:
        input_path: Path to the raw JSON data
        output_base_path: Base path for the silver layer
        execution_date: Execution date in YYYY-MM-DD format
    """
    logger.info(f"Starting transformation from bronze to silver layer for date {execution_date}")
    
    try:
        # Read the raw data
        with open(input_path, 'r') as f:
            breweries = json.load(f)
        
        logger.info(f"Loaded {len(breweries)} breweries from bronze layer")
        
        # Convert to DataFrame
        df = pd.DataFrame(breweries)
        
        # Clean and transform data
        # 1. Fill missing values
        df['brewery_type'] = df['brewery_type'].fillna('unknown')
        df['state'] = df['state'].fillna('unknown')
        df['city'] = df['city'].fillna('unknown')
        
        # 2. Standardize state names (convert to lowercase)
        df['state'] = df['state'].str.lower()
        
        # 3. Create a date column for the execution date
        df['extraction_date'] = execution_date
        
        # 4. Select and reorder columns
        columns = [
            'id', 'name', 'brewery_type', 'address_1', 'address_2', 'address_3',
            'city', 'state_province', 'postal_code', 'country', 'longitude', 
            'latitude', 'phone', 'website_url', 'state', 'street', 'extraction_date'
        ]
        
        # Only include columns that exist in the dataframe
        columns = [col for col in columns if col in df.columns]
        df = df[columns]
        
        # Partition by state and save as Parquet
        for state, state_df in df.groupby('state'):
            if state == 'unknown' or not state:
                state = 'unknown'
                
            # Create the output directory
            output_dir = os.path.join(output_base_path, f"state={state}", f"extraction_date={execution_date}")
            os.makedirs(output_dir, exist_ok=True)
            
            # Save as Parquet
            output_path = os.path.join(output_dir, "breweries.parquet")
            state_df.to_parquet(output_path, index=False)
            
            logger.info(f"Saved {len(state_df)} breweries for state '{state}' to {output_path}")
        
        logger.info(f"Successfully transformed brewery data to silver layer")
        
    except Exception as e:
        logger.error(f"Error transforming brewery data: {str(e)}")
        raise
