from ftw.builder import builder_registry
from opengever.webactions.interfaces import IWebActionsStorage
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.globalrequest import getRequest


class WebActionBuilder(object):
    """Creates a webaction that is persisted in the storage.
    """

    def __init__(self, session):
        self.session = session
        self.arguments = {
            'title': u'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'display': 'actions-menu',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
        }
        self.owner = None

    def having(self, **kwargs):
        self.arguments.update(kwargs)
        return self

    def titled(self, title):
        self.arguments['title'] = title
        return self

    def owned_by(self, owner):
        self.owner = owner
        return self

    def create(self, **kwargs):
        action = {}
        action.update(self.arguments)
        storage = getMultiAdapter((getSite(), getRequest()), IWebActionsStorage)
        action_id = storage.add(action)

        if self.owner is not None:
            storage._actions[action_id]['owner'] = self.owner

        return storage.get(action_id)

builder_registry.register('webaction', WebActionBuilder)
