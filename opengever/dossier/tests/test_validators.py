from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import set_current_client_id
from plone.app.testing import TEST_USER_ID


class TestStardEndValidator(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestStardEndValidator, self).setUp()
        self.grant('Manager')

        client = create_client(clientid='Plone')
        create_ogds_user(TEST_USER_ID, assigned_client=[client, ])
        set_current_client_id(self.portal, clientid='Plone')

    def test_start_date_must_be_before_end_date(self):
        dossier = create(Builder('dossier')
                         .having(title=u'Testdossier',
                                 responsible=TEST_USER_ID,
                                 start=date(2013, 02, 01),
                                 end=date(2013, 01, 01)))

        self.browser.open('%s/edit' % (dossier.absolute_url()))
        self.browser.click('Save')

        self.assertEquals(
            u'The start date must be before the end date.',
            self.browser.css('div.error')[0].plain_text())

    def test_changing_invalid_dates_on_edit_form_is_possible(self):

        dossier = create(Builder('dossier')
                         .having(title=u'Testdossier',
                                 responsible=TEST_USER_ID,
                                 start=date(2013, 02, 01),
                                 end=date(2013, 01, 01)))

        self.browser.open('%s/edit' % (dossier.absolute_url()))
        self.browser.fill({'Closing Date': 'February 2, 2013'})
        self.browser.click('Save')

        self.browser.assert_url(dossier.absolute_url())
