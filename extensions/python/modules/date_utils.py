import datetime

def get_date_range_year(year: int) -> list[datetime.datetime]:
    """
    Generate a list of datetime objects for all dates in a given year.
    
    If the specified year is the current year, the last date will be the current date.
    Otherwise, the last date will be December 31st of the specified year.
    
    Args:
        year (int): The year for which to generate the date range.
    
    Returns:
        list[datetime.datetime]: A list of datetime objects representing all dates in the year.
    """

    first_day = datetime.datetime(year=year, month=1, day=1)
    last_day = datetime.datetime(year=year, month=12, day=31)

    if first_day.year == datetime.datetime.now().year:
        last_day = datetime.datetime.now()
    return get_date_range(first_day, last_day)

def get_date_range(from_time: datetime.datetime, to_time: datetime.datetime) -> list[datetime.datetime]:
    """
    Generate a list of datetime objects between two given datetime points.
    
    Args:
        from_time (datetime.datetime): The starting datetime.
        to_time (datetime.datetime): The ending datetime.
    
    Returns:
        list[datetime.datetime]: A list of datetime objects representing each day between from_time and to_time, inclusive.
    """
    
    date_list: list[datetime.datetime] = []
    date_difference = to_time - from_time
    days_difference = date_difference.days
    total_days = int(days_difference)

    for i in range(total_days + 1):
        """
        Addiert die Anzahl der Tage zum Startdatum und fügt das Ergebnis der Liste hinzu.
        Beim addieren wird bereits beachtet, dass auch der Monat und das Jahr korrekt angepasst werden.
        """
        date_list.append(from_time + datetime.timedelta(days=i))

    return date_list