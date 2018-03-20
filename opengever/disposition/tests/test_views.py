from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_SAMPLING
from opengever.disposition.disposition import IDisposition
from opengever.testing import FunctionalTestCase
from plone.protect import createToken


class TestUpdateTransferNumber(FunctionalTestCase):
    """Test disposition overviews function as intended."""

    def setUp(self):
        super(TestUpdateTransferNumber, self).setUp()
        self.grant('Records Manager')
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository')
                                 .titled(u'Repository A')
                                 .having(
                                     archival_value=ARCHIVAL_VALUE_SAMPLING)
                                 .within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository)
                               .having(title=u'Dossier A',
                                       start=date(2016, 1, 19),
                                       end=date(2016, 3, 19),
                                       public_trial='limited-public',
                                       archival_value='archival worthy'))

        self.disposition = create(Builder('disposition').having(
            dossiers=[self.dossier1],
            transfer_number=u'Ablieferung 2013-44'))

    @browsing
    def test_update_transfer_number(self, browser):
        self.grant('Archivist')
        browser.login().open(self.disposition,
                             {'transfer_number': u'Ablieferung 2018-1',
                              '_authenticator': createToken()},
                             view=u'update-transfer-number')

        self.assertEquals({u'proceed': True}, browser.json)
        self.assertEquals(u'Ablieferung 2018-1',
                          IDisposition(self.disposition).transfer_number)
