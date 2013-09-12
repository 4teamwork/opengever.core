from five import grok
from logging import getLogger
from plone.indexer import indexer
from zope.interface import Interface
from opengever.repository.behaviors.frenchtitle  import IFrenchTitleBehavior


LOG = getLogger('opengever.repository')

# FrenchTitleBehavior
@indexer(IFrenchTitleBehavior)
def german_title(obj):
    try:
        return obj.Title(language='de')
    except TypeError:
        LOG.error('Object with IFrenchTitleBehavior has no support for '
                  'Title(language="de"). %s' % str(obj))
        return obj.Title()
grok.global_adapter(german_title, name='Title')


@indexer(IFrenchTitleBehavior)
def french_title(obj):
    try:
        return obj.Title(language='fr')
    except TypeError:
        LOG.error('Object with IFrenchTitleBehavior has no support for '
                  'Title(language="fr"). %s' % str(obj))
        return obj.Title()
grok.global_adapter(french_title, name='title_fr')


@indexer(Interface)
def french_title_fallback(obj):
    return ''
grok.global_adapter(french_title_fallback, name='title_fr')
