from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from plone import api
from zope.interface import classProvides
from zope.interface import implements


class RepositoryFirst(object):
    """Change content order, move repository root to first position.

    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous

    def __iter__(self):
        for item in self.previous:
            if item.get('_type') == 'opengever.repository.repositoryroot':
                portal = api.portal.get()
                path = item['_path']
                repo_root = portal.restrictedTraverse(path.strip('/'))
                repo_parent = aq_parent(aq_inner(repo_root))
                repo_parent.moveObject(repo_root.getId(), 0)

            yield item
