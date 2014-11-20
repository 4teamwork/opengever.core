from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import create_plone_user
from opengever.testing import FunctionalTestCase
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
import transaction


class TestMailWorkflow(FunctionalTestCase):

    def change_user(self):
        create_plone_user(self.portal, 'hugo.boss')
        self.login(user_id='hugo.boss')
        setRoles(self.portal, 'hugo.boss', ['Contributor'])
        transaction.commit()

    def test_mail_active_state_is_initial_state(self):
        mail = create(Builder('mail').with_dummy_message())
        self.assertEquals('mail-state-active', api.content.get_state(obj=mail))

    def test_mail_can_be_removed_with_remove_gever_content_permission(self):
        mail = create(Builder('mail'))
        self.grant('Editor')
        api.content.transition(obj=mail,
                               transition='mail-transition-remove')
        self.assertEquals('mail-state-removed', api.content.get_state(obj=mail))

    def test_mail_cant_be_removed_without_remove_gever_content_permission(self):
        mail = create(Builder('mail'))
        self.change_user()
        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=mail, transition='mail-transition-remove')

    def test_mail_can_only_be_restored_with_manage_portal_permission(self):
        mail = create(Builder('mail').in_state('mail-state-removed'))

        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=mail,
                                   transition='mail-transition-restore')

        self.grant('Manager')
        api.content.transition(obj=mail,
                               transition='mail-transition-restore')

        self.assertEquals('mail-state-active',
                          api.content.get_state(obj=mail))
