from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.interfaces import IBaseCustodyPeriods
from opengever.base.interfaces import IRetentionPeriodRegister
from opengever.testing import IntegrationTestCase
from plone import api
from plone.dexterity.utils import createContentInContainer
import json


def set_retention_period_restricted(value):
    api.portal.set_registry_record(
        'is_restricted', value, interface=IRetentionPeriodRegister)


class TestCustodyPeriodDefault(IntegrationTestCase):

    def setUp(self):
        super(TestCustodyPeriodDefault, self).setUp()
        self.field = ILifeCycle['custody_period']

    def get_custody_period(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_custody_period(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    def get_fti(self, portal_type):
        types_tool = api.portal.get_tool('portal_types')
        return types_tool[portal_type]

    @browsing
    def test_custody_period_default(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.repository_root)
        factoriesmenu.add(u'Repository Folder')
        browser.fill({'Title (German)': 'My Repofolder',
                      'Title (English)': 'My Repofolder'}).save()

        self.assertEqual(
            30,
            self.get_custody_period(browser.context))

    @browsing
    def test_custody_period_acquired_default(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder)
        self.set_custody_period(self.leaf_repofolder, 100)

        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        self.assertEqual(
            100,
            self.get_custody_period(browser.context))

    @browsing
    def test_intermediate_folder_doesnt_break_default_aq(self, browser):
        self.login(self.regular_user, browser=browser)

        # An intermediate folderish object that doesn't have the respective
        # field shouldn't break acquisition of the default
        self.set_custody_period(self.leaf_repofolder, 100)

        fti = self.get_fti('opengever.repository.repositoryfolder')
        fti.allowed_content_types = fti.allowed_content_types + ('Dummy',)

        dummy = createContentInContainer(self.leaf_repofolder, 'Dummy')
        browser.open(dummy)

        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_custody_period(dossier)
        self.assertEqual(100, value)


class TestCustodyPeriodVocabulary(IntegrationTestCase):

    def setUp(self):
        super(TestCustodyPeriodVocabulary, self).setUp()
        self.field = ILifeCycle['custody_period']

    def get_custody_period(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_custody_period(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_custody_period_choices_configurable_via_registry(self, browser):
        self.login(self.regular_user, browser=browser)

        # Note: The static fallback default (30) needs to be part of this
        # value range for the default to validate
        api.portal.set_registry_record(
            'custody_periods', interface=IBaseCustodyPeriods,
            value=[u'1', u'2', u'3', u'30', u'99']
        )
        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        form_field = browser.find('Regular safeguard period (years)')

        self.assertEqual([u'1', u'2', u'3', u'30', u'99'], form_field.options_values)

    @browsing
    def test_custody_period_default_choices(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.repository_root)
        factoriesmenu.add(u'Repository Folder')
        form_field = browser.find('Regular safeguard period (years)')
        self.assertEqual(
            ['0', '30', '100', '150'],
            form_field.options_values)

    @browsing
    def test_invalid_acquired_value_falls_back_to_all_choices(self, browser):
        self.login(self.administrator, browser=browser)

        # If vocab is supposed to be restricted, but we find an invalid value
        # via acquisition, the vocab should fall back to offering all choices
        invalid_value = 7
        self.set_custody_period(self.branch_repofolder, invalid_value)
        self.set_custody_period(self.leaf_repofolder, invalid_value)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Regular safeguard period (years)')
        self.assertEqual(
            ['0', '30', '100', '150'],
            form_field.options_values)

    @browsing
    def test_falsy_acquisition_value_falls_back_to_all_choices(self, browser):
        self.login(self.administrator, browser=browser)

        # If vocab is supposed to be restricted, but we find a  value via
        # acquisition that is falsy, the vocab should offer all choices
        # XXX: This probably should check for None instead of falsyness
        falsy_value = 0
        self.set_custody_period(self.leaf_repofolder, falsy_value)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Regular safeguard period (years)')
        self.assertEqual(
            ['0', '30', '100', '150'],
            form_field.options_values)

    @browsing
    def test_vocab_is_not_restricted_by_aq_value(self, browser):
        self.login(self.administrator, browser=browser)

        self.set_custody_period(self.leaf_repofolder, 100)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Regular safeguard period (years)')
        self.assertSetEqual(
            set(['0', '30', '100', '150']),
            set(form_field.options_values))

    @browsing
    def test_acquired_value_is_suggested_as_default(self, browser):
        self.login(self.administrator, browser=browser)

        self.set_custody_period(self.leaf_repofolder, 100)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Regular safeguard period (years)')

        self.assertEqual('100', form_field.value)


class TestCustodyPeriodPropagation(IntegrationTestCase):

    def setUp(self):
        super(TestCustodyPeriodPropagation, self).setUp()
        self.field = ILifeCycle['custody_period']

    def get_custody_period(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_custody_period(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_change_does_not_propagate_to_children(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_custody_period(dossier)
        # Dossier should have default custody period
        self.assertEqual(30, value)

        browser.open(self.leaf_repofolder, view='edit')
        # Increase custody period
        browser.fill({'Regular safeguard period (years)': '100'}).save()

        value = self.get_custody_period(dossier)
        self.assertEqual(30, value)


class TestRetentionPeriodDefault(IntegrationTestCase):

    def setUp(self):
        super(TestRetentionPeriodDefault, self).setUp()
        self.field = ILifeCycle['retention_period']

    def get_retention_period(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_retention_period(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    def get_fti(self, portal_type):
        types_tool = api.portal.get_tool('portal_types')
        return types_tool[portal_type]

    @browsing
    def test_retention_period_default(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.repository_root)
        factoriesmenu.add(u'Repository Folder')
        browser.fill({'Title (German)': 'My Repofolder',
                      'Title (English)': 'My Repofolder'}).save()
        dossier = browser.context

        value = self.get_retention_period(dossier)
        self.assertEqual(5, value)

    @browsing
    def test_retention_period_acquired_default(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.leaf_repofolder)
        self.set_retention_period(self.leaf_repofolder, 15)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_retention_period(dossier)
        self.assertEqual(15, value)

    @browsing
    def test_intermediate_folder_doesnt_break_default_aq(self, browser):
        self.login(self.administrator, browser=browser)

        # An intermediate folderish object that doesn't have the respective
        # field shouldn't break acquisition of the default
        self.set_retention_period(self.leaf_repofolder, 15)

        fti = self.get_fti('opengever.repository.repositoryfolder')
        fti.allowed_content_types = fti.allowed_content_types + ('Dummy',)

        dummy = createContentInContainer(self.leaf_repofolder, 'Dummy')
        browser.open(dummy)

        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_retention_period(dossier)
        self.assertEqual(15, value)


class TestRetentionPeriodVocabulary(IntegrationTestCase):

    def setUp(self):
        super(TestRetentionPeriodVocabulary, self).setUp()
        self.field = ILifeCycle['retention_period']

    def get_retention_period(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_retention_period(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_retention_period_choices_configurable_via_registry(self, browser):
        self.login(self.administrator, browser=browser)

        # Note: The static fallback default (5) needs to be part of this
        # value range for the default to validate
        api.portal.set_registry_record(
            'retention_period', interface=IRetentionPeriodRegister,
            value=[u'1', u'2', u'3', u'4', u'5', u'99']
        )
        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        form_field = browser.find('Retention period (years)')

        self.assertEqual(
            [u'1', u'2', u'3', u'4', u'5', u'99'],
            form_field.options_values)

    @browsing
    def test_retention_period_default_choices_are_unrestricted(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        form_field = browser.find('Retention period (years)')
        self.assertEqual(
            ['5', '10', '15', '20', '25'],
            form_field.options_values)

    @browsing
    def test_choices_not_limited_by_aq_value(self, browser):
        self.login(self.administrator, browser=browser)

        all_choices = ['5', '10', '15', '20', '25']

        for value in all_choices:
            self.set_retention_period(self.leaf_repofolder, value)
            browser.open(self.leaf_repofolder)

            factoriesmenu.add(u'Business Case Dossier')
            form_field = browser.find('Retention period (years)')
            self.assertEqual(all_choices, form_field.options_values)

    @browsing
    def test_acquired_value_is_suggested_as_default(self, browser):
        self.login(self.administrator, browser=browser)

        self.set_retention_period(self.leaf_repofolder, 15)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Retention period (years)')

        self.assertEqual('15', form_field.value)
        # Default listed first
        self.assertEqual('15', form_field.options_values[0])


class TestRetentionPeriodPropagation(IntegrationTestCase):

    def setUp(self):
        super(TestRetentionPeriodPropagation, self).setUp()
        self.field = ILifeCycle['retention_period']

    def get_retention_period(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_retention_period(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_change_does_not_propagate_to_children(self, browser):
        self.login(self.administrator, browser=browser)

        # Start with a long retention period
        self.set_retention_period(self.branch_repofolder, 25)
        self.set_retention_period(self.leaf_repofolder, 25)

        self.assertEqual(25, self.get_retention_period(self.branch_repofolder))
        self.assertEqual(25, self.get_retention_period(self.leaf_repofolder))
        self.assertEqual(15, self.get_retention_period(self.dossier))
        self.assertEqual(15, self.get_retention_period(self.subdossier))

        # Reduce retention period
        browser.open(self.branch_repofolder, view='edit')
        browser.fill({'Retention period (years)': '5'}).save()

        # Reduced retention period does not propagate to dossier
        self.assertEqual(5, self.get_retention_period(self.branch_repofolder))
        self.assertEqual(25, self.get_retention_period(self.leaf_repofolder))
        self.assertEqual(15, self.get_retention_period(self.dossier))
        self.assertEqual(15, self.get_retention_period(self.subdossier))


class TestArchivalValueDefault(IntegrationTestCase):

    def setUp(self):
        super(TestArchivalValueDefault, self).setUp()
        self.field = ILifeCycle['archival_value']

    def get_archival_value(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_archival_value(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    def get_fti(self, portal_type):
        types_tool = api.portal.get_tool('portal_types')
        return types_tool[portal_type]

    @browsing
    def test_archival_value_default(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.repository_root)
        factoriesmenu.add(u'Repository Folder')
        browser.fill({'Title (German)': 'My Folder',
                      'Title (English)': 'My Folder'}).save()
        dossier = browser.context

        value = self.get_archival_value(dossier)
        self.assertEqual(u'unchecked', value)

    @browsing
    def test_archival_value_acquired_default(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.leaf_repofolder)
        self.set_archival_value(self.leaf_repofolder, u'archival worthy')
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_archival_value(dossier)
        self.assertEqual(u'archival worthy', value)

    @browsing
    def test_intermediate_folder_doesnt_break_default_aq(self, browser):
        self.login(self.administrator, browser=browser)

        # An intermediate folderish object that doesn't have the respective
        # field shouldn't break acquisition of the default
        self.set_archival_value(self.leaf_repofolder, u'archival worthy')

        fti = self.get_fti('opengever.repository.repositoryfolder')
        fti.allowed_content_types = fti.allowed_content_types + ('Dummy',)

        dummy = createContentInContainer(self.leaf_repofolder, 'Dummy')
        browser.open(dummy)

        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_archival_value(dossier)
        self.assertEqual(u'archival worthy', value)


class TestArchivalValueVocabulary(IntegrationTestCase):

    def setUp(self):
        super(TestArchivalValueVocabulary, self).setUp()
        self.field = ILifeCycle['archival_value']

    def get_archival_value(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_archival_value(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_archival_value_default_choices_are_unrestricted(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.repository_root)
        factoriesmenu.add(u'Repository Folder')
        form_field = browser.find('Archival value')
        self.assertEqual(
            ['unchecked',
             'prompt',
             'archival worthy',
             'not archival worthy',
             'archival worthy with sampling'],
            form_field.options_values)

    @browsing
    def test_vocab_is_not_restricted_by_aq_value(self, browser):
        self.login(self.administrator, browser=browser)

        self.set_archival_value(self.leaf_repofolder, u'prompt')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Archival value')
        self.assertSetEqual(
            set(['unchecked',
                 'prompt',
                 'archival worthy',
                 'not archival worthy',
                 'archival worthy with sampling']),
            set(form_field.options_values))

    @browsing
    def test_acquired_value_is_suggested_as_default(self, browser):
        self.login(self.administrator, browser=browser)

        self.set_archival_value(self.leaf_repofolder, u'prompt')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Archival value')

        self.assertEqual('prompt', form_field.value)


class TestDateOfSubmission(IntegrationTestCase):

    @browsing
    def test_is_only_visible_for_managers_on_add_form(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        self.assertIsNone(browser.forms['form'].find_field('Date of submission'))

        self.login(self.manager, browser=browser)
        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        self.assertIsNotNone(browser.forms['form'].find_field('Date of submission'))

    @browsing
    def test_is_only_visible_for_managers_on_edit_form(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.dossier, view='edit')
        self.assertIsNone(browser.forms['form'].find_field('Date of submission'))
        browser.css('#form-buttons-cancel').first.click()

        self.login(self.manager, browser=browser)
        browser.open(self.dossier, view='edit')
        self.assertIsNotNone(browser.forms['form'].find_field('Date of submission'))


class TestDateOfCassation(IntegrationTestCase):

    @browsing
    def test_is_only_visible_for_managers_on_add_form(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        self.assertIsNone(browser.forms['form'].find_field('Date of cassation'))

        self.login(self.manager, browser=browser)
        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        self.assertIsNotNone(browser.forms['form'].find_field('Date of cassation'))

    @browsing
    def test_is_only_visible_for_managers_on_edit_form(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.dossier, view='edit')
        self.assertIsNone(browser.forms['form'].find_field('Date of cassation'))
        browser.css('#form-buttons-cancel').first.click()

        self.login(self.manager, browser=browser)
        browser.open(self.dossier, view='edit')
        self.assertIsNotNone(browser.forms['form'].find_field('Date of cassation'))


class TestLifeCycleFieldsAreProtected(IntegrationTestCase):

    @browsing
    def test_fields_are_only_visible_on_add_form_if_permission_available(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        self.assertIsNotNone(browser.forms['form'].find_field('Retention period (years)'))
        self.assertIsNotNone(browser.forms['form'].find_field(
            'Comment about retention period assessment'))
        self.assertIsNotNone(browser.forms['form'].find_field('Archival value'))
        self.assertIsNotNone(browser.forms['form'].find_field(
            'Comment about archival value assessment'))
        self.assertIsNotNone(browser.forms['form'].find_field('Regular safeguard period (years)'))

        browser.css('#form-buttons-cancel').first.click()

        self.leaf_repofolder.manage_permission("Edit lifecycle and classification", roles=[])
        factoriesmenu.add(u'Business Case Dossier')
        self.assertIsNone(browser.forms['form'].find_field('Retention period (years)'))
        self.assertIsNone(browser.forms['form'].find_field(
            'Comment about retention period assessment'))
        self.assertIsNone(browser.forms['form'].find_field('Archival value'))
        self.assertIsNone(browser.forms['form'].find_field(
            'Comment about archival value assessment'))
        self.assertIsNone(browser.forms['form'].find_field('Regular safeguard period (years)'))

    @browsing
    def test_fields_are_only_visible_on_edit_form_if_permission_available(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, view='edit')
        self.assertIsNotNone(browser.forms['form'].find_field('Retention period (years)'))
        self.assertIsNotNone(browser.forms['form'].find_field(
            'Comment about retention period assessment'))
        self.assertIsNotNone(browser.forms['form'].find_field('Archival value'))
        self.assertIsNotNone(browser.forms['form'].find_field(
            'Comment about archival value assessment'))
        self.assertIsNotNone(browser.forms['form'].find_field('Regular safeguard period (years)'))

        browser.css('#form-buttons-cancel').first.click()

        self.leaf_repofolder.manage_permission("Edit lifecycle and classification", roles=[])
        browser.open(self.dossier, view='edit')
        self.assertIsNone(browser.forms['form'].find_field('Retention period (years)'))
        self.assertIsNone(browser.forms['form'].find_field(
            'Comment about retention period assessment'))
        self.assertIsNone(browser.forms['form'].find_field('Archival value'))
        self.assertIsNone(browser.forms['form'].find_field(
            'Comment about archival value assessment'))
        self.assertIsNone(browser.forms['form'].find_field('Regular safeguard period (years)'))

    @browsing
    def test_create_dossier_via_api_only_overwrites_lifecycle_fields_if_permission_available(self, browser):
        self.login(self.regular_user, browser)
        self.assertEqual(u'unchecked', ILifeCycle(self.leaf_repofolder).archival_value)
        self.assertEqual(30, ILifeCycle(self.leaf_repofolder).custody_period)
        self.assertEqual(5, ILifeCycle(self.leaf_repofolder).retention_period)

        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'archival_value': u'prompt',
            u'custody_period': 100,
            u'responsible': self.regular_user.id,
            u'retention_period': 10,
            u'title': u'Sanierung B\xe4rengraben 2016',
        }
        with self.observe_children(self.leaf_repofolder) as children:
            browser.open(self.leaf_repofolder, data=json.dumps(payload),
                         method='POST', headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        dossier = children['added'].pop()

        self.assertEqual(u'prompt', ILifeCycle(dossier).archival_value)
        self.assertEqual(100, ILifeCycle(dossier).custody_period)
        self.assertEqual(10, ILifeCycle(dossier).retention_period)

        self.leaf_repofolder.manage_permission("Edit lifecycle and classification", roles=[])
        with self.observe_children(self.leaf_repofolder) as children:
            browser.open(self.leaf_repofolder, data=json.dumps(payload),
                         method='POST', headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        dossier = children['added'].pop()

        self.assertEqual(u'unchecked', ILifeCycle(dossier).archival_value)
        self.assertEqual(30, ILifeCycle(dossier).custody_period)
        self.assertEqual(5, ILifeCycle(dossier).retention_period)

    @browsing
    def test_edit_dossier_via_api_overwrites_lifecycle_fields_if_permission_available(self, browser):
        self.login(self.regular_user, browser)
        self.assertEqual(u'unchecked', ILifeCycle(self.dossier).archival_value)
        self.assertEqual(30, ILifeCycle(self.dossier).custody_period)
        self.assertEqual(15, ILifeCycle(self.dossier).retention_period)

        payload = {
            u'archival_value': u'prompt',
            u'custody_period': 100,
            u'retention_period': 10,
        }
        browser.open(self.dossier, data=json.dumps(payload),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual(u'prompt', ILifeCycle(self.dossier).archival_value)
        self.assertEqual(100, ILifeCycle(self.dossier).custody_period)
        self.assertEqual(10, ILifeCycle(self.dossier).retention_period)

    @browsing
    def test_edit_dossier_via_api_does_not_overwrite_lifecycle_fields_if_permission_missing(self, browser):
        self.login(self.regular_user, browser)
        self.assertEqual(u'unchecked', ILifeCycle(self.dossier).archival_value)
        self.assertEqual(30, ILifeCycle(self.dossier).custody_period)
        self.assertEqual(15, ILifeCycle(self.dossier).retention_period)

        payload = {
            u'archival_value': u'prompt',
            u'custody_period': 100,
            u'retention_period': 10,
        }
        self.dossier.manage_permission("Edit lifecycle and classification", roles=[])
        browser.open(self.dossier, data=json.dumps(payload),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual(u'unchecked', ILifeCycle(self.dossier).archival_value)
        self.assertEqual(30, ILifeCycle(self.dossier).custody_period)
        self.assertEqual(15, ILifeCycle(self.dossier).retention_period)
