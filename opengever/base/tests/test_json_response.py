from opengever.base import _
from opengever.base.response import JSONResponse
from opengever.testing import FunctionalTestCase
import json


class TestUnitJSONResponse(FunctionalTestCase):

    def setUp(self):
        super(TestUnitJSONResponse, self).setUp()
        self.response = JSONResponse(self.request)
        self.info_message = _('infomessage')
        self.error_message = _('errormessage')

    def test_empty_jsonresponse(self):
        self.assertEqual(self.response.dump(), '{}')

    def test_info_message(self):
        self.assertEqual(self.response.info(self.info_message).dump(),
         json.dumps({'messages': [
                        {'messageClass': 'info',
                         'messageTitle': 'Information',
                         'message': 'infomessage',
                        }
                    ]}
                ))

    def test_error_message(self):
        self.assertEqual(self.response.error(self.error_message).dump(),
         json.dumps({'messages': [
                        {'messageClass': 'error',
                         'messageTitle': 'Error',
                         'message': 'errormessage',
                        }
                    ]}
                ))

    def test_multiple_messages(self):
        self.assertEqual(self.response.error(self.error_message)
                                      .info(self.info_message)
                                      .error(self.error_message).dump(),
         json.dumps({'messages': [
                        {'messageClass': 'error',
                         'messageTitle': 'Error',
                         'message': 'errormessage',
                        },
                        {'messageClass': 'info',
                         'messageTitle': 'Information',
                         'message': 'infomessage',
                        },
                        {'messageClass': 'error',
                         'messageTitle': 'Error',
                         'message': 'errormessage',
                        }
                    ]}
                ))

    def test_custom_data(self):
        self.assertEqual(self.response.data(name='peter').dump(),
                         json.dumps({'name': 'peter'}))

    def test_multiple_custom_data(self):
        self.assertEqual(self.response.data(name='peter',
                                            foo=123,
                                            bar=None).dump(),
                         json.dumps({'name': 'peter',
                                     'foo': 123,
                                     'bar': None}))

    def test_protected_data_throws_assertion_error(self):
        with self.assertRaises(AssertionError):
            self.response.data(messages='peter')

        with self.assertRaises(AssertionError):
            self.response.data(proceed='peter')

    def test_proceed(self):
        self.assertEqual(self.response.proceed().dump(),
                         json.dumps({'proceed': True}))

    def test_remain(self):
        self.assertEqual(self.response.remain().dump(),
                         json.dumps({'proceed': False}))

    def test_full_response(self):
        self.assertEqual(self.response.data(name='peter')
                                      .info(self.info_message)
                                      .error(self.error_message)
                                      .proceed()
                                      .dump(),
         json.dumps({'messages': [
            {'messageTitle': 'Information',
             'message': 'infomessage',
             'messageClass': 'info'},
            {'messageTitle': 'Error',
             'message': 'errormessage',
             'messageClass': 'error'}],
             'name': 'peter',
             'proceed': True}
        ))
