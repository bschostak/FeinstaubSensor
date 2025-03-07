from app import analyze_sensor, draw_graph

start_year = int(input("Geben Sie den Startjahr ein (default=2024): ").strip() or "2024")
end_year = int(input("Geben Sie den Endjahr ein (default=2024): ").strip() or "2024")
sensor_type = "dht22"
sensor_id = input("Geben Sie die Sensor-ID ein (default=63047): ").strip() or "63047"

# [0] = Datum, [1] = Durchschnittstemperatur, [2] = Höchsttemperatur, [3] = Tiefstemperatur, [4] = Temperaturdifferenz
analysed_data = analyze_sensor(start_year, end_year, sensor_type, sensor_id)

draw_graph(analysed_data)
