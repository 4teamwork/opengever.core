from datetime import date
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.dexterity import erroneous_fields
from opengever.activity.model import Activity
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.task.adapters import IResponseContainer
from opengever.task.adapters import Response
from opengever.task.interfaces import ITaskSettings
from opengever.task.task import ITask
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from z3c.relationfield.relation import RelationValue
from zope.component import createObject
from zope.component import getUtility
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds
import transaction


class TestTaskIntegration(FunctionalTestCase):
    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestTaskIntegration, self).setUp()
        self.portal.portal_types['opengever.task.task'].global_allow = True

    def test_adding(self):
        t1 = create(Builder('task').titled('Task 1'))
        self.failUnless(ITask.providedBy(t1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.task.task')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.task.task')
        schema = fti.lookupSchema()
        self.assertEquals(ITask, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.task.task')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(ITask.providedBy(new_object))

    def test_view(self):
        t1 = create(Builder('task').titled('Task 1'))
        view = t1.restrictedTraverse('@@tabbedview_view-overview')
        self.assertEquals([], view.get_sub_tasks())

        t2 = create(Builder('task')
                    .within(t1)
                    .titled('Task 2'))

        self.assertEquals([t2.get_sql_object()], view.get_sub_tasks())

    @browsing
    def test_task_title_length_is_validated_to_a_max_of_256(self, browser):
        dossier = create(Builder('dossier'))
        browser.login().open(dossier, view='++add++opengever.task.task')

        browser.fill({'Title': 257 * 'x',
                      'Task Type': 'To comment'
                      })

        # Fill Responible manually
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            self.get_org_unit().id() + ':' + TEST_USER_ID)
        browser.find('Save').click()

        self.assertEquals({u'Title': ['Value is too long']},
                          erroneous_fields())

        browser.fill({'Title': 256 * 'x'})

        # We need to fill it again, because of a known bug in lxml
        # https://github.com/4teamwork/ftw.testbrowser/pull/17
        # https://github.com/4teamwork/ftw.testbrowser/issues/53
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            self.get_org_unit().id() + ':' + TEST_USER_ID)

        browser.find('Save').click()
        self.assertTrue(len(dossier.objectValues()),
                        'Expect one item in dossier')

    @browsing
    def test_hide_date_of_completion_field_in_add_form(self, browser):
        dossier = create(Builder('dossier'))
        browser.login().open(dossier, view='++add++opengever.task.task')

        self.assertEqual(
            'hidden',
            browser.css('input#form-widgets-date_of_completion').first.type)

    @browsing
    def test_show_date_of_completion_field_in_edit_form(self, browser):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier).titled('Task 1'))

        browser.login().visit(task, view="edit")

        self.assertNotEqual(
            'hidden',
            browser.css('input#form-widgets-date_of_completion').first.type)

    def test_relateddocuments(self):
        # create document and append it to the relatedItems of the task
        doc3 = create(Builder("document").titled("a-testthree"))
        intids = getUtility(IIntIds)
        o_iid = intids.getId(doc3)

        t1 = create(Builder('task')
                    .titled('Task 1')
                    .having(relatedItems=[RelationValue(o_iid)]))

        doc1 = create(Builder("document").within(t1).titled("btestone"))
        doc2 = create(Builder("document").within(t1).titled("ctesttwo"))
        view = t1.restrictedTraverse('tabbedview_view-relateddocuments')
        results = [aa.Title for aa in view.table_source.build_query()]
        self.assertTrue(doc3.Title() in results)

        # check sorting
        view.request.set('sort', u'sortable_title')
        results = [aa.Title for aa in view.table_source.build_query()]
        self.assertTrue(results == [doc3.Title(), doc1.Title(), doc2.Title()])

        view.request.set('ACTUAL_URL', t1.absolute_url())
        self.failUnless(view())

    def test_addresponse(self):
        t1 = create(Builder('task').titled('Task 1'))
        res = Response("")
        container = IResponseContainer(t1)
        container.add(res)
        self.failUnless(res in container)

    @browsing
    def test_addresponse_fails_without_transition(self, browser):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier).titled('some task'))
        with browser.expect_http_error(reason='Bad Request'):
            browser.login().open(task, view='addresponse')

    def test_task_type_category(self):
        t1 = create(Builder('task').titled('Task 1'))
        t1.task_type = u'information'
        self.assertEquals(
            u'unidirectional_by_reference', t1.task_type_category)
        t1.task_type = u'approval'
        self.assertEquals(
            u'bidirectional_by_reference', t1.task_type_category)

    @browsing
    def test_task_with_invalid_unicode_character_charakter_in_text_is_displayed(self, browser):
        task = create(Builder('task')
                      .titled('Task 1')
                      .having(text=u'\uf04aHello Unicode Error Character!'))
        browser.login().open(task, view='tabbedview_view-overview')
        self.assertIn('Hello Unicode Error Character!', browser.contents)

    def test_task_date_subscriber(self):
        member = self.portal.restrictedTraverse('plone_portal_state').member()
        t1 = create(Builder('task')
                    .titled('Task 1')
                    .having(responsible=member.getId(),
                            issuer=member.getId()))

        wft = t1.portal_workflow

        self.failUnless(t1.expectedStartOfWork is None)
        wft.doActionFor(t1, 'task-transition-open-in-progress')

        self.failUnless(t1.expectedStartOfWork == date.today())

        self.failUnless(t1.date_of_completion is None)
        wft.doActionFor(t1, 'task-transition-in-progress-resolved')
        self.failUnless(t1.date_of_completion == date.today())

        wft.doActionFor(t1, 'task-transition-resolved-in-progress')
        self.failUnless(t1.date_of_completion is None)

        t2 = create(Builder('task')
                    .titled('Task 2')
                    .having(issuer=member.getId()))

        self.failUnless(t2.date_of_completion is None)
        wft.doActionFor(t2, 'task-transition-open-tested-and-closed')
        self.failUnless(t2.date_of_completion == date.today())

    def test_adding_a_subtask_add_response_on_main_task(self):
        intids = getUtility(IIntIds)
        maintask = create(Builder('task').titled('maintask'))
        subtask = create(Builder('task')
                         .within(maintask)
                         .titled('maintask'))

        response = IResponseContainer(maintask)[-1]
        self.assertEquals(intids.getId(subtask), response.added_object.to_id)
        self.assertEquals('transition-add-subtask', response.transition)

    def test_adding_a_subtask_via_remote_request_does_not_add_response_to_main_task(self):
        maintask = create(Builder('task').titled('maintask'))

        # all different remote requests should not
        # generate an response
        maintask.REQUEST.environ['X_OGDS_AC'] = 'hugo.boss'
        create(Builder('task').within(maintask).titled('subtask'))
        self.assertEquals(0, len(IResponseContainer(maintask)))

        maintask.REQUEST.environ['X_OGDS_AC'] = None
        maintask.REQUEST.environ['X_OGDS_AUID'] = 'org-unit-1'
        create(Builder('task').within(maintask).titled('subtask'))
        self.assertEquals(0, len(IResponseContainer(maintask)))

        maintask.REQUEST.environ['X_OGDS_AUID'] = None
        maintask.REQUEST.set('X-CREATING-SUCCESSOR', True)
        create(Builder('task').within(maintask).titled('subtask'))
        self.assertEquals(0, len(IResponseContainer(maintask)))

    def test_adding_a_document_add_response_on_main_task(self):
        intids = getUtility(IIntIds)
        maintask = create(Builder('task').titled('maintask'))
        document = create(Builder('document')
                          .within(maintask)
                          .titled('Letter to Peter'))

        response = IResponseContainer(maintask)[-1]
        self.assertEquals(intids.getId(document), response.added_object.to_id)
        self.assertEquals('transition-add-document', response.transition)

    @browsing
    def test_responsible_client_for_multiple_orgunits(self, browser):
        create(Builder('org_unit')
               .with_default_groups()
               .id('org-unit-2')
               .having(title='Org Unit 2',
                       admin_unit=self.admin_unit))

        dossier = create(Builder('dossier'))

        browser.login().visit(dossier)
        factoriesmenu.add('Task')

        browser.fill({'Title': 'Task title',
                      'Task Type': 'To comment'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            self.get_org_unit().id() + ':' + TEST_USER_ID)
        browser.find('Save').click()

        task = dossier.objectValues()[0]
        self.assertEquals(
            'org-unit-1',
            task.responsible_client,
            'The client should be stored after submitting the form')
        self.assertEquals(
            TEST_USER_ID,
            task.responsible,
            'The user should be stored after submitting the form')

    @browsing
    def test_create_a_task_for_every_selected_person_with_multiple_orgunits(self, browser):
        client2 = create(Builder('org_unit')
                         .with_default_groups()
                         .id('org-unit-2')
                         .having(title='Org Unit 2',
                                 admin_unit=self.admin_unit))
        user = create(Builder('ogds_user')
                      .assign_to_org_units([client2])
                      .having(userid='some.user'))

        dossier = create(Builder('dossier'))
        doc = create(Builder("document").titled("test-doc")
                                        .within(dossier))

        responsible_users = [
            self.get_org_unit().id() + ':' + TEST_USER_ID,
            client2.id() + ':' + user.userid
        ]

        browser.login().visit(dossier)
        factoriesmenu.add('Task')
        browser.fill({'Title': 'Task title',
                      'Task Type': 'To comment',
                      'Related Items': doc})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(responsible_users)

        browser.find('Save').click()

        tasks = filter(lambda item: ITask.providedBy(item),
                       dossier.objectValues())
        self.assertEquals(2, len(tasks), 'Expect 2 tasks')
        self.assertEquals(TEST_USER_ID, tasks[0].responsible)
        self.assertEquals('org-unit-1', tasks[0].responsible_client)
        self.assertEquals(user.userid, tasks[1].responsible)
        self.assertEquals('org-unit-2', tasks[1].responsible_client)

        activities = Activity.query.all()
        self.assertEquals(2, len(activities))
        self.assertEquals(u'task-added', activities[0].kind)
        self.assertEquals(TEST_USER_ID, activities[0].actor_id)
        self.assertEquals(u'task-added', activities[1].kind)
        self.assertEquals(TEST_USER_ID, activities[1].actor_id)

    @browsing
    def test_create_a_task_for_every_selected_person_with_one_orgunit(self, browser):
        user = create(Builder('ogds_user')
                      .assign_to_org_units([self.org_unit])
                      .having(userid='some.user'))

        dossier = create(Builder('dossier'))

        responsible_users = [
            self.get_org_unit().id() + ':' + TEST_USER_ID,
            self.get_org_unit().id() + ':' + user.userid
        ]

        browser.login().visit(dossier)
        factoriesmenu.add('Task')
        browser.fill({'Title': 'Task title',
                      'Task Type': 'To comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(responsible_users)

        browser.find('Save').click()

        tasks = dossier.objectValues()
        self.assertEquals(2, len(tasks), 'Expect 2 tasks')
        self.assertEquals(TEST_USER_ID, tasks[0].responsible)
        self.assertEquals('org-unit-1', tasks[0].responsible_client)
        self.assertEquals(user.userid, tasks[1].responsible)
        self.assertEquals('org-unit-1', tasks[1].responsible_client)

        activities = Activity.query.all()
        self.assertEquals(2, len(activities))
        self.assertEquals(u'task-added', activities[0].kind)
        self.assertEquals(TEST_USER_ID, activities[0].actor_id)
        self.assertEquals(u'task-added', activities[1].kind)
        self.assertEquals(TEST_USER_ID, activities[1].actor_id)


class TestDossierSequenceNumber(FunctionalTestCase):

    def test_if_task_is_inside_a_maindossier_is_maindossier_number(self):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))

        self.assertEquals(
            dossier.get_sequence_number(),
            task.get_dossier_sequence_number())

    def test_if_task_is_inside_a_subdossier_is_subdossiers_number(self):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))
        task = create(Builder('task').within(subdossier))

        self.assertEquals(
            subdossier.get_sequence_number(),
            task.get_dossier_sequence_number())

    def test_handles_multiple_levels_of_subdossier_correctly(self):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))
        subsubdossier = create(Builder('dossier').within(subdossier))
        task = create(Builder('task').within(subsubdossier))

        self.assertEquals(
            subsubdossier.get_sequence_number(),
            task.get_dossier_sequence_number())

    def test_its_inboxs_number_for_forwardings(self):
        inbox = create(Builder('inbox'))
        task = create(Builder('task').within(inbox))

        self.assertEquals(None, task.get_dossier_sequence_number())


