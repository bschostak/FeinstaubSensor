import unittest
from unittest.mock import patch, MagicMock
import json

# Import the module under test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.year_fetcher import get_available_years, fetch_available_years

class TestSensorCommunityScraper(unittest.TestCase):

    @patch("modules.year_fetcher.requests.get")
    def test_get_available_years_with_valid_html(self, mock_get):
        html_content = """
        <html>
            <body>
                <a href="/2021/">2021/</a>
                <a href="/2022-03-01/">2022-03-01</a>
                <a href="/random/">random</a>
            </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.content = html_content.encode("utf-8")
        mock_get.return_value = mock_response

        expected_years = ['2021', '2022']
        actual_years = get_available_years()
        self.assertEqual(actual_years, expected_years)

    @patch("modules.year_fetcher.requests.get")
    def test_get_available_years_with_exception(self, mock_get):
        mock_get.side_effect = Exception("Connection error")
        result = get_available_years()
        self.assertEqual(result, [])

    @patch("modules.year_fetcher.get_available_years")
    def test_fetch_available_years(self, mock_get_years):
        mock_get_years.return_value = ['2020', '2021']
        result = fetch_available_years()
        self.assertEqual(result, json.dumps(['2020', '2021']))

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSensorCommunityScraper))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)