from opengever.dossier import _
from opengever.dossier.browser.report import DossierReporter


def _get_filing_part(filing_number, part):
    if filing_number:
        parts = filing_number.split('-')
        if len(parts) == 4:
            try:
                return int(parts[part])
            except ValueError:
                return parts[part]
        elif part == 1 and len(parts) == 1:
            # only filing is set
            # return it if the filing part is asked
            return parts[0]
        return


def filing_no_filing(filing_number):
    """Helper wich only return the year of the filing number"""

    return _get_filing_part(filing_number, 1)


def filing_no_year(filing_number):
    """Helper wich only return the year of the filing number"""

    return _get_filing_part(filing_number, 2)


def filing_no_number(filing_number):
    """Helper wich only return the number of the filing number"""

    return _get_filing_part(filing_number, 3)


class DossierFilingNumberReporter(DossierReporter):
    """DossierReporter addition, which add filing columns to the xls-export.
    """
    @property
    def _columns(self):
        filing_columns = [
            {'id': 'filing_no',
             'title': _('filing_no_filing'),
             'transform': filing_no_filing},

            {'id': 'filing_no',
             'title': _('filing_no_year'),
             'transform': filing_no_year},

            {'id': 'filing_no',
             'title': _('filing_no_number'),
             'transform': filing_no_number},

            {'id': 'filing_no',
             'title': _(u'filing_no', default="Filing number")},
        ]
        filing_columns.reverse()

        columns = super(DossierFilingNumberReporter, self)._columns

        index = [col.get('id') for col in columns].index('review_state')
        for column in filing_columns:
            columns.insert(index, column)

        return columns
