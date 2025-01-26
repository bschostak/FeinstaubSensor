import datetime
import requests # Ist kein Fehler.
import csv

from pathlib import Path

# https://archive.sensor.community/2024-01-01/2024-01-01_bme280_sensor_113.csv
# https://archive.sensor.community/2023/2023-01-01/2023-01-01_bme280_sensor_113.csv.gz

def generate_urls(start_year: int, end_year: int, sensor_type: str, sensor_id: str) -> list[tuple[str, str]]:
    base_url = "http://archive.sensor.community"

    urls: list[tuple[str, str]] = []

    #* So sieht tulpe aus:
    # list:
    # [(url, file_name)
    # (url, file_name)]

    for year in range(start_year, end_year + 1):
        for date in get_date_range_year(year):
            file_name = f"{date.year}-{date.month:02d}-{date.day:02d}_{sensor_type}_sensor_{sensor_id}.csv"
            url = f"{base_url}/{date.year}-{date.month:02d}-{date.day:02d}/{file_name}"
            urls.append((url, file_name))

    
    return urls

    # * Beispiel-URLs:
    # https://archive.sensor.community/2023-01-02/2023-01-02_bme280_sensor_113.csv

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
    
    for i in range(total_days+1):
        """
        Addiert die Anzahl der Tage zum Startdatum und fügt das Ergebnis der Liste hinzu.
        Beim addieren wird bereits beachtet, dass auch der Monat und das Jahr korrekt angepasst werden.
        """
        date_list.append(from_time + datetime.timedelta(days=i))

    return date_list

def download_file(url: str, file_name: str) -> str | None:
    if Path(file_name).exists():
        print(f"File {file_name} already exists.")
        return file_name
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, "wb") as file:
            file.write(response.content)
        print(f"File {file_name} downloaded successfully.")
        return file_name
    else:
        print(f"Failed to download file {file_name}. Status code: {response.status_code}")
        return None

def open_csv_file(file_name: str) -> list[tuple[float, datetime.datetime]]:
    with open(file_name, "r") as file:
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

def calculate_avarage_temperature(data: list[tuple[float, datetime.datetime]]) -> float:
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


start_year = int(input("Geben Sie den Startjahr ein: ").strip() or "2024")
end_year = int(input("Geben Sie den Endjahr ein: ").strip() or "2024")
sensor_type = input("Geben Sie den Sensor-Typ ein: ").strip() or "dht22"
sensor_id = input("Geben Sie die Sensor-ID ein: ").strip() or "63047"

if start_year > end_year:
    print("Das Startjahr darf nicht größer als das Endjahr sein.")
    exit(1)

if start_year < 2024:
    print("Das Startjahr darf nicht kleiner als 2024 sein.")
    exit(1)


analysed_data: list[tuple[datetime.datetime, float, float, float, float]] = []

urls = generate_urls(start_year, end_year, sensor_type, sensor_id)
for url in urls:
    # print(url)
    downloaded_file_name = download_file(url=url[0], file_name=f"./sensor_data/{url[1]}")
    if downloaded_file_name is None:
        continue
    
    csv_file = open_csv_file(downloaded_file_name)
    avarage = calculate_avarage_temperature(csv_file)
    max = calculate_max_temperature(csv_file)
    min = calculate_min_temperature(csv_file)
    diff = calculate_temperature_difference(csv_file)
    date = csv_file[0][1]
    
    analysed_data.append((date, avarage, max, min, diff))
    
print(analysed_data)


#NOTE: Das funktioniert nur ab dem Jahr 2024.

#TODO: Durchschnittstemperatur, Höchsttemperatur, Tiefstemperatur, Temperaturdifferenz
#TODO: Unterstützung für den alten Typ der Sensoren hinzufügen

#* Sensor: id: 63047, dht22