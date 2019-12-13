url = 'https://example.org/ordnungssystem/fuehrung/?items.fl=filesize,filename'
response = session.get(url)
items = response.json()['items']
