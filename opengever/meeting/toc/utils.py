from opengever.base.filename import unidecode
from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.base.interfaces import IReferenceNumberSettings
from Products.CMFPlone.utils import safe_unicode
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryAdapter
import unicodedata


def normalise_unicode(string):
    return unicodedata.normalize('NFKC', safe_unicode(string))


def normalise_string(string):
    if string is None:
        return
    return unidecode(normalise_unicode(string)).lower()


def first_title_char(item):
    return normalise_string(item["title"])[:1]


def to_human_sortable_key(string):
    """To correctly sort reference number strings such as 'ab 10.2' after 'ab 1.2'
    we need to separate numbers from other characters and cast them.
    """
    if string is None:
        return []
    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IReferenceNumberSettings)
    formatter = queryAdapter(IReferenceNumberFormatter, name=proxy.formatter)
    return formatter.sorter(string)


def repo_refnum(item):
    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IReferenceNumberSettings)
    formatter = queryAdapter(IReferenceNumberFormatter, name=proxy.formatter)

    refnum = item['dossier_reference_number']
    if refnum is None:
        return None
    elif formatter.repository_dossier_seperator in refnum:
        repo_refnum, remainder = refnum.split(formatter.repository_dossier_seperator, 1)
        return repo_refnum
