from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import traverse
from zope.interface import classProvides
from zope.interface import implements
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class SetCreatorSection(object):
    """Section that sets the creator for the object if creator is given.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context

    def __iter__(self):
        for item in self.previous:
            path = item.get('_path')
            if not path:
                yield item
                continue

            obj = traverse(self.context, path, None)
            if obj is None:
                log.warning("Cannot set creator for {}. "
                            "Object doesn't exist".format(path))
                yield item
                continue

            self.set_creator(obj, item)

            yield item

    def set_creator(self, obj, item):
        creator = item.get('_creator')

        if creator:
            obj.setCreators((creator,))
