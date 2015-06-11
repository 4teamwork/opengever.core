from collective.dexteritytextindexer import searchable
from opengever.base import _
from opengever.base.utils import get_preferred_language_code
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives.form import Schema
from plone.i18n.normalizer.base import mapUnicode
from plone.indexer import indexer
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import num_sort_regex
from Products.CMFPlone.CatalogTool import zero_fill
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.utils import safe_unicode
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.schema import TextLine


class ITranslatedTitleSupport(Interface):
    """Mark objects with translated title support."""


class TranslatedTitleMixin(object):
    """All types which use the translated title behavior need to extend
    this mixin.
    """

    def Title(self, language=None):
        title = ITranslatedTitle(self).translated_title(language)
        if isinstance(title, unicode):
            return title.encode('utf-8')
        return title or ''


class ITranslatedTitle(Schema):
    """Behavior schema adding translated title fields to dexterity
    content.
    """

    directives.order_before(title_de='*')
    searchable('title_de')
    title_de = TextLine(title=_(u'label_title_de',
                                default=u'Title (German)'),
                        required=True)

    directives.order_before(title_fr='*')
    searchable('title_fr')
    title_fr = TextLine(title=_(u'label_title_fr',
                                default=u'Title (French)'),
                        required=False)


alsoProvides(ITranslatedTitle, IFormFieldProvider)


class TranslatedTitle(object):

    def __init__(self, context):
        self.context = context

    def translated_title(self, language=None):
        language = get_preferred_language_code()
        title = getattr(self, 'title_%s' % language, None)
        if not title:
            title = getattr(self, 'title_de', None)

        return title

    def _get_title_de(self):
        return self.context.title_de

    def _set_title_de(self, value):
        if isinstance(value, str):
            raise ValueError('title_de must be unicode.')
        self.context.title_de = value

    title_de = property(_get_title_de, _set_title_de)

    def _get_title_fr(self):
        return getattr(self.context, 'title_fr', None)

    def _set_title_fr(self, value):
        if isinstance(value, str):
            raise ValueError('title_fr must be unicode.')
        self.context.title_fr = value

    title_fr = property(_get_title_fr, _set_title_fr)


@indexer(ITranslatedTitleSupport)
def translated_title_indexer(obj):
    return obj.Title(language='de')


@indexer(ITranslatedTitleSupport)
def translated_sortable_title_indexer(obj):
    title = getattr(obj, 'Title', None)
    if title is not None:
        if safe_callable(title):
            # CUSTOM
            title = title(language='de')
            # / CUSTOM

        if isinstance(title, basestring):
            # Ignore case, normalize accents, strip spaces
            sortabletitle = mapUnicode(safe_unicode(title)).lower().strip()
            # Replace numbers with zero filled numbers
            sortabletitle = num_sort_regex.sub(zero_fill, sortabletitle)
            # Truncate to prevent bloat
            sortabletitle = sortabletitle[:70].encode('utf-8')
            return sortabletitle

            # XXX Use this implementation for plone 4.3
            # from Products.CMFPlone.CatalogTool import MAX_SORTABLE_TITLE
            # # Truncate to prevent bloat, take bits from start and end
            # if len(sortabletitle) > MAX_SORTABLE_TITLE:
            #     start = sortabletitle[:(MAX_SORTABLE_TITLE - 13)]
            #     end = sortabletitle[-10:]
            #     sortabletitle = start + '...' + end
            # return sortabletitle.encode('utf-8')
    return ''
