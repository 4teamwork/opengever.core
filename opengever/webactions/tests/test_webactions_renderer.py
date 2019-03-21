from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import IntegrationTestCase
from opengever.webactions.interfaces import IWebActionsRenderer
from zope.component import getMultiAdapter


class TestWebActionRendererTitleButtons(IntegrationTestCase):

    display = 'title-buttons'
    icon = 'fa-helicopter'
    adapter_interface = IWebActionsRenderer

    expected_data = [
        '<a title="Action 1" href="http://example.org/endpoint" '
        'class="webaction_button fa fa-helicopter"></a>',

        '<a title="Action 2" href="http://example.org/endpoint" '
        'class="webaction_button fa fa-helicopter"></a>']

    def setUp(self):
        super(TestWebActionRendererTitleButtons, self).setUp()
        create(Builder('webaction')
               .titled(u'Action 1')
               .having(order=5, enabled=True, display=self.display, icon_name=self.icon))

        create(Builder('webaction')
               .titled(u'Action 2')
               .having(order=10, enabled=True, display=self.display, icon_name=self.icon))

    def test_data_returned_by_webaction_renderer(self):
        self.login(self.regular_user)
        renderer = getMultiAdapter((self.dossier, self.request),
                                   self.adapter_interface,
                                   name=self.display)
        rendered_data = renderer()

        self.assertEqual(self.expected_data, rendered_data)


class TestWebActionRendererActionButtons(TestWebActionRendererTitleButtons):

    display = 'action-buttons'
    icon = 'fa-helicopter'

    expected_data = [
            '<a title="Action 1" href="http://example.org/endpoint" '
            'class="webaction_button fa fa-helicopter">'
            '<span class="subMenuTitle actionText">Action 1</span></a>',

            '<a title="Action 2" href="http://example.org/endpoint" '
            'class="webaction_button fa fa-helicopter">'
            '<span class="subMenuTitle actionText">Action 2</span></a>']
