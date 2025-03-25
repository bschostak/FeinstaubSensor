import datetime
from .date_utils import get_date_range_year

# * Beispiel-URLs:
# new: https://archive.sensor.community/2024-01-02/2024-01-02_dht22_sensor_113.csv
# old: https://archive.sensor.community/2023/2023-01-01/2023-01-02_dht22_sensor_113.csv.gz

base_url :str = "http://archive.sensor.community/"

def parse_file_name(date: datetime.datetime, sensor_type: str, sensor_id: str) -> str:
    if date.year >= 2024:
        return f"{date.year}-{date.month:02d}-{date.day:02d}_{sensor_type}_sensor_{sensor_id}.csv"
    else:
        return f"{date.year}-{date.month:02d}-{date.day:02d}_{sensor_type}_sensor_{sensor_id}.csv.gz"

def parse_url(date: datetime.datetime, sensor_type: str, sensor_id: str) -> str:
    if date.year >= 2024:
        return f"{base_url}/{date.year}-{date.month:02d}-{date.day:02d}/{parse_file_name(date, sensor_type, sensor_id)}"
    else:
        return f"{base_url}{date.year}/{date.year}-{date.month:02d}-{date.day:02d}/{parse_file_name(date, sensor_type, sensor_id)}"

def generate_urls(start_year: int, end_year: int, sensor_type: str, sensor_id: str) -> list[tuple[str, str]]:
    urls: list[tuple[str, str]] = []

    #* So sieht tulpe aus:
    # list:
    # [(sensor_url, file_name)
    # (sensor_url, file_name)]

    for year in range(int(start_year), int(end_year) + 1):
        for date in get_date_range_year(year):
            file_name = parse_file_name(date, sensor_type, sensor_id)
            sensor_url = parse_url(date, sensor_type, sensor_id)
            urls.append((sensor_url, file_name))

    return urls

def generate_single_sensor_url(start_year: int, end_year: int, sensor_type: str, sensor_id: str) -> str:
    url :str = "sensor.blablabla.de/" + str(start_year) + "-" + str(end_year) + "/" + str(sensor_type) + "/" + str(sensor_id) + ".csv"
    return url