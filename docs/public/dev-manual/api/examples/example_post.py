dossier_data = {
    "@type": "opengever.dossier.businesscasedossier",
    "title": "Ein neues Dossier via API",
    "responsible": "peter.muster",
    "custody_period": 30,
    "archival_value": "unchecked",
    "retention_period": 10,
}

url = 'https://example.org/ordnungssystem/fuehrung/'
response = session.post(url, json=dossier_data)
new_dossier_url = response.headers['Location']
