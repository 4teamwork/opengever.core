from config_entities import AdminUnit
from config_entities import Cluster
from os.path import expanduser
from os.path import join as pjoin


SESSION_COOKIES_DIR = expanduser('~/.opengever/rewrite_rule_smoketests')
SESSION_COOKIES_FILE = pjoin(SESSION_COOKIES_DIR, 'session_cookies.json')


CLUSTERS_TO_TEST = [
    Cluster(
        'https://dev.onegovgever.ch',
        admin_units=[
            AdminUnit('fd'),
            AdminUnit('rk'),
        ],
        new_portal=False,
        gever_ui_is_default=True,
    ),

    Cluster(
        'https://dev.teamraum.ch',
        admin_units=[
            AdminUnit('fd'),
            AdminUnit('tr', is_dedicated_teamraum=True),
        ],
        new_portal=True,
        gever_ui_is_default=True,
    ),

    Cluster(
        'https://test.onegovgever.ch',
        admin_units=[
            AdminUnit('fd'),
            AdminUnit('rk'),
        ],
        new_portal=False,
        gever_ui_is_default=False,
    ),

    Cluster(
        'https://lab.onegovgever.ch',
        admin_units=[
            AdminUnit('fd'),
        ],
        new_portal=False,
        gever_ui_is_default=False,
    ),

    Cluster(
        'https://demo.teamraum.ch',
        admin_units=[
            AdminUnit('tr', is_dedicated_teamraum=True),
        ],
        new_portal=True,
        gever_ui_is_default=True,
    ),

]
