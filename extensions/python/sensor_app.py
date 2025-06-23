from NeutralinoExtension import *  # noqa: F403
import threading
import modules.data_operations as data_operations
from modules.data_operations import SensorData

from pathlib import Path
from typing import Optional
from modules.data_operations import AnalyzedSensorData
from modules.data_operations import AnalyzedSensor

from modules.url_generator import generate_urls
from modules.file_operations import download_file, extract_archive, check_encoding_of_file, open_and_parse_csv_file, delete_sensor_data_files  # noqa: F401
from modules.data_analysis import *

#* Extension from Neutralino.js
SENSOR_DATA_DIR = Path("./sensor_data")


stop_event = threading.Event()

def stop_download() -> None:
    """
    Stops the ongoing download process.

    This function sets the global stop_event flag, signaling any active download 
    threads to halt their execution. It should be called when the user wishes 
    to cancel a file download before completion.

    Usage:
        stop_download()  # Cancels the download process

    Returns:
        None
    """
    stop_event.set()

def process_archive(file_name: str, extension=None) -> str:
    if file_name.endswith(".gz"):
        extracted_file: str = extract_archive(file_name, extension=extension)
        return extracted_file.replace(".gz", "")
    return file_name


def process_sensor_data(file_name: str) -> list[SensorData]:
    file_encoding: str = check_encoding_of_file(file_name)
    return open_and_parse_csv_file(file_name, file_encoding)


def download_sensor_data(urls: list[tuple[str, str]], extension=None) -> Optional[list[str]]:
    if extension is None:
        raise ValueError("Extension cannot be None")

    downloaded_files = []

    stop_event.clear()
    
    for url in urls:
        if stop_event.is_set():
            extension.sendMessage("analyzeSensorWrapperResult", "Download process cancelled.")
            return None

        downloaded_file_name: str | None = download_file(url[0], f"{SENSOR_DATA_DIR}/{url[1]}", extension)
        
        if downloaded_file_name:
            downloaded_files.append(process_archive(downloaded_file_name, extension))

    return downloaded_files


# NOTE: Should I use None on extension and then check if its None to give error, or leave it simply empty?

#NOTE: Make optional for all method returns that can be a speicfied value or None.

def analyze_sensor(start_year: int, end_year: int, sensor_type: str, sensor_id: str, 
                   debug=False, extension=None
                   ) -> Optional[AnalyzedSensor]:

    if extension is None:
        raise ValueError("Extension cannot be None")


    SENSOR_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    analysed_data: AnalyzedSensor = AnalyzedSensor(sensor_id, [], [])
    
    modified_start_year = start_year
    
    for year in range(start_year, end_year + 1):
        if not data_operations.exists_sensor_data_in_year(sensor_id, year):
            continue
        extension.sendMessage("analyzeSensorWrapperResult", f"Data for sensor {sensor_id} in year {year} already exists in the database.")
        modified_start_year += 1
        loaded_data: AnalyzedSensor = data_operations.load_sensor_data(sensor_id, year, year)
        analysed_data.temperature_data.extend(loaded_data.temperature_data)
        analysed_data.humidity_data.extend(loaded_data.humidity_data)
        if year == end_year:
            extension.sendMessage("analyzeSensorWrapperResult", f"Data for sensor {sensor_id} already exists for the year {start_year} to {end_year}.")
            return analysed_data
            
    
    urls: list[tuple[str, str]] = generate_urls(modified_start_year, end_year, sensor_type, sensor_id)

    downloaded_files: list[str] | None = download_sensor_data(urls, extension)

    if not downloaded_files:
        return None
    
    total_parsed_data: list[SensorData] = []
    
    for file_name in downloaded_files:
        csv_parsed_data: list[SensorData] = process_sensor_data(file_name)
        total_parsed_data.extend(csv_parsed_data)
        
        measurement_date = csv_parsed_data[0].timestamp
        average_temperature = calculate_average_temperature(csv_parsed_data)
        max_temperature = calculate_max_temperature(csv_parsed_data)
        min_temperature = calculate_min_temperature(csv_parsed_data)
        temperature_diff = calculate_temperature_difference(csv_parsed_data)
        
        average_humidity = calculate_average_humidity(csv_parsed_data)
        max_humidity = calculate_max_humidity(csv_parsed_data)
        min_humidity = calculate_min_humidity(csv_parsed_data)
        humidity_diff = calculate_humidity_difference(csv_parsed_data)
        
        analysed_data.temperature_data.append(AnalyzedSensorData(sensor_id, measurement_date, average_temperature, max_temperature, min_temperature, temperature_diff))
        analysed_data.humidity_data.append(AnalyzedSensorData(sensor_id, measurement_date, average_humidity, max_humidity, min_humidity, humidity_diff))    
    data_operations.insert_data(total_parsed_data)
    return analysed_data
