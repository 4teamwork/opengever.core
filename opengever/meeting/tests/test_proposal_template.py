from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.meeting.command import MIME_DOCX
from opengever.testing import IntegrationTestCase


class TestProposalTemplate(IntegrationTestCase):

    features = (
        'meeting',
        )

    @browsing
    def test_adding_new_proposal_template(self, browser):
        self.login(self.administrator, browser)

        browser.open(self.templates)
        self.assertIn('Proposal Template', factoriesmenu.addable_types(browser))

        browser.open(self.templates, view='++add++opengever.meeting.proposaltemplate')
        browser.fill({'Title': 'Baugesuch', 'File': ('Binary Data', 'Baugesuch.docx', MIME_DOCX)}).save()
        statusmessages.assert_no_error_messages()
        baugesuch = self.templates.objectValues()[-1]
        browser.open(baugesuch, view='tabbedview_view-overview')
        self.assertDictContainsSubset({'Title': 'Baugesuch'}, dict(browser.css('.documentMetadata table').first.lists()))
        self.assertEquals('Baugesuch.docx', browser.css('.documentMetadata span.filename').first.text)

    @browsing
    def test_uploading_non_docx_files_is_not_allowed(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.templates, view='++add++opengever.meeting.proposaltemplate')
        browser.fill({
            'Title': u'Geb\xfchren',
            'File': ('DATA', 'Wrong.txt', 'text/plain')}).save()
        statusmessages.assert_message('There were some errors.')
        self.assertEquals(
            ['Only word files (.docx) can be added here.'],
            browser.css('#formfield-form-widgets-file .error').text)
