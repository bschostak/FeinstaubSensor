###########################################################################
#!This file is for testing the GUI and file creation with Python extension.
###########################################################################

from NeutralinoExtension import *  # noqa: F403
import datetime
import requests
import csv
import base64
import matplotlib.pyplot as plt
import gzip
import chardet
from pathlib import Path
import os

#* Extension from Neutralino.js
ext = None  # Will be set from main.py

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

def get_date_range_year(year: int) -> list[datetime.datetime]:
    """
    Gibt eine Liste von Datumsobjekten zurück, die alle Tage des angegebenen Jahres enthalten.
    Falls das Jahr das aktuelle Jahr ist, wird der letzte Tag durch den heutigen Tag ersetzt.
    """
    first_day = datetime.datetime(year=year, month=1, day=1)
    last_day = datetime.datetime(year=year, month=12, day=31)

    if first_day.year == datetime.datetime.now().year:
        last_day = datetime.datetime.now()
    return get_date_range(first_day, last_day)

def get_date_range(from_time: datetime.datetime, to_time: datetime.datetime) -> list[datetime.datetime]:
    """
    Gibt eine Liste aller Daten zwischen zwei gegebenen Datumsobjekten zurück.
    """
    date_list: list[datetime.datetime] = []
    date_difference = to_time - from_time
    days_difference = date_difference.days
    total_days = int(days_difference)

    for i in range(total_days + 1):
        """
        Addiert die Anzahl der Tage zum Startdatum und fügt das Ergebnis der Liste hinzu.
        Beim addieren wird bereits beachtet, dass auch der Monat und das Jahr korrekt angepasst werden.
        """
        date_list.append(from_time + datetime.timedelta(days=i))

    return date_list

def download_file(url: str, file_name: str, extension=None) -> str | None:
    global ext
    ext = extension

    if Path(file_name).exists():
        ext.sendMessage('analyzeSensorWrapperResult', f"File {file_name} already exists.")
        return file_name
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, "wb") as file:
            file.write(response.content)
        ext.sendMessage('analyzeSensorWrapperResult', f"File {file_name} downloaded successfully.")
        return file_name
    else:
        ext.sendMessage('analyzeSensorWrapperResult', f"Failed to download file {file_name}. Status code: {response.status_code}")
        return None

def extract_archive(file_name: str, extension=None) -> None:
    global ext
    ext = extension

    with gzip.open(file_name, "rb") as file:
        content = file.read()
    with open(file_name.replace(".gz", ""), "wb") as file:
        file.write(content)
    ext.sendMessage('analyzeSensorWrapperResult', f"File {file_name} extracted successfully.")

def check_encoding_of_file(file_name: str) -> str:
    with open(file_name, "rb") as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
    return result["encoding"] if result["encoding"] is not None else "utf-8"
def open_csv_file(file_name: str, file_encoding: str) -> list[tuple[float, datetime.datetime]]:
    with open(file_name, "r", encoding=file_encoding) as file:
        reader = csv.reader(file, dialect='excel')
        data = list(reader)
    data.pop(0)

    extracted_data: list[tuple[float, datetime.datetime]] = []
    for row in data:
        separated = row[0].split(";")
        timestamp = datetime.datetime.strptime(separated[5], "%Y-%m-%dT%H:%M:%S")
        temperature = float(separated[6])
        extracted_data.append((temperature, timestamp))

    return extracted_data

def calculate_average_temperature(data: list[tuple[float, datetime.datetime]]) -> float:
    total_temperature = 0.0

    for row in data:
        total_temperature += row[0]

    return total_temperature / len(data)

def calculate_max_temperature(data: list[tuple[float, datetime.datetime]]) -> float:
    highest_temperature = data[0][0]

    for row in data:
        if row[0] > highest_temperature:
            highest_temperature = row[0]

    return highest_temperature

def calculate_min_temperature(data: list[tuple[float, datetime.datetime]]) -> float:
    lowest_temperature = data[0][0]

    for row in data:
        if row[0] < lowest_temperature:
            lowest_temperature = row[0]

    return lowest_temperature

def calculate_temperature_difference(data: list[tuple[float, datetime.datetime]]) -> float:
    temperature_difference = calculate_max_temperature(data) - calculate_min_temperature(data)

    return temperature_difference

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def draw_graph(analysed_data: list[tuple[datetime.datetime, float, float, float, float]]):
    dates = [data[0].timestamp() for data in analysed_data]
    avg_temps = [data[1] for data in analysed_data]
    high_temps = [data[2] for data in analysed_data]
    low_temps = [data[3] for data in analysed_data]
    temp_diffs = [data[4] for data in analysed_data]

    plt.figure(figsize=(10, 6))

    plt.plot(dates, avg_temps, label='Ø', color='blue')
    plt.plot(dates, high_temps, label='max', color='red')
    plt.plot(dates, low_temps, label='min', color='green')
    plt.plot(dates, temp_diffs, label='diff', color='orange')

    plt.xlabel('Datum')
    plt.ylabel('Temperatur (°C)')
    plt.title('Temperaturanalyse')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig('temperaturanalyse.png')

    base64_image: str = get_image_base64('temperaturanalyse.png')

    return base64_image


def delete_sensor_data_files(debug=None, extension=None):
    global ext
    ext = extension
    
    data_dir = Path("./sensor_data")
    
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        ext.sendMessage('analyzeSensorWrapperResult', "Created sensor_data directory.")
        return

    deleted_files_count: int = 0
    
    for file_path in data_dir.glob("*"):
        if file_path.suffix in ['.csv', '.gz'] or file_path.name.endswith('.csv.gz'):
            try:
                os.remove(file_path)
                deleted_files_count += 1
            except Exception as e:
                ext.sendMessage('analyzeSensorWrapperResult', f"Error deleting {file_path}: {str(e)}")
    
    ext.sendMessage('analyzeSensorWrapperResult', f"Deleted {deleted_files_count} sensor data files.")


def analyze_sensor(start_year: int, end_year: int, sensor_type: str, sensor_id: str, debug=False, extension=None):
    global ext
    ext = extension

    analysed_data: list[tuple[datetime.datetime, float, float, float, float]] = []

    urls = generate_urls(start_year, end_year, sensor_type, sensor_id)

    for url in urls:
        downloaded_file_name = download_file(url=url[0], file_name=f"./sensor_data/{url[1]}", extension=extension)
        if downloaded_file_name is None:
            continue
        if downloaded_file_name.endswith(".gz"):
            extract_archive(downloaded_file_name, extension=extension)
            downloaded_file_name = downloaded_file_name.replace(".gz", "")

        file_encoding = check_encoding_of_file(downloaded_file_name)
        csv_file = open_csv_file(downloaded_file_name, file_encoding)
        average = calculate_average_temperature(csv_file)
        max_temperature = calculate_max_temperature(csv_file)
        min_temperature = calculate_min_temperature(csv_file)
        temperature_diff = calculate_temperature_difference(csv_file)
        measurement_date = csv_file[0][1]

        analysed_data.append((measurement_date, average, max_temperature, min_temperature, temperature_diff))

    return analysed_data

# print(analysed_data) ##* Eine CLI-Ansicht der Daten