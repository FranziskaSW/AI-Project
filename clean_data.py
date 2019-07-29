import pandas as pd
import os
from datetime import datetime, timedelta
import math
import csv
import holidays
import json
import pickle
cwd = os.getcwd()
us_holidays = holidays.UnitedStates()

from os import listdir
from os.path import isfile, join

def load_data(path = cwd+'/data/tripdata'):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    files.sort()
    data = pd.read_csv(path+'/'+files[0])

    for file in files[1:]:
        data_month = pd.read_csv(path+'/'+file)
        print(file, data.shape, data_month.shape)
        data = data.append(data_month, ignore_index = True)

    data['starttime'] = pd.to_datetime(data['Start date'], format='%Y-%m-%d %H:%M:%S')
    data['endtime'] = pd.to_datetime(data['End date'], format='%Y-%m-%d %H:%M:%S')

    return data


def get_stations(path = cwd + '/data/Capital_Bike_Share_Locations.csv', grid_size=30):
    stations = pd.read_csv(path)
    stations['CAPACITY'] = stations.NUMBER_OF_BIKES + stations.NUMBER_OF_EMPTY_DOCKS
    stations = stations[['TERMINAL_NUMBER', 'LATITUDE', 'LONGITUDE', 'CAPACITY']]
    stations.columns = ['id', 'latitude', 'longitude', 'capacity']

    # clusters
    offset_lat = (stations.latitude.max() - stations.latitude.min()) / grid_size
    offset_lon = (stations.longitude.max() - stations.longitude.min()) / grid_size
    stations['lat'] = stations.latitude.apply(lambda x: math.floor(x / offset_lat) * offset_lat)
    stations['lon'] = stations.longitude.apply(lambda x: math.floor(x / offset_lon) * offset_lon)

    new_stat = stations.groupby(['lat', 'lon']).count().reset_index()
    new_stat.id = range(0, new_stat.shape[0])
    new_stat = new_stat[['id', 'lat', 'lon']]

    stations_rough = stations.merge(new_stat, how='left',
                                    left_on=['lat', 'lon'],
                                    right_on=['lat', 'lon'])
    cluster_size = stations_rough.groupby(by='id_y').count().reset_index()[['id_y', 'id_x']]
    cluster_size.rename(columns={'id_y': 'cluster_id', 'id_x': 'cluster_size'}, inplace=True)

    return stations, stations_rough, cluster_size

def load_weatherdata(path=cwd + '/data/weatherdata.json'):
    with open(path) as json_file:
        weather = json.load(json_file)
    weather_df = pd.DataFrame(weather['observations'])
    weather_df['datetime'] = pd.to_datetime(weather_df['time_gmt'], format='%Y-%m-%d %H:%M:%S')
    return weather_df

def clean_weatherdata(weatherdata):
    phrases = weatherdata.phrase.value_counts()
    phrases = phrases.reset_index()

    phrases['wind'] = phrases['index'].apply(lambda x: int('Windy' in x))

    winter = ['Wintry', 'Snow', 'Freezing', 'Sleet']
    thunder = ['T-', 'Thunder', 'Squalls']
    extreme = ['Heavy', 'T-Storm', 'Thunder', 'Squalls']

    phrases['wintry'] = phrases['index'].apply(lambda x: int(any([term in x for term in winter])))
    phrases['thunderstorm'] = phrases['index'].apply(lambda x: int(any([term in x for term in thunder])))
    phrases['extreme_weather'] = phrases['index'].apply(lambda x: int(any([term in x for term in extreme])))

    light_rain = ['Light Rain', 'Light Drizzle', 'Light Freezing Rain']  # give 1
    heavy_rain = ['Rain', 'Heavy Rain']  # give 2, do this first because otherwise would overwrite 'Light Rain'
    foggy = ['Fog', 'Mist', 'Haze']
    clear_sky = ['Fair', 'Partly Cloudy']  # give 1

    phrases['foggy'] = phrases['index'].apply(lambda x: int(any([term in x for term in foggy])))

    phrases['rain'] = 0
    phrases['rain'][phrases['index'].apply(lambda x: any([term in x for term in heavy_rain]))] = 2
    phrases['rain'][phrases['index'].apply(lambda x: any([term in x for term in light_rain]))] = 1

    phrases['clear_sky'] = phrases['index'].apply(lambda x: int(any([term in x for term in clear_sky])))
    phrases = phrases.drop(columns='phrase')
    phrases.rename(columns={'index': 'phrase'}, inplace=True)

    return phrases

