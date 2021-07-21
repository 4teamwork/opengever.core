from opengever.api.remote_task_base import RemoteTaskBaseService
from opengever.base.exceptions import MalformedOguid
from opengever.base.oguid import Oguid
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.task.browser.accept.utils import accept_forwarding_with_successor
from plone.protect.interfaces import IDisableCSRFProtection
from zExceptions import BadRequest
from zope.interface import alsoProvides
from opengever.base.exceptions import InvalidOguidIntIdPart


class AcceptRemoteForwardingPost(RemoteTaskBaseService):
    required_params = ('forwarding_oguid', )
    optional_params = ('dossier_oguid', 'text', )

    def is_assigned_to_current_admin_unit(self, forwarding):
        org_unit = forwarding.get_assigned_org_unit()
        return org_unit.admin_unit == get_current_admin_unit()

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        # Extract and validate parameters, assign defaults
        params = self.extract_params()

        raw_forwarding_oguid = params['forwarding_oguid']
        raw_dossier_oguid = params.get('dossier_oguid')
        response_text = params.get('text', u'')

        # Validate that Oguid is well-formed and refers to a forwarding that is
        # actually remote. Turn any Python exceptions into proper
        # 400 Bad Request responses with details in the JSON body.
        try:
            forwarding_oguid = Oguid.parse(raw_forwarding_oguid)

        except MalformedOguid as exc:
            raise BadRequest(self.format_exception(exc))

        forwarding = Task.query.by_oguid(raw_forwarding_oguid)
        if not forwarding:
            raise BadRequest('No object found for forwarding_oguid "{}".'.format(raw_forwarding_oguid))

        if raw_dossier_oguid:
            try:
                dossier = Oguid.parse(raw_dossier_oguid).resolve_object()
            except MalformedOguid as exc:
                raise BadRequest(self.format_exception(exc))
            except InvalidOguidIntIdPart:
                dossier = None
            # dossier could be None due to exception or as returned by resolve
            if not dossier:
                raise BadRequest('No object found for dossier_oguid "{}".'.format(raw_dossier_oguid))
        else:
            dossier = None

        if not self.is_assigned_to_current_admin_unit(forwarding):
            raise BadRequest('Forwarding must be assigned to the current admin unit.')

        if not self.is_remote(forwarding_oguid):
            raise BadRequest(
                'Forwarding must be on remote admin unit. '
                'Oguid %s refers to a local task, however.' % raw_forwarding_oguid)

        successor = accept_forwarding_with_successor(
            self.context, raw_forwarding_oguid, response_text, dossier)

        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", successor.absolute_url())

        serialized_successor = self.serialize(successor)
        return serialized_successor
