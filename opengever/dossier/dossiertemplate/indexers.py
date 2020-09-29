from opengever.dossier.dossiertemplate.behaviors import IDossierTemplate
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.dossier.indexers import SearchableTextExtender
from plone.indexer import indexer
from zope.component import adapter


@indexer(IDossierTemplateMarker)
def DossierTemplateSubjectIndexer(obj):
    aobj = IDossierTemplate(obj)
    return aobj.keywords


@adapter(IDossierTemplateMarker)
class DossierTemplateSearchableTextExtender(SearchableTextExtender):
    """Make dossier templates full text searchable."""


@indexer(IDossierTemplateMarker)
def is_subdossier(obj):
    return obj.is_subdossier()
