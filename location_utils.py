import requests
import urllib
import json
import pandas as pd
from app import app

def get_address(lat, lon):
    params = urllib.parse.urlencode({
        "latlng": f"{lat},{lon}",
        "key": app.config['GOOGLE_API_KEY']
        })
    request_url = f"{app.config['GOOGLE_API_BASE_URL']}{app.config['GOOGLE_GEOCODE_API_PATH']}?{params}"
    response = requests.get(url=request_url).json()
    formated_address = response['results'][1]['formatted_address']
    return formated_address

def add_location_to_df(df):
    locations = []
    for index, row in df.iterrows():
        addr = get_address(row['lat'], row['lon'])
        locations.append(addr)
    df['location'] = locations
    return df


