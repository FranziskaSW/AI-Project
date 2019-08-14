folder_path = '/home/franzi/briedenCloud/share/data/'

#################### add the new columns
method = 'test'

file_path = folder_path + method + '_data_1.csv'
file_path_old = folder_path + method + '_data_1_old.csv'

data = pd.read_csv(file_path)
data.to_csv(file_path_old, index=False)

threshold_temps = [30, 40, 50, 60, 70, 80]
data['temp'] = 0
for i in range(0,len(threshold_temps)):
    data['temp'][data.temperature >= threshold_temps[i]] = threshold_temps[i]

threshold_hums = [40, 50, 60, 70, 80, 90]
data['hum'] = 0
for i in range(0,len(threshold_hums)):
    data['hum'][data.humidity >= threshold_hums[i]] = threshold_hums[i]

data = data[['Unnamed: 0', 'Unnamed: 0.1', 'cluster_id', 'L1', 'L2', 'weekday',
           'holiday', 'time', 'month', 'clear_sky', 'extreme_weather', 'foggy',
           'humidity', 'thunderstorm', 'rain', 'temperature', 'wind', 'wintry',
             'temp', 'hum', 'demand']]

data.to_csv(file_path, index=False)

###################  split into subsets

parts = 1000
for i in [1]:
    data = pd.read_csv(folder_path + 'test_data_' + str(i) + '.csv')
    slicer = np.linspace(0, data.shape[0], parts+1)
    print(slicer)
    for ind in range(0, parts):
        first = int(slicer[ind])
        last = int(slicer[ind+1] - 1)
        # print(str(ind).zfill(4), first, last)
        subset = data.iloc[first:last]
        subset.to_csv(folder_path + 'subsets/test_data_' + str(i) + '_' + str(ind).zfill(4) + '.csv')