from opengever.base.browser.helper import get_css_class
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossier
from opengever.mail.behaviors import IMailInAddressMarker, IMailInAddress
from opengever.ogds.base.interfaces import IContactInformation
from plone.app.layout.viewlets import content
from plone.memoize.instance import memoize
from zope.component import getUtility, getAdapter
from opengever.dossier import _


class BusinessCaseByline(content.DocumentBylineViewlet):
    """ Specific DocumentByLine, for the Businesscasedossier Type"""

    update = content.DocumentBylineViewlet.update

    def get_css_class(self):
        return get_css_class(self.context)

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
        dossier = IDossier(self.context)
        return getattr(dossier, 'filing_no', None)

    # TODO: should be more generic ;-)
    #       use sequence_number instead of intid
    def email(self):
        """Displays email-address if the IMailInAddressMarker behavior
         is provided and the dossier is Active"""
        if IMailInAddressMarker.providedBy(self.context) \
        and self.workflow_state() == 'dossier-state-active':
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

    def get_items(self):
        info = getUtility(IContactInformation)
        dossier = IDossier(self.context)
        return [
            {'class': 'responsible',
             'label': _('label_responsible', default='by'),
             'content': info.render_link(dossier.responsible),
             'replace': True
            }
        ]
