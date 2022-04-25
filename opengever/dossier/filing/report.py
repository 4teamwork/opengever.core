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

    filing_columns = (
        {
            'id': 'filing_no_filing',
            'is_default': True,
            'transform': filing_no_filing,
        },
        {
            'id': 'filing_no_year',
            'is_default': True,
            'transform': filing_no_year,
        },
        {
            'id': 'filing_no_number',
            'is_default': True,
            'transform': filing_no_number,
        },
        {
            'id': 'filing_no',
            'is_default': True,
        },
    )

    @property
    def column_settings(self):
        dossier_column_settings = DossierReporter.column_settings
        cols = [c['id'] for c in dossier_column_settings]

        # Try to place filing columns before review_state
        try:
            index = cols.index('review_state')
        except ValueError:
            index = 4

        before = dossier_column_settings[:index]
        after = dossier_column_settings[index:]
        return before + self.filing_columns + after
