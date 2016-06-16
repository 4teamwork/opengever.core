from opengever.testing import FunctionalTestCase
from plone import api
import string


class TestTrixSablonTransform(FunctionalTestCase):

    def setUp(self):
        super(TestTrixSablonTransform, self).setUp()
        self.transforms = api.portal.get_tool('portal_transforms')

    def apply_transform(self, value):
        return self.transforms.convert('trix_to_sablon', value).getData()

    def test_transform_strips_disallowed_html_tags(self):
        value = (
            "<div><span>Foo</span><abbr>gnahahah</abbr>"
            "<h1>Title</h1>"
            "</div>"
        )
        self.assertEqual(
            "<div>FoognahahahTitle</div>", self.apply_transform(value))

    def test_transform_doesnt_strip_whitespace_when_all_elements_are_valid(self):
        value = """&nbsp;
            <div>
        </div>
        """ + string.whitespace

        self.assertEqual(value, self.apply_transform(value))

    def test_transform_doesnt_strip_whitespace_when_stripping_invalid_tags(self):
        value = "\n<span>\n\n\t  Foo!  </span>"

        self.assertEqual("\n\n\n\t  Foo!  ", self.apply_transform(value))
