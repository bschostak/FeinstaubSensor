import datetime

def calculate_average_temperature(data: list[tuple[float, datetime.datetime]]) -> float:
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
