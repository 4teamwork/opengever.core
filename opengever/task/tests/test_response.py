from ftw.builder import Builder
from ftw.builder import create
from opengever.task.adapters import IResponseContainer
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
import transaction
import unittest2
import urllib


class TestResponse(FunctionalTestCase):

    use_browser=True

    def setUp(self):
        super(TestResponse, self).setUp()
        self.portal.portal_types['opengever.task.task'].global_allow = True

        create(Builder('admin_unit').as_current_admin_unit())

        test_user_1 = create(Builder('ogds_user')
               .having(userid=TEST_USER_ID, firstname='Test', lastname='User'))

        test_user_2 = create(Builder('ogds_user')
                             .having(userid='testuser2',
                                     firstname='Test',
                                     lastname='User2'))

        create(Builder('org_unit')
               .assign_users([test_user_1])
               .as_current_org_unit()
               .having(client_id='plone', title="Plone"))

        create(Builder('org_unit')
               .having(client_id='client2', title="Client 2")
               .assign_users([test_user_2])
               .assign_users([test_user_1], to_inbox=False))

        # create_plone_user(self.portal, 'testuser2')

        self.grant('Contributor', 'Editor')
        login(self.portal, TEST_USER_NAME)

        self.dossier = create(Builder("dossier"))

        self.task = create(Builder('task')
                           .within(self.dossier)
                           .having(title="Test task 1",
                                   issuer=TEST_USER_ID,
                                   text=u'',
                                   responsible='testuser2',
                                   responsible_client='client2',
                                   task_type="direct-execution"))

        self.successor = create(Builder('task')
                                .within(self.dossier)
                                .having(title="Test task 1",
                                        responsible='testuser2',
                                        issuer=TEST_USER_ID,
                                        text=u'',
                                        task_type="direct-execution",
                                        responsible_client='client2'))

        self.doc1 = create(Builder("document")
                           .within(self.dossier)
                           .titled("Doc 1"))
        self.doc2 = create(Builder("document")
                           .within(self.dossier)
                           .titled("Doc 2"))
        transaction.commit()

    # XXX This test should rework complety and convert
    # in to a functional test.
    # we skip them for now
    @unittest2.skip("Skip because complete refactoring is needed.")
    def test_response_view(self):
        # test added objects info
        add_simple_response(
            self.task, text=u'field', added_object=[self.doc1, self.doc2])

        # test field changes info
        add_simple_response(
            self.task, text=u'field',
            field_changes=(
                (ITask['responsible'], TEST_USER_ID),
                (ITask['responsible_client'], 'plone'),
                ),
            transition=u'task-transition-open-in-progress')

        # test successsor info
        successor_oguid = ISuccessorTaskController(self.successor).get_oguid()
        add_simple_response(self.task, successor_oguid=successor_oguid)

        transaction.commit()

        self.assertEquals(len(IResponseContainer(self.task)), 3)

        # test different responeses and their infos
        self.browser.open(
            '%s/tabbedview_view-overview' % self.task.absolute_url())

        # TODO: replace with OGBrowse API. What is it looking for?
        self.assertEquals(
            'Added successor task',
            self.browser.css('div.response-info div span.label')[0].plain_text())

        successor_info = """<span class="issueChange"><span class="wf-task-state-open"><a href="http://nohost/plone/dossier-1/task-2" target="_blank" title="[Plone] > dossier-1 > Test task 1"><span class="rollover-breadcrumb icon-task-remote-task">Test task 1</span></a>  <span class="discreet">(Client2 / <a href="http://nohost/plone/@@user-details/testuser2">User 2 Test (testuser2)</a>)</span></span></span>"""

        self.assertTrue(successor_info in self.browser.contents)

        responsible_container = self.browser.xpath("//div[@class='response-info']/div[descendant-or-self::*[contains(text(), 'label_responsible')]]")[0]
        links = responsible_container.xpath("./*/a")
        self.assertEquals(['User 2 Test (testuser2)', 'User Test (test_user_1_)'],
                          [l.text for l in links])
        self.assertEquals(['http://nohost/plone/@@user-details/testuser2',
                           'http://nohost/plone/@@user-details/test_user_1_'],
                          [l.attrib["href"] for l in links])

        documents = self.browser.css(".contenttype-opengever-document-document")
        self.assertEquals(['Doc 1', 'Doc 2'], [d.plain_text() for d in documents])
        self.assertEquals(['http://nohost/plone/dossier-1/document-1',
                           'http://nohost/plone/dossier-1/document-2'],
                          [d.attrib["href"] for d in documents])

        # edit and delete should not be possible
        self.assertEquals([], self.browser.css("input[type='submit']"))

    def test_add_form(self):
        data = {'form.widgets.transition':'task-transition-open-in-progress'}
        self.browser.open('%s/addresponse' % self.task.absolute_url(),
                          data=urllib.urlencode(data))

        self.assertEquals('Test task 1: task-transition-open-in-progress',
                          self.browser.locate(".documentFirstHeading").text)

        self.browser.fill_in("form.widgets.text", value="peter")
        self.browser.click("form.buttons.save")
        self.assertEquals(len(IResponseContainer(self.task)), 1)

    def test_add_form_with_related_items(self):
        self.browser.open('%s/addresponse' % self.task.absolute_url())

        self.browser.fill_in("form.widgets.relatedItems.widgets.query",
                             value=u"Doc 1")
        self.browser.click("form.widgets.relatedItems.buttons.search")
        self.browser.check("Doc 1")
        self.browser.click("form.buttons.save")

        self.assertEquals(len(IResponseContainer(self.task)), 1)
        self.assertEquals(self.task.relatedItems[0].to_object, self.doc1)
