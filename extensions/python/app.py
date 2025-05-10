from NeutralinoExtension import *  # noqa: F403
import datetime
import threading
from pathlib import Path
from typing import Optional

from modules.url_generator import generate_urls
from modules.file_operations import download_file, extract_archive, check_encoding_of_file, open_and_parse_csv_file, delete_sensor_data_files  # noqa: F401
from modules.data_analysis import calculate_average_temperature, calculate_max_temperature, calculate_min_temperature, calculate_temperature_difference
from modules.visualization import draw_interactive_graph  # noqa: F401

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


def process_sensor_data(file_name) -> list[tuple[float, datetime.datetime]]:
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
                   ) -> Optional[list[tuple[datetime.datetime, float, float, float, float]]]:

    if extension is None:
        raise ValueError("Extension cannot be None")


    SENSOR_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
    urls: list[tuple[str, str]] = generate_urls(start_year, end_year, sensor_type, sensor_id)

    downloaded_files: list[str] | None = download_sensor_data(urls, extension)

    if not downloaded_files:
        return None

    analysed_data: list[tuple[datetime.datetime, float, float, float, float]] = []

    for file_name in downloaded_files:
        csv_parsed_data = process_sensor_data(file_name)
        
        measurement_date = csv_parsed_data[0][1]
        average = calculate_average_temperature(csv_parsed_data)
        max_temperature = calculate_max_temperature(csv_parsed_data)
        min_temperature = calculate_min_temperature(csv_parsed_data)
        temperature_diff = calculate_temperature_difference(csv_parsed_data)

        analysed_data.append((measurement_date, average, max_temperature, min_temperature, temperature_diff))

    return analysed_data
