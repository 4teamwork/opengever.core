from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.testing import SolrIntegrationTestCase


class TestContentsReorderedHandler(SolrIntegrationTestCase):

    @browsing
    def test_reindex_getObjPositionInParent_if_reordering_contents_through_folder_contents(self, browser):
        self.login(self.manager, browser=browser)

        view = u'/@solrsearch?fl=getObjPositionInParent&depth=1&fq=object_provides:{}'.format(
            ITaskTemplate.__identifier__)

        tasktemplate_1 = self.tasktemplate
        tasktemplate_2 = create(Builder('tasktemplate').within(self.tasktemplatefolder))
        self.commit_solr()

        browser.open(self.tasktemplatefolder.absolute_url(), view=view,
                     method='GET', headers=self.api_headers)

        self.assertItemsEqual([
            {u'UID': tasktemplate_1.UID(),
             u'getObjPositionInParent': 0},
            {u'UID': tasktemplate_2.UID(),
             u'getObjPositionInParent': 1},
            ], browser.json["items"])

        # 'folder_moveitem' is a skins python script which will be used if ordering
        # through the contents-tab provided by plone.
        self.tasktemplatefolder.unrestrictedTraverse('folder_moveitem')(tasktemplate_1.id, 1)
        self.commit_solr()

        browser.open(self.tasktemplatefolder.absolute_url(), view=view,
                     method='GET', headers=self.api_headers)

        self.assertItemsEqual([
            {u'UID': tasktemplate_1.UID(),
             u'getObjPositionInParent': 1},
            {u'UID': tasktemplate_2.UID(),
             u'getObjPositionInParent': 0},
            ], browser.json["items"])
