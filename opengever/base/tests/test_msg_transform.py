from distutils.spawn import find_executable
from opengever.base.transforms.msg2mime import Msg2MimeTransform
from opengever.core.testing import MSGCONVERT_SERVICE_INTEGRATION_TESTING
from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING
from opengever.testing import assets
from opengever.testing import IntegrationTestCase
from unittest import skipIf


HAS_MSGCONVERT = find_executable('msgconvert')


class TestMSGTransformUsingService(IntegrationTestCase):

    layer = MSGCONVERT_SERVICE_INTEGRATION_TESTING

    def test_msg_transform_produces_eml_using_service(self):
        msg_filename = assets.path_to_asset('testmail.msg')
        with open(msg_filename, 'rb') as msg_file:
            msg_data = msg_file.read()
        transform = Msg2MimeTransform()
        eml = transform.transform(msg_data)
        self.assertIn('MIME-Version: 1.0', eml)


@skipIf(not HAS_MSGCONVERT, 'msgconvert is required')
class TestMSGTransformUsingExecutable(IntegrationTestCase):

    layer = OPENGEVER_INTEGRATION_TESTING

    def test_msg_transform_produces_eml_using_executable(self):
        msg_filename = assets.path_to_asset('testmail.msg')
        with open(msg_filename, 'rb') as msg_file:
            msg_data = msg_file.read()
        transform = Msg2MimeTransform()
        eml = transform.transform(msg_data)
        self.assertIn('MIME-Version: 1.0', eml)
