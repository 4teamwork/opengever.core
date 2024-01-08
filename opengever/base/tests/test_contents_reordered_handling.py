from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.document import IDocumentSchema
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.testing import SolrIntegrationTestCase
from opengever.workspace.interfaces import IToDoList
import json


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

    @browsing
    def test_reindex_getObjPositionInParent_if_reordering_tasktemplates_through_the_tabbed_view(self, browser):
        self.login(self.administrator, browser=browser)

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

        browser.open(self.tasktemplatefolder.absolute_url(), view="@@tabbed_view/reorder",
                     headers={'Content-Type': 'application/x-www-form-urlencoded'},
                     method="POST",
                     data={'new_order[]': [tasktemplate_2.id, tasktemplate_1.id]})
        self.commit_solr()

        browser.open(self.tasktemplatefolder.absolute_url(), view=view,
                     method='GET', headers=self.api_headers)

        self.assertItemsEqual([
            {u'UID': tasktemplate_1.UID(),
             u'getObjPositionInParent': 1},
            {u'UID': tasktemplate_2.UID(),
             u'getObjPositionInParent': 0},
            ], browser.json["items"])

    @browsing
    def test_reindex_getObjPositionInParent_if_reordering_documents_through_the_restapi(self, browser):
        self.login(self.administrator, browser=browser)

        view = u'/@solrsearch?fl=getObjPositionInParent&depth=1&fq=object_provides:{}'\
               u'&sort=getObjPositionInParent asc'.format(IDocumentSchema.__identifier__)

        doc_1 = self.document
        doc_2 = self.decided_proposal.load_model().excerpt_document.resolve_document()
        doc_3 = self.shadow_document

        browser.open(self.dossier.absolute_url(), view=view,
                     method='GET', headers=self.api_headers)

        self.assertItemsEqual(
            [
                {u'UID': doc_1.UID(), u'getObjPositionInParent': 0},
                {u'UID': doc_2.UID(), u'getObjPositionInParent': 9},
                {u'UID': doc_3.UID(), u'getObjPositionInParent': 15},
            ], browser.json["items"])

        new_order = {'ordering': {'obj_id': doc_2.id, 'delta': -9}}
        browser.open(self.dossier, data=json.dumps(new_order), method='PATCH', headers=self.api_headers)
        self.commit_solr()

        browser.open(self.dossier.absolute_url(), view=view, method='GET', headers=self.api_headers)
        self.assertItemsEqual(
            [
                {u'UID': doc_2.UID(), u'getObjPositionInParent': 0},
                {u'UID': doc_1.UID(), u'getObjPositionInParent': 1},
                {u'UID': doc_3.UID(), u'getObjPositionInParent': 15},
            ], browser.json["items"])

    @browsing
    def test_reindex_getObjPositionInParent_if_reordering_tasktemplates_through_the_restapi(self, browser):
        self.login(self.administrator, browser=browser)

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

        data = {'ordering': {'obj_id': tasktemplate_1.id, 'delta': 1}}

        browser.open(self.tasktemplatefolder, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)
        self.commit_solr()

        browser.open(self.tasktemplatefolder.absolute_url(), view=view,
                     method='GET', headers=self.api_headers)

        self.assertItemsEqual([
            {u'UID': tasktemplate_1.UID(),
             u'getObjPositionInParent': 1},
            {u'UID': tasktemplate_2.UID(),
             u'getObjPositionInParent': 0},
            ], browser.json["items"])

    @browsing
    def test_reindex_getObjPositionInParent_if_reordering_todos_through_the_restapi(self, browser):
        self.activate_feature('workspace')
        self.login(self.administrator, browser=browser)

        view = u'/@solrsearch?fl=getObjPositionInParent&depth=1'

        todo_1 = self.assigned_todo
        todo_2 = self.completed_todo

        browser.open(self.todolist_introduction.absolute_url(), view=view,
                     method='GET', headers=self.api_headers)

        self.assertItemsEqual([
            {u'UID': todo_1.UID(),
             u'getObjPositionInParent': 0},
            {u'UID': todo_2.UID(),
             u'getObjPositionInParent': 1},
            ], browser.json["items"])

        data = {'ordering': {'obj_id': todo_1.id, 'delta': 1}}

        browser.open(self.todolist_introduction, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)
        self.commit_solr()

        browser.open(self.todolist_introduction.absolute_url(), view=view,
                     method='GET', headers=self.api_headers)

        self.assertItemsEqual([
            {u'UID': todo_1.UID(),
             u'getObjPositionInParent': 1},
            {u'UID': todo_2.UID(),
             u'getObjPositionInParent': 0},
            ], browser.json["items"])

    @browsing
    def test_reindex_getObjPositionInParent_if_reordering_todolists_through_the_restapi(self, browser):
        self.activate_feature('workspace')
        self.login(self.administrator, browser=browser)

        view = u'/@solrsearch?fl=getObjPositionInParent&depth=1&fq=object_provides:{}'.format(
            IToDoList.__identifier__)

        todolist_1 = self.todolist_general
        todolist_2 = self.todolist_introduction

        browser.open(self.workspace.absolute_url(), view=view,
                     method='GET', headers=self.api_headers)

        self.assertItemsEqual([
            {u'UID': todolist_1.UID(),
             u'getObjPositionInParent': 4},
            {u'UID': todolist_2.UID(),
             u'getObjPositionInParent': 5},
            ], browser.json["items"])

        data = {'ordering': {'obj_id': todolist_1.id, 'delta': 1}}

        browser.open(self.workspace, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)
        self.commit_solr()

        browser.open(self.workspace.absolute_url(), view=view,
                     method='GET', headers=self.api_headers)

        self.assertItemsEqual([
            {u'UID': todolist_1.UID(),
             u'getObjPositionInParent': 5},
            {u'UID': todolist_2.UID(),
             u'getObjPositionInParent': 4},
            ], browser.json["items"])
