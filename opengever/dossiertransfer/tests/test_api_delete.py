from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.dossiertransfer.model import DossierTransfer
from opengever.testing import IntegrationTestCase
from plone import api
import pytz


class TestDossierTransfersDelete(IntegrationTestCase):

    features = ('dossier-transfers', )

    @browsing
    def test_delete_dossier_transfer(self, browser):
        self.login(self.secretariat_user, browser=browser)

        with freeze(datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)):
            transfer = create(Builder('dossier_transfer'))
            session = create_session()
            session.add(transfer)
            session.flush()

        self.assertEqual(1, DossierTransfer.query.count())

        browser.open(self.portal, view='@dossier-transfers/%s' % transfer.id,
                     method='DELETE', headers=self.api_headers)

        self.assertEqual(204, browser.status_code)
        self.assertEqual('', browser.contents)
        self.assertEqual(0, DossierTransfer.query.count())


class TestDossierTransfersDeletePermissions(IntegrationTestCase):

    features = ('dossier-transfers', )

    def create_transfers(self):
        with freeze(datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)):
            session = create_session()

            self.login(self.secretariat_user)

            transfer = create(Builder('dossier_transfer')
                              .having(
                                  title='Transfer owned by secretariat_user'))
            session.add(transfer)
            session.flush()
            self.transfer_owned_by_secretariat = transfer

            transfer2 = create(Builder('dossier_transfer')
                               .having(
                                   title='Transfer2 owned by secretariat_user'))
            session.add(transfer2)
            session.flush()
            self.transfer2_owned_by_secretariat = transfer2

            transfer3 = create(Builder('dossier_transfer')
                               .having(
                                   title='Transfer3 owned by secretariat_user'))
            session.add(transfer3)
            session.flush()
            self.transfer3_owned_by_secretariat = transfer3

            self.login(self.dossier_responsible)

            transfer = create(Builder('dossier_transfer')
                              .having(
                                  title='Transfer owned by dossier_responsible'))
            session.add(transfer)
            session.flush()
            self.transfer_owned_by_responsible = transfer

            transfer2 = create(Builder('dossier_transfer')
                               .having(
                                   title='Transfer2 owned by dossier_responsible'))
            session.add(transfer2)
            session.flush()
            self.transfer2_owned_by_responsible = transfer2

            transfer3 = create(Builder('dossier_transfer')
                               .having(
                                   title='Transfer3 owned by dossier_responsible'))
            session.add(transfer3)
            session.flush()
            self.transfer3_owned_by_responsible = transfer3

            self.login(self.manager)

            create(Builder('admin_unit')
                   .id('other1')
                   .having(title='Other AU 1'))

            create(Builder('admin_unit')
                   .id('other2')
                   .having(title='Other AU 2'))

            transfer = create(Builder('dossier_transfer')
                              .having(
                                  title='Transfer between other admin units',
                                  source_id='other1',
                                  target_id='other2'))
            session.add(transfer)
            session.flush()
            self.transfer_between_other_units = transfer

    def delete_transfer(self, transfer, browser):
        browser.open(self.portal, view='@dossier-transfers/%s' % transfer.id,
                     method='DELETE', headers=self.api_headers)

    @browsing
    def test_delete_permissions(self, browser):
        self.create_transfers()

        expected = {
            # User in inbox group
            self.secretariat_user.id: [
                (self.transfer_owned_by_secretariat, 204),
                (self.transfer_owned_by_responsible, 204),
                (self.transfer_between_other_units, 401),
            ],
            # User owning one of the transfers
            self.dossier_responsible.id: [
                (self.transfer2_owned_by_secretariat, 401),
                (self.transfer2_owned_by_responsible, 204),
                (self.transfer_between_other_units, 401),
            ],
            # User not in inbox group and not owning any transfers
            self.regular_user.id: [
                (self.transfer3_owned_by_secretariat, 401),
                (self.transfer3_owned_by_responsible, 401),
                (self.transfer_between_other_units, 401),
            ],
        }

        browser.raise_http_errors = False
        for user_id, expectations in expected.items():
            user = api.user.get(userid=user_id)
            self.login(user, browser=browser)

            for transfer, expected_status in expectations:
                self.delete_transfer(transfer, browser)
                self.assertEqual(
                    expected_status,
                    browser.status_code,
                    'Expected HTTP status %s for request by user %s on '
                    'transfer %r (%s)' % (
                        expected_status, user, transfer, transfer.title))
