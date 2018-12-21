from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.interfaces import IBaseCustodyPeriods
from opengever.base.interfaces import IRetentionPeriodRegister
from opengever.testing import IntegrationTestCase
from plone import api
from plone.dexterity.utils import createContentInContainer


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
        factoriesmenu.add(u'RepositoryFolder')
        browser.fill({'Title': 'My Dossier'}).save()

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
        form_field = browser.find('Custody period (years)')

        # Restricted based on fallback default (30)
        self.assertEqual([u'30', u'99'], form_field.options_values)

    @browsing
    def test_custody_period_default_choices(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.repository_root)
        factoriesmenu.add(u'RepositoryFolder')
        form_field = browser.find('Custody period (years)')
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

        form_field = browser.find('Custody period (years)')
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

        form_field = browser.find('Custody period (years)')
        self.assertEqual(
            ['0', '30', '100', '150'],
            form_field.options_values)

    @browsing
    def test_aq_value_is_contained_in_choices_if_restricted(self, browser):
        self.login(self.administrator, browser=browser)

        self.set_custody_period(self.leaf_repofolder, 30)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Custody period (years)')
        self.assertIn('30', form_field.options_values)

    @browsing
    def test_vocab_is_restricted_if_indicated_by_aq_value(self, browser):
        self.login(self.administrator, browser=browser)

        self.set_custody_period(self.leaf_repofolder, 100)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Custody period (years)')
        self.assertSetEqual(
            set(['100', '150']),
            set(form_field.options_values))

    @browsing
    def test_acquired_value_is_suggested_as_default(self, browser):
        self.login(self.administrator, browser=browser)

        self.set_custody_period(self.leaf_repofolder, 100)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Custody period (years)')

        self.assertEqual('100', form_field.value)
        # Default listed first
        self.assertEqual('100', form_field.options_values[0])

    @browsing
    def test_restriction_works_in_edit_form(self, browser):
        self.login(self.administrator, browser=browser)

        self.set_custody_period(self.leaf_repofolder, 100)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()

        browser.click_on('Edit')
        form_field = browser.find('Custody period (years)')
        self.assertSetEqual(
            set(['100', '150']),
            set(form_field.options_values))


