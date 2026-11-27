# -*- coding: utf-8 -*-
from datetime import datetime
from mock import patch
from opengever.exportng import catalog
from opengever.exportng.tests.base import SyncerTestMixin
from opengever.testing import IntegrationTestCase
import shutil
import tempfile


RESPONSIBLE = u'robert.ziegler@gever.local'
TYPE_CORRECTION = u'COO.111.100.1.2148924'
TYPE_DIRECT_EXECUTION = u'COO.111.100.1.2148922'
TYPE_INFORMATION = u'COO.111.100.1.2148921'


class FakeTaskPDFView(object):
    """The PDF is rendered by an external service, which is not available."""

    def __init__(self, context, request):
        pass

    def __call__(self):
        return b'%PDF-1.4 fake'


def activity(uid, name, created, **overrides):
    """Expected activity of an open task with default settings."""
    data = {
        u'objexternalkey': uid,
        u'objname': name,
        u'actinstdefinition': TYPE_DIRECT_EXECUTION,
        u'objcreatedby': RESPONSIBLE,
        u'objcreatedat': created,
        u'actinstparticipant': u'foo@example.com',
        u'actinststate': u'STARTABLE',
        u'actinstenddeadline': u'2016-11-01T23:59:59.999999',
    }
    data.update(overrides)
    return data


def task_rows(uid, objectids, created, name, activities):
    """Expected rows of a task, one per related document and one for the
    generated task pdf (`<uid>-doc`).
    """
    rows = {}
    for objectid in list(objectids) + [uid + u'-doc']:
        rows[(uid, objectid)] = {
            'objexternalkey': uid,
            'objectid': objectid,
            'objname': name,
            'objcreatedat': datetime.strptime(created, '%Y-%m-%dT%H:%M:%S'),
            'objcreatedby': RESPONSIBLE,
            'procinstactivities': activities,
        }
    return rows


