# -*- coding: utf-8 -*-
from opengever.base.interfaces import IBaseClientID
from opengever.dossier.archive import FILING_NO_KEY
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter
from zope.component import getUtility
from zope.component import queryAdapter
import inspect
import re


LEGACY_PREFIX_MAPPING = {
         'fd-fds':     {u'Finanzdirektion':                  u'Direktion'},
         'dbk-dbks':   {u'Direktion für Bildung und Kultur': u'Direktion'},
         'sd-sds':     {u'Sicherheitsdirektion':             u'Direktion'},
         'vd-vds':     {u'Volkswirtschaftsdirektion':        u'Direktion'},
         'gd-gds':     {u'Gesundheitsdirektion':             u'Direktion'},
         'bd-bds':     {u'Baudirektion':                     u'Direktion'},
         'ska-ska':    {u'Staatskanzlei':                    u'Direktion'},
         'di-dis':     {u'Direktion des Innern':             u'Direktion'},
         'dbk-aku':    {u'Direktion für Bildung und Kultur': u'Direktion'},
         'mandant1':   {u'Mandantendirektion':               u'Direktion'},
                         }

PREVIOUS_CLIENT_PREFIXES = {
                           'di-zibu':  ['DI.ZBD'],
                           'kom-nlk':  ['BD.NLK'],
                           'mandant1': ['OG'],
                          }


def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    def tryint(s):
        try:
            return int(s)
        except ValueError:
            return s
    # Strip dots in order to treat dotted prefixes the same as regular
    # prefixes when it comes to sorting
    s = s.replace('.', ' ')
    return [tryint(c) for c in re.split('([0-9]+)', s)]


def safe_utf8(token):
    if isinstance(token, unicode):
        token = token.encode('utf-8')
    return token


class Checker(object):
    """A Checker facilitates defining and running checks and storing their
    results.
    When a Checker's run() method is called, it executes all its methods that
    start with 'check_', and stores their results in self.results, the key
    being the name of the checker method.

    the format_results() method gathers all results from checkers previously
    run and formats them as an ASCII table using the first line of the checker
    methods' docstrings as the title.
    """

    def __init__(self, options):
        self.options = options
        self.results = {}

        # Gather all checkers.
        # Any instance method starting with 'check_' is considered a checker
        attrs = [getattr(self, attr) for attr in dir(self)]
        methods = [attr for attr in attrs if inspect.ismethod(attr)]
        self.checkers = [m for m in methods if m.__name__.startswith('check_')]

    def run(self):
        for checker in self.checkers:
            self.results[checker.__name__] = checker()

    def get_checker_title(self, checker):
        # Strip 'Check for ' prefix if it exists
        CHECK_FOR = 'check for '
        title = checker.__doc__.split('\n')[0]
        if title.lower().startswith(CHECK_FOR):
            title = title[len(CHECK_FOR):]
        # Strip whitespace
        title = title.strip()
        # Strip punctuation
        title = title.strip('.')
        # Uppercase first letter
        title = title[0].upper() + title[1:]
        return title

    def format_result_line(self, items):
        items = [str(safe_utf8(item)) for item in items]
        out = ''
        out += items[0].ljust(35) + ' '
        out += items[1].ljust(25) + ' '
        out += ' '.join(items[2:])
        out += '\n'
        return out

    def format_results(self):
        out = ''
        out += '==================\n'
        out += 'Overall Statistics\n'
        out += '==================\n'
        out += '\n'

        for checker in self.checkers:
            checker_results = self.results[checker.__name__]
            title = self.get_checker_title(checker)
            out += title.ljust(35) + ' %s\n' % len(checker_results)

        if self.options.verbose:
            out += '\n'
            out += '-' * 74 + '\n'
            out += '\n'

            for checker in self.checkers:
                title = self.get_checker_title(checker)
                out += '\n'
                out += "%s\n" % title
                out += "=" * len(title) + "\n"
                for tup in self.results[checker.__name__]:
                    out += self.format_result_line(tup)

        return out


