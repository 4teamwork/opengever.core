from ftw.builder import Builder
from ftw.builder import create
from opengever.mail.mail import OGMail
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
        setRoles(self.portal, 'hugo.boss', ['Contributor', 'Editor', 'Reviewer', 'Publisher'])
        transaction.commit()

    def test_mail_active_state_is_initial_state(self):
        mail = create(Builder('mail').with_dummy_message())
        self.assertEquals(OGMail.active_state, api.content.get_state(obj=mail))

    def test_mail_can_be_removed_with_remove_gever_content_permission(self):
        self.grant('Manager')
        mail = create(Builder('mail').trashed())
        api.content.transition(obj=mail, transition='mail-transition-remove')

        self.assertEquals(OGMail.removed_state,
                          api.content.get_state(obj=mail))

    def test_mail_cant_be_removed_if_it_is_not_trashed(self):
        mail = create(Builder('mail'))
        self.grant('Manager')
        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=mail, transition='mail-transition-remove')

    def test_mail_cant_be_removed_without_remove_gever_content_permission(self):
        # Only manager has 'Delete GEVER content' permission by default
        self.grant('Manager')
        mail = create(Builder('mail').trashed())
        self.change_user()
        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=mail, transition='mail-transition-remove')

    def test_mail_can_only_be_restored_with_manage_portal_permission(self):
        mail = create(Builder('mail').removed())

        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=mail,
                                   transition='mail-transition-restore')

        self.grant('Manager')
        api.content.transition(obj=mail,
                               transition='mail-transition-restore')

        self.assertEquals(OGMail.active_state,
                          api.content.get_state(obj=mail))
