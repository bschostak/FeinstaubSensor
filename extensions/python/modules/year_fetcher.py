import requests
from bs4 import BeautifulSoup
import json
import re


def get_available_years():
    """
    Fetches available years from the sensor.community archive website.
    Returns a list of years as strings, extracting year parts from dates.
    """
    try:
        url = "https://archive.sensor.community"
        response = requests.get(url)
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        years = set()
        
        for link in soup.find_all("a"):
            text = link.get_text(strip=True)
            
            if text.endswith('/'):
                text = text[:-1]
            
            if text.isdigit() and len(text) == 4:
                years.add(text)
            
            # Date format (e.g., "2024-01-01")
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', text):
                year = text.split('-')[0]
                years.add(year)
        
        years_list = sorted(list(years))
        return years_list
        
    except Exception as e:
        print(f"Error fetching available years: {str(e)}")
        return []


def fetch_available_years(parameter=None):
    years = get_available_years()
    return json.dumps(years)


# For testing purposes - will only run when script is executed directly
if __name__ == "__main__":
    years = get_available_years()
    print("Available years:", years)
