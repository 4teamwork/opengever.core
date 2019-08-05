from contextlib import contextmanager
from datetime import datetime
from lxml.cssselect import LxmlTranslator
from opengever.base.date_time import as_utc
from opengever.contact.sources import ContactsSource
from opengever.document.versioner import Versioner
from operator import attrgetter
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.PloneLanguageTool.LanguageTool import LanguageBinding
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.intid.interfaces import IIntIds
from zope.security.management import endInteraction
from zope.security.management import newInteraction
import logging
import pytz
import transaction


DEFAULT_TZ = pytz.timezone('Europe/Zurich')


@contextmanager
def time_based_intids():
    """To ensure predictable IntIds in tests, this context manager patches
    the IntIds utility so that IntIds are created based on the current time
    """
    original_intids = getUtility(IIntIds)

    class TimeBasedIntIds(type(original_intids)):

        def __init__(self):
            self.__dict__ = original_intids.__dict__

        def _generateId(self):
            intid = int(datetime.now(pytz.UTC).strftime('10%H%M%S00'))
            while intid in self.refs:
                intid += 1
            return intid

    globals()['TimeBasedIntIds'] = TimeBasedIntIds
    patched_intids = TimeBasedIntIds()
    getSite().getSiteManager().registerUtility(patched_intids, IIntIds)
    try:
        yield
    finally:
        getSite().getSiteManager().registerUtility(original_intids, IIntIds)
        globals().pop('TimeBasedIntIds')


@contextmanager
def incrementing_intids(starting_number=99000):
    """In testing environments we often want to have predictable intids,
    but using a time based version may not work well when time is frozen.
    This implementation replaces the intids generator with an incrementing one.
    """
    original_intids = getUtility(IIntIds)
    counter = {'number': starting_number}

    class IncrementingIntIds(type(original_intids)):

        def __init__(self):
            self.__dict__ = original_intids.__dict__

        def _generateId(self):
            counter['number'] += 1
            intid = counter['number']
            while intid in self.refs:
                intid += 1
            return intid

    globals()['IncrementingIntIds'] = IncrementingIntIds
    patched_intids = IncrementingIntIds()
    getSite().getSiteManager().registerUtility(patched_intids, IIntIds)
    try:
        yield
    finally:
        getSite().getSiteManager().registerUtility(original_intids, IIntIds)
        globals().pop('IncrementingIntIds')


def localized_datetime(*args, **kwargs):
    """Localize timezone naive datetime to default timezone and return as utc.

    """
    if args or kwargs:
        dt = datetime(*args, **kwargs)
    else:
        dt = datetime.now()

    return as_utc(DEFAULT_TZ.localize(dt))


def create_plone_user(portal, userid, password='demo09'):
    acl_users = getToolByName(portal, 'acl_users')
    acl_users.source_users.addUser(userid, userid, password)


def obj2brain(obj, unrestricted=False):
    catalog = getToolByName(obj, 'portal_catalog')
    query = {'path': {'query': '/'.join(obj.getPhysicalPath()), 'depth': 0}}

    if unrestricted:
        brains = catalog.unrestrictedSearchResults(query)
    else:
        brains = catalog(query)

    if len(brains) == 0:
        raise Exception('Not in catalog: %s' % obj)

    return brains[0]


def index_data_for(obj):
    catalog = getToolByName(obj, 'portal_catalog')
    return catalog.getIndexDataForRID(obj2brain(obj, unrestricted=True).getRID())


def set_preferred_language(request, code):
    binding = LanguageBinding(api.portal.get_tool('portal_languages'))
    binding.DEFAULT_LANGUAGE = code
    binding.LANGUAGE = code
    request['LANGUAGE_TOOL'] = binding


def add_languages(codes, support_combined=True):
    lang_tool = api.portal.get_tool('portal_languages')
    if support_combined:
        lang_tool.use_combined_language_codes = True

    for code in codes:
        lang_tool.addSupportedLanguage(code)

    transaction.commit()


def create_document_version(doc, version_id, data=None, comment=None):
    vdata = data or 'VERSION {} DATA'.format(version_id)
    doc.file.data = vdata

    if comment is None:
        comment = u'This is Version %s' % version_id

    Versioner(doc).create_version(comment)


def css_to_xpath(css):
    return LxmlTranslator().css_to_xpath(css)


def get_contacts_source():
    return ContactsSource(api.portal.get())


def get_contacts_token(obj):
    return get_contacts_source().getTerm(obj).token


def obj2paths(objs):
    """Returns a list of paths (string) for the given objects.
    """
    return ['/'.join(obj.getPhysicalPath()) for obj in objs]


@contextmanager
def fake_interaction():
    """Context manager that temporarily sets up a fake IInteraction.

    This may be needed in cases where no real request is being processed
    (there's no actual publishing going on), but still a call to
    checkPermission() is necessary.

    That call would otherwise fail with zope.security.interfaces.NoInteraction.

    Initially needed for standalone testing of z3c.forms, inspired by
    from z3c/formwidget//query/README.txt.

    For more details see zope.security.management and ZPublisher.Publish.
    """
    newInteraction()
    try:
        yield
    finally:
        endInteraction()


class CapturingLogHandler(logging.NullHandler):
    """Log handler that just captures logged records in a list.
    """

    def __init__(self, *args, **kwargs):
        super(CapturingLogHandler, self).__init__(*args, **kwargs)
        self._records = []

    def handle(self, record):
        self._records.append(record)

    @property
    def records(self):
        return self._records

    @property
    def msgs(self):
        return map(attrgetter('msg'), self._records)

    def pop_records(self):
        records = self._records
        self._records = []
        return records

    def pop_msgs(self):
        return map(attrgetter('msg'), self.pop_records())

    def clear(self):
        self._records = []
