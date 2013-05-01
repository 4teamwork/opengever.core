from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.PortalFolder import PortalFolderBase
from five import grok
from zope.schema.interfaces import IVocabularyFactory
from zope.i18n import translate


class RestrictedAddableDossiersVocabularyFactory(grok.GlobalUtility):
    """A list of content types which are restricted addable on the context.
    Those types have the
    `opengever.dossier.behaviors.restricteddossier.IRestrictedDossier`
    behavior enabled and are defined as addable content types in the FTI of
    the current context.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.repository.RestrictedAddableDossiersVocabulary')

    marker_behavior = 'opengever.dossier.behaviors.restricteddossier.' + \
        'IRestrictedDossier'

    def __call__(self, context):
        # catch some bad contexts (such as KSS validator)
        try:
            context.portal_type
        except AttributeError:
            return []

        # get default allowed types, but not the allowed types directly from
        # the context because they may already be filtered.
        if not isinstance(context, PortalFolderBase):
            return []
        types = PortalFolderBase.allowedContentTypes(context)

        # find the dexterity FTIs using the IRestrictedDossier behavior
        restricted_types = filter(
            lambda fti: getattr(fti, 'behaviors') and
                self.marker_behavior in fti.behaviors, types)

        # create the terms
        terms = []
        for fti in restricted_types:
            title = translate(fti.title,
                              domain=fti.i18n_domain,
                              context=context.REQUEST)
            terms.append(SimpleVocabulary.createTerm(
                    fti.id, fti.id, title))

        # create the vocabulary
        return SimpleVocabulary(terms)
