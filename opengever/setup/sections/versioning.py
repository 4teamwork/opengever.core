from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from opengever.document.checkout import handlers
from opengever.document.checkout.handlers import create_initial_version
from zope.interface import classProvides
from zope.interface import implements


class DisabledInitialVersion(object):
    """Disable automatical creation of initial versions for documents."""

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous

    def __iter__(self):
        handlers.DISABLE_INITIAL_VERSION = True
        try:
            for item in self.previous:
                yield item
        finally:
            handlers.DISABLE_INITIAL_VERSION = False


class ManualInitialVersion(object):
    """Manually create initial version for documents."""

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context

        self.typekey = defaultMatcher(options, 'type-key', name, 'type',
                                      ('portal_type', 'Type'))
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')

    def __iter__(self):
        for item in self.previous:
            keys = item.keys()
            pathkey = self.pathkey(*keys)[0]
            typekey = self.typekey(*keys)[0]

            assert item[typekey] == 'opengever.document.document', \
                'unexpected type, only documents are supported'

            path = item[pathkey]
            obj = self.context.unrestrictedTraverse(path.lstrip('/'), None)
            if obj is None:
                yield item
                continue

            create_initial_version(obj)
            yield item
