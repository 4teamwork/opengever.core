from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.tasktemplates.vocabularies import ActiveTasktemplatefoldersVocabulary
from opengever.testing import IntegrationTestCase


class TestActiveTasktemplatefoldersVocabulary(IntegrationTestCase):

    @browsing
    def test_contains_only_active_tasktemplatefolders(self, browser):
        self.login(self.administrator, browser=browser)
        vocabulary = ActiveTasktemplatefoldersVocabulary()(None)
        self.assertIn(self.tasktemplatefolder.UID(), vocabulary)

        url = '{}/@workflow/tasktemplatefolder-transition-activ-inactiv'.format(
            self.tasktemplatefolder.absolute_url())
        browser.open(url, method='POST', headers=self.api_headers)
        vocabulary = ActiveTasktemplatefoldersVocabulary()(None)
        self.assertNotIn(self.tasktemplatefolder.UID(), vocabulary)

    @browsing
    def test_does_not_contain_subtasktemplatefolders(self, browser):
        self.activate_feature('tasktemplatefolder_nesting')
        self.login(self.administrator, browser=browser)

        browser.open(self.tasktemplatefolder)
        factoriesmenu.add(u'Task Template Folder')
        browser.fill({'Title': 'Baugesuch', 'Type': 'parallel'}).submit()
        subtasktemplatefolder = browser.context

        vocabulary = ActiveTasktemplatefoldersVocabulary()(None)
        self.assertIn(self.tasktemplatefolder.UID(), vocabulary)
        self.assertNotIn(subtasktemplatefolder.UID(), vocabulary)
