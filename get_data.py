import urllib.request
import json
import zipfile, io
with open('bucket.json') as f:
    data = json.load(f)

base_url = 'https://s3.amazonaws.com/capitalbikeshare-data/'
for item in data['Contents']:
    print('start ', item)
    response = urllib.request.urlopen('{}{}'.format(base_url, item['Key']))
    data = response.read()
    print('finished to read')
    z = zipfile.ZipFile(io.BytesIO(data))
    print('save a zip')
    z.extractall()
    print('finished to extract')