class FilingNumberHelper(object):
    """Mixin that provides some helper methods for dealing with filing numbers.
    """

    def __init__(self, plone):
        self.plone = plone
        self.catalog = getToolByName(plone, 'portal_catalog')
        self.registry = getUtility(IRegistry)

        self.client_id = self.plone.id                                # ska-arch
        self.client_title = self.client_id.replace('-', ' ').upper()  # SKA ARCH
        self.current_client_prefix = self.registry.forInterface(IBaseClientID).client_id
        self.legacy_prefixes = LEGACY_PREFIX_MAPPING.get(self.client_id, {})

        self._filing_number_counters = None
        self._filing_numbers = None

    def get_filing_number(self, obj):
        """Given a dossier object, return its filing number.
        """
        if not IDossierMarker.providedBy(obj):
            raise ValueError("%s is not a dossier object." % obj)
        dossier = getAdapter(obj, IDossier)
        return dossier.filing_no

    def set_filing_number(self, obj, filing_no):
        """Given a dossier object and a filing number, set the filing number
        for that dossier and reindex the object.
        """
        if not IDossierMarker.providedBy(obj):
            raise ValueError("%s is not a dossier object." % obj)
        dossier = getAdapter(obj, IDossier)
        dossier.filing_no = filing_no
        obj.reindexObject()

    def get_filing_numbers(self):
        """Get a list of tuples containing all filing numbers and the path
        to the corresponsing dossier objects.

        Empty filing numbers will be omitted.
        """
        # Memoize
        if not self._filing_numbers:
            brains = self.catalog(object_provides=IDossierMarker.__identifier__)

            filing_numbers = []
            for b in brains:
                obj = b.getObject()
                fn = self.get_filing_number(obj)
                path = b.getPath()
                if fn:
                    filing_numbers.append((fn, path))

            filing_numbers.sort(key=lambda x: alphanum_key(x[0]))
            self._filing_numbers = filing_numbers
        return self._filing_numbers

    def get_filing_number_counters(self):
        """Return the dictionary that represents the mapping of filing number
        counter keys to their Increaser object.
        """
        if not self._filing_number_counters:

            ann = queryAdapter(self.plone, IAnnotations)
            if ann is not None:
                self._filing_number_counters = ann.get(FILING_NO_KEY, {})

            if ann is None:
                raise KeyError("No annotations found on Plone site root!")
        return self._filing_number_counters

    def get_associated_filing_numbers(self, counter_key):
        """Return a sorted list of filing numbers and paths for all filing
        numbers associated with the counter identified by `counter_key`.

        The client id prefix will be stripped for determining matches, so
        the association is fuzzy.
        """
        fns_and_paths = self.get_filing_numbers()
        associated_fns = []
        for fn, path in fns_and_paths:
            if self.get_prefixless_filing_number(fn).startswith(counter_key):
                associated_fns.append((fn, path))
        associated_fns.sort(key=lambda x: alphanum_key(x[0]))
        return associated_fns

    def get_highest_filing_number(self, fns_and_paths):
        """From a list of filing numbers and paths running on the same counter,
        return the filing number with the highest counter value.
        """
        prefixless_fns = [(self.get_prefixless_filing_number(fn), fn, path)
                            for fn, path in fns_and_paths]
        prefixless_fns.sort(key=lambda x: alphanum_key(x[0]))
        return prefixless_fns[-1][1]

    def get_minimal_counter_value(self, counter_key):
        """Given a counter key, return the minimal valid counter value.
        """
        associated_fns = self.get_associated_filing_numbers(counter_key)
        highest_fn = self.get_highest_filing_number(associated_fns)
        min_value = self.get_number_part(highest_fn)
        return min_value

    def get_number_part(self, fn):
        """Given a filing number, return only the sequence number (the
        rightmost part of the number).

        If the filing number was issued for a subdossier, the subdossier
        part of the sequence number will be omitted.
        """
        prefixless_fn = self.get_prefixless_filing_number(fn)
        # Get rightmost part
        number_part = prefixless_fn.split('-')[-1]

        # Ignore any subdossier suffixes
        if '.' in number_part:
            number_part = number_part.split('.')[0]
        return int(number_part)

    def get_prefixless_filing_number(self, fn):
        """Strip the client prefix from a filing number.
        """
        for prefix in self.get_possible_client_prefixes():
            if fn.startswith("%s-" % prefix):
                return fn.replace("%s-" % prefix, '', 1)
        return fn

    def get_possible_client_prefixes(self):
        """Get all possible client prefixes that this client could have, or
        have had in the past, considering previous prefixes for renamed client,
        and old filing number schemas (dotted prefixes).
        """
        current_prefix = self.current_client_prefix
        # Current prefix
        yield current_prefix
        # Dotted prefix (if applicable)
        dotted_prefix = current_prefix.replace(' ', '.')
        if not current_prefix == dotted_prefix:
            yield dotted_prefix
        # Previously used prefixes (if applicable)
        for prev_prefix in self.get_previous_client_prefixes():
            yield prev_prefix

    def get_previous_client_prefixes(self):
        """Return the previous prefixes this client used to have in the past
        (This is a configuration value).
        """
        return PREVIOUS_CLIENT_PREFIXES.get(self.client_id, [])


