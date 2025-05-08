import requests
import gzip
import chardet
import csv
import datetime
import os
from pathlib import Path

#* Extension from Neutralino.js
ext = None  # Will be set from main.py


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

# NOTE: Old implementation
# def extract_archive(file_name: str, extension=None) -> None:
#     global ext
#     ext = extension
#
#     with gzip.open(file_name, "rb") as file:
#         content = file.read()
#     with open(file_name.replace(".gz", ""), "wb") as file:
#         file.write(content)
#     ext.sendMessage('analyzeSensorWrapperResult', f"File {file_name} extracted successfully.")

def extract_archive(file_name: str, extension=None) -> str:
    # global ext
    
    if extension is None:
        raise ValueError("Extension cannot be None")

    ext = extension

    with gzip.open(file_name, "rb") as file:
        content = file.read()
    
    extracted_file_name: str = file_name.replace(".gz", "")
    with open(extracted_file_name, "wb") as file:
        file.write(content)
    
    ext.sendMessage('analyzeSensorWrapperResult', f"File {file_name} extracted successfully.")
    
    return extracted_file_name


def check_encoding_of_file(file_name: str) -> str:
    with open(file_name, "rb") as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
    return result["encoding"] if result["encoding"] is not None else "utf-8"


def open_and_parse_csv_file(file_name: str, file_encoding: str) -> list[tuple[float, datetime.datetime]]:
    """
    Open and parse a CSV file containing sensor data.
    
    Reads a CSV file with semicolon-separated values, extracts temperature and timestamp
    from specific columns, and returns a list of temperature-timestamp tuples.
    
    Args:
        file_name (str): Path to the CSV file to be opened.
        file_encoding (str): Encoding of the CSV file.
    
    Returns:
        list[tuple[float, datetime.datetime]]: A list of tuples containing temperature 
        and corresponding timestamp, with the header row removed.
    """

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


def delete_sensor_data_files(debug=None, extension=None) -> None:
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