def yearly_data_starttime(data, year):
    print(data.shape, year)
    start = datetime(year=year, month=1, day=1, hour=0, minute=0)
    end = datetime(year=year+1, month=1, day=1, hour=0, minute=0)
    data_year = data[(data.starttime >= start) & (data.starttime < end)]
    print(data_year.shape, data.shape, year)
    return data_year

def tripdata_to_station_pickups(startdate, enddate, data, stations_rough, cluster_size, weatherdata, weather_phrases):
    data = data[['starttime', 'Start station number']]
    data_s = stations_rough.merge(data, how='right', left_on='id_x', right_on='Start station number')[
        ['starttime', 'id_y', 'lat', 'lon']]

    # within next 90 minutes will have x pickups at station
    time = startdate
    delta = timedelta(minutes=90)

    pickups_combined = pd.read_pickle(cwd+'/data/pickups_empty.pkl')
    step = 1

    first_year = startdate.year
    current_year = first_year
    data_year = yearly_data_starttime(data_s, first_year)

    while time < enddate:
        print(time, time + delta, current_year)

        if time.year == current_year + 1:

            # final save of data from last year
            pickups.to_pickle(cwd + '/data/pickups_' + str(current_year) + '.pkl')
            pickups.to_csv(cwd + '/data/pickups_' + str(current_year) + '.csv')

            # get data for next year
            current_year += 1
            print('--------------- next year, use data for ', current_year)
            data_year = yearly_data_starttime(data_s, current_year)

            pickups = pd.read_pickle(cwd + '/data/pickups_empty.pkl')

        pickups = data_year[(data_year.starttime >= time) &
                         (data_year.starttime < time + delta)].groupby(['id_y', 'lat', 'lon']).count()  # Member type

        # multi-index to single index and rename columns
        pickups = pickups.reset_index()
        pickups.rename(columns={'id_y': 'cluster_id', 'starttime': 'pickups'}, inplace=True)

        # cluster size
        pickups = pickups.merge(cluster_size, how='left')

        pickups['holiday'] = int(time in us_holidays)
        pickups['weekday'] = time.weekday()
        pickups['time'] = time.time()
        pickups['month'] = time.month

        # weather data
        try:
            current_weather = weatherdata[(weatherdata.datetime >= time - timedelta(minutes=30)) &
                                         (weatherdata.datetime < time + timedelta(minutes=29))].iloc[0]
        except IndexError:
            print('use last available weather information')
            pass

        pickups['phrase'] = current_weather['phrase']
        pickups['temperature'] = current_weather['temp']
        pickups['humidity'] = current_weather['humidity']
        pickups = pickups.merge(weather_phrases, how='left')
        pickups = pickups.drop(columns='phrase')

        pickups_combined = pd.concat([pickups_combined, pickups], ignore_index=True)

        # pickups_empty = pd.DataFrame(columns=list(pickups.columns))
        # pickups_empty.to_pickle(cwd+'/data/pickups_empty.pkl')

        if not (step%50):
            print(step, ' save csv and pkl')
            pickups.to_pickle(cwd + '/data/pickups_' + str(current_year) + '.pkl')
            pickups.to_csv(cwd + '/data/pickups_' + str(current_year) + '.csv')

        time += delta
        step += 1
    # final save of data
    pickups.to_pickle(cwd + '/data/pickups_' + str(current_year) + '.pkl')
    pickups.to_csv(cwd + '/data/pickups_' + str(current_year) + '.csv')

    return pickups_combined


def yearly_data_endtime(data, year):
    print(data.shape, year)
    start = datetime(year=year, month=1, day=1, hour=0, minute=0)
    end = datetime(year=year+1, month=1, day=1, hour=0, minute=0)
    data_year = data[(data.endtime >= start) & (data.endtime < end)]
    print(data_year.shape, data.shape, year)
    return data_year

