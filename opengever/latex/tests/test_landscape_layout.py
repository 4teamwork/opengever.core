from ftw.testing import MockTestCase
from mocker import ANY
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.layouts.landscape import LandscapeLayout
from opengever.latex.testing import LATEX_ZCML_LAYER
from opengever.ogds.base import utils
from zope.component import adaptedBy


class TestLandscapeLayout(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def setUp(self):
        super(TestLandscapeLayout, self).setUp()
        self.context = self.stub()

        client = self.create_dummy(title='CLIENT ONE',
                                   clientid='client1')
        self._ori_get_current_client = utils.get_current_client
        get_current_client = self.mocker.replace(
            'opengever.ogds.base.utils.get_current_client')
        self.expect(get_current_client()).result(client).count(0, None)

        self.portal_membership = self.stub()
        self.mock_tool(self.portal_membership, 'portal_membership')

        member = self.stub()
        self.expect(self.context.Creator()).result('john.doe')
        self.expect(self.portal_membership.getMemberById('john.doe')).result(
            member)
        self.expect(member.getProperty('phone_number', '&nbsp;')).result(
            '012 345 6789')

    def tearDown(self):
        super(TestLandscapeLayout, self).tearDown()
        utils.get_current_client = self._ori_get_current_client

    def test_adapts_landscape_request_layer(self):
        self.replay()

        adapts = adaptedBy(LandscapeLayout)
        self.assertEqual(len(adapts), 3)
        self.assertEqual(adapts[1], ILandscapeLayer)

    def test_show_contact(self):
        request = self.create_dummy()
        builder = self.stub()
        self.expect(builder.add_file('logo.pdf', data=ANY))

        self.replay()

        layout = LandscapeLayout(self.context, request, builder)

        self.assertEqual(layout.get_render_arguments()['show_contact'],
                         False)

    def test_rendering(self):
        request = self.create_dummy()
        builder = self.stub()
        self.expect(builder.add_file('logo.pdf', data=ANY))

        self.replay()
        layout = LandscapeLayout(self.context, request, builder)

        latex = layout.render_latex('CONTENT LATEX')
        self.assertIn('CONTENT LATEX', latex)
        self.assertIn(layout.get_packages_latex(), latex)
        self.assertIn(r'\includegraphics{logo.pdf}', latex)
        self.assertNotIn(r'T direkt ', latex)
        self.assertNotIn(r'\phantom{foo}\vspace{-2\baselineskip}', latex)

    def test_box_sizes_and_positions(self):
        request = self.create_dummy()
        builder = self.stub()
        self.expect(builder.add_file('logo.pdf', data=ANY))

        self.replay()
        layout = LandscapeLayout(self.context, request, builder)
        layout.show_contact = True
        layout.show_organisation = True

        latex = layout.render_latex('LATEX CONTENT')
        self.assertIn(r'begin{textblock}{58mm\TPHorizModule} '
                      r'(220mm\TPHorizModule',
                      latex)

        self.assertIn(r'\begin{textblock}{58mm\TPHorizModule}'
                      r' (220mm\TPHorizModule, 54mm\TPVertModule)',
                      latex)
