from opengever.base.transition import ITransitionExtender
from opengever.dossier.base import DOSSIER_STATE_RESOLVED
from opengever.dossier.resolve import AlreadyBeingResolved
from opengever.dossier.resolve import InvalidDates
from opengever.dossier.resolve import LockingResolveManager
from opengever.dossier.resolve import MSG_ALREADY_BEING_RESOLVED
from opengever.dossier.resolve import PreconditionsViolated
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services.workflow.transition import WorkflowTransition
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.WorkflowCore import WorkflowException
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import alsoProvides
import plone.protect.interfaces


class GEVERWorkflowTransition(WorkflowTransition):

    def recurse_transition(self, objs, comment, publication_dates,
                           include_children=False):

        data = json_body(self.request)

        for obj in objs:
            if publication_dates:
                deserializer = queryMultiAdapter((obj, self.request),
                                                 IDeserializeFromJson)
                deserializer(data=publication_dates)

            adapter = queryMultiAdapter(
                (obj, getRequest()), ITransitionExtender, name=self.transition)
            if adapter:
                errors = adapter.validate_schema(data)
                if errors:
                    raise BadRequest(errors)

            self.wftool.doActionFor(obj, self.transition,
                                    comment=comment, transition_params=data)
            if include_children and IFolderish.providedBy(obj):
                self.recurse_transition(
                    obj.objectValues(), comment, publication_dates,
                    include_children)


class GEVERDossierWorkflowTransition(GEVERWorkflowTransition):
    """This endpoint handles workflow transitions for dossiers.

    Some transitions (like resolving dossiers) are always performed
    recursively, and require lots of custom logic.

    Others, which don't require custom handling, are delegated to the default
    implementation.
    """

    CUSTOMIZED_TRANSITIONS = ['dossier-transition-resolve']

    def reply(self):
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
                errors=e.errors,
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

        # TODO: Do we need to handle comments and publication dates
        # etc. for dossier transitions like the original implementation does?
        # For now we also extract these, but we don't do anything with them
        # in the case of resolving a dossier.
        comment = data.get('comment', '')
        include_children = data.get('include_children', False)
        publication_dates = self.parse_publication_dates(data)

        args = [self.context], comment, publication_dates, include_children

        if self.transition == 'dossier-transition-resolve':
            self.resolve_dossier(*args)
        else:
            raise BadRequest('Unexpected custom transition %r' % self.transition)

    def resolve_dossier(self, objs, comment, publication_dates,
                        include_children=False):
        if self.is_already_resolved():
            # XXX: This should be prevented by the workflow tool.
            # For some reason it currently doesn't.
            raise BadRequest('Dossier has already been resolved.')

        # Reject explicit attempts to non-recursively resolve a dossier
        if not json_body(self.request).get('include_children', True):
            raise BadRequest('Resolving dossier must always be recursive')

        resolve_manager = LockingResolveManager(self.context)

        if resolve_manager.is_archive_form_needed():
            raise BadRequest(
                "Can't resolve dossiers via REST API if filing number "
                "feature is activated")

        resolve_manager.resolve()

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
