import requests

url = 'http://93.19.210.30/support.py'
myobj = {'somekey': 'somevalue'}

x = requests.post(url, data = myobj)