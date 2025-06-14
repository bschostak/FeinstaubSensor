import sqlite3
import datetime

connection = sqlite3.connect("sensor.db")

class SensorData:
    def __init__(self, sensor_id: int, location: int, lat: float, lon: float, timestamp: datetime.datetime, temperature: float):
        self.sensor_id = sensor_id
        self.location = location
        self.lat = lat
        self.lon = lon
        self.timestamp = timestamp
        self.temperature = temperature

class AnalyzedSensorData:
    def __init__(self, sensor_id: int, timestamp: datetime.datetime, avg: float, max: float, min: float, diff: float):
        self.sensor_id = sensor_id
        self.timestamp = timestamp
        self.avg = avg
        self.max = max
        self.min = min
        self.diff = diff
        
        

def create_table():
    """Create the users table if it doesn't exist."""
    connection.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
                        sensor_id INTEGER,
                        location INTEGER NOT NULL,
                        lat DOUBLE,
                        lon DOUBLE,
                        timestamp DATETIME,
                        temperature DOUBLE,
                        PRIMARY KEY(sensor_id, timestamp)
                        )''')
    connection.commit()

def insert_data(data: list[SensorData]):
    rows = []
    for d in data:
        row = (d.sensor_id, d.location, d.lat, d.lon, d.timestamp, d.temperature)
        rows.append(row)
    
    connection.executemany("INSERT OR IGNORE INTO sensor_data (sensor_id, location, lat, lon, timestamp, temperature) VALUES (?, ?, ?, ?, ?, ?)", rows)
    connection.commit()

def exists_sensor_data_in_year(sensor_id: int, year: int) -> bool:
    query_result = connection.execute('''
                                         SELECT sensor_id
                                         FROM sensor_data
                                         WHERE sensor_id = ?
                                           AND CAST(strftime('%Y', date) AS INT) = ?
                                         ''', (sensor_id, year)).fetchall()

    return len(query_result) > 0

def load_sensor_data(sensor_id: int, from_year: int, to_year: int) -> list[AnalyzedSensorData]:
    query_result = connection.execute('''
                                         SELECT AVG(temperature),
                                                MAX(temperature),
                                                MIN(temperature),
                                                (MAX(temperature) - MIN(temperature)),
                                                DATE(date)
                                         FROM sensor_data
                                         WHERE sensor_id = ?
                                           AND CAST(strftime('%Y', date) AS INT) BETWEEN ? AND ?
                                         GROUP BY DATE(date)
                                         ORDER BY DATE(date)
                                         ''', (sensor_id, from_year, to_year)).fetchall()

    result_data: list[AnalyzedSensorData] = []

    for row in query_result:
        sensor_date: datetime.datetime = datetime.datetime.strptime(str(row[4]), '%Y-%m-%d')
        average_temperature: float = float(row[0])
        max_temperature: float = float(row[1])
        min_temperature: float = float(row[2])
        temperature_diff: float = float(row[3])
        result_data.append(AnalyzedSensorData(sensor_id, sensor_date, average_temperature, max_temperature, min_temperature, temperature_diff))
    return result_data

create_table()

# sensor_id
# location
# lat
# lon
# timestamp
# temperature