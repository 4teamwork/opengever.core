from opengever.dossier.templatefolder.form import get_templates
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory


@implementer(IVocabularyFactory)
class DocumentTemplatesVocabulary(object):

    def __call__(self, context):
        return get_templates(context)
