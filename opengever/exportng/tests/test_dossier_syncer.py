# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime
from opengever.exportng.tests.base import SyncerTestMixin
from opengever.testing import IntegrationTestCase


REPOFOLDER_UID = u'createrepositorytree000000000003'
RESPONSIBLE = u'robert.ziegler@gever.local'
MEETING_RESPONSIBLE = u'franzi.muller@gever.local'


def dossier_row(uid, **overrides):
    """Expected row of an active dossier with default settings."""
    row = {
        'objexternalkey': uid,
        'objprimaryrelated': REPOFOLDER_UID,
        'objcreatedat': None,
        'objmodifiedat': None,
        'botitle': None,
        'bodescription': u'',
        'objcreatedby': RESPONSIBLE,
        'bostate': u'EDIT',
        'objterms': [],
        'objvalidfrom': date(2016, 1, 1),
        'objvalidto': None,
        'gboresponsible': RESPONSIBLE,
        'boforeignnumber': None,
        'gborelateddossiers': [],
        'bonumberhistory': [None],
        'bosequencenumber': None,
        'objcategory': None,
        'customfieldsjson': None,
        'classification': u'UNPROTECTED',
        'privacyprotection': False,
        'disclosurestatus': u'NOTASSESSED',
        'disclosurestatusstatement': None,
        'retentionperiod': 15,
        'retentionperiodcomment': None,
        'archivalvalue': u'NOTASSESSED',
        'archivalvaluecomment': None,
        'regularsafeguardperiod': 30,
        'objsecread': [],
        'objsecchange': [],
        'fadmins': [],
        'gboprotected': False,
        '_sort_key': None,
    }
    row.update(overrides)
    return row


def meeting_dossier_row(uid, **overrides):
    defaults = {
        'objcreatedby': MEETING_RESPONSIBLE,
        'gboresponsible': MEETING_RESPONSIBLE,
    }
    defaults.update(overrides)
    return dossier_row(uid, **defaults)


