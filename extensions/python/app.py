from NeutralinoExtension import *  # noqa: F403
import datetime
import threading
from pathlib import Path

from modules.url_generator import generate_urls
from modules.file_operations import download_file, extract_archive, check_encoding_of_file, open_and_parse_csv_file, delete_sensor_data_files  # noqa: F401
from modules.data_analysis import calculate_average_temperature, calculate_max_temperature, calculate_min_temperature, calculate_temperature_difference
from modules.visualization import draw_interactive_graph  # noqa: F401

#* Extension from Neutralino.js
ext = None  # Will be set from main.py


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

# FIX: The sensor file will be not downloaded with this implementaion.
# The event need to be setted to off, wehn we click on the "send" button.
def analyze_sensor(start_year: int, end_year: int, sensor_type: str, sensor_id: str, debug=False, extension=None):
    global ext
    ext = extension

    analysed_data: list[tuple[datetime.datetime, float, float, float, float]] = []

    data_dir = Path("./sensor_data")

    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        
    urls: list[tuple[str, str]] = generate_urls(start_year, end_year, sensor_type, sensor_id)

    for url in urls:
        if stop_event.is_set():  # Stop processing if the cancellation event is triggered
            ext.sendMessage('analyzeSensorWrapperResult', "Download process cancelled.")
            break

        downloaded_file_name: str | None = download_file(url=url[0], file_name=f"./sensor_data/{url[1]}", extension=extension)
        
        if downloaded_file_name is None:
            continue

        if downloaded_file_name.endswith(".gz"):
            extract_archive(downloaded_file_name, extension=extension)
            downloaded_file_name = downloaded_file_name.replace(".gz", "")

        file_encoding: str = check_encoding_of_file(downloaded_file_name)
        csv_parsed_data: list[tuple[float, datetime.datetime]] = open_and_parse_csv_file(downloaded_file_name, file_encoding)
        
        # Ensure processing only continues if stop_event is not set
        if stop_event.is_set():
            ext.sendMessage('analyzeSensorWrapperResult', "Processing cancelled after download.")
            break
        
        average: float = calculate_average_temperature(csv_parsed_data)
        max_temperature: float = calculate_max_temperature(csv_parsed_data)
        min_temperature: float = calculate_min_temperature(csv_parsed_data)
        temperature_diff: float = calculate_temperature_difference(csv_parsed_data)
        measurement_date = csv_parsed_data[0][1]

        analysed_data.append((measurement_date, average, max_temperature, min_temperature, temperature_diff))


    # NOTE: Old implementation
    # for url in urls:
    #     # TODO: Implement this block below
    #     if stop_event.is_set():  # Stop processing if the cancellation event is triggered
    #         ext.sendMessage('analyzeSensorWrapperResult', "Download process cancelled.")
    #         break
    #
    #     downloaded_file_name: str | None = download_file(url=url[0], file_name=f"./sensor_data/{url[1]}", extension=extension)
    #     if downloaded_file_name is None:
    #         continue
    #     if downloaded_file_name.endswith(".gz"):
    #         extract_archive(downloaded_file_name, extension=extension)
    #         downloaded_file_name = downloaded_file_name.replace(".gz", "")
    #
    #     file_encoding: str = check_encoding_of_file(downloaded_file_name)
    #     csv_parsed_data: list[tuple[float, datetime.datetime]] = open_and_parse_csv_file(downloaded_file_name, file_encoding)
    #     average: float = calculate_average_temperature(csv_parsed_data)
    #     max_temperature: float = calculate_max_temperature(csv_parsed_data)
    #     min_temperature: float = calculate_min_temperature(csv_parsed_data)
    #     temperature_diff: float = calculate_temperature_difference(csv_parsed_data)
    #     measurement_date = csv_parsed_data[0][1]
    #
    #     analysed_data.append((measurement_date, average, max_temperature, min_temperature, temperature_diff))

    return analysed_data
