from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from opengever.base.behaviors.changed import IChanged
from plone.dexterity.utils import datify
from zope.interface import classProvides
from zope.interface import implements
import logging
import tzlocal


logger = logging.getLogger('opengever.setup.sections.set_dates')


class SetDatesSection(object):
    """Sets modification and creation date"""
    implements(ISection)
    classProvides(ISectionBlueprint)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')

    def set_changed(self, obj, changed):
        changed = datify(changed).asdatetime()
        if changed.tzinfo is None:
            changed = tzlocal.get_localzone().localize(changed)
        IChanged(obj).changed = changed
        obj.reindexObject(idxs=['changed'])

    def __iter__(self):
        for item in self.previous:
            obj = self._get_obj(item)
            changed = item.get("changed")
            if changed:
                self.set_changed(obj, changed)

            yield item

    def _get_obj(self, item):
        path = item.get(self.pathkey(*item.keys())[0], None)
        # Skip the Plone site object itself
        if not path:
            return None

        obj = self.context.unrestrictedTraverse(
            path.encode('utf-8').lstrip('/'), None)

        return obj
