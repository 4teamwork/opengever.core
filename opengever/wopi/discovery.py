from collections import defaultdict
from opengever.wopi.interfaces import IWOPISettings
from plone import api
from xml.etree import cElementTree as ET
import requests


_ACTIONS = {}


def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def actions_by_extension(net_zone='external-https'):
    global _ACTIONS

    url = api.portal.get_registry_record(
        name='discovery_url', interface=IWOPISettings)
    if url in _ACTIONS:
        return _ACTIONS[url]

    resp = requests.get(url)
    tree = ET.XML(resp.text)
    wopi_discovery = etree_to_dict(tree)['wopi-discovery']

    actions = {}
    net_zones = wopi_discovery['net-zone']
    if not isinstance(net_zones, list):
        net_zones = [net_zones]
    for zone in net_zones:
        if zone['@name'] == net_zone:
            for app in zone['app']:
                app_name = app['@name']
                favicon_url = app['@favIconUrl']
                for action in app['action']:
                    action_name = action['@name']
                    ext = action.get('@ext')
                    if not ext:
                        continue
                    urlsrc = action['@urlsrc']
                    if ext not in actions:
                        actions[ext] = {}
                    actions[ext][action_name] = {
                        'app': app_name,
                        'urlsrc': urlsrc,
                        'favicon_url': favicon_url,
                    }
    _ACTIONS[url] = actions
    return _ACTIONS[url]
