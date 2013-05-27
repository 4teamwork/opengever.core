from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import set_current_client_id
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestLocalRolesSetter(FunctionalTestCase):

    def test_responsible_has_local_editor_role_on_task_when_is_added(self):
        task = Builder('task').having(responsible='hugo.boss').create()

        self.assertEquals(
            ('Editor', ), task.get_local_roles_for_userid('hugo.boss'))

    def test_new_responsible_has_local_editor_role_on_task_when_is_changed(self):
        task = Builder('task').having(responsible='hugo.boss').create()

        task.responsible = 'james.bond'
        notify(ObjectModifiedEvent(task))

        self.assertEquals(
            ('Editor', ), task.get_local_roles_for_userid('james.bond'))

    def test_dont_remove_editor_role_when_responsible_is_changed(self):
        task = Builder('task').having(responsible='hugo.boss').create()

        task.responsible = 'james.bond'
        notify(ObjectModifiedEvent(task))

        self.assertEquals(
            ('Editor', ), task.get_local_roles_for_userid('hugo.boss'))

    def test_responsible_has_reader_role_on_related_items_when_task_is_added(self):
        document = Builder('document').create()
        Builder('task').having(
            responsible='hugo.boss').relate_to(document).create()

        self.assertEquals(
            ('Reader', ), document.get_local_roles_for_userid('hugo.boss'))

    def test_responsible_has_reader_role_on_related_items_when_responsible_is_changed(self):
        document = Builder('document').create()
        task = Builder('task').having(
            responsible='hugo.boss').relate_to(document).create()

        task.responsible = 'james.bond'
        notify(ObjectModifiedEvent(task))

        self.assertEquals(
            ('Reader', ),
            document.get_local_roles_for_userid('james.bond'))

    def test_responsible_of_a_bidirectional_by_ref_task_has_reader_and_editor_role_on_related_items(self):
        document = Builder('document').create()
        Builder('task').bidirectional_by_reference().\
            having(responsible='hugo.boss').relate_to(document).create()

        self.assertEquals(
            ('Editor', 'Reader', ), document.get_local_roles_for_userid('hugo.boss'))

    def test_responsible_has_contributor_role_on_distinct_parent_when_task_is_added(self):
        dossier = Builder('dossier').create()
        Builder('task').within(
            dossier).having(responsible='hugo.boss').create()

        self.assertEquals(
            ('Contributor', ),
            dossier.get_local_roles_for_userid('hugo.boss'))

    def test_responsible_has_contributor_role_on_distinct_parent_when_task_is_updated(self):
        dossier = Builder('dossier').create()
        task = Builder('task').within(
            dossier).having(responsible='hugo.boss').create()

        task.responsible = 'james.bond'
        notify(ObjectModifiedEvent(task))

        self.assertEquals(
            ('Contributor', ),
            dossier.get_local_roles_for_userid('james.bond'))

    def test_inbox_group_of_the_responsible_client_has_the_same_localroles_like_the_responsible(self):
        create_client(clientid="client1",
                      inbox_group='client1_inbox_users')
        set_current_client_id(self.portal)

        dossier = Builder('dossier').create()
        document = Builder('document').create()
        task = Builder('task').within(dossier).relate_to(
            document).having(
                responsible='hugo.boss',
                responsible_client='client1').create()

        self.assertEquals(
            ('Editor', ),
            task.get_local_roles_for_userid('client1_inbox_users'))
        self.assertEquals(
            ('Reader', ),
            document.get_local_roles_for_userid('client1_inbox_users'))
        self.assertEquals(
            ('Contributor', ),
            dossier.get_local_roles_for_userid('client1_inbox_users'))

    def test_use_inbox_group_when_inbox_is_responsible(self):
        create_client(clientid="client1", inbox_group='client1_inbox_users')
        set_current_client_id(self.portal)
        task = Builder('task').having(responsible='inbox:client1').create()

        self.assertEquals(
            ('Editor', ),
            task.get_local_roles_for_userid('client1_inbox_users'))

        self.assertEquals(
            (), task.get_local_roles_for_userid('inbox:client1'))
