from opengever.workflow.bulk_transition_information import WorkflowBulkTransitionInformation
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.services import Service
from zope.interface import alsoProvides


class BuklTransitionInformation(Service):
    """This endpoint returns information about the workflow assigned to the
    given context

    We need this endpoint in the UI to list possible workflow transitions for
    a list of objects of the same type.
    """
    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        transition_data = WorkflowBulkTransitionInformation().extract_transitions(self.context)

        return {
            '@id': '/'.join((self.context.absolute_url(), '@workflow-bulk-transition')),
            'transitions': transition_data.serialize()
        }
