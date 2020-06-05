from ftw.testbrowser import browsing
from opengever.activity.model import Activity
from opengever.activity.model import Subscription
from opengever.testing import IntegrationTestCase
from opengever.testing.event_recorder import get_recorded_events
from opengever.testing.event_recorder import register_event_recorder
from requests_toolbelt.utils import formdata
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class TestFormFields(IntegrationTestCase):

    @browsing
    def test_date_of_completion_field_is_only_shown_in_edit_form(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        browser.open(self.dossier, view='++add++opengever.task.task')
        self.assertEqual(
            'hidden',
            browser.css('input#form-widgets-date_of_completion').first.type)

        # seq_subtask_1 is a task with state 'open' and allows editing
        browser.visit(self.seq_subtask_1, view="edit")
        self.assertNotEqual(
            'hidden',
            browser.css('input#form-widgets-date_of_completion').first.type)

    @browsing
    def test_informed_principals_is_only_shown_in_add_form_with_activity_enabled(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        browser.open(self.dossier, view='++add++opengever.task.task')
        self.assertEqual(0, len(browser.css('select#form-widgets-informed_principals')))

        browser.open(self.seq_subtask_1, view='edit')
        self.assertEqual(0, len(browser.css('select#form-widgets-informed_principals')))

        self.activate_feature('activity')
        browser.open(self.dossier, view='++add++opengever.task.task')
        self.assertEqual(1, len(browser.css('select#form-widgets-informed_principals')))

        browser.open(self.seq_subtask_1, view='edit')
        self.assertEqual(0, len(browser.css('select#form-widgets-informed_principals')))


class TestTaskAddForm(IntegrationTestCase):

    @browsing
    def test_add_form_does_not_list_shadow_documents_as_relatable(self, browser):
        """Dossier responsible has created the shadow document.

        This test ensures he does not get it offered as a relatable document on
        tasks.
        """
        self.login(self.dossier_responsible, browser)
        contenttree_url = '/'.join((
            self.dossier.absolute_url(),
            '++add++opengever.task.task',
            '++widget++form.widgets.relatedItems',
            '@@contenttree-fetch',
        ))
        browser.open(
            contenttree_url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=formdata.urlencode({'href': '/'.join(self.dossier.getPhysicalPath()), 'rel': 0}),
        )
        expected_documents = [
            '2015',
            '2016',
            '[No Subject]',
            u'Antrag f\xfcr Kreiselbau',
            u'Die B\xfcrgschaft',
            u'Diskr\xe4te Dinge',
            u'Initialvertrag f\xfcr Bearbeitung',
            u'Initialvertrag f\xfcr Bearbeitung',
            'Personaleintritt',
            u're: Diskr\xe4te Dinge',
            u'Vertr\xe4ge',
            u'Vertr\xe4gsentwurf',
            u'Vertragsentwurf \xdcberpr\xfcfen',
            u'Vertragsentw\xfcrfe 2018',
        ]
        self.assertEqual(expected_documents, browser.css('li').text)


class TestTaskEditForm(IntegrationTestCase):

    @browsing
    def test_edit_responsible_adds_reassign_response(self, browser):
        self.login(self.administrator, browser=browser)
        self.set_workflow_state('task-state-open', self.task)
        browser.open(self.task, view='edit')

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.find('Save').click()

        browser.open(self.task, view='tabbedview_view-overview')
        answer = browser.css('.answer')[0]
        self.assertEquals('answer reassign', answer.get('class'))
        self.assertEquals(
            [u'Reassigned from B\xe4rfuss K\xe4thi (kathi.barfuss) to K\xf6nig '
             u'J\xfcrgen (jurgen.konig) by Kohler Nicole (nicole.kohler)'],
            answer.css('h3').text)

    @browsing
    def test_edit_responsible_records_activity(self, browser):
        self.activate_feature('activity')
        self.login(self.administrator, browser=browser)
        self.set_workflow_state('task-state-open', self.task)

        browser.open(self.task, view='edit')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user.id)
        browser.find('Save').click()

        activity = Activity.query.order_by(Activity.created.desc()).first()
        self.assertEquals(u'task-transition-reassign', activity.kind)
        self.assertEquals(
            [(u'robert.ziegler', u'task_issuer'),
             (u'jurgen.konig', u'task_responsible')],
            [(sub.watcher.actorid, sub.role) for sub in Subscription.query.all()
             if sub.resource.int_id == self.task.int_id])

    @browsing
    def test_modify_event_is_fired_but_only_once(self, browser):
        register_event_recorder(IObjectModifiedEvent)

        self.login(self.administrator, browser=browser)
        self.set_workflow_state('task-state-open', self.task)
        browser.open(self.task, view='edit')

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user.id)
        browser.find('Save').click()

        events = get_recorded_events()
        self.assertEquals(1, len(events))
        self.assertEqual(self.task, events[0].object)
