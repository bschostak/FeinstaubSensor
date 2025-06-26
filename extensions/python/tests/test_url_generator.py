import unittest
from unittest.mock import patch
from datetime import datetime

# Import the module under test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.url_generator import parse_file_name, parse_url, generate_urls

class TestSensorArchiveUtils(unittest.TestCase):

    def test_parse_file_name_new_format(self):
        date = datetime(2024, 1, 2)
        expected = "2024-01-02_dht22_sensor_113.csv"
        result = parse_file_name(date, "dht22", "113")
        self.assertEqual(result, expected)

    def test_parse_file_name_old_format(self):
        date = datetime(2023, 1, 2)
        expected = "2023-01-02_dht22_sensor_113.csv.gz"
        result = parse_file_name(date, "dht22", "113")
        self.assertEqual(result, expected)

    def test_parse_url_new_format(self):
        date = datetime(2024, 1, 2)
        expected = "http://archive.sensor.community//2024-01-02/2024-01-02_dht22_sensor_113.csv"
        result = parse_url(date, "dht22", "113")
        self.assertEqual(result, expected)

    def test_parse_url_old_format(self):
        date = datetime(2023, 1, 2)
        expected = "http://archive.sensor.community/2023/2023-01-02/2023-01-02_dht22_sensor_113.csv.gz"
        result = parse_url(date, "dht22", "113")
        self.assertEqual(result, expected)

    @patch("modules.url_generator.get_date_range_year")
    def test_generate_urls(self, mock_date_range):
        mock_date_range.return_value = [datetime(2023, 1, 2)]
        expected_url = "http://archive.sensor.community/2023/2023-01-02/2023-01-02_dht22_sensor_113.csv.gz"
        expected_file = "2023-01-02_dht22_sensor_113.csv.gz"

        results = generate_urls(2023, 2023, "dht22", "113")
        self.assertEqual(results, [(expected_url, expected_file)])

    #TODO: Finish this test
    def test_generate_urls_multiple_years(self):
        expected_urls = [
            ("http://archive.sensor.community/2023/2023-01-02/2023-01-02_dht22_sensor_113.csv.gz", "2023-01-02_dht22_sensor_113.csv.gz"),
            ("http://archive.sensor.community/2024-01-02/2024-01-02_dht22_sensor_113.csv", "2024-01-02_dht22_sensor_113.csv")
        ]
        
        results = generate_urls(2023, 2024, "dht22", "113")

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSensorArchiveUtils))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
