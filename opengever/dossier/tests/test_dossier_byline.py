from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.interfaces import IMailSettings
from ftw.testbrowser import browsing
from opengever.base.tests.byline_base_test import TestBylineBase
from opengever.core.testing import activate_filing_number
from opengever.core.testing import inactivate_filing_number
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import create_ogds_user
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import json
import transaction


class TestDossierByline(TestBylineBase):

    def setUp(self):
        super(TestDossierByline, self).setUp()

        self.intids = getUtility(IIntIds)

        create_ogds_user('hugo.boss')
        self.dossier = self.create_dossier()

        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSettings)
        mail_settings.mail_domain = u'opengever.4teamwork.ch'
        transaction.commit()

    def create_dossier(self):
        return create(Builder('dossier')
                      .in_state('dossier-state-active')
                      .having(reference_number_prefix='5',
                              responsible='hugo.boss',
                              start=date(2013, 11, 6),
                              end=date(2013, 11, 7)))

    @browsing
    def test_dossier_byline_responsible_display(self, browser):
        browser.login().open(self.dossier)

        responsible = self.get_byline_value_by_label('Responsible:')
        self.assertEquals('Boss Hugo (hugo.boss)', responsible.text)

    @browsing
    def test_dossier_byline_responsible_is_linked_to_user_details(self, browser):
        browser.login().open(self.dossier)

        responsible = self.get_byline_value_by_label('Responsible:')
        self.assertEqual('http://nohost/plone/@@user-details/hugo.boss',
                          responsible.get('href'))

    @browsing
    def test_dossier_byline_state_display(self, browser):
        browser.login().open(self.dossier)

        state = self.get_byline_value_by_label('State:')
        self.assertEquals('dossier-state-active', state.text)

    @browsing
    def test_dossier_byline_start_date_display(self, browser):
        browser.login().open(self.dossier)

        start_date = self.get_byline_value_by_label('from:')
        self.assertEquals('Nov 06, 2013', start_date.text)

    @browsing
    def test_dossier_byline_sequence_number_display(self, browser):
        browser.login().open(self.dossier)

        seq_number = self.get_byline_value_by_label('Sequence Number:')
        self.assertEquals('1', seq_number.text)

    @browsing
    def test_dossier_byline_reference_number_display(self, browser):
        browser.login().open(self.dossier)

        ref_number = self.get_byline_value_by_label('Reference Number:')
        self.assertEquals('Client1 / 1', ref_number.text)

    @browsing
    def test_dossier_byline_email_display(self, browser):
        browser.login().open(self.dossier)

        dossier_id = self.intids.getId(self.dossier)
        mail = self.get_byline_value_by_label('E-Mail:')
        self.assertEquals('%d@opengever.4teamwork.ch' % dossier_id, mail.text)

    @browsing
    def test_dossier_byline_hide_filing_number(self, browser):
        browser.login().open(self.dossier)

        self.assertEquals(None,
                          self.get_byline_value_by_label('Filing Number:'))

    @browsing
    def test_dossier_byline_editlink_for_comments(self, browser):
        browser.login().visit(self.dossier)
        comment = self.get_byline_value_by_label('Dossiernote:')
        # There are both labels (show/hide by css/js)
        self.assertEquals(['Edit Note', 'Add Note'],
                          comment.css('#editNoteLink .linkLabel').text)

    @browsing
    def test_dossier_byline_show_comments_editlink_on_maindossier_only(
            self, browser):
        browser.login().visit(self.dossier)
        comment = self.get_byline_value_by_label('Dossiernote:')
        self.assertTrue(comment,
                        'Expect the edit comment link in dossier byline')

        subdossier = create(Builder('dossier').within(self.dossier))
        browser.visit(subdossier)
        comment = self.get_byline_value_by_label('Dossiernote:')
        self.assertFalse(comment,
                         'Expect NO edit comment link on subdossier')

    @browsing
    def test_dossier_byline_hide_comments_editlink_without_modify_rights(
            self, browser):
        self.dossier.manage_permission('Modify portal content',
                                       roles=[],
                                       acquire=False)
        transaction.commit()
        browser.login().visit(self.dossier)
        comment = self.get_byline_value_by_label('Dossiernote:')
        self.assertFalse(comment,
                         'Expect NO edit comment link on dossier')

    @browsing
    def test_dossier_byline_comments_editlink_data(self, browser):
        browser.login().visit(self.dossier)
        link = browser.css('#editNoteLink').first
        dossier_data = IDossier(self.dossier)

        # No comments
        self.assertEquals(type(json.loads(link.attrib['data-i18n'])),
                          dict)
        self.assertEquals('',
                          link.attrib['data-notecache'])
        self.assertEquals('Add Note', link.css('.add .linkLabel').first.text)

        # With comments
        dossier_data.comments = u'This is a comment'
        transaction.commit()

        browser.open(self.dossier)
        link = browser.css('#editNoteLink').first
        self.assertEquals(str(dossier_data.comments),
                          link.attrib['data-notecache'])
        self.assertEquals('Edit Note', link.css('.edit .linkLabel').first.text)


class TestFilingBusinessCaseByline(TestBylineBase):

    def setUp(self):
        super(TestFilingBusinessCaseByline, self).setUp()
        activate_filing_number(self.portal)

        create_ogds_user('hugo.boss')
        self.dossier = create(Builder('dossier')
               .in_state('dossier-state-active')
               .having(reference_number_prefix='5',
                       responsible='hugo.boss',
                       start=date(2013, 11, 6),
                       end=date(2013, 11, 7),
                       filing_no='OG-Amt-2013-5'))

    def tearDown(self):
        inactivate_filing_number(self.portal)
        super(TestFilingBusinessCaseByline, self).tearDown()

    @browsing
    def test_dossier_byline_filing_number_display(self, browser):
        browser.login().open(self.dossier)

        filing_number = self.get_byline_value_by_label('Filing Number:')
        self.assertEquals('OG-Amt-2013-5', filing_number.text)
