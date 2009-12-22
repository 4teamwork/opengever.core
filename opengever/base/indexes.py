from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from zope.component import getMultiAdapter
from five import grok

@indexer(IDexterityContent)
def breadcrumb_titlesIndexer(obj):
    breadcrumbs_view = getMultiAdapter((obj, obj.REQUEST),
                                       name='breadcrumbs_view')
    return breadcrumbs_view.breadcrumbs()
grok.global_adapter(breadcrumb_titlesIndexer, name="breadcrumb_titles")
