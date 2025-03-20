import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import json


#TODO: Make it all into function 
# Step 1: Make a request to the website
url = "https://archive.sensor.community"  # Replace with the website URL
response = requests.get(url)

# Step 2: Parse the HTML content
soup = BeautifulSoup(response.content, "html.parser")

# Step 3: Extract data (example: extracting all links and text)
data = []
for link in soup.find_all("a"):
    data.append({
        "text": link.get_text(strip=True),
        "url": link.get("href")
    })

# Step 4: Convert data to JSON
json_data = json.dumps(data, indent=4)

# Step 5: Save to a JSON file
with open("website_data.json", "w") as json_file:
    json_file.write(json_data)

print("Data saved to website_data.json")

#TODO: Review this and make it work, or delete it
def get_available_years():
    try:
        response = requests.get("https://archive.sensor.community/")

        print("WOLOLO: " + response.json())
        
        if response.status_code == 200:
            years = [folder for folder in response.json() if folder.isdigit()]
            years.sort()
            return years
        else:
            return []
    except Exception as e:
        print(f"Error fetching available years: {str(e)}")
        return []

# test: str = get_available_years()
# print(test)