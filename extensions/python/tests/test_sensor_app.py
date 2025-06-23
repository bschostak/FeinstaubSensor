import unittest
from unittest.mock import Mock, patch, MagicMock, call
import threading
from pathlib import Path
import tempfile
import shutil
from typing import Optional

# Import the module under test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import sensor_app
from modules.data_operations import SensorData, AnalyzedSensorData, AnalyzedSensor
from datetime import datetime


class TestSensorApp(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_extension = Mock()
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_sensor_data_dir = sensor_app.SENSOR_DATA_DIR
        sensor_app.SENSOR_DATA_DIR = self.test_dir / "sensor_data"
        
        # Reset stop_event before each test
        sensor_app.stop_event.clear()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up temporary directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        
        # Restore original SENSOR_DATA_DIR
        sensor_app.SENSOR_DATA_DIR = self.original_sensor_data_dir
        
        # Reset stop_event
        sensor_app.stop_event.clear()


class TestStopDownload(TestSensorApp):
    
    def test_stop_download_sets_event(self):
        """Test that stop_download sets the stop_event."""
        # Ensure event is not set initially
        self.assertFalse(sensor_app.stop_event.is_set())
        
        # Call stop_download
        sensor_app.stop_download()
        
        # Verify event is set
        self.assertTrue(sensor_app.stop_event.is_set())


class TestProcessArchive(TestSensorApp):
    
    def test_process_archive_with_gz_extension(self):
        """Test processing archive with .gz extension."""
        with patch('sensor_app.extract_archive') as mock_extract:
            mock_extract.return_value = "test_file.csv.gz"
            
            result = sensor_app.process_archive("test_file.csv.gz", self.mock_extension)
            
            mock_extract.assert_called_once_with("test_file.csv.gz", extension=self.mock_extension)
            self.assertEqual(result, "test_file.csv")
    
    def test_process_archive_without_gz_extension(self):
        """Test processing archive without .gz extension."""
        result = sensor_app.process_archive("test_file.csv", self.mock_extension)
        self.assertEqual(result, "test_file.csv")


class TestProcessSensorData(TestSensorApp):
    
    @patch('sensor_app.open_and_parse_csv_file')
    @patch('sensor_app.check_encoding_of_file')
    def test_process_sensor_data(self, mock_check_encoding, mock_parse_csv):
        """Test processing sensor data from CSV file."""
        # Setup mocks
        mock_check_encoding.return_value = "utf-8"
        mock_sensor_data = [
            SensorData("123", datetime.now(), 25.5, 60.0),
            SensorData("123", datetime.now(), 26.0, 65.0)
        ]
        mock_parse_csv.return_value = mock_sensor_data
        
        result = sensor_app.process_sensor_data("test_file.csv")
        
        mock_check_encoding.assert_called_once_with("test_file.csv")
        mock_parse_csv.assert_called_once_with("test_file.csv", "utf-8")
        self.assertEqual(result, mock_sensor_data)


class TestDownloadSensorData(TestSensorApp):
    
    def test_download_sensor_data_extension_none_raises_error(self):
        """Test that download_sensor_data raises ValueError when extension is None."""
        urls = [("http://example.com/file1.csv", "file1.csv")]
        
        with self.assertRaises(ValueError) as context:
            sensor_app.download_sensor_data(urls, extension=None)
        
        self.assertEqual(str(context.exception), "Extension cannot be None")
    
    @patch('sensor_app.download_file')
    @patch('sensor_app.process_archive')
    def test_download_sensor_data_success(self, mock_process_archive, mock_download_file):
        """Test successful download of sensor data."""
        urls = [
            ("http://example.com/file1.csv.gz", "file1.csv.gz"),
            ("http://example.com/file2.csv.gz", "file2.csv.gz")
        ]
        
        mock_download_file.side_effect = ["file1.csv.gz", "file2.csv.gz"]
        mock_process_archive.side_effect = ["file1.csv", "file2.csv"]
        
        result = sensor_app.download_sensor_data(urls, self.mock_extension)
        
        self.assertEqual(result, ["file1.csv", "file2.csv"])
        self.assertEqual(mock_download_file.call_count, 2)
        self.assertEqual(mock_process_archive.call_count, 2)
    
    @patch('sensor_app.download_file')
    def test_download_sensor_data_with_stop_event(self, mock_download_file):
        """Test download cancellation when stop_event is set."""
        urls = [("http://example.com/file1.csv", "file1.csv")]
        
        # Set stop event before download
        sensor_app.stop_event.set()
        
        result = sensor_app.download_sensor_data(urls, self.mock_extension)
        
        self.assertIsNone(result)
        self.mock_extension.sendMessage.assert_called_with(
            "analyzeSensorWrapperResult", 
            "Download process cancelled."
        )
        mock_download_file.assert_not_called()
    
    @patch('sensor_app.download_file')
    @patch('sensor_app.process_archive')
    def test_download_sensor_data_with_failed_download(self, mock_process_archive, mock_download_file):
        """Test handling of failed downloads."""
        urls = [
            ("http://example.com/file1.csv", "file1.csv"),
            ("http://example.com/file2.csv", "file2.csv")
        ]
        
        # First download succeeds, second fails
        mock_download_file.side_effect = ["file1.csv", None]
        mock_process_archive.return_value = "file1.csv"
        
        result = sensor_app.download_sensor_data(urls, self.mock_extension)
        
        self.assertEqual(result, ["file1.csv"])
        self.assertEqual(mock_download_file.call_count, 2)
        mock_process_archive.assert_called_once()


class TestAnalyzeSensor(TestSensorApp):
    
    def test_analyze_sensor_extension_none_raises_error(self):
        """Test that analyze_sensor raises ValueError when extension is None."""
        with self.assertRaises(ValueError) as context:
            sensor_app.analyze_sensor(2023, 2023, "dht22", "123", extension=None)
        
        self.assertEqual(str(context.exception), "Extension cannot be None")
    
    @patch('sensor_app.data_operations')
    def test_analyze_sensor_data_already_exists(self, mock_data_operations):
        """Test analyze_sensor when data already exists in database."""
        # Setup mocks
        mock_data_operations.exists_sensor_data_in_year.return_value = True
        mock_analyzed_data = AnalyzedSensor("123", [], [])
        mock_data_operations.load_sensor_data.return_value = mock_analyzed_data
        
        result = sensor_app.analyze_sensor(2023, 2023, "dht22", "123", extension=self.mock_extension)
        
        self.assertEqual(result.sensor_id, "123")
        mock_data_operations.exists_sensor_data_in_year.assert_called_with("123", 2023)
        mock_data_operations.load_sensor_data.assert_called_with("123", 2023, 2023)
    
    @patch('sensor_app.data_operations')
    @patch('sensor_app.generate_urls')
    @patch('sensor_app.download_sensor_data')
    def test_analyze_sensor_download_fails(self, mock_download, mock_generate_urls, mock_data_operations):
        """Test analyze_sensor when download fails."""
        # Setup mocks
        mock_data_operations.exists_sensor_data_in_year.return_value = False
        mock_generate_urls.return_value = [("http://example.com/file.csv", "file.csv")]
        mock_download.return_value = None
        
        result = sensor_app.analyze_sensor(2023, 2023, "dht22", "123", extension=self.mock_extension)
        
        self.assertIsNone(result)
    
    @patch('sensor_app.data_operations')
    @patch('sensor_app.generate_urls')
    @patch('sensor_app.download_sensor_data')
    @patch('sensor_app.process_sensor_data')
    @patch('sensor_app.calculate_average_temperature')
    @patch('sensor_app.calculate_max_temperature')
    @patch('sensor_app.calculate_min_temperature')
    @patch('sensor_app.calculate_temperature_difference')
    @patch('sensor_app.calculate_average_humidity')
    @patch('sensor_app.calculate_max_humidity')
    @patch('sensor_app.calculate_min_humidity')
    @patch('sensor_app.calculate_humidity_difference')
    def test_analyze_sensor_success(self, mock_humidity_diff, mock_min_humidity, mock_max_humidity,
                                  mock_avg_humidity, mock_temp_diff, mock_min_temp, mock_max_temp,
                                  mock_avg_temp, mock_process_data, mock_download, mock_generate_urls,
                                  mock_data_operations):
        """Test successful sensor analysis."""
        # Setup mocks
        mock_data_operations.exists_sensor_data_in_year.return_value = False
        mock_generate_urls.return_value = [("http://example.com/file.csv", "file.csv")]
        mock_download.return_value = ["file.csv"]
        
        test_timestamp = datetime(2023, 1, 1)
        mock_sensor_data = [
            SensorData("123", test_timestamp, 25.5, 60.0),
            SensorData("123", test_timestamp, 26.0, 65.0)
        ]
        mock_process_data.return_value = mock_sensor_data
        
        # Setup calculation mocks
        mock_avg_temp.return_value = 25.75
        mock_max_temp.return_value = 26.0
        mock_min_temp.return_value = 25.5
        mock_temp_diff.return_value = 0.5
        mock_avg_humidity.return_value = 62.5
        mock_max_humidity.return_value = 65.0
        mock_min_humidity.return_value = 60.0
        mock_humidity_diff.return_value = 5.0
        
        result = sensor_app.analyze_sensor(2023, 2023, "dht22", "123", extension=self.mock_extension)
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(result.sensor_id, "123")
        self.assertEqual(len(result.temperature_data), 1)
        self.assertEqual(len(result.humidity_data), 1)
        
        # Verify temperature data
        temp_data = result.temperature_data[0]
        self.assertEqual(temp_data.sensor_id, "123")
        self.assertEqual(temp_data.timestamp, test_timestamp)
        self.assertEqual(temp_data.avg, 25.75)
        self.assertEqual(temp_data.max, 26.0)
        self.assertEqual(temp_data.min, 25.5)
        self.assertEqual(temp_data.diff, 0.5)
        
        # Verify humidity data
        humidity_data = result.humidity_data[0]
        self.assertEqual(humidity_data.sensor_id, "123")
        self.assertEqual(humidity_data.timestamp, test_timestamp)
        self.assertEqual(humidity_data.avg, 62.5)
        self.assertEqual(humidity_data.max, 65.0)
        self.assertEqual(humidity_data.min, 60.0)
        self.assertEqual(humidity_data.diff, 5.0)
        
        # Verify data insertion
        mock_data_operations.insert_data.assert_called_once_with(mock_sensor_data)
    
    @patch('sensor_app.data_operations')
    @patch('sensor_app.generate_urls')
    @patch('sensor_app.download_sensor_data')
    @patch('sensor_app.process_sensor_data')
    @patch('sensor_app.calculate_average_temperature')
    @patch('sensor_app.calculate_max_temperature')
    @patch('sensor_app.calculate_min_temperature')
    @patch('sensor_app.calculate_temperature_difference')
    @patch('sensor_app.calculate_average_humidity')
    @patch('sensor_app.calculate_max_humidity')
    @patch('sensor_app.calculate_min_humidity')
    @patch('sensor_app.calculate_humidity_difference')
    def test_analyze_sensor_multiple_years_partial_existing(self, mock_humidity_diff, mock_min_humidity,
                                                          mock_max_humidity, mock_avg_humidity, mock_temp_diff,
                                                          mock_min_temp, mock_max_temp, mock_avg_temp,
                                                          mock_process_data, mock_download, mock_generate_urls,
                                                          mock_data_operations):
        """Test analyze_sensor with multiple years where some data already exists."""
        # Setup mocks - 2023 exists, 2024 doesn't
        def exists_side_effect(sensor_id, year):
            return year == 2023
        
        mock_data_operations.exists_sensor_data_in_year.side_effect = exists_side_effect
        
        existing_data = AnalyzedSensor("123", 
                                     [AnalyzedSensorData("123", datetime(2023, 1, 1), 20.0, 25.0, 15.0, 10.0)],
                                     [AnalyzedSensorData("123", datetime(2023, 1, 1), 50.0, 60.0, 40.0, 20.0)])
        mock_data_operations.load_sensor_data.return_value = existing_data
        
        mock_generate_urls.return_value = [("http://example.com/2024_file.csv", "2024_file.csv")]
        mock_download.return_value = ["2024_file.csv"]
        
        test_timestamp_2024 = datetime(2024, 1, 1)
        mock_sensor_data_2024 = [SensorData("123", test_timestamp_2024, 30.0, 70.0)]
        mock_process_data.return_value = mock_sensor_data_2024

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSensorApp))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestStopDownload))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestProcessArchive))
    # test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestProcessSensorData))
    # test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDownloadSensorData))
    # test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAnalyzeSensor))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)