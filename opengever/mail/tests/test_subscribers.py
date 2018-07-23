from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestSubscribers(FunctionalTestCase):
    """Test mail update events fire as designed."""

    def setUp(self):
        super(TestSubscribers, self).setUp()

        self.root = create(Builder('repository_root'))
        self.repo = create(Builder('repository').within(self.root))
        self.dossier = create(Builder('dossier').within(self.repo))

    @browsing
    def test_modifying_title_updates_filename(self, browser):
        mail = create(
            Builder('mail').within(self.dossier).with_dummy_message())

        browser.login().open(mail, view='edit')
        browser.fill({'Title': 'My new mail Title'}).submit()

        self.assertEqual(u'My new mail Title.eml', mail.message.filename)
