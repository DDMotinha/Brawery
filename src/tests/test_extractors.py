import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from src.extractors.brewery_api import extract_breweries

class TestBreweryAPI(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.test_dir, "breweries.json")
        
        # Sample API response
        self.mock_breweries = [
            {
                "id": "10-56-brewing-company-knox",
                "name": "10-56 Brewing Company",
                "brewery_type": "micro",
                "address_1": "400 Brown Cir",
                "address_2": null,
                "address_3": null,
                "city": "Knox",
                "state_province": "Indiana",
                "postal_code": "46534",
                "country": "United States",
                "longitude": "-86.627954",
                "latitude": "41.289715",
                "phone": "6308165790",
                "website_url": null,
                "state": "Indiana",
                "street": "400 Brown Cir"
            },
            {
                "id": "10-barrel-brewing-co-bend-1",
                "name": "10 Barrel Brewing Co",
                "brewery_type": "large",
                "address_1": "62970 18th St",
                "address_2": null,
                "address_3": null,
                "city": "Bend",
                "state_province": "Oregon",
                "postal_code": "97701-9847",
                "country": "United States",
                "longitude": "-121.28170597038259",
                "latitude": "44.08683530625218",
                "phone": "5415851007",
                "website_url": "http://www.10barrel.com",
                "state": "Oregon",
                "street": "62970 18th St"
            }
        ]
    
    @patch('src.extractors.brewery_api.requests.get')
    def test_extract_breweries_success(self, mock_get):
        # Configure the mock to return a successful response
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_breweries
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the function
        result = extract_breweries(self.output_path, per_page=2, max_pages=1)
        
        # Verify the function called the API correctly
        mock_get.assert_called_once_with(
            "https://api.openbrewerydb.org/v1/breweries",
            params={"page": 1, "per_page": 2}
        )
        
        # Verify the output file was created with the correct content
        self.assertTrue(os.path.exists(self.output_path))
        with open(self.output_path, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data, self.mock_breweries)
        
        # Verify the function returned the correct count
        self.assertEqual(result, 2)
    
    @patch('src.extractors.brewery_api.requests.get')
    def test_extract_breweries_empty_response(self, mock_get):
        # Configure the mock to return an empty response
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the function
        result = extract_breweries(self.output_path, per_page=2, max_pages=1)
        
        # Verify the output file was created with an empty list
        self.assertTrue(os.path.exists(self.output_path))
        with open(self.output_path, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data, [])
        
        # Verify the function returned 0
        self.assertEqual(result, 0)
    
    @patch('src.extractors.brewery_api.requests.get')
    def test_extract_breweries_api_error(self, mock_get):
        # Configure the mock to raise an exception
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        # Verify the function raises the exception
        with self.assertRaises(Exception):
            extract_breweries(self.output_path, per_page=2, max_pages=1)
        
        # Verify the output file was not created
        self.assertFalse(os.path.exists(self.output_path))
    
    def tearDown(self):
        # Clean up the temporary directory
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)

if __name__ == '__main__':
    unittest.main()
