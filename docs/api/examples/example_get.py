url = 'https://example.org/ordnungssystem/fuehrung/'
response = session.get(url)
title = response.json()['title']
