from collective.vdexvocabulary.term import VdexTerm
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class RawDossierTypesGet(Service):
    """API Endpoint that returns the raw contents of the dossier_types VDEX
    vocabulary. They are returned

    - in unaltered order (even though orderSignificant may be False)
    - unfiltered (hidden terms are included)

    This is needed in order for the frontend to be able to map dossier types
    to colors in a deterministic way that is stable over time.

    Because dossier types are mapped to a fixed-length color palette, and
    types that have already been mapped to a color once MUST keep that color,
    we need to provide the frontend with a list of dossier types where
    historical terms keep their position, and new terms only ever are appended
    at the end.

    This endpoint facilitates this, together with the following rules for
    editing the dossier_types.vdex file:

    - New terms must only be appended at the end
    - Terms are never removed, but set to hidden instead (registry).
      They will then be omitted from the regular vocabularies / sources,
      which are elephant vocabs, but not this endpoint.
    - Renames are ok (if the type is supposed to keep its color)

    GET /@raw-dossier-types HTTP/1.1
    """

    def reply(self):
        vf = getUtility(IVocabularyFactory, name='opengever.dossier.dossier_types')
        lang_tool = api.portal.get_tool('portal_languages')
        lang = lang_tool.getPreferredLanguage()

        items = vf.getTerms(lang)
        terms = []

        for item in items:
            terms.append(
                VdexTerm(
                    item["key"],
                    item["key"],
                    item["value"],
                    item["description"],
                )
            )

        serializer = getMultiAdapter(
            (SimpleVocabulary(terms), self.request),
            interface=ISerializeToJson,
        )

        vocab_id = '/'.join([self.context.absolute_url(), '@raw-dossier-types'])
        return serializer(vocab_id)
