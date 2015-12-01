from collective.dexteritytextindexer import searchable
from opengever.base import _
from opengever.base.utils import get_preferred_language_code
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives.form import Schema
from plone.i18n.normalizer.base import mapUnicode
from plone.indexer import indexer
from Products.CMFPlone.CatalogTool import MAX_SORTABLE_TITLE
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
    title_de = TextLine(
        title=_(u'label_title_de', default=u'Title (German)'),
        required=True)

    directives.order_before(title_fr='*')
    searchable('title_fr')
    title_fr = TextLine(
        title=_(u'label_title_fr', default=u'Title (French)'),
        required=True)


alsoProvides(ITranslatedTitle, IFormFieldProvider)


class TranslatedTitle(object):

    FALLBACK_LANGUAGE = 'de'

    def __init__(self, context):
        self.context = context

    def translated_title(self, language=None):
        if not language:
            language = get_preferred_language_code()

        title = getattr(self, 'title_{}'.format(language), None)
        if not title:
            title = getattr(self,
                            'title_{}'.format(self.FALLBACK_LANGUAGE), None)

        return title

    @property
    def title_de(self):
        return self.context.title_de

    @title_de.setter
    def title_de(self, value):
        if not isinstance(value, unicode):
            raise ValueError('title_de must be unicode.')
        self.context.title_de = value

    @property
    def title_fr(self):
        return self.context.title_fr

    @title_fr.setter
    def title_fr(self, value):
        if not isinstance(value, unicode):
            raise ValueError('title_fr must be unicode.')
        self.context.title_fr = value


@indexer(ITranslatedTitleSupport)
def translated_title_indexer(obj):
    return obj.Title(language='de')


@indexer(ITranslatedTitleSupport)
def translated_sortable_title_indexer(obj):
    ## mostly copied from Products.CMFPlone.CatalogTool.sortable_title
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

            # Truncate to prevent bloat, take bits from start and end
            if len(sortabletitle) > MAX_SORTABLE_TITLE:
                start = sortabletitle[:(MAX_SORTABLE_TITLE - 13)]
                end = sortabletitle[-10:]
                sortabletitle = start + '...' + end
            return sortabletitle.encode('utf-8')

    return ''
