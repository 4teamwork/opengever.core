from Acquisition import aq_parent
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.meeting.committee import Committee
from plone import api
from zope.interface import classProvides
from zope.interface import implements


SUPPORTED_MODELS = {'opengever.meeting.committee': Committee}


class ModelConstructor(object):
    """Create sql-model for content types that rely on them."""

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous

    def __iter__(self):
        for item in self.previous:
            self.create_model(item)
            yield item

    def create_model(self, item):
        item_type = item.get('_type')
        if not item_type in SUPPORTED_MODELS:
            return

        data = self.get_data(item)
        obj_class = SUPPORTED_MODELS.get(item_type)
        model_data = obj_class.partition_data(data)[1]

        portal = api.portal.get()
        path = item['_path']
        obj = portal.restrictedTraverse(path.strip('/'))
        parent = aq_parent(obj)

        obj.create_model(model_data, parent)

    def get_data(self, item):
        """return all keys for an item - drop the controllers."""

        return dict(each for each in item.items() if not each[0].startswith('_'))
