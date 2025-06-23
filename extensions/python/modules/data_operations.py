import sqlite3
import datetime
# SQLite database connection
# check_same_thread=False allows the connection to be used across different threads
connection = sqlite3.connect("sensor_data.db", check_same_thread=False)

class SensorData:
    def __init__(self, sensor_id: int, location: int, lat: float, lon: float, timestamp: datetime.datetime, temperature: float | None, humidity: float | None):
        self.sensor_id = sensor_id
        self.location = location
        self.lat = lat
        self.lon = lon
        self.timestamp = timestamp
        self.temperature = temperature
        self.humidity = humidity

class AnalyzedSensorData:
    def __init__(self, sensor_id: int, timestamp: datetime.datetime, avg: float, max: float, min: float, diff: float):
        self.sensor_id = sensor_id
        self.timestamp = timestamp
        self.avg = avg
        self.max = max
        self.min = min
        self.diff = diff
    
    def __str__(self):
        return f"(sensor_id={self.sensor_id}, timestamp={self.timestamp}, avg={self.avg}, max={self.max}, min={self.min}, diff={self.diff})"
        
class AnalyzedSensor:
    def __init__(self, sensor_id: int, temperature_data: list[AnalyzedSensorData], humidity_data: list[AnalyzedSensorData]):
        self.sensor_id = sensor_id
        self.temperature_data = temperature_data
        self.humidity_data = humidity_data

def create_table():
    """Create the users table if it doesn't exist."""
    connection.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
                        sensor_id INTEGER,
                        location INTEGER NOT NULL,
                        lat DOUBLE,
                        lon DOUBLE,
                        timestamp DATETIME,
                        temperature DOUBLE,
                        humidity DOUBLE,
                        PRIMARY KEY(sensor_id, timestamp)
                        )''')
    connection.commit()

def insert_data(data: list[SensorData]):
    print(f"Inserting {len(data)} rows into sensor_data table.")
    rows = []
    for d in data:
        row = (d.sensor_id, d.location, d.lat, d.lon, d.timestamp, d.temperature, d.humidity)
        rows.append(row)
    
    connection.executemany("INSERT OR IGNORE INTO sensor_data (sensor_id, location, lat, lon, timestamp, temperature, humidity) VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
    connection.commit()

def exists_sensor_data_in_year(sensor_id: int, year: int) -> bool:
    query_result = connection.execute('''
                                         SELECT sensor_id
                                         FROM sensor_data
                                         WHERE sensor_id = ?
                                           AND CAST(strftime('%Y', timestamp) AS INT) = ?
                                         ''', (sensor_id, year)).fetchall()

    return len(query_result) > 0

def load_sensor_data(sensor_id: int, from_year: int, to_year: int) -> AnalyzedSensor:
    query_result = connection.execute('''
                                         SELECT AVG(temperature),
                                                MAX(temperature),
                                                MIN(temperature),
                                                (MAX(temperature) - MIN(temperature)),
                                                DATE(timestamp),
                                                AVG(humidity),
                                                MAX(humidity),
                                                MIN(humidity),
                                                (MAX(humidity) - MIN(humidity))
                                         FROM sensor_data
                                         WHERE sensor_id = ?
                                           AND temperature IS NOT NULL
                                           AND humidity IS NOT NULL                                         
                                           AND CAST(strftime('%Y', timestamp) AS INT) BETWEEN ? AND ?
                                         GROUP BY DATE(timestamp)
                                         ORDER BY DATE(timestamp)
                                         ''', (sensor_id, from_year, to_year)).fetchall()
    
    temperature_result_data: list[AnalyzedSensorData] = []
    humidity_result_data: list[AnalyzedSensorData] = []

    for row in query_result:
        sensor_date: datetime.datetime = datetime.datetime.strptime(str(row[4]), '%Y-%m-%d')
        average_temperature: float = float(row[0])
        max_temperature: float = float(row[1])
        min_temperature: float = float(row[2])
        temperature_diff: float = float(row[3])
        average_humidity: float = float(row[5])
        max_humidity: float = float(row[6])
        min_humidity: float = float(row[7])
        humidity_diff: float = float(row[8])
        humidity_result_data.append(AnalyzedSensorData(sensor_id, sensor_date, average_humidity, max_humidity, min_humidity, humidity_diff))
        temperature_result_data.append(AnalyzedSensorData(sensor_id, sensor_date, average_temperature, max_temperature, min_temperature, temperature_diff))
    return AnalyzedSensor(sensor_id=sensor_id, temperature_data=temperature_result_data, humidity_data=humidity_result_data)

create_table()