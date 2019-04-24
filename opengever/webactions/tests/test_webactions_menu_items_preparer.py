from opengever.webactions.interfaces import IWebActionsMenuItemsPreparer
from opengever.webactions.tests.test_webactions_renderer import TestWebActionRendererTitleButtons
from urllib import urlencode


class TestWebActionRendererActionsMenu(TestWebActionRendererTitleButtons):

    display = 'actions-menu'
    icon = ''
    adapter_interface = IWebActionsMenuItemsPreparer

    params = {'context': 'http://nohost/plone/ordnungssystem/fuhrung'
              '/vertrage-und-vereinbarungen/dossier-1',
              'orgunit': 'fa'}

    expected_data = [
        {'action': 'http://example.org/endpoint?{}'.format(urlencode(params)),
         'description': '',
         'extra': {'class': 'actionicon-object_webaction',
                   'id': 'webaction-0',
                   'separator': 'actionSeparator'},
         'icon': None,
         'selected': False,
         'submenu': None,
         'title': u'Action 1'},
        {'action': 'http://example.org/endpoint?{}'.format(urlencode(params)),
         'description': '',
         'extra': {'class': 'actionicon-object_webaction',
                   'id': 'webaction-1',
                   'separator': None},
         'icon': None,
         'selected': False,
         'submenu': None,
         'title': u'Action 2'}]


class TestWebActionRendererUserMenu(TestWebActionRendererActionsMenu):

    display = 'user-menu'

    params = {'context': 'http://nohost/plone/ordnungssystem/fuhrung'
              '/vertrage-und-vereinbarungen/dossier-1',
              'orgunit': 'fa'}

    expected_data = [
        {'title': u'Action 1',
         'category': 'webactions',
         'url': 'http://example.org/endpoint?{}'.format(urlencode(params)),
         'separator': None,
         'id': 'webaction-0'},
        {'title': u'Action 2',
         'category': 'webactions',
         'url': 'http://example.org/endpoint?{}'.format(urlencode(params)),
         'separator': 'actionSeparator',
         'id': 'webaction-1'}]


class TestWebActionRendererAddMenu(TestWebActionRendererActionsMenu):

    display = 'add-menu'
    icon = 'fa-helicopter'

    params = {'context': 'http://nohost/plone/ordnungssystem/fuhrung'
              '/vertrage-und-vereinbarungen/dossier-1',
              'orgunit': 'fa'}

    expected_data = [
        {'action': 'http://example.org/endpoint?{}'.format(urlencode(params)),
         'description': '',
         'extra': {'class': 'webaction fa-helicopter',
                   'id': 'webaction-0',
                   'separator': 'actionSeparator'},
         'icon': None,
         'selected': False,
         'submenu': None,
         'title': u'Action 1'},
        {'action': 'http://example.org/endpoint?{}'.format(urlencode(params)),
         'description': '',
         'extra': {'class': 'webaction fa-helicopter',
                   'id': 'webaction-1',
                   'separator': None},
         'icon': None,
         'selected': False,
         'submenu': None,
         'title': u'Action 2'}]
