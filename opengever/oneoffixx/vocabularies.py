from opengever.oneoffixx.interfaces import IOneoffixxSettings
from plone import api
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import json


@implementer(IVocabularyFactory)
class OneOffixxFileTypesVocabulary(object):

    def __call__(self, context):
        terms = []
        items = json.loads(
            api.portal.get_registry_record(
                interface=IOneoffixxSettings, name="filetype_tag_mapping"))

        for item in items:
            terms.append(
                SimpleTerm(value=item['tag'], token=item['tag'], title=item['label']))

        return SimpleVocabulary(terms)
