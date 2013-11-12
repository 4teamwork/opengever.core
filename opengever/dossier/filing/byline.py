from opengever.dossier import _
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.behaviors.filing import IFilingNumberMarker
from opengever.dossier.viewlets.byline import BusinessCaseByline


class FilingBusinessCaseByline(BusinessCaseByline):

    def get_filing_no(self):
        if IFilingNumberMarker(self.context):
            return IFilingNumber(self.context).filing_no

    def get_items(self):
        """Append the filing number to the default businesscase byline."""

        items = super(FilingBusinessCaseByline, self).get_items()
        index = [attr.get('class') for attr in items].index('email')

        filing_number = {
            'class': 'filing_no',
            'label': _('label_filing_no', default='Filing Number'),
            'content': self.get_filing_no(),
            'replace': False}

        items.insert(index, filing_number)
        return items
