from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.tasktemplates.browser.trigger import get_datamanger_key
from plone import api
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class ActiveTasktemplatefoldersVocabulary(object):

    def __call__(self, context):
        terms = []
        for templatefolder in self.get_tasktemplatefolder():
            if templatefolder.getObject().is_subtasktemplatefolder():
                continue
            terms.append(SimpleTerm(value=templatefolder.UID,
                                    token=templatefolder.UID,
                                    title=templatefolder.Title))

        return SimpleVocabulary(terms)

    def get_tasktemplatefolder(self):
        return api.content.find(
            portal_type='opengever.tasktemplates.tasktemplatefolder',
            review_state='tasktemplatefolder-state-activ')


@implementer(IVocabularyFactory)
class TasktemplatesVocabulary(object):

    def __call__(self, context):
        terms = []
        tasktemplatefolder = self.get_selected_tasktemplatefolder(context)
        assert tasktemplatefolder, 'No selectd tasktemplatefolder'

        for template in self.get_tasktemplates(tasktemplatefolder):
            terms.append(SimpleTerm(value=template.UID,
                                    token=template.UID,
                                    title=template.Title))

        return SimpleVocabulary(terms)

    def get_selected_tasktemplatefolder(self, context):
        dm = getUtility(IWizardDataStorage)
        uid = dm.get(get_datamanger_key(context), 'tasktemplatefolder')
        return api.content.get(UID=uid)

    def get_tasktemplates(self, tasktemplatefolder):
        return api.content.find(
            context=tasktemplatefolder,
            portal_type='opengever.tasktemplates.tasktemplate',
            sort_on='getObjPositionInParent'
            )
