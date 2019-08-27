from opengever.base.response import AutoResponseChangesTracker
from opengever.workspace.interfaces import IToDo
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from zope.component import adapter
from zope.interface import Interface


@adapter(IToDo, Interface)
class DeserializeToDoFromJson(DeserializeFromJson):
    def __call__(self, validate_all=False, data=None, create=False):
        if create:
            return super(DeserializeToDoFromJson, self).__call__(validate_all,
                                                               data, create)
        if data is None:
            data = json_body(self.request)

        changes_tracker = AutoResponseChangesTracker(self.context, self.request)
        with changes_tracker.track_changes(data.keys()):
            result = super(DeserializeToDoFromJson, self).__call__(validate_all,
                                                                 data, create)

        return result
