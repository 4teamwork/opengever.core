import requests

session = requests.Session()
session.auth = ('username', 'password')
session.headers.update({'Accept': 'application/json'})