def tripdata_to_station_returns(startdate, enddate, data, stations_rough, cluster_size, weatherdata, weather_phrases):
    data = data[['endtime', 'End station number']]
    data_s = stations_rough.merge(data, how='right', left_on='id_x', right_on='End station number')[
        ['endtime', 'id_y', 'lat', 'lon']]

    # within next 90 minutes will have x returns at station
    time = startdate
    delta = timedelta(minutes=90)

    returns_combined = pd.read_pickle(cwd+'/data/returns_empty.pkl')
    step = 1

    first_year = startdate.year
    current_year = first_year
    data_year = yearly_data_endtime(data_s, first_year)

    while time < enddate:
        print(time, time + delta, current_year)

        if time.year == current_year + 1:
            # final save of data from last year
            returns.to_pickle(cwd+'/data/returns_'+str(current_year)+'.pkl')
            returns.to_csv(cwd+'/data/returns_'+str(current_year)+'.csv')

            # get data for next year
            current_year += 1
            print('--------------- next year, use data for ', current_year)
            data_year = yearly_data_endtime(data_s, current_year)

            returns = pd.read_pickle(cwd+'/data/returns_empty.pkl')

        returns = data_year[(data_year.endtime >= time) &
                         (data_year.endtime < time + delta)].groupby(['id_y', 'lat', 'lon']).count()  # Member type

        # multi-index to single index and rename columns
        returns = returns.reset_index()
        returns.rename(columns={'id_y': 'cluster_id', 'endtime': 'returns'}, inplace=True)

        # cluster size
        returns = returns.merge(cluster_size, how='left')

        returns['holiday'] = int(time in us_holidays)
        returns['weekday'] = time.weekday()
        returns['time'] = time.time()
        returns['month'] = time.month

        # weather data
        try:
            current_weather = weatherdata[(weatherdata.datetime >= time - timedelta(minutes=30)) &
                                         (weatherdata.datetime < time + timedelta(minutes=29))].iloc[0]
        except IndexError:
            print('use last available weather information')
            pass

        returns['phrase'] = current_weather['phrase']
        returns['temperature'] = current_weather['temp']
        returns['humidity'] = current_weather['humidity']
        returns = returns.merge(weather_phrases, how='left')
        returns = returns.drop(columns='phrase')

        returns_combined = pd.concat([returns_combined, returns], ignore_index=True)

        # returns_empty = pd.DataFrame(columns=list(returns.columns))
        # returns_empty.to_pickle(cwd+'/data/returns_empty.pkl')

        if not (step%50):
            print(step, ' save csv and pkl')
            returns.to_pickle(cwd+'/data/returns_'+str(current_year)+'.pkl')
            returns.to_csv(cwd+'/data/returns_'+str(current_year)+'.csv')

        time += delta
        step += 1

    # final save of data
    returns.to_pickle(cwd + '/data/returns_' + str(current_year) + '.pkl')
    returns.to_csv(cwd + '/data/returns_' + str(current_year) + '.csv')

    return returns_combined


if __name__ == "__main__":

    startdate = datetime(year=2015, month=1, day=1, hour=0, minute=0)
    enddate = datetime(year=2019, month=7, day=1, hour=0, minute=0)

    print('--------tripdata------')
    # data = load_data()
    # data.to_pickle(cwd+'/data/tripdata_2015-now.pkl')
    data = pd.read_pickle(cwd+'/data/tripdata_2015-now.pkl')

    print('-------stations--------')
    stations, stations_rough, cluster_size = get_stations()

    print('----------weather--------')
    weatherdata = load_weatherdata()
    weather_phrases = clean_weatherdata(weatherdata)

    print('---------tripdata-to-stations---------')
    pickups = tripdata_to_station_pickups(startdate, enddate, data, stations_rough, cluster_size, weatherdata, weather_phrases)

    print('---------tripdata-to-returns---------')
    pickups = tripdata_to_station_returns(startdate, enddate, data, stations_rough, cluster_size, weatherdata, weather_phrases)
