from copy import deepcopy
from opengever.base.security import elevated_privileges
from opengever.base.transition import ITransitionExtender
from opengever.dossier.activate import DossierActivator
from opengever.dossier.base import DOSSIER_STATE_RESOLVED
from opengever.dossier.deactivate import DossierDeactivator
from opengever.dossier.reactivate import Reactivator
from opengever.dossier.resolve import AlreadyBeingResolved
from opengever.dossier.resolve import InvalidDates
from opengever.dossier.resolve import LockingResolveManager
from opengever.dossier.resolve import MSG_ALREADY_BEING_RESOLVED
from opengever.dossier.resolve import PreconditionsViolated
from opengever.sign.sign import Signer
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.serializer.converters import IJsonCompatible
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.restapi.services.workflow.transition import WorkflowTransition
from plone.restapi.types.utils import get_fieldset_infos
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_jsonschema_properties
from plone.restapi.types.utils import iter_fields
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
import plone.protect.interfaces


class GEVERWorkflowTransition(WorkflowTransition):

    def check_action_available(self):
        actions = self.wftool.listActionInfos(object=self.context)
        action_ids = [action['id'] for action in actions
                      if action['category'] == 'workflow']

        if self.transition in action_ids:
            return None

        return dict(type='Bad Request',
                    message="Invalid transition '{0}'.\n"
                            "Valid transitions are:\n"
                            "{1}".format(self.transition,
                                         '\n'.join(sorted(action_ids))))

    def reply(self):
        """Access review history with elevated privileges, if necessary.

        There is an issue in the `WorkflowTransition` service when the user
        performs a transition into a state where his access is revoked. The
        service will raise a `WorkflowException` when attempting to access
        `review_history` while rendering the response. This will prevent the
        transition from being executed.

        We work around this issue when we read the history with elevated privileges.
        """

        error = self.check_action_available()
        if error:
            self.request.response.setStatus(400)
            return dict(error=error)

        if self.transition is None:
            self.request.response.setStatus(400)
            return dict(error=dict(type="BadRequest", message="Missing transition"))

        data = json_body(self.request)

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        comment = data.get("comment", "")
        include_children = data.get("include_children", False)
        publication_dates = {}
        if "effective" in data:
            publication_dates["effective"] = data["effective"]
        if "expires" in data:
            publication_dates["expires"] = data["expires"]

        try:
            response = self.recurse_transition(
                [self.context], comment, publication_dates, include_children
            )

        except WorkflowException as e:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="WorkflowException",
                    message=translate(str(e), context=self.request),
                )
            )

        with elevated_privileges():
            history = self.wftool.getInfoFor(self.context, "review_history")
        action = history[-1]

        action["title"] = self.context.translate(
            self.wftool.getTitleForStateOnType(
                action["review_state"], self.context.portal_type
            ).decode("utf8")
        )
        if response and isinstance(response, dict):
            action['transition_response'] = response
        return json_compatible(action)

    def recurse_transition(self, objs, comment, publication_dates,
                           include_children=False):

        data = self.request_data()

        for obj in objs:
            if publication_dates:
                deserializer = queryMultiAdapter((obj, self.request),
                                                 IDeserializeFromJson)
                deserializer(data=publication_dates)

            adapter = queryMultiAdapter(
                (obj, getRequest()), ITransitionExtender, name=self.transition)
            if adapter:
                errors = adapter.validate_schema(deepcopy(data))
                if errors:
                    raise BadRequest(errors)

            response = self.wftool.doActionFor(obj, self.transition, comment=comment,
                                               transition_params=data)
            if include_children and IFolderish.providedBy(obj):
                self.recurse_transition(
                    obj.objectValues(), comment, publication_dates,
                    include_children)

            return response

    def request_data(self):
        return json_body(self.request)


