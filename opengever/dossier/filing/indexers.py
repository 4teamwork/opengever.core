from opengever.dossier.interfaces import IDossierArchiver
from five import grok
from opengever.dossier.behaviors.filing import IFilingNumberMarker
from plone.indexer import indexer


@indexer(IFilingNumberMarker)
def filing_no(obj):
    """filing number indexer"""
    return IDossierArchiver(obj).get_indexer_value()

grok.global_adapter(filing_no, name="filing_no")


@indexer(IFilingNumberMarker)
def searchable_filing_no(obj):
    """Searchable filing number indexer"""
    return IDossierArchiver(obj).get_indexer_value(searchable=True)

grok.global_adapter(searchable_filing_no, name="searchable_filing_no")
