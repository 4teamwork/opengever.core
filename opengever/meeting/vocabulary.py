from five import grok
from opengever.meeting.service import meeting_service
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class ReferenceFormatterVocabulary(grok.GlobalUtility):
    grok.provides(IVocabularyFactory)
    grok.name('opengever.meeting.CommissionVocabulary')

    def __call__(self, context):
        terms = []

        for commission in meeting_service().all_commissions():
            terms.append(SimpleTerm(value=commission,
                                    token=commission.commission_id,
                                    title=commission.title))
        return SimpleVocabulary(terms)
