from five import grok
from logging import getLogger
from plone.indexer import indexer
from zope.interface import Interface
from opengever.repository.behaviors.alternativetitle  import \
    IAlternativeTitleBehaviorMarker
from opengever.repository import utils as lang_utils


LOG = getLogger('opengever.repository')

# AlternativeTitleBehavior

@indexer(IAlternativeTitleBehaviorMarker)
def primary_title(obj):
    try:
        return obj.Title(language=lang_utils.getPrimaryLanguageCode())
    except TypeError:
        LOG.error('Object with IAlternativeTitleBehavior has no support for '
                  'Title(language="%s"). %s' %
                  (lang_utils.getPrimaryLanguageCode(), str(obj)))
        return obj.Title()
grok.global_adapter(primary_title, name='Title')


@indexer(IAlternativeTitleBehaviorMarker)
def alternative_title(obj):
    try:
        return obj.Title(language=lang_utils.getAlternativeLanguageCode())
    except TypeError:
        LOG.error('Object with IAlternativeTitleBehavior has no support for '
                  'Title(language="%s"). %s' %
                  (lang_utils.getAlternativeLanguageCode(), str(obj)))
        return obj.Title()
grok.global_adapter(alternative_title, name='alternative_title')


@indexer(Interface)
def alternative_title_fallback(obj):
    return ''
grok.global_adapter(alternative_title_fallback, name='alternative_title')
