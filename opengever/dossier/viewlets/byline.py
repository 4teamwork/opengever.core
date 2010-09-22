from zope.component import getUtility, getAdapter

from plone.app.layout.viewlets import content
from plone.memoize.instance import memoize

from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossier, IDossierMarker
from opengever.mail.behaviors import IMailInAddressMarker, IMailInAddress
from opengever.ogds.base.interfaces import IContactInformation


class Byline(content.DocumentBylineViewlet):
    update = content.DocumentBylineViewlet.update

    @memoize
    def workflow_state(self):
        state = self.context_state.workflow_state()
        workflows = self.context.portal_workflow.getWorkflowsFor(
            self.context.aq_explicit)
        if workflows:
            for w in workflows:
                if state in w.states:
                    return w.states[state].title or state


class BusinessCaseByline(Byline):
    """ Specific DocumentByLine, for the Businesscasedossier Type"""

    update = content.DocumentBylineViewlet.update

    def start(self):
        dossier = IDossier(self.context)
        return dossier.start

    def responsible(self):
        info = getUtility(IContactInformation)
        dossier = IDossier(self.context)
        return info.render_link(dossier.responsible)

    def end(self):
        dossier = IDossier(self.context)
        return dossier.end

    @memoize
    def sequence_number(self):
        seqNumb = getUtility(ISequenceNumber)
        return seqNumb.get_number(self.context)

    @memoize
    def reference_number(self):
        refNumb = getAdapter(self.context, IReferenceNumber)
        return refNumb.get_number()

    def get_filing_no(self):
        dossier = IDossierMarker(self.context)
        return getattr(dossier, 'filing_no', None)

    # TODO: should be more generic ;-)
    #       use sequence_number instead of intid
    def email(self):
        if IMailInAddressMarker.providedBy(self.context):
            return IMailInAddress(self.context).get_email_address()

    @memoize
    def workflow_state(self):
        state = self.context_state.workflow_state()
        workflows = self.context.portal_workflow.getWorkflowsFor(
            self.context.aq_explicit)
        if workflows:
            for w in workflows:
                if state in w.states:
                    return w.states[state].title or state
