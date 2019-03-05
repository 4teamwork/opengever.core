from opengever.webactions.interfaces import IWebActionsMenuItemsPreparer
from opengever.webactions.tests.test_webactions_renderer import TestWebActionRendererTitleButtons


class TestWebActionRendererActionsMenu(TestWebActionRendererTitleButtons):

    display = 'actions-menu'
    icon = ''
    adapter_interface = IWebActionsMenuItemsPreparer

    expected_data = [
        {'action': 'http://example.org/endpoint',
         'description': '',
         'extra': {'class': 'actionicon-object_webaction',
                   'id': 'webaction-0',
                   'separator': 'actionSeparator'},
         'icon': None,
         'selected': False,
         'submenu': None,
         'title': u'Action 1'},
        {'action': 'http://example.org/endpoint',
         'description': '',
         'extra': {'class': 'actionicon-object_webaction',
                   'id': 'webaction-1',
                   'separator': None},
         'icon': None,
         'selected': False,
         'submenu': None,
         'title': u'Action 2'}]
