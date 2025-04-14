import unittest
import json
import os
import tempfile
import pandas as pd
import shutil
from src.transformers.bronze_to_silver import transform_bronze_to_silver
from src.transformers.silver_to_gold import transform_silver_to_gold

class TestTransformers(unittest.TestCase):
    
    def setUp(self):
        # Create temporary directories for test data
        self.test_dir = tempfile.mkdtemp()
        self.bronze_dir = os.path.join(self.test_dir, "bronze")
        self.silver_dir = os.path.join(self.test_dir, "silver")
        self.gold_dir = os.path.join(self.test_dir, "gold")
        
        os.makedirs(self.bronze_dir, exist_ok=True)
        os.makedirs(self.silver_dir, exist_ok=True)
        os.makedirs(self.gold_dir, exist_ok=True)
        
        # Sample brewery data
        self.sample_breweries = [
            {
                "id": "brewery-1",
                "name": "Brewery One",
                "brewery_type": "micro",
                "city": "City A",
                "state": "california",
                "country": "United States"
            },
            {
                "id": "brewery-2",
                "name": "Brewery Two",
                "brewery_type": "brewpub",
                "city": "City B",
                "state": "california",
                "country": "United States"
            },
            {
                "id": "brewery-3",
                "name": "Brewery Three",
                "brewery_type": "micro",
                "city": "City C",
                "state": "oregon",
                "country": "United States"
            },
            {
                "id": "brewery-4",
                "name": "Brewery Four",
                "brewery_type": None,
                "city": "City D",
                "state": None,
                "country": "United States"
            }
        ]
        
        # Create bronze layer test file
        self.bronze_file = os.path.join(self.bronze_dir, "breweries.json")
        with open(self.bronze_file, 'w') as f:
            json.dump(self.sample_breweries, f)
        
        self.execution_date = "2023-01-01"
    
    def test_bronze_to_silver_transformation(self):
        # Call the transformation function
        transform_bronze_to_silver(
            input_path=self.bronze_file,
            output_base_path=self.silver_dir,
            execution_date=self.execution_date
        )
        
        # Check that the silver layer files were created
        california_path = os.path.join(
            self.silver_dir, 
            "state=california", 
            f"extraction_date={self.execution_date}", 
            "breweries.parquet"
        )
        oregon_path = os.path.join(
            self.silver_dir, 
            "state=oregon", 
            f"extraction_date={self.execution_date}", 
            "breweries.parquet"
        )
        unknown_path = os.path.join(
            self.silver_dir, 
            "state=unknown", 
            f"extraction_date={self.execution_date}", 
            "breweries.parquet"
        )
        
        # Verify files exist
        self.assertTrue(os.path.exists(california_path))
        self.assertTrue(os.path.exists(oregon_path))
        self.assertTrue(os.path.exists(unknown_path))
        
        # Verify file contents
        ca_df = pd.read_parquet(california_path)
        or_df = pd.read_parquet(oregon_path)
        unknown_df = pd.read_parquet(unknown_path)
        
        self.assertEqual(len(ca_df), 2)  # Two California breweries
        self.assertEqual(len(or_df), 1)  # One Oregon brewery
        self.assertEqual(len(unknown_df), 1)  # One unknown state brewery
        
        # Verify extraction date was added
        self.assertTrue('extraction_date' in ca_df.columns)
        self.assertEqual(ca_df['extraction_date'].iloc[0], self.execution_date)
    
    def test_silver_to_gold_transformation(self):
        # First create the silver layer data
        transform_bronze_to_silver(
            input_path=self.bronze_file,
            output_base_path=self.silver_dir,
            execution_date=self.execution_date
        )
        
        # Then transform to gold layer
        gold_output_path = os.path.join(
            self.gold_dir, 
            f"extraction_date={self.execution_date}", 
            "breweries_agg.parquet"
        )
        
        transform_silver_to_gold(
            input_base_path=self.silver_dir,
            output_path=gold_output_path,
            execution_date=self.execution_date
        )
        
        # Verify gold layer file exists
        self.assertTrue(os.path.exists(gold_output_path))
        
        # Verify gold layer content
        gold_df = pd.read_parquet(gold_output_path)
        
        # Should have 3 rows: micro/california, brewpub/california, micro/oregon, unknown/unknown
        self.assertEqual(len(gold_df), 4)
        
        # Verify the counts
        micro_ca = gold_df[(gold_df['brewery_type'] == 'micro') & (gold_df['state'] == 'california')]
        self.assertEqual(micro_ca['count'].iloc[0], 1)
        
        brewpub_ca = gold_df[(gold_df['brewery_type'] == 'brewpub') & (gold_df['state'] == 'california')]
        self.assertEqual(brewpub_ca['count'].iloc[0], 1)
        
        micro_or = gold_df[(gold_df['brewery_type'] == 'micro') & (gold_df['state'] == 'oregon')]
        self.assertEqual(micro_or['count'].iloc[0], 1)
        
        unknown = gold_df[(gold_df['brewery_type'] == 'unknown') & (gold_df['state'] == 'unknown')]
        self.assertEqual(unknown['count'].iloc[0], 1)
    
    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main()
