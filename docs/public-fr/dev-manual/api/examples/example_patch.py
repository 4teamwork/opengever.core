dossier_data = {
    "title": "Neuer Titel"
}

url = 'https://example.org/ordnungssystem/fuehrung/dossier-42'
response = session.patch(url, json=dossier_data)
