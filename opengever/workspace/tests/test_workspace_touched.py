from datetime import datetime
from ftw.builder.builder import Builder
from ftw.builder.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.behaviors.touched import ITouched
from opengever.testing import SolrIntegrationTestCase
from plone import api


class TestWorkspaceTouched(SolrIntegrationTestCase):

    features = ('workspace',)

    @browsing
    def test_touched_date_is_set_correctly_on_new_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        with freeze(datetime(2020, 6, 12)):
            workspace = create(Builder("workspace")
                               .within(self.workspace_root))
            self.assertEqual("2020-06-12", str(ITouched(workspace).touched))

    @browsing
    def test_modifying_content_touches_the_workspaces_in_path(self, browser):
        self.login(self.workspace_admin, browser=browser)

        self.assertEqual("2016-08-31", str(ITouched(self.workspace).touched))

        with freeze(datetime(2020, 6, 12)):
            browser.open(self.workspace_folder_document, view="edit")
            browser.fill({u"Title": "Modified subdocument"}).save()
            self.assertEqual("2020-06-12", str(ITouched(self.workspace).touched))

    @browsing
    def test_adding_content_touches_the_workspaces_in_path(self, browser):
        self.login(self.workspace_admin, browser=browser)

        self.assertEqual("2016-08-31", str(ITouched(self.workspace).touched))

        with freeze(datetime(2020, 6, 12)):
            create(Builder('document').within(self.workspace_folder))
            self.assertEqual("2020-06-12", str(ITouched(self.workspace).touched))

    @browsing
    def test_deleting_content_touches_the_workspaces_in_path(self, browser):
        self.login(self.manager, browser=browser)

        self.assertEqual("2016-08-31", str(ITouched(self.workspace).touched))

        with freeze(datetime(2020, 6, 12)):
            api.content.delete(obj=self.workspace_folder_document)
            self.assertEqual("2020-06-12", str(ITouched(self.workspace).touched))

    @browsing
    def test_moving_content_touches_the_workspaces_in_path(self, browser):
        self.login(self.workspace_admin, browser=browser)
        new_workspace = create(Builder("workspace")
                               .within(self.workspace_root))
        self.assertEqual("2016-08-31", str(ITouched(self.workspace).touched))

        with freeze(datetime(2020, 6, 12)):
            api.content.move(source=self.workspace_folder_document, target=new_workspace)
            self.assertEqual("2020-06-12", str(ITouched(self.workspace).touched))
            self.assertEqual("2020-06-12", str(ITouched(new_workspace).touched))
