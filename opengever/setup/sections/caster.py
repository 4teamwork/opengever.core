from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Expression
from zope.interface import classProvides, implements
import logging


class EmptystringCasterSection(object):
    """set all Empty Strings to None """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])
        self.fields = Expression(
            options['fields'], transmogrifier, name, options)

    def __iter__(self):
        for item in self.previous:
            for k, v in item.items():
                if v == '' and k in self.fields(item):
                    item[k] = None

            yield item