class GEVERDossierWorkflowTransition(GEVERWorkflowTransition):
    """This endpoint handles workflow transitions for dossiers.

    Some transitions (like resolving dossiers) are always performed
    recursively, and require lots of custom logic.

    Others, which don't require custom handling, are delegated to the default
    implementation.

    Finally, some transitions are not allowed through the RESTAPI, notably
    everything that is linked to archiving, as these should only be managed
    through the offer process.
    """

    CUSTOMIZED_TRANSITIONS = ['dossier-transition-resolve',
                              'dossier-transition-activate',
                              'dossier-transition-deactivate',
                              'dossier-transition-reactivate']

    def reply(self):
        error = self.check_action_available()
        if error:
            self.request.response.setStatus(400)
            return dict(error=error)

        if self.transition not in self.CUSTOMIZED_TRANSITIONS:
            # Delegate to default implementation
            return super(GEVERDossierWorkflowTransition, self).reply()

        try:
            self.perform_custom_transition()

        except WorkflowException as e:
            self.request.response.setStatus(400)
            msg = self.translate(str(e))
            return dict(error=dict(
                type='WorkflowException',
                message=msg))

        except PreconditionsViolated as e:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='PreconditionsViolated',
                errors=map(self.translate, e.errors),
                message=self.translate(str(e))))

        except InvalidDates as e:
            # From the REST API's point of view, invalid dates are just
            # another violated precondition.
            self.request.response.setStatus(400)
            msg = self.translate(str(e))
            errors = ['The dossier %s has a invalid end_date' % title
                      for title in e.invalid_dossier_titles]
            return dict(error=dict(
                type='PreconditionsViolated',
                errors=errors,
                message=msg))

        except AlreadyBeingResolved as e:
            self.request.response.setStatus(400)
            msg = self.translate(MSG_ALREADY_BEING_RESOLVED)
            return dict(error=dict(
                type='AlreadyBeingResolved',
                message=msg))

        except BadRequest as e:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='Bad Request',
                message=str(e)))

        action = self.get_latest_wf_action()
        return json_compatible(action)

    def perform_custom_transition(self):
        data = json_body(self.request)
        self.disable_csrf_protection()

        # validate transition schemas
        adapter = queryMultiAdapter(
            (self.context, getRequest()), ITransitionExtender,
            name=self.transition)

        if adapter:
            errors = adapter.validate_schema(deepcopy(data))
            if errors:
                raise BadRequest(errors)

        # TODO: Do we need to handle comments and publication dates
        # etc. for dossier transitions like the original implementation does?
        # For now we also extract these, but we don't do anything with them
        # in the case of resolving a dossier.
        comment = data.get('comment', '')
        publication_dates = self.parse_publication_dates(data)
        args = [self.context], comment, publication_dates

        if adapter and data:
            data = adapter.deserialize(data)

        if self.transition == 'dossier-transition-resolve':
            self.resolve_dossier(*args, **data)
        elif self.transition == 'dossier-transition-activate':
            self.activate_dossier(*args)
        elif self.transition == 'dossier-transition-deactivate':
            self.deactivate_dossier(*args)
        elif self.transition == 'dossier-transition-reactivate':
            self.reactivate_dossier(*args)
        else:
            raise BadRequest('Unexpected custom transition %r' % self.transition)

    def activate_dossier(self, objs, comment, publication_dates,
                         include_children=False):
        # Reject explicit attempts to non-recursively activate a dossier
        if not json_body(self.request).get('include_children', True):
            raise BadRequest('Activating dossier must always be recursive')

        activator = DossierActivator(self.context)
        activator.activate()

    def resolve_dossier(self, objs, comment, publication_dates,
                        include_children=False, **kwargs):
        if self.is_already_resolved():
            # XXX: This should be prevented by the workflow tool.
            # For some reason it currently doesn't.
            raise BadRequest('Dossier has already been resolved.')

        # Reject explicit attempts to non-recursively resolve a dossier
        if not json_body(self.request).get('include_children', True):
            raise BadRequest('Resolving dossier must always be recursive')

        resolve_manager = LockingResolveManager(self.context)
        resolve_manager.resolve(**kwargs)

    def deactivate_dossier(self, objs, comment, publication_dates,
                           include_children=False):
        # Reject explicit attempts to non-recursively deactivate a dossier
        if not json_body(self.request).get('include_children', True):
            raise BadRequest('Deactivating dossier must always be recursive')

        deactivator = DossierDeactivator(self.context)
        deactivator.deactivate()

    def reactivate_dossier(self, objs, comment, publication_dates,
                           include_children=False):
        # Reject explicit attempts to non-recursively reactivate a dossier
        if not json_body(self.request).get('include_children', True):
            raise BadRequest('Reactivating dossier must always be recursive')

        reactivator = Reactivator(self.context)
        reactivator.reactivate()

    def get_latest_wf_action(self):
        history = self.wftool.getInfoFor(self.context, "review_history")
        action = history[-1]
        action['title'] = self.context.translate(
            self.wftool.getTitleForStateOnType(
                action['review_state'],
                self.context.portal_type).decode('utf8'))

        return action

    def translate(self, msg):
        return translate(msg, context=self.request)

    def is_already_resolved(self):
        wfstate = api.content.get_state(obj=self.context)
        return wfstate == DOSSIER_STATE_RESOLVED

    def disable_csrf_protection(self):
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

    def parse_publication_dates(self, data):
        publication_dates = {}
        if 'effective' in data:
            publication_dates['effective'] = data['effective']
        if 'expires' in data:
            publication_dates['expires'] = data['expires']
        # Archetypes has different field names
        if 'effectiveDate' in data:
            publication_dates['effectiveDate'] = data['effectiveDate']
        if 'expirationDate' in data:
            publication_dates['expirationDate'] = data['expirationDate']
        return publication_dates


