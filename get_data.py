import urllib.request
import json
import zipfile, io
with open('bucket.json') as f:
    data = json.load(f)

base_url = 'https://s3.amazonaws.com/capitalbikeshare-data/'
for item in data['Contents']:
    response = urllib.request.urlopen('{}{}'.format(base_url, item['Key']))
    data = response.read()
    z = zipfile.ZipFile(io.BytesIO(data))
    z.extractall()
