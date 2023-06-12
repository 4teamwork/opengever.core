from collective import dexteritytextindexer
from opengever.base.interfaces import ISequenceNumber
from opengever.base.utils import unrestrictedPathToCatalogBrain
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplate
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from plone.indexer import indexer
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer


@indexer(IDossierTemplateMarker)
def DossierTemplateSubjectIndexer(obj):
    aobj = IDossierTemplate(obj)
    return aobj.keywords


@indexer(IDossierTemplateMarker)
def dossier_type(obj):
    return IDossierTemplate(obj).dossier_type


@implementer(dexteritytextindexer.IDynamicTextIndexExtender)
@adapter(IDossierTemplateMarker)
class DossierTemplateSearchableTextExtender(object):
    """Make dossier templates full text searchable."""

    def __init__(self, context):
        self.context = context

    def __call__(self):
        searchable = []
        # append some other attributes to the searchableText index
        # sequence_number
        seqNumb = getUtility(ISequenceNumber)
        searchable.append(str(seqNumb.get_number(self.context)))

        # comments
        comments = getattr(IDossierTemplate(self.context), 'comments', None)
        if comments:
            searchable.append(comments.encode('utf-8'))

        # keywords
        keywords = IDossierTemplate(self.context).keywords
        if keywords:
            searchable.extend(
                keyword.encode('utf-8') if isinstance(keyword, unicode)
                else keyword
                for keyword in keywords)

        return ' '.join(searchable)


@indexer(IDossierTemplateMarker)
def is_subdossier(obj):
    return obj.is_subdossier()


@indexer(IDossierTemplateMarker)
def related_items(obj):
    brains = [unrestrictedPathToCatalogBrain(rel.to_path)
              for rel in IDossierTemplate(obj).related_documents if not rel.isBroken()]
    return [brain.UID for brain in brains if brain]