class TestCustodyPeriodPropagation(IntegrationTestCase):

    def setUp(self):
        super(TestCustodyPeriodPropagation, self).setUp()
        self.field = ILifeCycle['custody_period']

    def get_custody_period(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_custody_period(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_change_propagates_to_children(self, browser):
        self.login(self.administrator, browser=browser)

        # Start with a short custody period
        self.set_custody_period(self.leaf_repofolder, 30)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_custody_period(dossier)
        # Dossier should have inherited custody period from repofolder
        self.assertEqual(30, value)

        browser.open(self.leaf_repofolder, view='edit')
        # Increase custody period
        browser.fill({'Custody period (years)': '100'}).save()

        value = self.get_custody_period(dossier)
        # Increased custody period should have propagated to dossier
        self.assertEqual(100, value)

    @browsing
    def test_change_doesnt_propagate_if_old_value_still_valid(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({
            'Title': 'My Dossier',
            'Custody period (years)': '150'}).save()
        dossier = browser.context

        value = self.get_custody_period(dossier)
        self.assertEqual(150, value)

        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Custody period (years)': '30'}).save()

        value = self.get_custody_period(dossier)
        self.assertEqual(150, value)

    @browsing
    def test_propagation_is_depth_limited(self, browser):
        """Propagation of custody period is depth limited to 2 levels.
        Not sure why this was implemented this way, but here we test for it.
        """
        self.login(self.administrator, browser=browser)

        # Start with a short custody period
        self.set_custody_period(self.branch_repofolder, 30)
        repofolder2 = create(Builder('repository').within(self.branch_repofolder))
        repofolder3 = create(Builder('repository').within(repofolder2))

        browser.open(repofolder3)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_custody_period(dossier)
        # Dossier should have inherited custody period from repofolder2
        self.assertEqual(30, value)

        browser.open(self.branch_repofolder, view='edit')
        # Increase custody period on top level repofolder
        browser.fill({'Custody period (years)': '100'}).save()

        # Increased custody period should have propagated to repofolder2, but
        # not dossier (because of depth limitation)
        self.assertEqual(100, self.get_custody_period(repofolder2))
        self.assertEqual(30, self.get_custody_period(dossier))


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
        factoriesmenu.add(u'RepositoryFolder')
        browser.fill({'Title': 'My Repofolder'}).save()
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
    def test_choices_not_limited_by_parent_when_unrestricted(self, browser):
        self.login(self.administrator, browser=browser)

        # When is_restriced is False, choices shall not be limited by
        # an acquired value -  i.e., we always have the full set of choices
        set_retention_period_restricted(False)
        all_choices = ['5', '10', '15', '20', '25']

        for value in all_choices:
            self.set_retention_period(self.leaf_repofolder, value)
            browser.open(self.leaf_repofolder)

            factoriesmenu.add(u'Business Case Dossier')
            form_field = browser.find('Retention period (years)')
            self.assertEqual(all_choices, form_field.options_values)

    @browsing
    def test_invalid_acquired_value_falls_back_to_all_choices(self, browser):
        self.login(self.administrator, browser=browser)

        # If vocab is supposed to be restricted, but we find an invalid value
        # via acquisition, the vocab should fall back to offering all choices
        set_retention_period_restricted(True)

        invalid_value = 7
        self.set_retention_period(self.branch_repofolder, invalid_value)
        self.set_retention_period(self.leaf_repofolder, invalid_value)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Retention period (years)')
        self.assertEqual(
            ['5', '10', '15', '20', '25'],
            form_field.options_values)

    @browsing
    def test_falsy_acquisition_value_falls_back_to_all_choices(self, browser):
        # If vocab is supposed to be restricted, but we find a  value via
        # acquisition that is falsy, the vocab should offer all choices
        # XXX: This probably should check for None instead of falsyness
        self.login(self.administrator, browser=browser)

        set_retention_period_restricted(True)

        falsy_value = 0
        self.set_retention_period(self.branch_repofolder, falsy_value)
        self.set_retention_period(self.leaf_repofolder, falsy_value)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Retention period (years)')
        self.assertEqual(
            ['5', '10', '15', '20', '25'],
            form_field.options_values)

    @browsing
    def test_aq_value_is_contained_in_choices_if_restricted(self, browser):
        self.login(self.administrator, browser=browser)

        set_retention_period_restricted(True)

        self.set_retention_period(self.leaf_repofolder, 15)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Retention period (years)')
        self.assertIn('15', form_field.options_values)

    @browsing
    def test_vocab_is_restricted_if_indicated_by_aq_value(self, browser):
        self.login(self.administrator, browser=browser)

        set_retention_period_restricted(True)

        self.set_retention_period(self.leaf_repofolder, 15)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Retention period (years)')
        self.assertSetEqual(
            set(['5', '10', '15']),
            set(form_field.options_values))

    @browsing
    def test_acquired_value_is_suggested_as_default(self, browser):
        self.login(self.administrator, browser=browser)

        set_retention_period_restricted(True)

        self.set_retention_period(self.leaf_repofolder, 15)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Retention period (years)')

        self.assertEqual('15', form_field.value)
        # Default listed first
        self.assertEqual('15', form_field.options_values[0])

    @browsing
    def test_restriction_works_in_edit_form(self, browser):
        self.login(self.administrator, browser=browser)

        set_retention_period_restricted(True)

        self.set_retention_period(self.leaf_repofolder, 15)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()

        browser.click_on('Edit')
        form_field = browser.find('Retention period (years)')
        self.assertSetEqual(
            set(['5', '10', '15']),
            set(form_field.options_values))


class TestRetentionPeriodPropagation(IntegrationTestCase):

    def setUp(self):
        super(TestRetentionPeriodPropagation, self).setUp()
        self.field = ILifeCycle['retention_period']

    def get_retention_period(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_retention_period(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_change_propagates_to_children(self, browser):
        self.login(self.administrator, browser=browser)

        set_retention_period_restricted(True)

        # Start with a long retention period
        self.set_retention_period(self.branch_repofolder, 25)
        self.set_retention_period(self.leaf_repofolder, 25)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_retention_period(dossier)
        # Dossier should have inherited retention period from repofolder
        self.assertEqual(25, value)

        browser.open(self.leaf_repofolder, view='edit')
        # Reduce retention period
        browser.fill({'Retention period (years)': '15'}).save()

        value = self.get_retention_period(dossier)
        # Reduced retention period should have propagated to dossier
        self.assertEqual(15, value)

    @browsing
    def test_change_doesnt_propagate_if_old_value_still_valid(self, browser):
        self.login(self.administrator, browser=browser)

        set_retention_period_restricted(True)
        browser.open(self.leaf_repofolder)
        self.set_retention_period(self.branch_repofolder, 25)
        self.set_retention_period(self.leaf_repofolder, 25)

        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({
            'Title': 'My Dossier',
            'Retention period (years)': '5'}).save()
        dossier = browser.context

        value = self.get_retention_period(dossier)
        self.assertEqual(5, value)

        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Retention period (years)': '15'}).save()

        value = self.get_retention_period(dossier)
        self.assertEqual(5, value)

    @browsing
    def test_propagation_is_depth_limited(self, browser):
        """Propagation of retention period is depth limited to 2 levels.
        Not sure why this was implemented this way, but here we test for it.
        """
        self.login(self.administrator, browser=browser)

        set_retention_period_restricted(True)
        # Start with a long retention period
        self.set_retention_period(self.branch_repofolder, 25)
        repofolder2 = create(Builder('repository').within(self.branch_repofolder))
        repofolder3 = create(Builder('repository').within(repofolder2))

        browser.open(repofolder3)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_retention_period(dossier)
        # Dossier should have inherited retention period from repofolder2
        self.assertEqual(25, value)

        browser.open(self.branch_repofolder, view='edit')
        # Reduce retention period on top level repofolder
        browser.fill({'Retention period (years)': '15'}).save()

        # Reduced retention period should have propagated to repofolder2, but
        # not dossier (because of depth limitation)
        self.assertEqual(15, self.get_retention_period(repofolder2))
        self.assertEqual(25, self.get_retention_period(dossier))


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
        factoriesmenu.add(u'RepositoryFolder')
        browser.fill({'Title': 'My Folder'}).save()
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
        factoriesmenu.add(u'RepositoryFolder')
        form_field = browser.find('Archival value')
        self.assertEqual(
            ['unchecked',
             'prompt',
             'archival worthy',
             'not archival worthy',
             'archival worthy with sampling'],
            form_field.options_values)

    @browsing
    def test_invalid_acquired_value_falls_back_to_all_choices(self, browser):
        # If vocab is supposed to be restricted, but we find an invalid value
        # via acquisition, the vocab should fall back to offering all choices

        self.login(self.administrator, browser=browser)

        invalid_value = 7
        self.set_archival_value(self.branch_repofolder, invalid_value)
        self.set_archival_value(self.leaf_repofolder, invalid_value)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Archival value')
        self.assertEqual(
            ['unchecked',
             'prompt',
             'archival worthy',
             'not archival worthy',
             'archival worthy with sampling'],
            form_field.options_values)

    @browsing
    def test_falsy_acquisition_value_falls_back_to_all_choices(self, browser):
        # If vocab is supposed to be restricted, but we find a  value via
        # acquisition that is falsy, the vocab should offer all choices
        # XXX: This probably should check for None instead of falsyness
        self.login(self.administrator, browser=browser)

        falsy_value = 0
        self.set_archival_value(self.branch_repofolder, falsy_value)
        self.set_archival_value(self.leaf_repofolder, falsy_value)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Archival value')
        self.assertEqual([
            'unchecked',
            'prompt',
            'archival worthy',
            'not archival worthy',
            'archival worthy with sampling'],
            form_field.options_values)

    @browsing
    def test_aq_value_is_contained_in_choices_if_restricted(self, browser):
        self.login(self.administrator, browser=browser)

        self.set_archival_value(self.leaf_repofolder, u'archival worthy')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Archival value')
        self.assertIn(u'archival worthy', form_field.options_values)

    @browsing
    def test_vocab_is_restricted_if_indicated_by_aq_value(self, browser):
        self.login(self.administrator, browser=browser)

        self.set_archival_value(self.leaf_repofolder, u'prompt')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Archival value')
        self.assertSetEqual(
            set(['prompt',
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
        # Default listed first
        self.assertEqual('prompt', form_field.options_values[0])

    @browsing
    def test_restriction_works_in_edit_form(self, browser):
        self.login(self.administrator, browser=browser)

        self.set_archival_value(self.leaf_repofolder, u'prompt')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()

        browser.click_on('Edit')
        form_field = browser.find('Archival value')

        self.assertSetEqual(
            set(['archival worthy',
                 'prompt',
                 'archival worthy with sampling',
                 'not archival worthy']),
            set(form_field.options_values))


class TestArchivalValuePropagation(IntegrationTestCase):

    def setUp(self):
        super(TestArchivalValuePropagation, self).setUp()
        self.field = ILifeCycle['archival_value']

    def get_archival_value(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_archival_value(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_change_propagates_to_children(self, browser):
        self.login(self.administrator, browser=browser)

        # Start with a loose archival value
        self.set_archival_value(self.branch_repofolder, u'unchecked')
        self.set_archival_value(self.leaf_repofolder, u'unchecked')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_archival_value(dossier)
        # Dossier should have inherited archival value from repofolder
        self.assertEqual(u'unchecked', value)

        browser.open(self.leaf_repofolder, view='edit')
        # Make archival value more strict
        browser.fill({'Archival value': 'prompt'}).save()

        value = self.get_archival_value(dossier)
        # Stricter archival value should have propagated to dossier
        self.assertEqual(u'prompt', value)

    @browsing
    def test_change_doesnt_propagate_if_old_value_still_valid(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({
            'Title': 'My Dossier',
            'Archival value': 'prompt'}).save()
        dossier = browser.context

        value = self.get_archival_value(dossier)
        self.assertEqual('prompt', value)

        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Archival value': 'unchecked'}).save()

        value = self.get_archival_value(dossier)
        self.assertEqual('prompt', value)

    @browsing
    def test_propagation_is_depth_limited(self, browser):
        """Propagation of archival value is depth limited to 2 levels.
        Not sure why this was implemented this way, but here we test for it.
        """
        self.login(self.administrator, browser=browser)

        # Start with a loose archival value
        self.set_archival_value(self.branch_repofolder, u'unchecked')
        repofolder2 = create(Builder('repository').within(self.branch_repofolder))
        repofolder3 = create(Builder('repository').within(repofolder2))

        browser.open(repofolder3)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_archival_value(dossier)
        # Dossier should have inherited archival value from repofolder2
        self.assertEqual(u'unchecked', value)

        browser.open(self.branch_repofolder, view='edit')
        # Make archival value more strict on top level repofolder
        browser.fill({'Archival value': 'prompt'}).save()

        # Stricter archival value should have propagated to repofolder2, but
        # not dossier (because of depth limitation)
        self.assertEqual(u'prompt', self.get_archival_value(repofolder2))
        self.assertEqual(u'unchecked', self.get_archival_value(dossier))


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
