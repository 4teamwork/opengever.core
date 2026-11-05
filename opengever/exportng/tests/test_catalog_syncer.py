from opengever.testing import IntegrationTestCase
from opengever.exportng.tests.layer import EXPORTNG_DB_INTEGRATION_TESTING
from ftw.testing import freeze
from datetime import date
from datetime import datetime
import pytz


class TestDossierSyncer(IntegrationTestCase):

    layer = EXPORTNG_DB_INTEGRATION_TESTING

    def setUp(self):
        super(TestDossierSyncer, self).setUp()
        from opengever.exportng.catalog import DossierSyncer
        from opengever.exportng.db import metadata
        from opengever.exportng.sync import Syncer
        metadata.drop_all()
        metadata.clear()
        Syncer().create_tables()
        self.syncer = DossierSyncer()
        metadata.create_all(checkfirst=True)

    def test_initial_dossier_sync(self):
        self.syncer.sync()

        self.syncer._sql_items = None
        self.assertEqual(len(self.syncer.sql_items), 11)
        self.assertEqual(
            self.syncer.sql_items['createtreatydossiers000000000001'][:-4],
            (
                u'createtreatydossiers000000000001',
                u'createrepositorytree000000000003',
                datetime(2016, 8, 31, 16, 1, 33),
                datetime(2016, 8, 31, 20, 25, 33),
                u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
                u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                u'robert.ziegler@gever.local',
                u'EDIT',
                [u'Finanzverwaltung', u'Vertr\xe4ge'],
                date(2016, 1, 1),
                None,
                u'robert.ziegler@gever.local',
                u'qpr-900-9001-\xf7',
                [],
                [None],
                1,
                None,
                None,
                u'UNPROTECTED',
                False,
                u'NOTASSESSED',
                None,
                15,
                None,
                u'NOTASSESSED',
                None,
                30,
                [],
                [],
                [],
                False,
                u'0001',
            )
        )

    def test_delta_dossier_sync(self):
        with freeze(datetime(2026, 5, 20, 14, 30, tzinfo=pytz.utc)):
            self.syncer.sync()
        self.syncer._sql_items = None
        self.syncer._catalog_items = None

        self.login(self.regular_user)
        self.dossier.title = u'Foo Bar'
        with freeze(datetime(2026, 5, 21, 18, 0, tzinfo=pytz.utc)):
            self.dossier.reindexObject()

        self.syncer.sync()
        self.syncer._sql_items = None
        self.assertEqual(
            self.syncer.sql_items['createtreatydossiers000000000001'][:-4],
            (
                u'createtreatydossiers000000000001',
                u'createrepositorytree000000000003',
                datetime(2016, 8, 31, 16, 1, 33),
                datetime(2026, 5, 21, 20, 0),
                u'Foo Bar',
                u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                u'robert.ziegler@gever.local',
                u'EDIT',
                [u'Finanzverwaltung', u'Vertr\xe4ge'],
                date(2016, 1, 1),
                None,
                u'robert.ziegler@gever.local',
                u'qpr-900-9001-\xf7',
                [],
                [None],
                1,
                None,
                None,
                u'UNPROTECTED',
                False,
                u'NOTASSESSED',
                None,
                15,
                None,
                u'NOTASSESSED',
                None,
                30,
                [],
                [],
                [],
                False,
                u'0001',
            )
        )
