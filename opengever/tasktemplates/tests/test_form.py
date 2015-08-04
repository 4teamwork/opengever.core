from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.testing import FunctionalTestCase


class TestAddTaskTemplateForm(FunctionalTestCase):

    def setUp(self):
        super(TestAddTaskTemplateForm, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.templatedossier = create(Builder('templatedossier'))

    @browsing
    def test_redirects_back_and_show_statusmessage_when_no_active_tasktemplatefolder_exists(self, browser):
        tasktemplatefolder = create(Builder('tasktemplatefolder'))

        browser.login().open(self.dossier, view='add-tasktemplate')
        self.assertEquals(self.dossier.absolute_url(), browser.url)
        self.assertEquals(
            ['Currently there are no activetask template folders registered.'],
            error_messages())

    @browsing
    def test_stay_on_view_if_active_tasktemplatefolders_exists(self, browser):
        tasktemplatefolder = create(Builder('tasktemplatefolder')
                                    .in_state('tasktemplatefolder-state-active'))

        browser.login().open(self.dossier, view='add-tasktemplate')
        self.assertEquals(
            '{}/add-tasktemplate'.format(self.dossier.absolute_url()),
            browser.url)
        self.assertEquals([], error_messages())
