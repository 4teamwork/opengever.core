from App.special_dtml import DTMLFile
from five import grok
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.interfaces import IReferenceNumber
from opengever.ogds.base.sort_helpers import SortHelpers
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
from zope.component import getMultiAdapter


@indexer(IDexterityContent)
def breadcrumb_titlesIndexer(obj):
    breadcrumbs_view = getMultiAdapter((obj, obj.REQUEST),
                                       name='breadcrumbs_view')
    return breadcrumbs_view.breadcrumbs()
grok.global_adapter(breadcrumb_titlesIndexer, name="breadcrumb_titles")


@indexer(IDexterityContent)
def referenceIndexer(obj):
    ref_number = IReferenceNumber(obj).get_number()
    return ref_number
grok.global_adapter(referenceIndexer, name="reference")


@indexer(IDexterityContent)
def title_de_indexer(obj):
    if ITranslatedTitleSupport.providedBy(obj):
        return ITranslatedTitle(obj).title_de
    return None

grok.global_adapter(title_de_indexer, name="title_de")


@indexer(IDexterityContent)
def title_fr_indexer(obj):
    if ITranslatedTitleSupport.providedBy(obj):
        return ITranslatedTitle(obj).title_fr
    return None

grok.global_adapter(title_fr_indexer, name="title_fr")


class KeyMapProxy(object):

    def __init__(self, index, callback):
        self.index = index
        self.callback = callback
        self._cache = {}

    def __getitem__(self, key):
        if key in self._cache:
            return self._cache[key]

        value = self.index._unindex.get(key, key)
        sort_value = self.callback(value, value)
        self._cache[key] = sort_value
        return sort_value


class UserTurboIndex(FieldIndex):
    meta_type = 'UserTurboIndex'

    def documentToKeyMap(self):
        sort_dict = SortHelpers().get_user_sort_dict()
        return KeyMapProxy(self, sort_dict.get)


manage_addUserTurboIndexForm = DTMLFile('dtml/addUserTurboIndex', globals())

def manage_addUserTurboIndex(self, id, extra=None,
                             REQUEST=None, RESPONSE=None, URL3=None):
    """Add a user turbo index"""
    return self.manage_addIndex(
        id, 'UserTurboIndex', extra=extra,
        REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
