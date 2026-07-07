from opengever.maintenance.debughelpers import setup_app
from opengever.maintenance.debughelpers import setup_plone
import csv

app = setup_app()
site = setup_plone(app)

base_url = 'http://foo/%s/' % site.id
public_base_url = 'https://%s.onegovgever.ch/' % site.id

uids = {}
items = site.portal_catalog.unrestrictedSearchResults()
for item in items:
    url = item.getURL().replace(base_url, public_base_url)
    uids[url] = item.UID

with open('/tmp/uids.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    for url, uid in uids.items():
        csvwriter.writerow([url, uid])
