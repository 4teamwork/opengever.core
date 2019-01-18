from opengever.base.filename import unidecode
from Products.CMFPlone.utils import safe_unicode
import unicodedata


def normalise_unicode(string):
    return unicodedata.normalize('NFKC', safe_unicode(string))


def normalise_string(string):
    if string is None:
        return
    return unidecode(normalise_unicode(string)).lower()


def first_title_char(item):
    return normalise_string(item["title"])[:1]