class TestDossierSyncer(SyncerTestMixin, IntegrationTestCase):

    syncer_class_name = 'DossierSyncer'
    modified_columns = {'botitle': u'Foo Bar', 'objmodifiedat': datetime(2026, 5, 21, 20, 0)}

    def expected_rows(self):
        rows = [
            dossier_row(
                u'createtreatydossiers000000000001',
                objcreatedat=datetime(2016, 8, 31, 16, 1, 33),
                objmodifiedat=datetime(2016, 8, 31, 20, 25, 33),
                botitle=u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
                bodescription=u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung '
                              u'sind hier abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                objterms=[u'Finanzverwaltung', u'Vertr\xe4ge'],
                boforeignnumber=u'qpr-900-9001-\xf7',
                bosequencenumber=1,
                _sort_key=u'0001',
            ),
            dossier_row(
                u'createexpireddossier000000000001',
                objcreatedat=datetime(2016, 8, 31, 16, 31, 33),
                objmodifiedat=datetime(2016, 8, 31, 18, 15, 33),
                botitle=u'Abgeschlossene Vertr\xe4ge',
                bodescription=u'Abgeschlossene Vertr\xe4ge vor 2000.',
                bostate=u'CLOSED',
                objterms=[u'Vertr\xe4ge'],
                objvalidfrom=date(1995, 1, 1),
                objvalidto=date(2000, 12, 31),
                bosequencenumber=2,
                _sort_key=u'0002',
            ),
            dossier_row(
                u'createinactivedossier00000000001',
                objcreatedat=datetime(2016, 8, 31, 16, 35, 33),
                objmodifiedat=datetime(2016, 8, 31, 18, 17, 33),
                botitle=u'Inaktive Vertr\xe4ge',
                bodescription=u'Inaktive Vertr\xe4ge von 2016.',
                bostate=u'CANCELLED',
                objterms=[u'Vertr\xe4ge'],
                objvalidto=date(2016, 12, 31),
                bosequencenumber=3,
                _sort_key=u'0003',
            ),
            dossier_row(
                u'createemptydossier00000000000001',
                objcreatedat=datetime(2016, 8, 31, 16, 39, 33),
                objmodifiedat=datetime(2016, 8, 31, 16, 39, 33),
                botitle=u'An empty dossier',
                disclosurestatus=u'PRIVATE',
                bosequencenumber=4,
                _sort_key=u'0004',
            ),
            dossier_row(
                u'createresolvabledossier000000001',
                objcreatedat=datetime(2016, 8, 31, 16, 41, 33),
                objmodifiedat=datetime(2016, 8, 31, 16, 43, 33),
                botitle=u'A resolvable main dossier',
                bosequencenumber=5,
                _sort_key=u'0005',
            ),
            meeting_dossier_row(
                u'createmeetings000000000000000001',
                objcreatedat=datetime(2016, 8, 31, 17, 3, 33),
                objmodifiedat=datetime(2016, 8, 31, 18, 19, 33),
                botitle=u'Sitzungsdossier 9/2017',
                objterms=[u'Finanzverwaltung', u'Vertr\xe4ge'],
                objvalidfrom=date(2016, 9, 12),
                bosequencenumber=6,
                _sort_key=u'0006',
            ),
            meeting_dossier_row(
                u'createmeetings000000000000000003',
                objcreatedat=datetime(2016, 8, 31, 17, 13, 33),
                objmodifiedat=datetime(2016, 8, 31, 17, 17, 33),
                botitle=u'Sitzungsdossier 8/2017',
                objvalidfrom=date(2016, 8, 17),
                bosequencenumber=7,
                _sort_key=u'0007',
            ),
            meeting_dossier_row(
                u'createmeetings000000000000000007',
                objcreatedat=datetime(2016, 8, 31, 17, 17, 33),
                objmodifiedat=datetime(2016, 8, 31, 17, 17, 33),
                botitle=u'Sitzungsdossier 7/2017',
                objvalidfrom=date(2016, 7, 17),
                gborelateddossiers=[
                    u'createtreatydossiers000000000001',
                    u'createmeetings000000000000000001',
                ],
                bosequencenumber=8,
                _sort_key=u'0008',
            ),
            meeting_dossier_row(
                u'createmeetings000000000000000008',
                objcreatedat=datetime(2016, 8, 31, 17, 21, 33),
                objmodifiedat=datetime(2016, 8, 31, 17, 21, 33),
                botitle=u'Sitzungsdossier 10/2016',
                objvalidfrom=date(2016, 10, 17),
                bosequencenumber=9,
                _sort_key=u'0009',
            ),
            dossier_row(
                u'createprotecteddossiers000000001',
                objcreatedat=datetime(2016, 8, 31, 20, 27, 33),
                objmodifiedat=datetime(2016, 8, 31, 20, 29, 33),
                botitle=u'Luftsch\xfctze',
                bodescription=u'Lichtbogen-L\xf6schkammern usw.',
                objsecread=[RESPONSIBLE],
                objsecchange=[RESPONSIBLE],
                gboprotected=True,
                bosequencenumber=10,
                _sort_key=u'0010',
            ),
            dossier_row(
                u'createprotecteddossiers000000003',
                objcreatedat=datetime(2016, 8, 31, 20, 31, 33),
                objmodifiedat=datetime(2016, 8, 31, 20, 35, 33),
                botitle=u'Zu allem \xdcbel',
                bodescription=u'Schl\xe4cht',
                objsecread=[RESPONSIBLE],
                objsecchange=[RESPONSIBLE],
                gboprotected=True,
                bosequencenumber=11,
                _sort_key=u'0011',
            ),
        ]
        return {row['objexternalkey']: row for row in rows}

    def object_to_modify(self):
        return self.dossier

    def modify(self, obj):
        obj.title = u'Foo Bar'
        obj.reindexObject()

    def object_to_delete(self):
        return self.empty_dossier
