from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.core.testing import activate_meeting_word_implementation
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.interfaces import IMeetingSettings
from opengever.testing import FunctionalTestCase
from plone import api
import transaction


class TestProposalTemplate(FunctionalTestCase):

    def setUp(self):
        super(TestProposalTemplate, self).setUp()
        activate_meeting_word_implementation()

    @browsing
    def test_adding_new_proposal_template(self, browser):
        vorlagen = create(Builder('templatefolder').titled(u'Vorlagen'))
        browser.login().open(vorlagen)
        factoriesmenu.add('Proposal Template')

        browser.fill({
            'Title': u'Baugesuch',
            'File': ('Binary Data', 'Baugesuch.docx', MIME_DOCX)}).save()
        statusmessages.assert_no_error_messages()

        baugesuch, = vorlagen.objectValues()
        browser.open(baugesuch, view='tabbedview_view-overview')
        self.assertDictContainsSubset(
            {'Title': 'Baugesuch',
             'File': u'baugesuch.docx \u2014 0 KB Checkout and edit Download copy'},
            dict(browser.css('.documentMetadata table').first.lists()))

    @browsing
    def test_uploading_non_docx_files_is_not_allowed(self, browser):
        vorlagen = create(Builder('templatefolder').titled(u'Vorlagen'))
        browser.login().open(vorlagen)
        factoriesmenu.add('Proposal Template')

        browser.fill({
            'Title': u'Baugesuch',
            'File': ('DATA', 'Wrong.txt', 'text/plain')}).save()
        statusmessages.assert_message('There were some errors.')
        self.assertEquals(
            ['Only word files (.docx) can be added here.'],
            browser.css('#formfield-form-widgets-file .error').text)

    @browsing
    def test_proposal_templates_not_addable_when_feature_disabled(self, browser):
        vorlagen = create(Builder('templatefolder').titled(u'Vorlagen'))
        browser.login().open(vorlagen)
        self.assertIn('Proposal Template', factoriesmenu.addable_types())

        api.portal.set_registry_record('is_word_implementation_enabled', False,
                                       interface=IMeetingSettings)
        transaction.commit()
        browser.reload()
        self.assertNotIn('Proposal Template', factoriesmenu.addable_types())
