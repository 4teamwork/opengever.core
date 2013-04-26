from StringIO import StringIO
from five import grok
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.dossier.filing_checker import FilingNumberChecker
from xlwt import Workbook, XFStyle, Font
from zope.interface import Interface
import transaction

# excel styles
TITLE_STYLE = XFStyle()
TITLE_STYLE.font.bold = True

OLD_STYLE = XFStyle()
OLD_STYLE.font.colour_index = 0x10
OLD_STYLE.font.outline = False

NEW_STYLE = XFStyle()
NEW_STYLE.font.colour_index = 0x11
NEW_STYLE.font.outline = False


class FakeOptions(object):

    def __init__(self):
        self.verbose = False


class FilingNumberFixer(FilingNumberChecker):

    def __init__(self, options, plone):
        self._fixed_dossiers = {}
        self._fixed_counters = {}

        FilingNumberChecker.__init__(self, options, plone)

    def log_fn_changes(self, path, old, new):
        if self._fixed_dossiers.get(path):
            self._fixed_dossiers[path].append((old, new))
        else:
            self._fixed_dossiers[path] = [(old, new), ]

    def log_counter_changes(self, key, old, new):
        if self._fixed_counters.get(key):
            self._fixed_counters[key].append((old, new))
        else:
            self._fixed_counters[key] = [(old, new), ]

    def fix_legacy_filing_prefixes(self):
        fn_and_paths = self.check_for_legacy_filing_prefixes()

        for fn, path in fn_and_paths:
            fn_parts = fn.split('-')
            new_fn = '%s-%s-%s-%s' % (
                self.current_client_prefix,
                self.legacy_prefixes.get(fn_parts[0]),
                fn_parts[1], fn_parts[2])

            obj = self.plone.unrestrictedTraverse(path.strip('/'))
            self._set_filing_number_without_reindex(obj, new_fn)

            # logging
            self.log_fn_changes(path, fn, new_fn)

        # check if the fix worked well
        # reset filing_numbers
        self._reset_filing_numbers()

        if len(self.check_for_legacy_filing_prefixes()) > 0:
            raise RuntimeError(
                "The legacy filing prefixes fixer wasn't successfully'"
                ", it exits still some legacy filing prefixes %s" %
                str(self.check_for_legacy_filing_prefixes()))

    def fix_missing_client_prefixes(self):

        fn_and_paths = self.check_for_missing_client_prefixes()

        for fn, path in fn_and_paths:
            new_fn = '%s-%s' % (
                self.current_client_prefix, fn)

            obj = self.plone.unrestrictedTraverse(path.strip('/'))
            self._set_filing_number_without_reindex(obj, new_fn)

            # logging
            self.log_fn_changes(path, fn, new_fn)

        # check if the fix worked well
        # reset filing_numbers
        self._reset_filing_numbers()

        if len(self.check_for_missing_client_prefixes()) > 0:
            raise RuntimeError(
                "The missing client prefixes fixer wasn't successfully , it "
                "exits still some filing numbers without a client"
                "prefixes %s" % str(
                    self.check_for_missing_client_prefixes()))

    def fix_inexistent_filing_prefixes(self, mapping):

        # get_dossiers with a inexistent filing_prefix
        bad_prefixes = self.check_for_inexistent_filing_prefixes()
        bad_prefixes = [prfx[0] for prfx in bad_prefixes]

        # check if every bad_prefix has now a mapping to a correct one.
        for prfx in bad_prefixes:
            if not mapping.get(prfx, None):
                raise AttributeError(
                    'Missing prefix mapping for bad prefix: %s' % (prfx))

        # get all dossiers wich should be fixed
        to_fix = []
        for prefix in bad_prefixes:
            to_fix += self.get_associated_to_filing_prefix_numbers(prefix)

        # fix
        for fn, path, prefix in to_fix:
            obj = self.plone.unrestrictedTraverse(path.strip('/'))
            new_fn = fn.replace(prefix, mapping.get(prefix))
            self._set_filing_number_without_reindex(obj, new_fn)

            # logging
            self.log_fn_changes(path, fn, new_fn)

        # check if the fix worked well
        # reset filing_numbers
        self._reset_filing_numbers()

        if len(self.check_for_inexistent_filing_prefixes()) > 0:
            raise RuntimeError(
                "The inexistent_filing_prefix fixer wasn't successfully'"
                ", it exits still some inexistent_filing_prefix %s" %
                str(self.check_for_inexistent_filing_prefixes()))

    def fix_duplicates(self):
        """Method wichi Fix all existing duplicates
        a fix for fuzzy duplicates isn't necessary, because
        they should allready fixed with the
        inexistent filing prefixes fixer.
        """

        # get dossiers with duplicates
        duplicates = self.check_for_duplicates()

        duplicate_mapping = {}
        for fn, path in duplicates:
            if duplicate_mapping.get(fn, None):
                duplicate_mapping[fn].append(path)
            else:
                duplicate_mapping[fn] = [path, ]

        for fn, paths in duplicate_mapping.items():
            # get_all_objs with the same fn
            objs = [self.plone.unrestrictedTraverse(path.strip('/'))
                    for path in paths]

            # sort on created date
            objs = sorted(objs, key=lambda obj: obj.created(), reverse=False)

            # give a new filing number for every duplicate
            for obj in objs[1:]:
                new_fn = self.set_next_filing_number(obj)

                # logging
                self.log_fn_changes(
                    '/'.join(obj.getPhysicalPath()), fn, new_fn)

        # check if the fix worked well
        # reset filing_numbers
        self._reset_filing_numbers()
        if len(self.check_for_duplicates()) > 0:
            raise RuntimeError(
                "The duplicates fixer wasn't successfully'"
                ", it exits still some duplicated filing numbers %s" %
                str(self.check_for_duplicates()))

        # also all fuzzy duplicates should be solved
        if len(self.check_for_fuzzy_duplicates()) > 0:
            raise RuntimeError(
                "The duplicates fixer wasn't successfully'"
                ", it exits still some FUZZY(!) duplicated filing numbers %s" %
                str(self.check_for_fuzzy_duplicates()))

    def fix_bad_counters(self):
        bad_counters = self.check_for_bad_counters()

        for key, old_value, highest_fn in bad_counters:
            new_value = self.get_number_part(highest_fn)
            self.set_counter_value(key, new_value)

            # logging
            self.log_counter_changes(key, old_value, new_value)

        # check if the fix
        if len(self.check_for_bad_counters()) > 0:
            raise RuntimeError(
                "The bad counters fixer wasn't successfully'"
                ", it exits still some bad counters %s" %
                str(self.check_for_duplicates()))

    def fix_counters_needing_initialization(self):
        counters = self.check_for_counters_needing_initialization()

        for counter_key, numbers in counters:
            associated_fns = self.get_associated_filing_numbers(counter_key)
            highest_fn = self.get_highest_filing_number(associated_fns)
            new_value = self.get_number_part(highest_fn)
            self.create_counter(counter_key, new_value)

            # logging
            self.log_counter_changes(counter_key, 'NONE', new_value)

        # check if the fix
        if len(self.check_for_counters_needing_initialization()) > 0:
            raise RuntimeError(
                "The counters who need a initialization fixer "
                "wasn't successfully', the following counters still need "
                "an initialization %s" % str(
                    self.check_for_counters_needing_initialization()))

    def fix_dotted_client_prefixes(self):
        fns_and_paths = self.check_for_dotted_client_prefixes()

        dotted_prefix = self.current_client_prefix.replace(' ', '.')
        current_prefix = self.current_client_prefix

        for fn, path in fns_and_paths:
            obj = self.plone.unrestrictedTraverse(path.strip('/'))
            new_fn = fn.replace(dotted_prefix, current_prefix)
            self._set_filing_number_without_reindex(obj, new_fn)

            # logging
            self.log_fn_changes(path, fn, new_fn)

        # check if the fix worked well
        # reset filing_numbers
        self._reset_filing_numbers()
        if len(self.check_for_dotted_client_prefixes()) > 0:
            raise RuntimeError(
                "The dotted client prefixes fixer wasn't successfully"
                ", the following fn still have an dotten client prefix "
                "%s." % str(self.check_for_dotted_client_prefixes()))


