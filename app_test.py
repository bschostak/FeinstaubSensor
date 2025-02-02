import unittest
import datetime
from app import parse_file_name, generate_urls, get_date_range_year, get_date_range, calculate_average_temperature, calculate_max_temperature, calculate_min_temperature

class TestAppMethods(unittest.TestCase):

    def test_parse_file_name(self):
        date = datetime.datetime(2024, 1, 2)
        sensor_type = "dht22"
        sensor_id = "113"
        expected = "2024-01-02_dht22_sensor_113.csv"
        self.assertEqual(parse_file_name(date, sensor_type, sensor_id), expected)

        date = datetime.datetime(2023, 1, 2)
        expected = "2023-01-02_dht22_sensor_113.csv.gz"
        self.assertEqual(parse_file_name(date, sensor_type, sensor_id), expected)

    def test_generate_urls(self):
        start_year = 2024
        end_year = 2024
        sensor_type = "dht22"
        sensor_id = "113"
        urls = generate_urls(start_year, end_year, sensor_type, sensor_id)
        self.assertGreater(len(urls), 0)
        self.assertTrue(urls[0][0].startswith("http://archive.sensor.community/"))

    def test_get_date_range_year(self):
        year = 2024
        dates = get_date_range_year(year)
        self.assertGreater(len(dates), 0)
        self.assertEqual(dates[0], datetime.datetime(2024, 1, 1))

    def test_get_date_range(self):
        from_time = datetime.datetime(2024, 1, 1)
        to_time = datetime.datetime(2024, 1, 3)
        expected = [
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 1, 2),
            datetime.datetime(2024, 1, 3)
        ]
        self.assertEqual(get_date_range(from_time, to_time), expected)

    def test_calculate_average_temperature(self):
        data = [(10.0, datetime.datetime(2024, 1, 1)), (20.0, datetime.datetime(2024, 1, 2))]
        expected = 15.0
        self.assertEqual(calculate_average_temperature(data), expected)

    def test_calculate_max_temperature(self):
        data = [(10.0, datetime.datetime(2024, 1, 1)), (20.0, datetime.datetime(2024, 1, 2))]
        expected = 20.0
        self.assertEqual(calculate_max_temperature(data), expected)

    def test_calculate_min_temperature(self):
        data = [(10.0, datetime.datetime(2024, 1, 1)), (20.0, datetime.datetime(2024, 1, 2))]
        expected = 10.0
        self.assertEqual(calculate_min_temperature(data), expected)

if __name__ == '__main__':
    unittest.main()