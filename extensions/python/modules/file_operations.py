import requests
import gzip
import chardet
import csv
import datetime
import os

from modules.data_operations import SensorData
from pathlib import Path
from typing import Optional

#* Extension from Neutralino.js
ext = None  # Will be set from main.py


def download_file(url: str, file_name: str, extension=None) -> Optional[str]:
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


def extract_archive(file_name: str, extension=None) -> str:
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


def open_and_parse_csv_file(file_name: str, file_encoding: str) -> list[SensorData]:
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
        
        if not is_valid_float(separated[6]) or not is_valid_float(separated[7]):
            continue
        
        sensor_id = int(separated[0])
        location = int(separated[2])
        lat = float(separated[3])
        lon = float(separated[4])
        timestamp = datetime.datetime.strptime(separated[5], "%Y-%m-%dT%H:%M:%S")
        temperature = float(separated[6])
        humidity = float(separated[7])
        extracted_data.append(SensorData(sensor_id, location, lat, lon, timestamp, temperature, humidity))

    return extracted_data

def is_valid_float(value: str) -> Optional[float]:
    """
    Convert a string to a float, returning None if conversion fails.
    
    Args:
        value (str): The string to convert.
    
    Returns:
        Optional[float]: The converted float or None if conversion fails.
    """
    try:
        return float(value)
    except ValueError:
        return None

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
