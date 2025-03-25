from NeutralinoExtension import *  # noqa: F403
import datetime
from pathlib import Path

from modules.url_generator import generate_urls
from modules.file_operations import download_file, extract_archive, check_encoding_of_file, open_csv_file, delete_sensor_data_files
from modules.data_analysis import calculate_average_temperature, calculate_max_temperature, calculate_min_temperature, calculate_temperature_difference
from modules.visualization import draw_graph

#* Extension from Neutralino.js
ext = None  # Will be set from main.py

def analyze_sensor(start_year: int, end_year: int, sensor_type: str, sensor_id: str, debug=False, extension=None):
    global ext
    ext = extension

    analysed_data: list[tuple[datetime.datetime, float, float, float, float]] = []

    # Create sensor_data directory if it doesn't exist
    data_dir = Path("./sensor_data")
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        
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