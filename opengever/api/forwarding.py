from opengever.api.task import deserialize_responsible
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.uuid.interfaces import IUUID
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.schema.interfaces import ValidationError


class AssignToDossier(Service):
    """Assigns a forwarding to a dossier.
    """

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        # Extract and validate parameters
        task_payload, target, comment = self.extract_params()

        transition_params = {'text': comment, 'dossier': IUUID(target)}

        if task_payload:
            responsible = deserialize_responsible(task_payload.get('responsible'))
            if responsible:
                task_payload.update(responsible)

            if task_payload.get("text") is None:
                task_payload["text"] = ""

            transition_params['task'] = task_payload
        try:
            task = api.portal.get_tool('portal_workflow').doActionFor(
                self.context,
                'forwarding-transition-assign-to-dossier',
                text=comment,
                transition_params=transition_params)
        except ValidationError as exc:
            raise BadRequest(
                "The task schema is invalid. Field: {}, Message: {}".format(
                    str(exc), exc.doc()))

        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", task.absolute_url())

        return self.serialize(task)

    def extract_params(self):
        json_data = json_body(self.request)

        task_payload = json_data.get("task")
        target_uid = json_data.get("target_uid")
        comment = json_data.get("comment", u'')

        if not target_uid:
            raise BadRequest('Required parameter "target_uid" is missing in body')

        target = api.content.get(UID=target_uid)

        if not target:
            raise BadRequest('target_uid: "{}" does not exist'.format(target_uid))

        if not IDossierMarker.providedBy(target):
            raise BadRequest('target_uid: "{}" is not a dossier'.format(target_uid))

        return task_payload, target, comment

    def serialize(self, obj):
        serializer = queryMultiAdapter(
            (obj, self.request), ISerializeToJson)
        serialized_obj = serializer()
        serialized_obj["@id"] = obj.absolute_url()
        return serialized_obj
