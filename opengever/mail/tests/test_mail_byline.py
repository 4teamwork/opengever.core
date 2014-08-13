from ftw.builder import Builder
from ftw.builder import create
from opengever.base.tests.byline_base_test import TestBylineBase
from opengever.testing import create_ogds_user
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestMailByline(TestBylineBase):

    use_browser = True

    def setUp(self):
        super(TestMailByline, self).setUp()

        self.grant('Manager')

        self.intids = getUtility(IIntIds)
        create_ogds_user('hugo.boss')

        self.mail = create(Builder('mail'))
        self.browser.open(self.mail.absolute_url())

    def test_dossier_byline_sequence_number_display(self):
        seq_number = self.get_byline_value_by_label('Sequence Number:')
        self.assertEquals('1', seq_number.text_content())

    def test_dossier_byline_reference_number_display(self):
        ref_number = self.get_byline_value_by_label('Reference Number:')
        self.assertEquals('Client1 / 1', ref_number.text_content())