class TestDeadlineDefaultValue(FunctionalTestCase):

    def setUp(self):
        super(TestDeadlineDefaultValue, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_deadline_is_today_plus_five_days_by_default(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test task',
                      'Task Type': 'comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            self.org_unit.id() + ':' + TEST_USER_ID)
        browser.css('#form-buttons-save').first.click()

        expected = date.today() + timedelta(days=5)
        self.assertEquals(expected, self.dossier.get('task-1').deadline)

    @browsing
    def test_deadline_use_registry_entry_to_calculate_timedelta(self, browser):
        registry = getUtility(IRegistry)
        registry.forInterface(ITaskSettings).deadline_timedelta = 12
        transaction.commit()

        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test task',
                      'Task Type': 'comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            self.org_unit.id() + ':' + TEST_USER_ID)

        browser.css('#form-buttons-save').first.click()

        expected = date.today() + timedelta(days=12)
        self.assertEquals(expected, self.dossier.get('task-1').deadline)


class TestTaskTypeTranslations(FunctionalTestCase):

    def setUp(self):
        super(TestTaskTypeTranslations, self).setUp()
        self.dossier = create(Builder('dossier'))
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.addSupportedLanguage('de-ch')
        lang_tool.setDefaultLanguage('de-ch')
        transaction.commit()

    @browsing
    def test_task_types_are_translated(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        task_type_widget = browser.forms['form'].find_widget('Auftragstyp')
        task_type_labels = task_type_widget.inputs_by_label.keys()
        self.assertEquals([
            'Zur Genehmigung',
            'Zur Stellungnahme',
            u'Zur Pr\xfcfung / Korrektur',
            'Zur direkten Erledigung',
            'Zum Bericht / Antrag',
            'Zur Kenntnisnahme'],
            task_type_labels)
