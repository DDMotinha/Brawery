import os
import pandas as pd
import glob
from typing import Dict, List, Any
from src.utils.logging_utils import setup_logger

logger = setup_logger()

def transform_silver_to_gold(input_base_path: str, output_path: str, execution_date: str) -> None:
    """
    Transform silver layer data to gold layer by aggregating brewery counts by type and location.
    
    Args:
        input_base_path: Base path for the silver layer
        output_path: Path where the gold layer data will be saved
        execution_date: Execution date in YYYY-MM-DD format
    """
    logger.info(f"Starting transformation from silver to gold layer for date {execution_date}")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Find all Parquet files for the given execution date
        pattern = os.path.join(input_base_path, "state=*", f"extraction_date={execution_date}", "breweries.parquet")
        parquet_files = glob.glob(pattern)
        
        if not parquet_files:
            logger.warning(f"No silver layer data found for execution date {execution_date}")
            return
            
        logger.info(f"Found {len(parquet_files)} silver layer files to process")
        
        # Read and concatenate all Parquet files
        dfs = []
        for file in parquet_files:
            df = pd.read_parquet(file)
            # Extract state from the file path
            state = file.split("state=")[1].split("/")[0]
            if 'state' not in df.columns:
                df['state'] = state
            dfs.append(df)
            
        if not dfs:
            logger.warning("No data found in silver layer files")
            return
            
        all_data = pd.concat(dfs, ignore_index=True)
        logger.info(f"Loaded {len(all_data)} breweries from silver layer")
        
        # Aggregate data by brewery type and state
        agg_data = all_data.groupby(['brewery_type', 'state']).size().reset_index(name='count')
        
        # Add execution date
        agg_data['extraction_date'] = execution_date
        
        # Save to gold layer as Parquet
        agg_data.to_parquet(output_path, index=False)
        logger.info(f"Successfully saved aggregated data to {output_path}")
        
    except Exception as e:
        logger.error(f"Error transforming silver to gold layer: {str(e)}")
        raise