class TestTaskSyncer(SyncerTestMixin, IntegrationTestCase):

    syncer_class_name = 'TaskSyncer'
    modified_columns = {
        'objname': u'Foo Bar',
        'procinstactivities': [activity(
            u'createtasks000000000000000000012', u'Foo Bar', u'2016-08-31T18:23:33',
            actinstdefinition=TYPE_INFORMATION,
            actinstenddeadline=u'2016-09-07T23:59:59.999999')],
    }

    def setUp(self):
        super(TestTaskSyncer, self).setUp()
        # The meeting subtask of the fixture has no task type, which is a
        # required field in real data.
        self.meeting_subtask.task_type = 'correction'
        # The serializer remembers dossiers with tasks in a module global.
        catalog.tasks_by_dossier.clear()
        self.data_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.data_dir)
        for patcher in (
            patch.object(catalog, 'get_data_dir', return_value=self.data_dir),
            patch.object(catalog, 'TaskPDFView', FakeTaskPDFView),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def row_key(self, row):
        return (row['objexternalkey'], row['objectid'])

    def keys_of(self, obj):
        uid = obj.UID()
        return [(uid, doc.UID()) for doc in obj.task_documents()] + [(uid, uid + u'-doc')]

    def expected_rows(self):
        rows = {}
        rows.update(task_rows(
            u'createtasks000000000000000000001',
            [u'createtasks000000000000000000003', u'createtreatydossiers000000000002'],
            u'2016-08-31T18:01:33', u'Vertragsentwurf \xdcberpr\xfcfen',
            [activity(
                u'createtasks000000000000000000002',
                u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
                u'2016-08-31T18:03:33',
                actinstdefinition=TYPE_CORRECTION,
                actinststate=u'COMPLETED',
                actinststartedat=u'2016-08-31T18:03:33',
                actinstcompletedat=u'2016-08-31T18:03:33',
            )]))
        rows.update(task_rows(
            u'createtasks000000000000000000004', [],
            u'2016-08-31T18:07:33', u'Personaleintritt',
            [
                activity(
                    u'createtasks000000000000000000005',
                    u'Mitarbeiter Dossier generieren', u'2016-08-31T18:09:33',
                    actinstnext=[u'createtasks000000000000000000006']),
                activity(
                    u'createtasks000000000000000000006',
                    u'Arbeitsplatz vorbereiten', u'2016-08-31T18:11:33',
                    actinststate=u'WAITING',
                    actinstprev=[u'createtasks000000000000000000005'],
                    actinstnext=[u'createtasks000000000000000000007']),
                activity(
                    u'createtasks000000000000000000007',
                    u'Vorstellungsrunde bei anderen Mitarbeitern', u'2016-08-31T18:13:33',
                    actinststate=u'WAITING',
                    actinstprev=[u'createtasks000000000000000000006']),
            ]))
        rows.update(task_rows(
            u'createtasks000000000000000000008',
            [u'createexpireddossier000000000002'],
            u'2016-08-31T18:15:33', u'Vertr\xe4ge abschliessen',
            [activity(
                u'createtasks000000000000000000008', u'Vertr\xe4ge abschliessen',
                u'2016-08-31T18:15:33',
                actinstdefinition=TYPE_CORRECTION,
                actinststate=u'COMPLETED',
                actinststartedat=u'2016-08-31T18:15:33',
                actinstcompletedat=u'2016-08-31T18:15:33',
                actinstenddeadline=u'2000-12-31T23:59:59.999999',
            )]))
        rows.update(task_rows(
            u'createtasks000000000000000000009',
            [u'createinactivedossier00000000002'],
            u'2016-08-31T18:17:33', u'Status \xdcberpr\xfcfen',
            [activity(
                u'createtasks000000000000000000009', u'Status \xdcberpr\xfcfen',
                u'2016-08-31T18:17:33')]))
        rows.update(task_rows(
            u'createtasks000000000000000000010',
            [u'createmeetings000000000000000002'],
            u'2016-08-31T18:19:33', u'Programm \xdcberpr\xfcfen',
            [activity(
                u'createtasks000000000000000000011', u'H\xf6rsaal reservieren',
                u'2016-08-31T18:21:33',
                actinstdefinition=TYPE_CORRECTION,
                actinstparticipant=RESPONSIBLE,
                actinststate=u'COMPLETED',
                actinststartedat=u'2016-08-31T18:21:33',
                actinstcompletedat=u'2016-08-31T18:21:33',
            )]))
        rows.update(task_rows(
            u'createtasks000000000000000000012',
            [u'createtreatydossiers000000000002'],
            u'2016-08-31T18:23:33', u'Vertragsentw\xfcrfe 2018',
            [activity(
                u'createtasks000000000000000000012', u'Vertragsentw\xfcrfe 2018',
                u'2016-08-31T18:23:33',
                actinstdefinition=TYPE_INFORMATION,
                actinstenddeadline=u'2016-09-07T23:59:59.999999',
            )]))
        rows.update(task_rows(
            u'createtasks000000000000000000013',
            [u'createtreatydossiers000000000002'],
            u'2016-08-31T18:25:33', u'Diskr\xe4te Dinge',
            [activity(
                u'createtasks000000000000000000013', u'Diskr\xe4te Dinge',
                u'2016-08-31T18:25:33',
                actinstenddeadline=u'2020-01-01T23:59:59.999999',
            )]))
        rows.update(task_rows(
            u'createtasks000000000000000000014',
            [u'createtreatydossiers000000000002'],
            u'2016-08-31T18:27:33', u're: Diskr\xe4te Dinge',
            [activity(
                u'createtasks000000000000000000014', u're: Diskr\xe4te Dinge',
                u'2016-08-31T18:27:33',
                actinstparticipant=u'inbox:fa',
                actinstenddeadline=u'2020-01-01T23:59:59.999999',
            )]))
        rows.update(task_rows(
            u'createprotecteddossiers000000005',
            [u'createprotecteddossiers000000004'],
            u'2016-08-31T20:35:33', u'Ein notwendiges \xdcbel',
            [activity(
                u'createprotecteddossiers000000005', u'Ein notwendiges \xdcbel',
                u'2016-08-31T20:35:33',
                actinstdefinition=TYPE_CORRECTION,
            )]))
        return rows

    def object_to_modify(self):
        return self.info_task

    def modify(self, obj):
        obj.title = u'Foo Bar'
        obj.reindexObject()

    def object_to_delete(self):
        return self.inactive_task
