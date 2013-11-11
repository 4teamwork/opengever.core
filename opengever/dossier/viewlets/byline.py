from opengever.base.viewlets.byline import BylineBase
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.mail.behaviors import IMailInAddressMarker, IMailInAddress
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

    def get_filing_no(self):
        dossier = IDossier(self.context)
        return getattr(dossier, 'filing_no', None)

    def email(self):
        """Displays email-address if the IMailInAddressMarker behavior
         is provided and the dossier is Active"""

        if IMailInAddressMarker.providedBy(self.context):
            if self.get_current_state() == 'dossier-state-active':
                address = IMailInAddress(self.context).get_email_address()
                return '<a href="mailto:%s">%s</a>' % (address, address)

    def get_items(self):
        return [
            {
                'class': 'responsible',
                'label': _('label_responsible', default='by'),
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
                'class': 'filing_no',
                'label': _('label_filing_no', default='Filing Number'),
                'content': self.get_filing_no(),
                'replace': False
            },
            {
                'class': 'email',
                'label': _('label_email_address', default='E-Mail'),
                'content': self.email(),
                'replace': True
            }
        ]
