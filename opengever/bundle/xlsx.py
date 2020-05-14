from opengever.setup.sections.xlssource import XlsSource
from plone.i18n.normalizer.de import normalizer
from uuid import uuid4
import os


class InvalidXLSXException(Exception):
    pass


class XLSXWalker(XlsSource):
    """Read one excel file with a repository and yield nodes for reach row.

    Reading the excel is done the same way as during opengever setup, thus
    we extend from the section blueprint. We customize it so that it only
    handles one excel file and can be used outside transmogrifier.
    """
    def __init__(self, xls_path):
        self.xls_path = xls_path
        self.refnum_to_guid = {}

    def __iter__(self):
        for item in self.walk():
            yield XLSXNode(item, self.refnum_to_guid)

    def walk(self):
        repository_id = os.path.basename(self.xls_path)

        keys, sheet_data = self.read_excel_file(self.xls_path)
        for rownum, row in enumerate(sheet_data):
            yield self.process_row(row, rownum, keys, repository_id)


class XLSXNode(object):

    def __init__(self, item, refnum_to_guid):
        self.item = item
        self.creation_date = None
        self.modification_date = None
        self.level, self.reference_number, self.reference_number_prefix = self.parse_reference_number()
        self.parent_reference_number = self.parse_parent_reference_number(refnum_to_guid)
        self.guid = self.make_guid()
        self.parent_guid = self.lookup_parent_guid(refnum_to_guid)

        refnum_to_guid[self.reference_number] = self.guid

    def parse_reference_number(self):
        reference_number = self.item.get('reference_number', None)
        if reference_number:
            level = len(reference_number.split('.'))
            reference_number_prefix = reference_number.split('.')[-1]
        else:
            level = 0
            reference_number = None
            reference_number_prefix = None

        return level, reference_number, reference_number_prefix

    def parse_parent_reference_number(self, refnum_to_guid):
        # there is only a parent reference number for sub-repofolders, and None
        # for the first repo-folders and the repo-root.
        if self.level <= 1:
            return None

        parent = self.reference_number.rsplit('.', 1)[0]
        if self.level and parent not in refnum_to_guid:
            raise InvalidXLSXException(
                    "Parent position {} for {} does not "
                    "exist!".format(parent, self.reference_number))
        return parent

    def make_guid(self):
        """Create a unique, but human readable GUID.
        """
        suffix = uuid4().hex[:8]
        guid = u'{}-{}-{}'.format(
            self.reference_number or 'ROOT',
            self.title,
            suffix
        )
        # Transliterate Umlauts to ae, oe, ue, after that safe-encode to ASCII
        return normalizer.normalize(guid).encode('ascii', errors='replace')

    def lookup_parent_guid(self, refnum_to_guid):
        if self.level:
            return refnum_to_guid[self.parent_reference_number]
        else:
            return None

    def is_document(self):
        return False

    def is_root(self):
        return self.level == 0

    def is_repo(self, repo_depth):
        return True

    @property
    def title(self):
        return self.item['effective_title']

    @property
    def title_fr(self):
        return self.item['effective_title_fr'] or None

    @property
    def valid_from(self):
        return self.item['valid_from'] or None

    @property
    def valid_until(self):
        return self.item['valid_until'] or None

    @property
    def description(self):
        return self.item['description'] or None

    @property
    def classification(self):
        return self.item.get('classification') or None

    @property
    def privacy_layer(self):
        return self.item.get('privacy_layer') or None

    @property
    def retention_period(self):
        return self.item.get('retention_period') or None

    @property
    def retention_period_annotation(self):
        return self.item['retention_period_annotation'] or None

    @property
    def archival_value(self):
        return self.item.get('archival_value') or None

    @property
    def archival_value_annotation(self):
        return self.item['archival_value_annotation'] or None

    @property
    def custody_period(self):
        return self.item.get('custody_period') or None
