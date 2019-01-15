from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.meeting.handlers import validate_template_file
from opengever.setup.interfaces import IDuringSetup
from opengever.testing import assets
from opengever.testing import IntegrationTestCase
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides
import os


class TestSablonTemplateValidation(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_invalid_template_is_not_rejected_but_status_is_shown(self, browser):
        self.login(self.administrator, browser)
        browser.open(
            self.templates,
            view='++add++opengever.meeting.sablontemplate',
        )
        sablon_template = assets.load('invalid_sablon_template.docx')
        browser.fill({
            'Title': u'Sablonv\xferlage',
            'File': (sablon_template, 'invalid_sablon_template.docx', 'text/plain'),
        }).save()
        statusmessages.assert_no_error_messages()

        # Go to the created template's detail view
        browser.open(browser.context.listFolderContents()[-1])

        self.assertEquals(['This template will not render correctly.'],
                          statusmessages.error_messages())

    @browsing
    def test_valid_template_is_accepted(self, browser):
        self.login(self.administrator, browser)
        browser.open(
            self.templates,
            view='++add++opengever.meeting.sablontemplate',
        )
        sablon_template = assets.load('valid_sablon_template.docx')
        browser.fill({
            'Title': u'Sablonv\xferlage',
            'File': (sablon_template, 'valid_sablon_template.docx', 'text/plain'),
        }).save()
        statusmessages.assert_no_error_messages()

        # Go to the created template's detail view
        browser.open(browser.context.listFolderContents()[-1])

        self.assertEquals([], statusmessages.error_messages())

    @browsing
    def test_validation_is_skipped_during_setup_in_development_mode(self, browser):
        """ During setup in development mode the validation of sablon template
        should be skipped."""
        self.login(self.meeting_user, browser)

        self.assertTrue(self.sablon_template.is_valid_sablon_template())

        IAnnotations(self.sablon_template)['opengever.meeting.sablon_template_is_valid'] = False
        self.assertFalse(self.sablon_template.is_valid_sablon_template())

        # validation is executed and sablon template is marked as valid
        validate_template_file(self.sablon_template, "foo")
        self.assertTrue(self.sablon_template.is_valid_sablon_template())

        IAnnotations(self.sablon_template)['opengever.meeting.sablon_template_is_valid'] = False
        self.assertFalse(self.sablon_template.is_valid_sablon_template())

        # validation is skipped in development mode during setup
        with DevelopmentModeEnvironEnabled():
            alsoProvides(self.request, IDuringSetup)
            validate_template_file(self.sablon_template, "foo")
            self.assertFalse(self.sablon_template.is_valid_sablon_template())


class DevelopmentModeEnvironEnabled():

    def __enter__(self):
        self.development_var = os.environ.get('IS_DEVELOPMENT_MODE')
        os.environ['IS_DEVELOPMENT_MODE'] = "True"

    def __exit__(self, type, value, traceback):
        if 'IS_DEVELOPMENT_MODE' in os.environ:
            os.environ.pop('IS_DEVELOPMENT_MODE')
        if self.development_var is not None:
            os.environ['IS_DEVELOPMENT_MODE'] = self.development_var