class FilingNumberChecker(Checker, FilingNumberHelper):
    """Checks a OpenGever client for different problems with filing numbers.
    """

    def __init__(self, options, plone):
        self._filing_numbers = []
        self._filing_number_counters = {}

        FilingNumberHelper.__init__(self, plone)
        Checker.__init__(self, options)

    def check_for_duplicates(self):
        """Check for duplicate filing numbers.
        Only exact duplicates are considered.
        """
        fns_and_paths = self.get_filing_numbers()
        fns = [fn for fn, path in fns_and_paths]

        dups = [fn for fn in fns if fns.count(fn) > 1]
        dups = list(set(dups))
        dups.sort(key=alphanum_key)
        dossiers_with_dups = [(fn, path) for (fn, path) in fns_and_paths if fn in dups]
        return dossiers_with_dups

    def check_for_fuzzy_duplicates(self):
        """Check for duplicate filing numbers (fuzzy).
        Finds duplicate filing numbers while ignoring client prefixes.
        """
        fns_and_paths = self.get_filing_numbers()
        prefixless_fns = [self.get_prefixless_filing_number(fn)
                                for fn, path in fns_and_paths]

        fuzzy_dups = [(self.get_prefixless_filing_number(fn), fn, path)
                        for fn, path in fns_and_paths
                        if prefixless_fns.count(
                            self.get_prefixless_filing_number(fn)) > 1]
        fuzzy_dups.sort(key=lambda x: alphanum_key(x[0]))
        return fuzzy_dups

    def check_for_legacy_filing_prefixes(self):
        """Check for legacy filing prefixes.
        For example:
        'Baudirektion-' instead of 'BD BDS-Direktion-'
        """
        legacy_numbers = []
        fns_and_paths = self.get_filing_numbers()
        for fn, path in fns_and_paths:
            for legacy_prefix in self.legacy_prefixes.keys():
                if fn.startswith("%s-" % legacy_prefix):
                    legacy_numbers.append((fn, path))
        return legacy_numbers

    def check_for_missing_client_prefixes(self):
        """Check for missing client prefixes.
        For example:
        Filing numbers should start with 'CLIENT ID-'.
        """
        dossiers_with_missing_client_prefix = []
        fns_and_paths = self.get_filing_numbers()
        for fn, path in fns_and_paths:
            if not fn.startswith(self.current_client_prefix):
                dossiers_with_missing_client_prefix.append((fn, path))
        return dossiers_with_missing_client_prefix

    def check_for_dotted_client_prefixes(self):
        """Check for dotted client prefixes.
        For example:
        Filing numbers that start with 'CLIENT.ID-' instead of 'CLIENT ID-'.
        """
        if not ' ' in self.current_client_prefix:
            # If there's no space in the current client prefix that could have
            # been substituted with a dot, this check doesn't make sense
            return []

        dotted_prefix = self.current_client_prefix.replace(' ', '.')
        dossiers_with_dotted_client_prefix = []
        fns_and_paths = self.get_filing_numbers()
        for fn, path in fns_and_paths:
            if not fn.startswith(self.current_client_prefix):
                if fn.startswith(dotted_prefix):
                    dossiers_with_dotted_client_prefix.append((fn, path))
        return dossiers_with_dotted_client_prefix

    def check_for_bad_counters(self):
        """Check for bad counters.
        (Counters that are lower than the highest issued FN for that counter)
        """
        bad_counters = []
        counters = self.get_filing_number_counters()
        for counter_key, increaser in counters.items():
            associated_fns = self.get_associated_filing_numbers(counter_key)

            if associated_fns:
                # If there are FNs associated with this counter, check
                # that the counter is at least as high as the highest FN
                highest_fn = self.get_highest_filing_number(associated_fns)
                if self.get_number_part(highest_fn) > increaser.value:
                    bad_counters.append((counter_key, increaser.value, highest_fn))

        return bad_counters
