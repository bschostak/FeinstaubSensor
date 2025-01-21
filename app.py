def generate_urls(start_year, end_year, sensor_type, sensor_id):
    base_url = "http://archive.sensor.community"
    urls = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            for day in range(1, 32):
                url = f"{base_url}/{year}-{month:02d}-{day:02d}/{year}-{month:02d}-{day:02d}_{sensor_type}_sensor_{sensor_id}.csv"
                urls.append(url)
    
    return urls
    # https://archive.sensor.community/2023-01-02/2023-01-02_bme280_sensor_113.csv

start_year = int(input("Geben Sie den Startjahr ein: "))
end_year = int(input("Geben Sie den Endjahr ein: "))
sensor_type = input("Geben Sie den Sensor-Typ ein: ")
sensor_id = input("Geben Sie die Sensor-ID ein: ")

urls = generate_urls(start_year, end_year, sensor_type, sensor_id)
for url in urls:
    print(url)
