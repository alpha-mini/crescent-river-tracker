import requests
from datetime import datetime
import csv
import os
import re

def get_detailed_location():
    # Target: Crescent River (IMO: 9800726)
    url = "https://www.vesselfinder.com/vessels/details/9800726"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text
        
        # Extracting data using Regex from the page source
        def extract(pattern):
            match = re.search(pattern, html)
            return match.group(1) if match else "N/A"

        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "lat": extract(r'lastPosLat":([\d\.-]+)'),
            "lon": extract(r'lastPosLon":([\d\.-]+)'),
            "course": extract(r'course":([\d\.]+)'),
            "speed": extract(r'speed":([\d\.]+)'),
            "status": extract(r'statusText":"([^"]+)"'),
            "destination": extract(r'destination":"([^"]+)"'),
            "eta": extract(r'eta":"([^"]+)"'),
            "draught": extract(r'draught":([\d\.]+)')
        }
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def save_data(data):
    file_name = "location_log.csv"
    # Fieldnames must match the keys in the data dictionary
    fields = ["timestamp", "lat", "lon", "course", "speed", "status", "destination", "eta", "draught"]
    file_exists = os.path.isfile(file_name)
    
    with open(file_name, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

if __name__ == "__main__":
    loc_data = get_detailed_location()
    if loc_data:
        save_data(loc_data)
        print(f"Logged: {loc_data
