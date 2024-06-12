from opengever.api import _
from opengever.api.actors import serialize_actor_id_to_json_summary
from opengever.api.not_reported_exceptions import BadRequest as NotReportedBadRequest
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.base.security import elevated_privileges
from opengever.ogds.base.actor import Actor
from opengever.workspace.activities import WorkspaceWatcherManager
from opengever.workspace.interfaces import IWorkspaceFolder
from opengever.workspace.participation import PARTICIPATION_ROLES
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Forbidden
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class ParticipationTraverseService(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ParticipationTraverseService, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@participations as parameters
        self.params.append(name)
        return self

    def prepare_response_item(self, participant):
        role = PARTICIPATION_ROLES.get(participant.get('roles')[0])
        managing_context = self.context.get_context_with_local_roles()

        # We manually serialize the actors'representer and extract the desired
        # properties to get a homogeneous json result for different actor types
        # XXX deprecated
        # We should use the participant_actor instead which will also avoid
        # having to resolve the actor in this endpoint.
        actor = Actor.lookup(participant.get('token'))
        represented_obj = actor.represents()
        if represented_obj:
            serialized_actor = getMultiAdapter(
                (represented_obj, self.request),
                interface=ISerializeToJsonSummary)()
        else:
            serialized_actor = {}

        return {
            '@id': '{}/@participations/{}'.format(managing_context.absolute_url(), actor.identifier),
            '@type': 'virtual.participations.{}'.format(actor.actor_type),
            'is_editable': managing_context == self.context and participant.get('can_manage'),
            'role': {
                'token': role.id,
                'title': role.translated_title(self.request),
            },
            'participant_actor': serialize_actor_id_to_json_summary(
                participant.get('token')),
            'participant': {
                '@id': serialized_actor.get('@id'),
                '@type': serialized_actor.get('@type'),
                'id': actor.identifier,
                'title': actor.get_label(),
                'email': serialized_actor.get('email'),
                'is_local': serialized_actor.get('is_local'),
                'active': serialized_actor.get('active'),
            }
        }

    def participants(self, context):
        manager = ManageParticipants(context, self.request)
        return manager.get_participants()

    def find_participant(self, token, context):
        for item in self.participants(context):
            if item.get('token') == token:
                return item

    def is_actor_allowed_to_participate(self, actor):
        """Validates the actor token if it' a avalid actor.
        """
        if actor.actor_type not in ['user', 'group']:
            raise BadRequest(
                _(u'disallowed_participant',
                  default=u'The actor ${actorid} is not allowed',
                  mapping={'actorid': actor.identifier}))

        if self.find_participant(
            actor.identifier, self.context.get_context_with_local_roles()
        ):
            raise BadRequest(
                _(u'duplicate_participant',
                  default='The participant ${actorid} already exists',
                  mapping={'actorid': actor.identifier}))

        if IWorkspaceFolder.providedBy(self.context):
            if not self.context.has_blocked_local_role_inheritance():
                raise Forbidden(
                    "The participations are not managed in this context. "
                    "Please block the role inheritance before adding "
                    "new participants.")

            if not self.find_participant(
                actor.identifier, self.context.get_parent_with_local_roles()
            ):
                raise BadRequest('The participant is not allowed')


class ParticipationsGet(ParticipationTraverseService):
    """API Endpoint which returns a list of all participants for the current
    workspace.

    GET workspace/@participations HTTP/1.1
    """
    def reply(self):
        if not self.context.access_members_allowed():
            raise Forbidden

        token = self.read_params()
        if token:
            return self.prepare_response_item(self.find_participant(
                token, self.context.get_context_with_local_roles()))
        else:
            result = {}
            result['items'] = self.get_response_items()
            return result

    def get_response_items(self):
        return [self.prepare_response_item(item) for item in
                self.participants(self.context.get_context_with_local_roles())]

    def read_params(self):
        if len(self.params) == 1:
            return self.params[0]
        return None


class ParticipationsDelete(ParticipationTraverseService):

    def reply(self):
        token = self.read_params()
        self.recursive_delete_participation(self.context, token, 0)
        self.request.response.setStatus(204)
        return None

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest(
                "Must supply token ID as URL path parameters.")

        return self.params[0]

    def recursive_delete_participation(self, obj, token, depth):
        """It is possible that a subfolder has blocked the role inheritance
        and has assigned it's own roles for a specific user. We have to be sure
        that this user will be deleted in the whole tree and not only in the
        current context.
        """
        if obj.get_context_with_local_roles() == obj and self.find_participant(token, obj):
            manager = ManageParticipants(obj, self.request)
            try:
                manager._delete(Actor.lookup(token).actor_type, token)
            except Unauthorized:
                raise BadRequest(
                    _(u'msg_cannot_manage_member_in_subfolder',
                      default=u'The participant cannot be deleted because he has access to a'
                      u' subfolder on which you do not have admin rights.'))
            except NotReportedBadRequest as exc:
                if(depth > 0):
                    raise NotReportedBadRequest(
                        _(u'msg_one_in_subfolder_must_remain_admin',
                          default=u'The participant cannot be deleted because he is the only '
                          u'administrator in a subfolder. At least one participant must remain'
                          u' an administrator.'))
                raise exc

        with elevated_privileges():
            folders = obj.listFolderContents(contentFilter={'portal_type': 'opengever.workspace.folder'})
        for folder in folders:
            self.recursive_delete_participation(folder, token, depth + 1)


class ParticipationsPatch(ParticipationTraverseService):

    def reply(self):
        participant = self.read_params()
        data = json_body(self.request)

        role = data.get('role')
        if isinstance(role, dict):
            role = role.get("token")

        if not role:
            self.request.RESPONSE.setStatus(204)
            return None

        actor = Actor.lookup(participant)
        manager = ManageParticipants(self.context, self.request)
        manager._modify(participant, role, actor.actor_type)
        return None

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest(
                "Must supply token ID as URL path parameters.")

        return self.params[0]


class ParticipationsPost(ParticipationTraverseService):

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        participations, notify_user = self.validate_data(json_body(self.request))
        results = []
        container = self.context.get_context_with_local_roles()
        for token, role in participations:
            actor = Actor.lookup(token, name_as_fallback=True)
            self.validate_participation(actor, role)

            assignment = SharingRoleAssignment(actor.identifier, [role], self.context)
            RoleAssignmentManager(self.context).add_or_update_assignment(assignment)

            activity_manager = WorkspaceWatcherManager(self.context)
            activity_manager.new_participant_added(actor.identifier, notify_user)

            results.append(self.prepare_response_item(self.find_participant(
                actor.identifier, container)))

        self.request.response.setStatus(201)
        if getattr(self, "return_list", False):
            managing_context = self.context.get_context_with_local_roles()
            return {
                "@id": '{}/@participations'.format(managing_context.absolute_url()),
                "items": results}
        return results[0]

    def validate_data(self, data):
        if 'participants' in data and ('participant' in data or 'role' in data):
            raise BadRequest(
                _(u'one_of_participants_and_participant',
                  default=u"Cannot specify both 'participants' and "
                          u"'participant' or 'role'"))

        if 'participants' in data:
            self.return_list = True
            participations = [self.extract_participation(participation) for
                              participation in data.get("participants")]
        else:
            participations = [self.extract_participation(data)]
        notify_user = data.get('notify_user', False)

        return participations, notify_user

    def extract_participation(self, data):
        participant = data.get('participant')
        if isinstance(participant, dict):
            participant = participant.get("token")

        role = data.get('role')
        if isinstance(role, dict):
            role = role.get("token")

        if not participant:
            raise BadRequest(_(u'missing_participant',
                               default=u"Missing parameter 'participant'"))

        if not role:
            raise BadRequest(_(u'missing_role',
                               default=u"Missing parameter 'role'"))

        return participant, role

    def validate_participation(self, actor, role):
        self.is_actor_allowed_to_participate(actor)

        if role not in PARTICIPATION_ROLES:
            raise BadRequest(
                _(u'invalid_role',
                  default=u'Role ${role} is not available. '
                          u'Available roles are: ${allowed_roles}',
                  mapping={'role': role,
                           'allowed_roles': PARTICIPATION_ROLES.keys()}))
