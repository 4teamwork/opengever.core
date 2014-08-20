from ftw.mail.interfaces import IEmailAddress
from opengever.base.viewlets.byline import BylineBase
from opengever.dossier import _
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossier
from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getUtility


class BusinessCaseByline(BylineBase):
    """ Specific DocumentByLine, for the Businesscasedossier Type"""

    def start(self):
        dossier = IDossier(self.context)
        return self.to_localized_time(dossier.start)

    def responsible(self):
        info = getUtility(IContactInformation)
        dossier = IDossier(self.context)
        return info.render_link(dossier.responsible)

    def end(self):
        dossier = IDossier(self.context)
        return self.to_localized_time(dossier.end)

    def mailto_link(self):
        """Displays email-address if the IMailInAddressMarker behavior
         is provided and the dossier is Active"""

        if self.get_current_state() in DOSSIER_STATES_OPEN:
            address = IEmailAddress(self.request
                ).get_email_for_object(self.context)
            return '<a href="mailto:%s">%s</a>' % (address, address)

    def get_items(self):
        return [
            {
                'class': 'responsible',
                'label': _('label_responsible', default='Responsible'),
                'content': self.responsible(),
                'replace': True
            },
            {
                'class': 'review_state',
                'label': _('label_workflow_state', default='State'),
                'content': self.workflow_state(),
                'replace': False
            },
            {
                'class': 'start_date',
                'label': _('label_start_byline', default='from'),
                'content': self.start(),
                'replace': False
            },
            {
                'class': 'end_date',
                'label': _('label_end_byline', default='to'),
                'content': self.end(),
                'replace': False
            },
            {
                'class': 'sequenceNumber',
                'label': _('label_sequence_number', default='Sequence Number'),
                'content': self.sequence_number(),
                'replace': False
            },
            {
                'class': 'reference_number',
                'label': _('label_reference_number',
                           default='Reference Number'),
                'content': self.reference_number(),
                'replace': False
            },
            {
                'class': 'email',
                'label': _('label_email_address', default='E-Mail'),
                'content': self.mailto_link(),
                'replace': True
            }
        ]
