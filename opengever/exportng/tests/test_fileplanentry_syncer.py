# -*- coding: utf-8 -*-
from datetime import datetime
from opengever.exportng.tests.base import SyncerTestMixin
from opengever.testing import IntegrationTestCase


ROOT_UID = u'createrepositorytree000000000001'


def fileplanentry_row(uid, **overrides):
    """Expected row of a repository folder with default settings."""
    row = {
        'objexternalkey': uid,
        'objprimaryrelated': ROOT_UID,
        'objcreatedat': None,
        'objmodifiedat': None,
        'fcstitle': {},
        'fcsdescription': u'',
        'felocation': None,
        'fcsbusinessnumber': None,
        'objvalidfrom': None,
        'objvaliduntil': None,
        '_sort_key': None,
    }
    row.update(overrides)
    return row


class TestFileplanEntrySyncer(SyncerTestMixin, IntegrationTestCase):

    syncer_class_name = 'FileplanEntrySyncer'
    modified_columns = {
        'fcstitle': {
            u'de': u'Foo Bar',
            u'en': u'Vertr\xe4ge und Vereinbarungen',
            u'fr': u'Contrats et accords',
        },
        'objmodifiedat': datetime(2026, 5, 21, 20, 0),
    }

    def expected_rows(self):
        rows = [
            fileplanentry_row(
                u'createrepositorytree000000000002',
                objcreatedat=datetime(2016, 8, 31, 9, 5, 33),
                objmodifiedat=datetime(2016, 8, 31, 9, 7, 33),
                fcstitle={u'de': u'F\xfchrung', u'en': u'F\xfchrung', u'fr': u'Direction'},
                fcsdescription=u'Alles zum Thema F\xfchrung.',
                fcsbusinessnumber=1,
                _sort_key=u'1',
            ),
            fileplanentry_row(
                u'createrepositorytree000000000003',
                objprimaryrelated=u'createrepositorytree000000000002',
                objcreatedat=datetime(2016, 8, 31, 9, 7, 33),
                objmodifiedat=datetime(2016, 8, 31, 21, 13, 33),
                fcstitle={
                    u'de': u'Vertr\xe4ge und Vereinbarungen',
                    u'en': u'Vertr\xe4ge und Vereinbarungen',
                    u'fr': u'Contrats et accords',
                },
                fcsbusinessnumber=1,
                _sort_key=u'1.1',
            ),
            fileplanentry_row(
                u'createrepositorytree000000000004',
                objcreatedat=datetime(2016, 8, 31, 9, 9, 33),
                objmodifiedat=datetime(2016, 8, 31, 9, 9, 33),
                fcstitle={
                    u'de': u'Rechnungspr\xfcfungskommission',
                    u'en': u'Rechnungspr\xfcfungskommission',
                    u'fr': u'Commission de v\xe9rification',
                },
                fcsbusinessnumber=2,
                _sort_key=u'2',
            ),
            fileplanentry_row(
                u'createrepositorytree000000000005',
                objcreatedat=datetime(2016, 8, 31, 9, 11, 33),
                objmodifiedat=datetime(2016, 8, 31, 9, 11, 33),
                fcstitle={
                    u'de': u'Spinn\xe4nnetzregistrar',
                    u'en': u'Spinn\xe4nnetzregistrar',
                    u'fr': u"Toile d'araign\xe9e",
                },
                fcsbusinessnumber=3,
                _sort_key=u'3',
            ),
        ]
        return {row['objexternalkey']: row for row in rows}

    def object_to_modify(self):
        return self.leaf_repofolder

    def modify(self, obj):
        obj.title_de = u'Foo Bar'
        obj.reindexObject()

    def object_to_delete(self):
        return self.empty_repofolder

    def delete(self, obj):
        # Repository folders can only be deleted through the deleter, which
        # marks the request accordingly.
        from opengever.repository.deleter import RepositoryDeleter
        RepositoryDeleter(obj).delete()
