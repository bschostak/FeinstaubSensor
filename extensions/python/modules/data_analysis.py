import datetime
from modules.data_operations import SensorData

def calculate_average_temperature(data: list[SensorData]) -> float:
    total_temperature = 0.0

    for row in data:
        total_temperature += row.temperature

    return total_temperature / len(data)


def calculate_max_temperature(data: list[SensorData]) -> float:
    highest_temperature = data[0].temperature

    for row in data:
        if row.temperature > highest_temperature:
            highest_temperature = row.temperature

    return highest_temperature


def calculate_min_temperature(data: list[SensorData]) -> float:
    lowest_temperature = data[0].temperature

    for row in data:
        if row.temperature < lowest_temperature:
            lowest_temperature = row.temperature

    return lowest_temperature


def calculate_temperature_difference(data: list[SensorData]) -> float:
    temperature_difference = calculate_max_temperature(data) - calculate_min_temperature(data)

    return temperature_difference

# Humidity

def calculate_average_humidity(data: list[SensorData]) -> float:
    total_humidity = 0.0

    for row in data:
        total_humidity += row.humidity

    return total_humidity / len(data)


def calculate_max_humidity(data: list[SensorData]) -> float:
    highest_humidity = data[0].humidity

    for row in data:
        if row.humidity > highest_humidity:
            highest_humidity = row.humidity

    return highest_humidity


def calculate_min_humidity(data: list[SensorData]) -> float:
    lowest_humidity = data[0].humidity

    for row in data:
        if row.humidity < lowest_humidity:
            lowest_humidity = row.humidity

    return lowest_humidity


def calculate_humidity_difference(data: list[SensorData]) -> float:
    humidity_difference = calculate_max_humidity(data) - calculate_min_humidity(data)

    return humidity_difference
