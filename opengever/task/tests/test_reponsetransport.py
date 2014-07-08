from DateTime import DateTime
from datetime import datetime
from ftw.testing import MockTestCase
from grokcore.component.testing import grok
from opengever.core.testing import ANNOTATION_LAYER
from opengever.task.adapters import Response, IResponseContainer
from opengever.task.task import ITask
from opengever.task.transporter import ExtractResponses
from opengever.task.transporter import IResponseTransporter
from opengever.task.transporter import ReceiveResponses
from z3c.relationfield import RelationValue
from zope.annotation.interfaces import IAttributeAnnotatable


class TestResponeTransporter(MockTestCase):

    layer = ANNOTATION_LAYER

    def setUp(self):
        super(TestResponeTransporter, self).setUp()
        grok('opengever.task.transporter')
        grok('opengever.task.adapters')

    def test_encoding_decoding(self):
        task = self.providing_stub([ITask])
        # rel_value = self.mocker.replace(RelationValue)
        # rel_value = self.expect(rel_value('hans')).result('RELATION VALUE')

        # relation = self.stub()
        # self.expect(relation.to_id).result('123')
        self.replay()

        trans = IResponseTransporter(task)

        self.assertEquals(trans._decode('hans'), 'hans')
        self.assertEquals(trans._decode(None), None)
        self.assertEquals(trans._decode([111, 'hans']), [111, 'hans'])

        #string
        self.assertEquals('hans', trans._decode(trans._encode('hans')))
        # unicode
        self.assertEquals(u'hans', trans._decode(trans._encode(u'hans')))
        self.assertEquals(u'h\xe4ns', trans._decode(trans._encode(u'h\xe4ns')))
        # datetime
        self.assertEquals(
            datetime(2012, 1, 1, 2, 2),
            trans._decode(trans._encode(datetime(2012, 1, 1, 2, 2))))
        # DateTime
        self.assertEquals(
            DateTime(2012, 1, 1, 2, 2),
            trans._decode(trans._encode(DateTime(2012, 1, 1, 2, 2))))
        # RelationValue
        trans.intids_mapping = {'123': '321'}
        value = RelationValue('123')
        self.assertEquals(trans._decode(trans._encode(value)).to_id, '321')
        #special type
        self.assertEquals(['special_type', 'special value'],
            trans._decode(['special_type', 'special value']))

    def test_creating_and_extraction(self):

        class DummyResponse(object):
            def getStatus(self):
                return 200

            def setHeader(self, foo, bar):
                pass

        class DummyRequest(dict):
            def __init__(self):
                self.response = DummyResponse()

        remote_task = self.providing_stub(
            [ITask, IAttributeAnnotatable])
        request = DummyRequest()
        context = self.providing_stub(
            [ITask, IAttributeAnnotatable])

        self.replay()

        response = Response(u'Sample text')
        response.creator = u'hugo.boss'
        response.date = DateTime("02.07.2010")

        response.add_change(
            'review_state', 'State', 'before-state', 'after-state')
        response.add_change(
            'responsible', 'Responsible', 'hugo.boss', 'james.bond')

        container = IResponseContainer(remote_task)
        container.add(response)

        # extract
        request.intids_mapping = {}
        data = ExtractResponses(remote_task, request)()

        # receive
        request['responses'] = data
        ReceiveResponses(context, request)()

        # check if the response is correctly synced
        self.assertTrue(len(IResponseContainer(context)) == 1)
        synced_response = IResponseContainer(context)[0]
        self.assertEquals(synced_response.text, response.text)
        self.assertEquals(synced_response.creator, response.creator)
        self.assertEquals(synced_response.date, response.date)
        # changes
        self.assertEquals(
            synced_response.changes,
            [
                {u'after': u'after-state',
                 u'id': u'review_state',
                 u'name': u'State',
                 u'before': u'before-state'},
                {u'after': u'james.bond',
                 u'id': u'responsible',
                 u'name': u'Responsible',
                 u'before': u'hugo.boss'}])
