from opengever.api.move import Move
from opengever.base.response import AutoResponseChangesTracker
from opengever.base.response import IResponseContainer
from opengever.base.response import MOVE_RESPONSE_TYPE
from opengever.base.response import Response
from opengever.workspace.interfaces import IToDo
from opengever.workspace.interfaces import IToDoList
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


class ToDoMove(Move):
    """Moves existing content objects.

    Required to track todo moves and add a move-response.
    """

    def reply(self):
        results = super(ToDoMove, self).reply()

        if not results:
            return

        for result in results:
            moved_object = self.get_object(result.get('target'))
            if not IToDo.providedBy(moved_object):
                continue

            container_before = self.get_object(
                self._parent_by_url(result.get('source')))
            container_after = self.context
            response = Response(MOVE_RESPONSE_TYPE)
            response.add_change(
                '',
                self._get_changes_text(container_before),
                self._get_changes_text(container_after))
            IResponseContainer(moved_object).add(response)

        return results

    def _parent_by_url(self, url):
        return '/'.join(url.strip('/').split('/')[:-1])

    def _is_todo_list(self, obj):
        return IToDoList.providedBy(obj)

    def _get_changes_text(self, obj):
        return obj.title if IToDoList.providedBy(obj) else ''
