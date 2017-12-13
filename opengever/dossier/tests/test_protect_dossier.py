from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from opengever.testing import IntegrationTestCase
from plone import api
from zope.component import getMultiAdapter
import json


class TestProtectDossier(IntegrationTestCase):

    def test_user_has_no_permission_if_not_dossier_manager(self):
        """ This test is related to the other test. We have to validate
        that the regular user is not allowed to protect dossiers by default.

        The problem is, that the permission-check will be cached very strong and it is
        painful to reset the cache (i.e. creating a new request, change user roles or
        change the path of the object.).
        """
        self.login(self.regular_user)

        self.assertFalse(
            api.user.has_permission('opengever.dossier: Protect dossier',
                                    obj=self.dossier))

    def test_user_has_dossier_protect_permission_if_it_has_dossier_manager_on_repo_root(self):
        self.login(self.regular_user)

        self.repository_root.manage_setLocalRoles(
            self.regular_user.getId(), ['DossierManager'])

        self.assertTrue(
            api.user.has_permission('opengever.dossier: Protect dossier',
                                    obj=self.dossier))

    def test_user_has_permission_if_dossier_manager_on_repo(self):
        self.login(self.regular_user)

        self.leaf_repofolder.manage_setLocalRoles(
            self.regular_user.getId(), ['DossierManager'])

        self.assertTrue(
            api.user.has_permission('opengever.dossier: Protect dossier',
                                    obj=self.dossier))

    def test_user_has_no_permission_to_protect_dossier_if_repo_folder_is_inactive(self):
        self.login(self.dossier_manager)

        self.assertTrue(
            api.user.has_permission('opengever.dossier: Protect dossier',
                                    obj=self.dossier))

        self.set_workflow_state(
            'repositoryfolder-state-inactive', self.leaf_repofolder)

        self.assertFalse(
            api.user.has_permission('opengever.dossier: Protect dossier',
                                    obj=self.dossier))

    @browsing
    def test_do_not_update_localroles_if_user_did_not_change_protection_fields(self, browser):
        self.login(self.dossier_manager, browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'})
        form = browser.find_form_by_field('Reading')
        form.find_widget('Reading and writing').fill([self.regular_user.getId()])
        browser.click_on('Save')
        new_dossier = browser.context
        new_dossier.manage_setLocalRoles('projekt_a', ['Contributor'])

        self.assert_local_roles(
            IProtectDossier(new_dossier).READING_AND_WRITING_ROLES,
            self.regular_user.getId(), new_dossier)

        self.assert_local_roles(['Contributor'], 'projekt_a', new_dossier)

        browser.open(new_dossier, view="@@edit")
        browser.click_on('Save')

        self.assert_local_roles(
            IProtectDossier(new_dossier).READING_AND_WRITING_ROLES,
            self.regular_user.getId(), new_dossier)

        self.assert_local_roles(['Contributor'], 'projekt_a', new_dossier)

    @browsing
    def test_update_localroles_if_user_has_changed_protection_fields(self, browser):
        self.login(self.dossier_manager, browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'})
        form = browser.find_form_by_field('Reading')
        form.find_widget('Reading and writing').fill(self.regular_user.getId())
        browser.click_on('Save')
        new_dossier = browser.context
        new_dossier.manage_setLocalRoles('projekt_a', ['Contributor'])

        self.assert_local_roles(
            IProtectDossier(new_dossier).READING_AND_WRITING_ROLES,
            self.regular_user.getId(), new_dossier)

        self.assert_local_roles(['Contributor'], 'projekt_a', new_dossier)

        browser.open(new_dossier, view="@@edit")
        browser.fill({'Title': 'My new Dossier'})
        form = browser.find_form_by_field('Reading')
        form.find_widget('Reading and writing').fill([])
        form.find_widget('Reading').fill([self.regular_user.getId()])
        browser.click_on('Save')

        self.assert_local_roles(
            IProtectDossier(new_dossier).READING_ROLES,
            self.regular_user.getId(), new_dossier)

        self.assert_local_roles([], 'projekt_a', new_dossier)

    @browsing
    def test_regular_user_cannot_see_protect_dossier_fields(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.dossier, view="@@edit")

        self.assertEqual(
            0, len(browser.css('select#form-widgets-IProtectDossier-reading')))

        self.assertEqual(
            0, len(browser.css('select#form-widgets-IProtectDossier-reading_and_writing')))

        self.assertNotIn('Protect', browser.css('fieldset legend').text)

    @browsing
    def test_dossier_manager_can_see_protect_dossier_fields(self, browser):
        self.login(self.dossier_manager, browser)

        browser.open(self.dossier, view="@@edit")

        self.assertEqual(
            1, len(browser.css('select#form-widgets-IProtectDossier-reading')))

        self.assertEqual(
            1, len(browser.css('select#form-widgets-IProtectDossier-reading_and_writing')))

        self.assertIn('Protect', browser.css('fieldset legend').text)

    @browsing
    def test_dossier_manager_can_set_protect_dossier_fields(self, browser):
        self.login(self.dossier_manager, browser)

        browser.open(self.dossier, view="@@edit")
        form = browser.find_form_by_field('Reading')
        form.find_widget('Reading').fill('projekt_a')
        form.find_widget('Reading and writing').fill('projekt_b')
        form.find_widget('Dossier manager').fill(self.dossier_manager.getId())
        browser.click_on('Save')

        self.assertEqual(['projekt_a'], IProtectDossier(self.dossier).reading)
        self.assertEqual(['projekt_b'], IProtectDossier(self.dossier).reading_and_writing)

    @browsing
    def test_current_user_is_default_dossier_manager(self, browser):
        self.login(self.dossier_manager, browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        field = browser.find('Dossier manager')
        selected_option = filter(lambda x: x.attrib.get('selected'),
                                 field.css('option'))[0]

        self.assertEqual(
            u'Fr\xfchling F\xe4ivel (faivel.fruhling)',
            selected_option.text)

        browser.fill({'Title': 'My Dossier'})
        browser.click_on('Save')

        self.assertEqual(
            self.dossier_manager.getId(),
            IProtectDossier(browser.context).dossier_manager)

    @browsing
    def test_add_dossier_will_enable_dossier_protection(self, browser):
        self.login(self.dossier_manager, browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'})
        form = browser.find_form_by_field('Reading')
        form.find_widget('Reading').fill(self.regular_user.getId())
        browser.click_on('Save')

        self.assert_local_roles(
            IProtectDossier(self.dossier).READING_ROLES,
            self.regular_user.getId(), browser.context)

    @browsing
    def test_edit_dossier_will_enable_dossier_protection(self, browser):
        self.login(self.dossier_manager, browser)

        browser.open(self.dossier, view="@@edit")
        form = browser.find_form_by_field('Reading')
        form.find_widget('Reading').fill(self.regular_user.getId())
        form.find_widget('Dossier manager').fill(self.dossier_manager.getId())
        browser.click_on('Save')

        self.assert_local_roles(
            IProtectDossier(self.dossier).READING_ROLES,
            self.regular_user.getId(), browser.context)

    def test_protect_dossier_will_disable_role_inheritance(self):
        self.login(self.dossier_manager)

        self.assertFalse(getattr(self.dossier, '__ac_local_roles_block__', False))

        dossier_protector = IProtectDossier(self.dossier)
        dossier_protector.reading = ['kathi.barfuss']
        dossier_protector.protect()

        self.assertTrue(getattr(self.dossier, '__ac_local_roles_block__', False))

        dossier_protector.reading = []
        dossier_protector.protect()

        self.assertFalse(getattr(self.dossier, '__ac_local_roles_block__', False))

    def test_protect_dossier_will_add_selected_reading_users_to_localroles(self):
        self.login(self.dossier_manager)

        dossier_protector = IProtectDossier(self.dossier)
        dossier_protector.reading = [self.regular_user.getId()]
        dossier_protector.protect()

        self.assert_local_roles(
            dossier_protector.READING_ROLES,
            self.regular_user.getId(), self.dossier)

    def test_protect_dossier_will_add_selected_reading_and_writing_users_to_localroles(self):
        self.login(self.dossier_manager)

        dossier_protector = IProtectDossier(self.dossier)
        dossier_protector.reading_and_writing = [self.regular_user.getId()]
        dossier_protector.protect()

        self.assert_local_roles(
            dossier_protector.READING_AND_WRITING_ROLES,
            self.regular_user.getId(), self.dossier)

    def test_full_dossier_protection_check(self):
        self.login(self.dossier_manager)

        dossier_protector = IProtectDossier(self.dossier)
        dossier_protector.reading = [self.regular_user.getId(), 'projekt_a']
        dossier_protector.reading_and_writing = [self.secretariat_user.getId(),
                                                 'projekt_b']
        dossier_protector.dossier_manager = self.dossier_manager.getId()
        dossier_protector.protect()

        self.assert_local_roles(
            dossier_protector.READING_ROLES,
            self.regular_user.getId(), self.dossier)

        self.assert_local_roles(
            dossier_protector.READING_ROLES,
            'projekt_a', self.dossier)

        self.assert_local_roles(
            dossier_protector.READING_AND_WRITING_ROLES,
            self.secretariat_user.getId(), self.dossier)

        self.assert_local_roles(
            dossier_protector.READING_AND_WRITING_ROLES,
            'projekt_b', self.dossier)

        self.assert_local_roles(
            dossier_protector.DOSSIER_MANAGER_ROLES,
            self.dossier_manager.getId(), self.dossier)

    def test_protect_dossier_wont_exclude_current_logged_in_user(self):
        self.login(self.dossier_manager)

        dossier_protector = IProtectDossier(self.dossier)
        dossier_protector.reading = [self.regular_user.getId()]
        dossier_protector.dossier_manager = self.dossier_manager.getId()
        dossier_protector.protect()

        self.assert_local_roles(
            IProtectDossier(self.dossier).DOSSIER_MANAGER_ROLES,
            self.dossier_manager.getId(), self.dossier)

    def test_reindex_object_security_on_dossier(self):
        self.login(self.dossier_manager)

        self.assertItemsEqual(
            ['Administrator', 'Contributor', 'Editor', 'Manager', 'Reader',
             'user:fa_users', 'user:{}'.format(self.regular_user.getId())],
            self.get_allowed_roles_and_users_for(self.dossier))

        dossier_protector = IProtectDossier(self.dossier)
        dossier_protector.reading = [self.regular_user.getId()]
        dossier_protector.reading_and_writing = []
        dossier_protector.dossier_manager = self.dossier_manager.getId()
        dossier_protector.protect()

        self.assertItemsEqual(
            ['Administrator', 'Contributor', 'Editor', 'Manager', 'Reader',
             'user:{}'.format(self.dossier_manager.getId()),
             'user:{}'.format(self.regular_user.getId())],
            self.get_allowed_roles_and_users_for(self.dossier))

    def test_check_protect_dossier_consistency_returns_no_messages_if_no_inconsistency(self):
        self.login(self.dossier_manager)

        dossier_protector = IProtectDossier(self.dossier)
        dossier_protector.reading = [self.regular_user.getId()]
        dossier_protector.protect()
        view = getMultiAdapter((self.dossier, self.request),
                               name="check_protect_dossier_consistency")

        self.assertIsNone(json.loads(view()).get('messages'))

    def test_check_protect_dossier_consistency_returns_error_msg_if_inconsistent(self):
        self.login(self.dossier_manager)

        dossier_protector = IProtectDossier(self.dossier)
        dossier_protector.reading = [self.regular_user.getId()]
        dossier_protector.protect()
        self.dossier.manage_setLocalRoles(self.regular_user.getId(), ['DossierManager'])
        view = getMultiAdapter((self.dossier, self.request),
                               name="check_protect_dossier_consistency")

        self.assertEqual(1, len(json.loads(view()).get('messages')))

