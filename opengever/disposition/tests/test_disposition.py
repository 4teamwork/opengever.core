from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testing import freeze
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from opengever.testing import obj2paths
from plone import api
from plone.protect import createToken


OFFERED_STATE = 'dossier-state-offered'


class TestDisposition(FunctionalTestCase):

    def setUp(self):
        super(TestDisposition, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .titled(u'Dossier A')
                               .as_expired()
                               .within(self.repository))
        self.dossier2 = create(Builder('dossier')
                               .in_state('dossier-state-resolved')
                               .within(self.repository))
        self.dossier3 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository))

        self.grant(
            'Contributor', 'Editor', 'Reader', 'Reviewer', 'Records Manager')

    def test_id_is_sequence_number_prefixed_with_disposition(self):
        disposition_1 = create(Builder('disposition'))
        disposition_2 = create(Builder('disposition'))

        self.assertEquals('disposition-1', disposition_1.getId())
        self.assertEquals('disposition-2', disposition_2.getId())

    def test_title_composed_disposition_label_adminunit_abbreviation_creation_year_and_sequence_number(self):

        with freeze(datetime(2014, 1, 1)):
            disposition = create(Builder('disposition'))

            expected = u'Disposition Client1 2014 1'
            self.assertEquals(expected, disposition.title)
            self.assertEquals(expected.decode('utf-8'), disposition.Title())
            self.assertEquals(expected, obj2brain(disposition).Title)

        with freeze(datetime(2016, 1, 1)):
            self.assertEquals(u'Disposition Client1 2014 1', disposition.title)

    @browsing
    def test_can_be_added(self, browser):
        browser.login().open(self.root)
        factoriesmenu.add('Disposition')
        browser.fill({'Transfer number': 'Ablieferung X29238',
                      'Dossiers': [self.dossier1, self.dossier3]})
        browser.find('Save').click()

        self.assertEquals(['Item created'], info_messages())

    @browsing
    def test_selected_dossiers_in_the_list_are_preselected(self, browser):
        data = {'paths:list': obj2paths([self.dossier1, self.dossier3]),
                '_authenticator': createToken()}
        browser.login().open(self.root,
                             view='++add++opengever.disposition.disposition',
                             data=data)

        browser.fill({'Transfer number': 'Ablieferung X29238'})
        browser.find('Save').click()

        self.assertEquals([self.dossier1, self.dossier3],
                          [rel.to_object for rel in browser.context.dossiers])

    @browsing
    def test_selected_dossiers_in_active_states_are_skipped(self, browser):
        dossier4 = create(Builder('dossier')
                          .within(self.repository))
        data = {'paths:list': obj2paths([dossier4]),
                '_authenticator': createToken()}

        browser.login().open(self.root,
                             view='++add++opengever.disposition.disposition',
                             data=data)
        browser.find('Save').click()

        self.assertEquals(['There were some errors.'], error_messages())
        self.assertEquals(['Required input is missing.'],
                          browser.css('.fieldErrorBox .error').text)

    @browsing
    def test_already_offered_dossiers_cant_be_selected(self, browser):
        data = {'paths:list': obj2paths([self.dossier1]),
                '_authenticator': createToken()}
        browser.login().open(self.root,
                             view='++add++opengever.disposition.disposition',
                             data=data)
        browser.find('Save').click()

        browser.login().open(self.root,
                             view='++add++opengever.disposition.disposition',
                             data=data)
        browser.find('Save').click()

        self.assertEquals(['There were some errors.'], error_messages())
        self.assertEquals(['The dossier Dossier A is already offered in '
                           'a different disposition.'],
                          browser.css('.fieldErrorBox .error').text)

    @browsing
    def test_only_expired_dossiers_can_be_added(self, browser):
        data = {'paths:list': obj2paths([self.dossier2]),
                '_authenticator': createToken()}
        browser.login().open(self.root,
                             view='++add++opengever.disposition.disposition',
                             data=data)

        browser.fill({'Transfer number': 'Ablieferung X29238'})
        browser.find('Save').click()

        self.assertEquals(['There were some errors.'], error_messages())
        self.assertEquals(
            ['The retention period of the selected dossiers is not expired.'],
            browser.css('.fieldErrorBox .error').text)

    @browsing
    def test_attached_dossier_are_set_to_offered_state(self, browser):
        data = {'paths:list': obj2paths([self.dossier1, self.dossier3]),
                '_authenticator': createToken()}
        browser.login().open(self.root,
                             view='++add++opengever.disposition.disposition',
                             data=data)
        browser.find('Save').click()

        self.assertEquals(OFFERED_STATE, api.content.get_state(self.dossier1))
        self.assertEquals(OFFERED_STATE, api.content.get_state(self.dossier3))

    @browsing
    def test_date_of_submission_is_set_today_for_attached_dossiers(self, browser):
        data = {'paths:list': obj2paths([self.dossier1, self.dossier3]),
                '_authenticator': createToken()}
        browser.login().open(self.root,
                             view='++add++opengever.disposition.disposition',
                             data=data)
        browser.find('Save').click()

        self.assertEquals(date.today(),
                          ILifeCycle(self.dossier1).date_of_submission)
        self.assertEquals(date.today(),
                          ILifeCycle(self.dossier3).date_of_submission)


class TestDispositionEditForm(FunctionalTestCase):

    def setUp(self):
        super(TestDispositionEditForm, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier').as_expired()
                               .within(self.repository))
        self.dossier2 = create(Builder('dossier')
                               .as_expired()
                               .in_state('dossier-state-inactive')
                               .within(self.repository))
        self.dossier3 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository))

        self.grant('Contributor', 'Editor', 'Reader', 'Reviewer', 'Records Manager')

    @browsing
    def test_set_added_dossiers_to_offered_state(self, browser):
        disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier1])
                             .within(self.root))

        browser.login().open(disposition, view='edit')
        browser.fill({'Dossiers': [self.dossier1, self.dossier2, self.dossier3]})
        browser.find('Save').click()

        self.assertEquals(OFFERED_STATE, api.content.get_state(self.dossier2))
        self.assertEquals(OFFERED_STATE, api.content.get_state(self.dossier3))

    @browsing
    def test_set_dropped_dossiers_to_former_state(self, browser):
        disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier1, self.dossier2, self.dossier3])
                             .within(self.root))

        browser.login().open(disposition, view='edit')
        browser.fill({'Dossiers': [self.dossier3]})
        browser.find('Save').click()

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.dossier1))
        self.assertEquals('dossier-state-inactive',
                          api.content.get_state(self.dossier2))
        self.assertEquals(OFFERED_STATE, api.content.get_state(self.dossier3))

    @browsing
    def test_reset_date_of_submission_for_dropped_dossiers(self, browser):
        disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier1, self.dossier2, self.dossier3])
                             .within(self.root))

        browser.login().open(disposition, view='edit')
        browser.fill({'Dossiers': [self.dossier3]})
        browser.find('Save').click()

        self.assertEquals(None, ILifeCycle(self.dossier1).date_of_submission)
        self.assertEquals(None, ILifeCycle(self.dossier2).date_of_submission)
        self.assertEquals(date.today(),
                          ILifeCycle(self.dossier3).date_of_submission)
