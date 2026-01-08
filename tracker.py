import requests
from datetime import datetime
import csv
import os
import re

def get_vessel_data():
    # Target: Crescent River (IMO: 9800726)
    url = "https://www.vesselfinder.com/vessels/details/9800726"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text
        
        # Helper to grab data from the page source
        def extract(pattern):
            match = re.search(pattern, html)
            return match.group(1) if match else "Unknown"

        return {
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
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_to_csv(data):
    file_name = "location_log.csv"
    fields = ["timestamp", "lat", "lon", "course", "speed", "status", "destination", "eta", "draught"]
    file_exists = os.path.isfile(file_name)
    
    with open(file_name, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

if __name__ == "__main__":
    data = get_vessel_data()
    if data:
        save_to_csv(data)
        print(f"Logged {data['destination']} with ETA {data['eta']}")
