from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.testing import FunctionalTestCase
import email


class TestEmailNotification(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestEmailNotification, self).setUp()
        # setup mail
        Mailing(self.portal).set_up()

        create(Builder('ogds_user')
               .assign_to_org_units([self.org_unit])
               .having(userid='hugo.boss',
                       firstname='Hugo',
                       lastname='Boss',
                       email='hugo.boss@example.org'))

        create(Builder('ogds_user')
               .assign_to_org_units([self.org_unit])
               .having(userid='franz.michel',
                       firstname='Franz',
                       lastname='Michel',
                       email='hugo.boss@example.org'))

        create(Builder('watcher').having(user_id='hugo.boss'))

        self.dossier = create(Builder('dossier').titled(u'Dossier A'))

    def tearDown(self):
        super(TestEmailNotification, self).tearDown()
        Mailing(self.layer['portal']).tear_down()

    @browsing
    def test_subject_is_title(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task',
                      'Responsible': 'hugo.boss',
                      'Task Type': 'comment'})
        browser.css('#form-buttons-save').first.click()

        mail = email.message_from_string(Mailing(self.portal).pop())

        self.assertEquals('Test Task', mail.get('Subject'))

    @browsing
    def test_from_and_to_addresses(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task',
                      'Responsible': 'hugo.boss',
                      'Task Type': 'comment'})
        browser.css('#form-buttons-save').first.click()

        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals('hugo.boss@example.org', mail.get('To'))
        self.assertEquals('Test User <test@example.org>', mail.get('From'))

    @browsing
    def test_see_on_gever_is_linked_to_resolve_notification_view(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task',
                      'Responsible': 'hugo.boss',
                      'Task Type': 'comment'})
        browser.css('#form-buttons-save').first.click()

        mail = email.message_from_string(Mailing(self.portal).pop())
        html_part = mail.get_payload()[0].as_string()

        # TODO: better assertion ...
        expected = '<a href=3D"http://nohost/plone/@@resolve_notification?notification_id=\n=3D1">View in GEVER</a>'

        self.assertIn(expected, html_part)
