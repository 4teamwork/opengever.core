from five import grok
from logging import getLogger
from plone.indexer import indexer
from zope.interface import Interface
from opengever.repository.behaviors.alternativetitle  import \
    IAlternativeTitleBehaviorMarker
from opengever.repository.interfaces import IRepositoryFolderRecords
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


LOG = getLogger('opengever.repository')

# AlternativeTitleBehavior

@indexer(IAlternativeTitleBehaviorMarker)
def primary_title(obj):
    # get configured primary language
    registry = getUtility(IRegistry)
    reg_proxy = registry.forInterface(IRepositoryFolderRecords)
    try:
        return obj.Title(language=reg_proxy.primary_language_code)
    except TypeError:
        LOG.error('Object with IAlternativeTitleBehavior has no support for '
                  'Title(language="%s"). %s' %
                  (reg_proxy.primary_language_code, str(obj)))
        return obj.Title()
grok.global_adapter(primary_title, name='Title')


@indexer(IAlternativeTitleBehaviorMarker)
def alternative_title(obj):
    # get configured alternative language
    registry = getUtility(IRegistry)
    reg_proxy = registry.forInterface(IRepositoryFolderRecords)
    try:
        return obj.Title(language=reg_proxy.alternative_language_code)
    except TypeError:
        LOG.error('Object with IAlternativeTitleBehavior has no support for '
                  'Title(language="%s"). %s' %
                  (reg_proxy.alternative_language_code, str(obj)))
        return obj.Title()
grok.global_adapter(alternative_title, name='alternative_title')


@indexer(Interface)
def alternative_title_fallback(obj):
    return ''
grok.global_adapter(alternative_title_fallback, name='alternative_title')