class GEVERTaskWorkflowTransition(GEVERWorkflowTransition):
    """This endpoint handles workflow transitions for tasks.
    """
    def request_data(self):
        """Extract responsible_client when a combined value is used (client,
        responsible separated by a colon) in the responsible field
        """
        data = super(GEVERTaskWorkflowTransition, self).request_data()
        task_deserializer = queryMultiAdapter((self.context, self.request),
                                              IDeserializeFromJson)

        task_deserializer.update_reponsible_field_data(data)

        return data


class WorkspaceWorkflowTransition(GEVERWorkflowTransition):
    """Handles workflow transitions for workspaces.

       Checks if workspace doesn't contain any checked out documents before
       deactivation.
    """

    def reply(self):
        if self.transition == 'opengever_workspace--TRANSITION--deactivate--active_inactive':
            catalog = getToolByName(self.context, 'portal_catalog')
            checked_out_docs = catalog.unrestrictedSearchResults(
                portal_type="opengever.document.document",
                path={
                    'query': '/'.join(self.context.getPhysicalPath()),
                    'depth': -1,
                },
                checked_out={'not': ''}
            )
            if len(checked_out_docs) > 0:
                self.request.response.setStatus(400)
                return dict(error=dict(
                    type='PreconditionsViolated',
                    message='Workspace contains checked out documents.'))

        return super(WorkspaceWorkflowTransition, self).reply()


class GEVERDocumentWorkflowTransition(GEVERWorkflowTransition):
    """This endpoint handles workflow transitions for documents
    """

    SIGNING_TRANSITIONS = ['document-transition-draft-signing',
                           'document-transition-final-signing']

    def reply(self):
        response = super(GEVERDocumentWorkflowTransition, self).reply()
        if self.transition in self.SIGNING_TRANSITIONS:
            pending_signing_job = Signer(
                self.context).serialize_pending_signing_job()
            response['redirect_url'] = pending_signing_job.get('redirect_url')
            response['invite_url'] = pending_signing_job.get('invite_url')
        return response


@implementer(IPublishTraverse)
class WorkflowSchemaGET(Service):

    def __init__(self, context, request):
        super(WorkflowSchemaGET, self).__init__(context, request)
        self.transition = None

    def publishTraverse(self, request, name):
        if self.transition is None:
            self.transition = name
        else:
            raise NotFound(self, name, request)
        return self

    def reply(self):
        if self.transition is None:
            self.request.response.setStatus(400)
            return dict(error=dict(type="BadRequest", message="Missing transition"))

        transition_extender = queryMultiAdapter(
            (self.context, self.request),
            ITransitionExtender, name=self.transition)

        if not transition_extender or not transition_extender.schemas:
            return {
                "properties": {},
                "required": [],
                "fieldsets": [],
            }

        schema = transition_extender.schemas[0]
        additional_schemata = []
        if len(transition_extender.schemas) > 1:
            additional_schemata = transition_extender.schemas[1]

        fieldsets = get_fieldsets(
            self.context, self.request, schema,
            additional_schemata=additional_schemata)
        properties = get_jsonschema_properties(
            self.context, self.request, fieldsets)

        required = []
        for field in iter_fields(fieldsets):
            name = field.field.getName()
            # Determine required fields
            if field.field.required:
                required.append(name)

        return {
            "properties": IJsonCompatible(properties),
            "required": required,
            "fieldsets": get_fieldset_infos(fieldsets),
        }
