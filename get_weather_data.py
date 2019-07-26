import requests
import pandas as pd
import json
import time


sm = pd.date_range(start='09/1/2010', end='7/26/2019', freq='MS')
em = pd.date_range(start='09/1/2010', end='7/26/2019', freq='M')

weather = {
    'observations': []
}

for i, s in enumerate(sm):
    try:
        time.sleep(2)
        print(str(s.date()).replace('-', ''), str(em[i]))
        r = requests.get('https://api.weather.com/v1/geocode/38.85/-77.04/observations/historical.json?apiKey=6532d6454b8aa370768e63d6ba5a832e&startDate={}&endDate={}&units=e'.format(
            str(s.date()).replace('-', ''), str(em[i].date()).replace('-', '')
        ))
        r = r.json()

        for item in r['observations']:
            weather['observations'].append({
                'time_gmt': str(pd.to_datetime(item['valid_time_gmt'], unit='s')),
                'phrase': item['wx_phrase'],
                'temp': item['temp'],
                'humidity': item['rh']

            })
    except:
        with open('weatherdata.json', 'w') as fp:
            json.dump(weather, fp)

with open('weatherdata.json', 'w') as fp:
    json.dump(weather, fp)

