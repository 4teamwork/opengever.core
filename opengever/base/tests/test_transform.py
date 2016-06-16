from opengever.testing import FunctionalTestCase
from plone import api
import string


class TestTrixSablonTransform(FunctionalTestCase):

    def setUp(self):
        super(TestTrixSablonTransform, self).setUp()
        self.transforms = api.portal.get_tool('portal_transforms')

    def test_transform_strips_disallowed_html_tags(self):
        value = (
            "<div><span>Foo</span><abbr></abbr>"
            "<h1>Title</h1>"
            "</div>"
        )
        output = self.transforms.convert('trix_to_sablon', value).getData()
        self.assertEqual("<div>FooTitle</div>", output)

    def test_transform_doesnt_strip_whitespace_when_all_elements_are_valid(self):
        value = """&nbsp;
            <div>
        </div>
        """ + string.whitespace

        output = self.transforms.convert('trix_to_sablon', value).getData()
        self.assertEqual(value, output)
