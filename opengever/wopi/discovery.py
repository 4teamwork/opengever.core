from collections import defaultdict
from logging import getLogger
from opengever.wopi.interfaces import IWOPISettings
from plone import api
from xml.etree import cElementTree as ET
import requests
import time


logger = getLogger('opengever.wopi')


WOPI_DISCOVERY_REFRESH_INTERVAL = 60 * 60 * 24
_WOPI_DISCOVERY = {
    'timestamp': 0,
    'url': None,
    'proof-key': None,
    'actions': {},
    'editable-extensions': {},
}


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


def run_discovery(net_zone='external-https', url=None):
    if url is None:
        url = api.portal.get_registry_record(
            name='discovery_url', interface=IWOPISettings)

    now = int(time.time())
    if (
        url == _WOPI_DISCOVERY['url']
        and _WOPI_DISCOVERY['timestamp'] + WOPI_DISCOVERY_REFRESH_INTERVAL > now
    ):
        return

    try:
        resp = requests.get(url)
        tree = ET.XML(resp.text)
        wopi_discovery = etree_to_dict(tree)['wopi-discovery']
    except Exception:
        logger.exception('WOPI discovery from %r failed:', url)
        return

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
    _WOPI_DISCOVERY['actions'] = actions

    extensions = set()
    for extension, actions in actions.items():
        if 'edit' in actions:
            extensions.add(extension)
    _WOPI_DISCOVERY['editable-extensions'] = extensions

    _WOPI_DISCOVERY['proof-key'] = wopi_discovery['proof-key']
    _WOPI_DISCOVERY['url'] = url
    _WOPI_DISCOVERY['timestamp'] = now


def actions_by_extension():
    run_discovery()
    return _WOPI_DISCOVERY['actions']


def editable_extensions():
    try:
        run_discovery()
        return _WOPI_DISCOVERY['editable-extensions']
    except KeyError:
        return set([])


def proof_key():
    run_discovery()
    return _WOPI_DISCOVERY['proof-key']
