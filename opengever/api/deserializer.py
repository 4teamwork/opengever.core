from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.response import IChangesTracker
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from zope.component import adapter
from zope.component import getMultiAdapter


@adapter(IDexterityContent, IOpengeverBaseLayer)
class GeverDeserializeToJson(DeserializeFromJson):
    def __call__(self, validate_all=False, data=None, create=False):
        if create:
            return super(GeverDeserializeToJson, self).__call__(validate_all,
                                                                data, create)
        if data is None:
            data = json_body(self.request)

        changes_tracker = getMultiAdapter((self.context, self.request),
                                          IChangesTracker)

        with changes_tracker.track_changes(data.keys()):
            result = super(GeverDeserializeToJson, self).__call__(validate_all,
                                                                  data, create)

        return result
