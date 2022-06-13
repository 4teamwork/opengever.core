from opengever.dossier.behaviors.filing import IFilingNumberMarker
from opengever.dossier.interfaces import IDossierArchiver
from plone.indexer import indexer


@indexer(IFilingNumberMarker)
def filing_no(obj):
    """filing number indexer"""
    return IDossierArchiver(obj).get_indexer_value()


@indexer(IFilingNumberMarker)
def searchable_filing_no(obj):
    """Searchable filing number indexer"""
    return IDossierArchiver(obj).get_indexer_value(searchable=True)
