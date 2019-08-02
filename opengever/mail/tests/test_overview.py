from ftw.mail.mail import IMail
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api


class TestGetCheckinWithoutCommentURL(IntegrationTestCase):

    features = ('bumblebee', )

    def test_returns_none_because_its_not_possible_to_checkin_emails(self):
        self.login(self.regular_user)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.mail_eml, self.request)
        self.assertIsNone(view.get_checkin_without_comment_url())


class TestGetOpenAsPdfURL(IntegrationTestCase):

    features = ('bumblebee', )

    def test_returns_none_for_unsupported_mail_conversion(self):
        self.login(self.regular_user)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.mail_eml, self.request)
        expected_url = (
            'http://nohost/plone/ordnungssystem/fuhrung'
            '/vertrage-und-vereinbarungen/dossier-1/document-29'
            '/bumblebee-open-pdf?filename=Die%20Buergschaft.pdf'
            )

        self.assertEqual(expected_url, view.get_open_as_pdf_url())

    def test_handles_non_ascii_characters_in_filename(self):
        self.login(self.regular_user)
        IMail(self.mail_eml).message.filename = u'GEVER - \xdcbernahme.msg'
        view = api.content.get_view('tabbedview_view-overview',
                                    self.mail_eml, self.request)

        expected_url = (
            u'http://nohost/plone/ordnungssystem/fuhrung'
            u'/vertrage-und-vereinbarungen/dossier-1/document-29'
            u'/bumblebee-open-pdf?filename=GEVER%20-%20%C3%9Cbernahme.pdf'
            )

        self.assertEqual(expected_url, view.get_open_as_pdf_url())


class TestMailOverview(IntegrationTestCase):

    @browsing
    def test_description_is_intelligently_formatted(self, browser):
        self.login(self.regular_user, browser)
        self.mail_eml.description = u'\n\n Foo\n    Bar\n'
        browser.open(self.mail_eml, view='tabbedview_view-overview')
        # Somehow what is `&nbsp;` in a browser is `\xa0` in ftw.testbrowser
        self.assertEqual(
            u'<br><br>\xa0Foo<br>\xa0\xa0\xa0\xa0Bar<br>',
            browser.css('#form-widgets-IDocumentMetadata-description')[0].innerHTML,
        )
