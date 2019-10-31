from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary
from opengever.task.reminder.model import REMINDER_TYPE_REGISTRY


@implementer(IVocabularyFactory)
class TaskReminderOptionsVocabulary(object):

    def __call__(self, context):
        terms = []
        options = REMINDER_TYPE_REGISTRY.values()
        for option in sorted(options, key=lambda x: x.sort_order):
            terms.append(SimpleTerm(
                option.option_type, title=option.option_title))

        return SimpleVocabulary(terms)
