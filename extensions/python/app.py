from NeutralinoExtension import *  # noqa: F403
import datetime
import threading
from pathlib import Path

from modules.url_generator import generate_urls
from modules.file_operations import download_file, extract_archive, check_encoding_of_file, open_and_parse_csv_file, delete_sensor_data_files  # noqa: F401
from modules.data_analysis import calculate_average_temperature, calculate_max_temperature, calculate_min_temperature, calculate_temperature_difference
from modules.visualization import draw_interactive_graph  # noqa: F401

#* Extension from Neutralino.js


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

def process_archive(file_name: str, extension=None):
    if file_name.endswith(".gz"):
        extracted_file: str = extract_archive(file_name, extension=extension)
        return extracted_file.replace(".gz", "")
    return file_name


def process_sensor_data(file_name):
    file_encoding: str = check_encoding_of_file(file_name)
    return open_and_parse_csv_file(file_name, file_encoding)


# NOTE: Should I use None on extension and then check if its None to give error, or leave it simply empty?
def analyze_sensor(start_year: int, end_year: int, sensor_type: str, sensor_id: str, debug=False, extension=None):
    if extension is None:
        raise ValueError("Extension cannot be None")

    ext = extension

    analysed_data: list[tuple[datetime.datetime, float, float, float, float]] = []

    data_dir = Path("./sensor_data")

    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        
    urls: list[tuple[str, str]] = generate_urls(start_year, end_year, sensor_type, sensor_id)

    stop_event.clear()

    for url in urls:
        if stop_event.is_set():
            ext.sendMessage('analyzeSensorWrapperResult', "Download process cancelled.")
            return None

        downloaded_file_name: str | None = download_file(url=url[0], file_name=f"./sensor_data/{url[1]}", extension=extension)
        

        if downloaded_file_name is None:
            continue

        downloaded_file_name = process_archive(downloaded_file_name, extension)
        
        csv_parsed_data: list[tuple[float, datetime.datetime]] = process_sensor_data(downloaded_file_name)

        
        average: float = calculate_average_temperature(csv_parsed_data)
        max_temperature: float = calculate_max_temperature(csv_parsed_data)
        min_temperature: float = calculate_min_temperature(csv_parsed_data)
        temperature_diff: float = calculate_temperature_difference(csv_parsed_data)
        measurement_date = csv_parsed_data[0][1]

        analysed_data.append((measurement_date, average, max_temperature, min_temperature, temperature_diff))

    return analysed_data
