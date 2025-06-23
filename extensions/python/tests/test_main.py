import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory (extensions/python) to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Mock the NeutralinoExtension module before importing main
mock_neutralino = MagicMock()
mock_neutralino.NeutralinoExtension = MagicMock()
sys.modules['NeutralinoExtension'] = mock_neutralino

# Mock other modules that might not be available during testing
sys.modules['sensor_app'] = MagicMock()
sys.modules['modules.year_fetcher'] = MagicMock()
sys.modules['modules.data_operations'] = MagicMock()
sys.modules['modules.visualization'] = MagicMock()

# Now import main
import main
from unittest.mock import Mock


class TestMainFunctions(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_ext = Mock()
        main.ext = self.mock_ext
        
    def tearDown(self):
        """Clean up after each test method."""
        self.mock_ext.reset_mock()

    def test_ping(self):
        """Test the ping function sends correct message."""
        test_data = "Hello"
        expected_message = 'Python says PONG, in reply to "Hello"'
        
        main.ping(test_data)
        
        self.mock_ext.sendMessage.assert_called_once_with("pingResult", expected_message)

    def test_taskLongRun(self):
        """Test the taskLongRun function sends progress messages and stop polling."""
        with patch('time.sleep'):  # Mock sleep to speed up test
            main.taskLongRun(None)
        
        # Check that progress messages were sent (5 times)
        progress_calls = [call for call in self.mock_ext.sendMessage.call_args_list 
                         if call[0][0] == "pingResult"]
        self.assertEqual(len(progress_calls), 5)
        
        # Check that stopPolling message was sent
        self.mock_ext.sendMessage.assert_any_call("stopPolling")
        
        # Verify the progress message format
        first_progress_call = progress_calls[0]
        self.assertIn("Long-running task: 1 / 5", first_progress_call[0][1])

    @patch('main.app.analyze_sensor')
    @patch('main.visualization.draw_interactive_graph')
    def test_analyze_sensor_wrapper_success(self, mock_draw_graph, mock_analyze_sensor):
        """Test analyze_sensor_wrapper with successful analysis."""
        # Setup mocks
        mock_analyzed_data = Mock()
        mock_analyze_sensor.return_value = mock_analyzed_data
        mock_draw_graph.return_value = "base64_html_data"
        
        test_data = ["123", "456", "dht22", "temperature"]
        
        main.analyze_sensor_wrapper(test_data)
        
        # Verify analyze_sensor was called with correct parameters
        mock_analyze_sensor.assert_called_once_with(123, 456, "dht22", "temperature", extension=self.mock_ext)
        
        # Verify graph was drawn
        mock_draw_graph.assert_called_once_with(mock_analyzed_data)
        
        # Verify message was sent
        self.mock_ext.sendMessage.assert_called_once_with("displaySensorHtml", "base64_html_data")

    @patch('main.app.analyze_sensor')
    def test_analyze_sensor_wrapper_failure(self, mock_analyze_sensor):
        """Test analyze_sensor_wrapper when analysis returns None."""
        mock_analyze_sensor.return_value = None
        
        test_data = ["123", "456", "dht22", "temperature"]
        
        main.analyze_sensor_wrapper(test_data)
        
        # Verify analyze_sensor was called
        mock_analyze_sensor.assert_called_once_with(123, 456, "dht22", "temperature", extension=self.mock_ext)
        
        # Verify no message was sent when analysis fails
        self.mock_ext.sendMessage.assert_not_called()

    @patch('main.app.delete_sensor_data_files')
    def test_delete_sensor_data_files_wrapper(self, mock_delete_files):
        """Test delete_sensor_data_files_wrapper calls the correct function."""
        test_data = "unused"
        
        main.delete_sensor_data_files_wrapper(test_data)
        
        mock_delete_files.assert_called_once_with(extension=self.mock_ext)

    @patch('main.app.stop_download')
    def test_stop_download_wrapper(self, mock_stop_download):
        """Test stop_download_wrapper calls the correct function."""
        test_data = "unused"
        
        main.stop_download_wrapper(test_data)
        
        mock_stop_download.assert_called_once()

    @patch('main.year_fetcher.fetch_available_years')
    def test_fetch_available_years_wrapper(self, mock_fetch_years):
        """Test fetch_available_years_wrapper fetches and sends year data."""
        mock_years_data = {"years": [2023, 2024]}
        mock_fetch_years.return_value = mock_years_data
        
        test_data = "unused"
        
        main.fetch_available_years_wrapper(test_data)
        
        mock_fetch_years.assert_called_once()
        self.mock_ext.sendMessage.assert_called_once_with("populateYearDropdowns", mock_years_data)


class TestProcessAppEvent(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_ext = Mock()
        main.ext = self.mock_ext
        
    def tearDown(self):
        """Clean up after each test method."""
        self.mock_ext.reset_mock()

    def test_processAppEvent_ping(self):
        """Test processAppEvent handles ping function call."""
        self.mock_ext.isEvent.return_value = True
        self.mock_ext.parseFunctionCall.return_value = ("ping", "test_data")
        
        test_event = {"event": "runPython", "data": "ping:test_data"}
        
        with patch('main.ping') as mock_ping:
            main.processAppEvent(test_event)
            mock_ping.assert_called_once_with("test_data")

    def test_processAppEvent_longRun(self):
        """Test processAppEvent handles longRun function call."""
        self.mock_ext.isEvent.return_value = True
        self.mock_ext.parseFunctionCall.return_value = ("longRun", "test_data")
        
        test_event = {"event": "runPython", "data": "longRun:test_data"}
        
        main.processAppEvent(test_event)
        
        self.mock_ext.sendMessage.assert_called_once_with("startPolling")
        self.mock_ext.runThread.assert_called_once_with(main.taskLongRun, "taskLongRun", "test_data")

    def test_processAppEvent_analyze_sensor_wrapper(self):
        """Test processAppEvent handles analyze_sensor_wrapper function call."""
        self.mock_ext.isEvent.return_value = True
        self.mock_ext.parseFunctionCall.return_value = ("analyze_sensor_wrapper", "test_data")
        
        test_event = {"event": "runPython", "data": "analyze_sensor_wrapper:test_data"}
        
        main.processAppEvent(test_event)
        
        self.mock_ext.runThread.assert_called_once_with(
            main.analyze_sensor_wrapper, "analyze_sensor_wrapper", "test_data"
        )

    def test_processAppEvent_delete_sensor_data_files_wrapper(self):
        """Test processAppEvent handles delete_sensor_data_files_wrapper function call."""
        self.mock_ext.isEvent.return_value = True
        self.mock_ext.parseFunctionCall.return_value = ("delete_sensor_data_files_wrapper", "test_data")
        
        test_event = {"event": "runPython", "data": "delete_sensor_data_files_wrapper:test_data"}
        
        main.processAppEvent(test_event)
        
        self.mock_ext.runThread.assert_called_once_with(
            main.delete_sensor_data_files_wrapper, "delete_sensor_data_files_wrapper", "test_data"
        )

    def test_processAppEvent_stop_download_wrapper(self):
        """Test processAppEvent handles stop_download_wrapper function call."""
        self.mock_ext.isEvent.return_value = True
        self.mock_ext.parseFunctionCall.return_value = ("stop_download_wrapper", "test_data")
        
        test_event = {"event": "runPython", "data": "stop_download_wrapper:test_data"}
        
        main.processAppEvent(test_event)
        
        self.mock_ext.runThread.assert_called_once_with(
            main.stop_download_wrapper, "stop_download_wrapper", "test_data"
        )

    def test_processAppEvent_fetch_available_years_wrapper(self):
        """Test processAppEvent handles fetch_available_years_wrapper function call."""
        self.mock_ext.isEvent.return_value = True
        self.mock_ext.parseFunctionCall.return_value = ("fetch_available_years_wrapper", "test_data")
        
        test_event = {"event": "runPython", "data": "fetch_available_years_wrapper:test_data"}
        
        main.processAppEvent(test_event)
        
        self.mock_ext.runThread.assert_called_once_with(
            main.fetch_available_years_wrapper, "fetch_available_years_wrapper", "test_data"
        )

    def test_processAppEvent_unknown_function(self):
        """Test processAppEvent handles unknown function calls gracefully."""
        self.mock_ext.isEvent.return_value = True
        self.mock_ext.parseFunctionCall.return_value = ("unknown_function", "test_data")
        
        test_event = {"event": "runPython", "data": "unknown_function:test_data"}
        
        # Should not raise an exception
        main.processAppEvent(test_event)
        
        # Should not call runThread for unknown functions
        self.mock_ext.runThread.assert_not_called()

    def test_processAppEvent_not_runPython_event(self):
        """Test processAppEvent ignores non-runPython events."""
        self.mock_ext.isEvent.return_value = False
        
        test_event = {"event": "otherEvent", "data": "test_data"}
        
        main.processAppEvent(test_event)
        
        # Should not parse function call or run threads
        self.mock_ext.parseFunctionCall.assert_not_called()
        self.mock_ext.runThread.assert_not_called()


if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMainFunctions))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestProcessAppEvent))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)