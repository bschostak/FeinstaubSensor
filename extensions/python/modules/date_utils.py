import datetime

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

    for i in range(total_days + 1):
        """
        Addiert die Anzahl der Tage zum Startdatum und fügt das Ergebnis der Liste hinzu.
        Beim addieren wird bereits beachtet, dass auch der Monat und das Jahr korrekt angepasst werden.
        """
        date_list.append(from_time + datetime.timedelta(days=i))

    return date_list