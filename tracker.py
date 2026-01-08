import requests
from datetime import datetime
import csv
import os
import re

def get_location():
    # Target: Crescent River (IMO: 9800726)
    url = "https://www.vesselfinder.com/vessels/details/9800726"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text
        
        # Regex to find Lat/Lon in the page source
        lat = re.search(r'lastPosLat":([\d\.-]+)', html).group(1)
        lon = re.search(r'lastPosLon":([\d\.-]+)', html).group(1)
        course = re.search(r'course":([\d\.]+)', html).group(1)
        
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "lat": lat,
            "lon": lon,
            "course": course
        }
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def save_data(data):
    file_name = "location_log.csv"
    file_exists = os.path.isfile(file_name)
    
    with open(file_name, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "lat", "lon", "course"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

if __name__ == "__main__":
    loc_data = get_location()
    if loc_data:
        save_data(loc_data)
        print(f"Success: {loc_data}")
