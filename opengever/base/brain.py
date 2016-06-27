from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.utils import get_preferred_language_code
from plone import api
from plone.memoize import ram


def cache_key(m, portal_type):
    return portal_type


@ram.cache(cache_key)
def supports_translated_title(portal_type):
    fti = api.portal.get_tool('portal_types').get(portal_type)
    return ITranslatedTitle.__identifier__ in fti.behaviors


def useBrains(self, brains):
    """ Sets up the Catalog to return an object (ala ZTables) that
    is created on the fly from the tuple stored in the self.data
    Btree.
    """

    self._old_useBrains(brains)

    class TranslatedTitleBrain(self._v_result_class):

        @property
        def Title(self):
            if supports_translated_title(self.portal_type):
                code = get_preferred_language_code()
                title = getattr(self, 'title_%s' % code, None)

                if isinstance(title, unicode):
                    return title.encode('utf-8')
                return title

            return super(TranslatedTitleBrain, self).Title

    self._v_result_class = TranslatedTitleBrain
