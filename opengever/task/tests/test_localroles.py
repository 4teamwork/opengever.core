from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestLocalRolesSetter(FunctionalTestCase):

    def setUp(self):
        super(TestLocalRolesSetter, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

    def test_responsible_has_local_editor_role_on_task_when_is_added(self):
        task = create(Builder('task').having(responsible='hugo.boss'))

        self.assertEquals(
            ('Editor', ), task.get_local_roles_for_userid('hugo.boss'))

    def test_new_responsible_has_local_editor_role_on_task_when_is_changed(self):
        task = create(Builder('task').having(responsible='hugo.boss'))

        task.responsible = 'james.bond'
        notify(ObjectModifiedEvent(task))

        self.assertEquals(
            ('Editor', ), task.get_local_roles_for_userid('james.bond'))

    def test_dont_remove_editor_role_when_responsible_is_changed(self):
        task = create(Builder('task').having(responsible='hugo.boss'))
        task.responsible = 'james.bond'
        notify(ObjectModifiedEvent(task))

        self.assertEquals(
            ('Editor', ), task.get_local_roles_for_userid('hugo.boss'))

    def test_responsible_has_reader_role_on_related_items_when_task_is_added(self):
        document = create(Builder('document'))
        create(Builder('task')
               .having(responsible='hugo.boss')
               .relate_to(document))

        self.assertEquals(
            ('Reader', ), document.get_local_roles_for_userid('hugo.boss'))

    def test_responsible_has_reader_role_on_related_items_when_responsible_is_changed(self):
        document = create(Builder('document'))
        task = create(Builder('task')
                      .having(responsible='hugo.boss')
                      .relate_to(document))

        task.responsible = 'james.bond'
        notify(ObjectModifiedEvent(task))

        self.assertEquals(
            ('Reader', ),
            document.get_local_roles_for_userid('james.bond'))

    def test_responsible_of_a_bidirectional_by_ref_task_has_reader_and_editor_role_on_related_items(self):
        document = create(Builder('document'))
        create(Builder('task')
               .bidirectional_by_reference()
               .having(responsible='hugo.boss')
               .relate_to(document))

        self.assertEquals(
            ('Editor', 'Reader', ), document.get_local_roles_for_userid('hugo.boss'))

    def test_responsible_has_contributor_role_on_distinct_parent_when_task_is_added(self):
        dossier = create(Builder('dossier'))
        create(Builder('task')
               .within(dossier)
               .having(responsible='hugo.boss'))

        self.assertEquals(
            ('Contributor', ),
            dossier.get_local_roles_for_userid('hugo.boss'))

    def test_responsible_has_contributor_role_on_distinct_parent_when_task_is_updated(self):
        dossier = create(Builder('dossier'))
        task = create(Builder('task')
                      .within(dossier).having(responsible='hugo.boss'))

        task.responsible = 'james.bond'
        notify(ObjectModifiedEvent(task))

        self.assertEquals(
            ('Contributor', ),
            dossier.get_local_roles_for_userid('james.bond'))

    def test_inbox_group_of_the_responsible_client_has_the_same_localroles_like_the_responsible_in_a_multiclient_setup(self):
        create_client(clientid="additional")

        dossier = create(Builder('dossier'))
        document = create(Builder('document'))
        task = create(Builder('task')
                      .within(dossier)
                      .relate_to(document)
                      .having(responsible='hugo.boss',
                              responsible_client='client1'))

        self.assertEquals(
            ('Editor', ),
            task.get_local_roles_for_userid('client1_inbox_users'))
        self.assertEquals(
            ('Reader', ),
            document.get_local_roles_for_userid('client1_inbox_users'))
        self.assertEquals(
            ('Contributor', ),
            dossier.get_local_roles_for_userid('client1_inbox_users'))

    def test_inbox_group_has_no_additional_localroles_in_a_oneclient_setup(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document'))
        task = create(Builder('task')
                      .within(dossier)
                      .relate_to(document)
                      .having(responsible='hugo.boss',
                              responsible_client='client1'))

        self.assertEquals(
            (),
            task.get_local_roles_for_userid('client1_inbox_users'))
        self.assertEquals(
            (),
            document.get_local_roles_for_userid('client1_inbox_users'))
        self.assertEquals(
            (),
            dossier.get_local_roles_for_userid('client1_inbox_users'))

    def test_use_inbox_group_when_inbox_is_responsible(self):
        dossier = create(Builder('dossier'))
        task = create(Builder('task')
                      .within(dossier)
                      .having(responsible='inbox:client1'))

        self.assertEquals(
            ('Editor', ),
            task.get_local_roles_for_userid('client1_inbox_users'))

        self.assertEquals(
            ('Contributor', ),
            dossier.get_local_roles_for_userid('client1_inbox_users'))

        self.assertEquals(
            (), task.get_local_roles_for_userid('inbox:client1'))
