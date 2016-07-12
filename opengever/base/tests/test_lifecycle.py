from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.behaviors import lifecycle
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.interfaces import IBaseCustodyPeriods
from opengever.base.interfaces import IRetentionPeriodRegister
from opengever.testing import add_languages
from opengever.testing import FunctionalTestCase
from plone import api
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


class TestCustodyPeriodDefault(FunctionalTestCase):

    def setUp(self):
        super(TestCustodyPeriodDefault, self).setUp()
        self.repofolder = create(Builder('repository'))
        self.field = ILifeCycle['custody_period']

    def get_custody_period(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_custody_period(self, obj, value):
        self.field.set(self.field.interface(obj), value)
        transaction.commit()

    def get_fti(self, portal_type):
        types_tool = api.portal.get_tool('portal_types')
        return types_tool[portal_type]

    @browsing
    def test_custody_period_default(self, browser):
        browser.login().open()
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_custody_period(dossier)
        self.assertEqual(30, value)

    @browsing
    def test_custody_period_acquired_default(self, browser):
        browser.login().open(self.repofolder)
        self.set_custody_period(self.repofolder, 100)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_custody_period(dossier)
        self.assertEqual(100, value)

    @browsing
    def test_intermediate_folder_doesnt_break_default_aq(self, browser):
        # An intermediate folderish object that doesn't have the respective
        # field shouldn't break acquisition of the default
        self.set_custody_period(self.repofolder, 100)

        fti = self.get_fti('opengever.repository.repositoryfolder')
        fti.allowed_content_types = fti.allowed_content_types + ('Dummy',)

        dummy = createContentInContainer(self.repofolder, 'Dummy')
        transaction.commit()
        browser.login().open(dummy)

        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_custody_period(dossier)
        self.assertEqual(100, value)


class TestCustodyPeriodVocabulary(FunctionalTestCase):

    def setUp(self):
        super(TestCustodyPeriodVocabulary, self).setUp()
        self.repofolder = create(Builder('repository'))
        self.field = ILifeCycle['custody_period']

    def get_custody_period(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_custody_period(self, obj, value):
        self.field.set(self.field.interface(obj), value)
        transaction.commit()

    @browsing
    def test_custody_period_choices_configurable_via_registry(self, browser):
        api.portal.set_registry_record(
            'custody_periods', interface=IBaseCustodyPeriods,
            value=[u'1', u'2', u'3', u'99']
        )
        transaction.commit()
        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        form_field = browser.find('Custody period (years)')

        self.assertEqual(
            [u'1', u'2', u'3', u'99'],
            form_field.options_values)

    @browsing
    def test_custody_period_default_choices(self, browser):
        browser.login().open()
        factoriesmenu.add(u'Business Case Dossier')
        form_field = browser.find('Custody period (years)')
        self.assertEqual(
            ['0', '30', '100', '150'],
            form_field.options_values)

    @browsing
    def test_invalid_acquired_value_falls_back_to_all_choices(self, browser):
        # If vocab is supposed to be restricted, but we find an invalid value
        # via acquisition, the vocab should fall back to offering all choices
        invalid_value = 7
        self.set_custody_period(self.repofolder, invalid_value)

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Custody period (years)')
        self.assertEqual(
            ['0', '30', '100', '150'],
            form_field.options_values)

    @browsing
    def test_falsy_acquisition_value_falls_back_to_all_choices(self, browser):
        # If vocab is supposed to be restricted, but we find a  value via
        # acquisition that is falsy, the vocab should offer all choices
        # XXX: This probably should check for None instead of falsyness
        falsy_value = 0
        self.set_custody_period(self.repofolder, falsy_value)

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Custody period (years)')
        self.assertEqual(
            ['0', '30', '100', '150'],
            form_field.options_values)

    @browsing
    def test_aq_value_is_contained_in_choices_if_restricted(self, browser):
        self.set_custody_period(self.repofolder, 30)

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Custody period (years)')
        self.assertIn('30', form_field.options_values)

    @browsing
    def test_vocab_is_restricted_if_indicated_by_aq_value(self, browser):
        self.set_custody_period(self.repofolder, 100)

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Custody period (years)')
        self.assertSetEqual(
            set(['100', '150']),
            set(form_field.options_values))

    @browsing
    def test_acquired_value_is_suggested_as_default(self, browser):
        self.set_custody_period(self.repofolder, 100)

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Custody period (years)')

        self.assertEqual('100', form_field.value)
        # Default listed first
        self.assertEqual('100', form_field.options_values[0])

    @browsing
    def test_restriction_works_in_edit_form(self, browser):
        self.set_custody_period(self.repofolder, 100)

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        transaction.commit()

        browser.click_on('Edit')
        form_field = browser.find('Custody period (years)')
        self.assertSetEqual(
            set(['100', '150']),
            set(form_field.options_values))


class TestCustodyPeriodPropagation(FunctionalTestCase):

    def setUp(self):
        super(TestCustodyPeriodPropagation, self).setUp()
        self.repofolder = create(Builder('repository'))
        self.field = ILifeCycle['custody_period']
        self.grant('Administrator')

    def get_custody_period(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_custody_period(self, obj, value):
        self.field.set(self.field.interface(obj), value)
        transaction.commit()

    @browsing
    def test_change_propagates_to_children(self, browser):
        # Start with a short custody period
        self.set_custody_period(self.repofolder, 30)

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_custody_period(dossier)
        # Dossier should have inherited custody period from repofolder
        self.assertEqual(30, value)

        browser.open(self.repofolder, view='edit')
        # Increase custody period
        browser.fill({'Custody period (years)': '100'}).save()
        transaction.commit()

        value = self.get_custody_period(dossier)
        # Increased custody period should have propagated to dossier
        self.assertEqual(100, value)

    @browsing
    def test_change_doesnt_propagate_if_old_value_still_valid(self, browser):
        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({
            'Title': 'My Dossier',
            'Custody period (years)': '150'}).save()
        dossier = browser.context

        value = self.get_custody_period(dossier)
        self.assertEqual(150, value)

        browser.open(self.repofolder, view='edit')
        browser.fill({'Custody period (years)': '30'}).save()
        transaction.commit()

        value = self.get_custody_period(dossier)
        self.assertEqual(150, value)

    @browsing
    def test_propagation_is_depth_limited(self, browser):
        """Propagation of custody period is depth limited to 2 levels.
        Not sure why this was implemented this way, but here we test for it.
        """
        # Start with a short custody period
        self.set_custody_period(self.repofolder, 30)
        repofolder2 = create(Builder('repository').within(self.repofolder))
        repofolder3 = create(Builder('repository').within(repofolder2))

        browser.login().open(repofolder3)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_custody_period(dossier)
        # Dossier should have inherited custody period from repofolder2
        self.assertEqual(30, value)

        browser.open(self.repofolder, view='edit')
        # Increase custody period on top level repofolder
        browser.fill({'Custody period (years)': '100'}).save()
        transaction.commit()

        # Increased custody period should have propagated to repofolder2, but
        # not dossier (because of depth limitation)
        self.assertEqual(100, self.get_custody_period(repofolder2))
        self.assertEqual(30, self.get_custody_period(dossier))


class TestRetentionPeriod(FunctionalTestCase):

    def setUp(self):
        super(TestRetentionPeriod, self).setUp()
        add_languages(['de-ch'])

        self.grant('Administrator')
        self.repo = create(Builder('repository')
                           .having(retention_period=15))

    def tearDown(self):
        super(TestRetentionPeriod, self).tearDown()
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IRetentionPeriodRegister)
        proxy.is_restricted = False

    @browsing
    def test_values_are_not_restricted_by_default(self, browser):
        browser.login().open(self.repo,
                     view='++add++opengever.repository.repositoryfolder')

        field = browser.css('#form-widgets-ILifeCycle-retention_period').first
        self.assertEqual(['5', '10', '15', '20', '25'], field.options_values)

    @browsing
    def test_default_value_is_value_of_the_parent(self, browser):
        browser.login().open(self.repo,
                     view='++add++opengever.repository.repositoryfolder')

        field = browser.css('#form-widgets-ILifeCycle-retention_period').first
        self.assertEqual(u'15', field.value)

    @browsing
    def test_restricted_can_be_activated_via_registry_setting(self, browser):
        # restrict retention_period
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IRetentionPeriodRegister)
        proxy.is_restricted = True
        transaction.commit()

        browser.login().open(self.repo,
                     view='++add++opengever.repository.repositoryfolder')

        field = browser.css('#form-widgets-ILifeCycle-retention_period').first
        self.assertEqual(['15', '5', '10'], field.options_values)

    @browsing
    def test_validator_respect_restriction_disabling(self, browser):
        browser.login().open(self.repo,
                             view='++add++opengever.repository.repositoryfolder')

        browser.fill({'Title': 'SubRepo',
                      'Retention period (years)': u'20'})
        browser.find('Save').click()

        sub_repo = browser.context
        self.assertEqual(20, lifecycle.ILifeCycle(sub_repo).retention_period)