class FixFilingNumbers(grok.View):
    grok.name('fix_filing')
    grok.context(Interface)

    def render(self):

        transaction.doom()

        fixer = FilingNumberFixer(FakeOptions(), self.context)
        fixer.run()

        # fix dotted clients
        fixer.fix_dotted_client_prefixes()
        # legacy filing prefixes
        fixer.fix_legacy_filing_prefixes()
        # missing client prefix
        fixer.fix_missing_client_prefixes()
        # bad counters
        fixer.fix_bad_counters()
        # inexistent filing prefix
        fixer.fix_inexistent_filing_prefixes(
            {'Hans': u'Amt',
             'Pesche': u'Leitung',
             'Blub': u'Leitung'})
        # counters need initialization
        fixer.fix_counters_needing_initialization()
        # duplicates
        fixer.fix_duplicates()

        # all fixers done
        checker = FilingNumberChecker(FakeOptions(), self.context)
        checker.run()
        if len([k for k, v in checker.results.items() if len(v) > 0]):
            raise RuntimeError(
                'All fixes done, but the Checker still detected '
                'some problems %s' % (str(checker.results)))

        data = self.generate_excel(
            fixer._fixed_dossiers, fixer.get_filing_number_counters())
        response = self.request.RESPONSE

        response.setHeader('Content-Type', 'application/vnd.ms-excel')
        set_attachment_content_disposition(
            self.request, "dossier_report.xls")

        return data

    def generate_excel(self, fixed_dossiers, counters):
        w = Workbook()

        self._add_dossier_sheet(w, fixed_dossiers)
        self._add_counters_sheet(w, counters)

        data = StringIO()
        w.save(data)
        data.seek(0)

        return data.read()

    def _add_dossier_sheet(self, w, dossiers):
        sheet = w.add_sheet('changed dossiers')

        for r, path in enumerate(dossiers.keys()):
            sheet.write(r, 0, path, TITLE_STYLE)

            counter = 1
            for fn_pair in dossiers.get(path):
                sheet.write(r, counter, fn_pair[0], OLD_STYLE)
                sheet.write(r, counter + 1, fn_pair[1], NEW_STYLE)
                counter += 2

        # set_size
        sheet.col(0).width = 17500
        for i in range(1, 16):
            sheet.col(i).width = 5000

    def _add_counters_sheet(self, w, counters):
        sheet = w.add_sheet('counters overview')
        for r, key in enumerate(counters.keys()):
            sheet.write(r, 0, key, TITLE_STYLE)
            sheet.write(r, 1, counters.get(key).value)

        # set_size
        sheet.col(0).width = 5000
        sheet.col(1).width = 5000
