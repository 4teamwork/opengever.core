from ftw.testing import MockTestCase
from opengever.base.behaviors.utils import set_attachment_content_disposition
from urllib import quote
from mocker import ANY


class TestAttachmentContentDisposition(MockTestCase):

    def setUp(self):
        super(TestAttachmentContentDisposition, self).setUp()
        self.header = []

        self.request = self.mocker.proxy({}, count=False)
        self.expect(
            self.request.response.setHeader(ANY, ANY)).call(
                lambda x, y: self.header.append(y)).count(0, None)

    def test_set_empty_filename(self):

        self.request['HTTP_USER_AGENT'] = ''

        self.replay()

        set_attachment_content_disposition(self.request, '')

        self.assertTrue(len(self.header) == 0)

    def test_set_ms_filename(self):
        """ In Ms we must remove the quotes.
        """

        self.expect(self.request.get('HTTP_USER_AGENT', ANY)).result('MSIE')

        self.replay()

        set_attachment_content_disposition(self.request, 'MS Name')

        self.assertEquals(
            self.header[0],
            'attachment; filename=%s' % quote('MS Name'))

    def test_filename(self):
        """ Normaly we have the filename in quotes
        """

        self.expect(self.request.get('HTTP_USER_AGENT', ANY)).result('DEF')

        self.replay()

        set_attachment_content_disposition(self.request, 'Default Name')

        self.assertEquals(
            self.header[0],
            'attachment; filename="%s"' % 'Default Name')
