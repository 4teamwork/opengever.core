from ftw.testing import MockTestCase
from mocker import ANY
from opengever.latex.layouts.default import DefaultLayout
from opengever.latex.testing import LATEX_ZCML_LAYER
from opengever.ogds.base import utils


class TestDefaultLayout(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def setUp(self):
        super(TestDefaultLayout, self).setUp()

        client = self.create_dummy(title='CLIENT ONE',
                                   clientid='client1')
        self._ori_get_current_client = utils.get_current_client
        get_current_client = self.mocker.replace(
            'opengever.ogds.base.utils.get_current_client')
        self.expect(get_current_client()).result(client).count(0, None)

        self.portal_membership = self.stub()
        self.mock_tool(self.portal_membership, 'portal_membership')

    def tearDown(self):
        super(TestDefaultLayout, self).tearDown()
        utils.get_current_client = self._ori_get_current_client

    def test_configuration(self):
        context = self.create_dummy()
        request = self.create_dummy()
        builder = self.create_dummy()

        self.replay()
        layout = DefaultLayout(context, request, builder)

        self.assertEqual(layout.show_contact, True)
        self.assertEqual(layout.show_logo, True)
        self.assertEqual(layout.show_organisation, False)

    def test_before_render_hook(self):
        context = self.create_dummy()
        request = self.create_dummy()
        builder = self.mocker.mock()
        self.expect(builder.add_file('logo.pdf', data=ANY))

        self.replay()
        layout = DefaultLayout(context, request, builder)

        layout.before_render_hook()

        packages = '\n'.join([
                r'\usepackage[utf8]{inputenc}',
                r'\usepackage{ae,aecompl}',
                r'\usepackage[ngerman]{babel}',
                r'\usepackage{fancyhdr}',
                r'\usepackage[left=35mm, right=10mm, top=55mm, ' + \
                    r'bottom=10.5mm]{geometry}',
                r'\usepackage{graphicx}',
                r'\usepackage{lastpage}',
                r'\usepackage[neveradjust]{paralist}',
                r'\usepackage{textcomp}',
                r'\usepackage[absolute, overlay]{textpos}',
                r'\usepackage[compact]{titlesec}',
                r'\usepackage{wrapfig}',
                r'\usepackage{array,supertabular}',
                r'\usepackage{setspace}',
                '',
                ])

        self.assertEqual(layout.get_packages_latex(), packages)

    def test_get_render_arguments(self):
        context = self.mocker.mock()
        request = self.create_dummy()
        builder = self.create_dummy()

        member = self.mocker.mock()
        self.expect(context.Creator()).result('john.doe')
        self.expect(self.portal_membership.getMemberById('john.doe')).result(
            member)
        self.expect(member.getProperty('phone_number', '&nbsp;')).result(
            '012 345 6789')

        self.replay()
        layout = DefaultLayout(context, request, builder)

        args = {
            'client_title': 'CLIENT ONE',
            'member_phone': '012 345 6789',
            'show_contact': True,
            'show_logo': True,
            'show_organisation': False,
            'location': 'Zug',
            }

        self.assertEqual(layout.get_render_arguments(), args)

    def test_get_remder_arguments_non_owner(self):
        context = self.mocker.mock()
        request = self.create_dummy()
        builder = self.create_dummy()

        self.expect(context.Creator()).result('john.doe')
        self.expect(
            self.portal_membership.getMemberById('john.doe')).result(None)

        self.replay()
        layout = DefaultLayout(context, request, builder)

        args = {
            'client_title': 'CLIENT ONE',
            'member_phone': '',
            'show_contact': True,
            'show_logo': True,
            'show_organisation': False,
            'location': 'Zug',
            }

        self.assertEqual(layout.get_render_arguments(), args)

    def test_rendering(self):
        context = self.stub()
        request = self.create_dummy()
        builder = self.stub()
        self.expect(builder.add_file('logo.pdf', data=ANY))

        member = self.stub()
        self.expect(context.Creator()).result('john.doe')
        self.expect(self.portal_membership.getMemberById('john.doe')).result(
            member)
        self.expect(member.getProperty('phone_number', '&nbsp;')).result(
            '012 345 6789')

        self.replay()
        layout = DefaultLayout(context, request, builder)

        latex = layout.render_latex('LATEX CONTENT')
        self.assertIn('LATEX CONTENT', latex)
        self.assertIn(layout.get_packages_latex(), latex)
        self.assertIn(r'\includegraphics{logo.pdf}', latex)
        self.assertIn(r'T direkt ', latex)
        self.assertIn(r'\phantom{foo}\vspace{-2\baselineskip}', latex)

    def test_box_sizes_and_positions(self):
        context = self.stub()
        request = self.create_dummy()
        builder = self.stub()
        self.expect(builder.add_file('logo.pdf', data=ANY))

        member = self.stub()
        self.expect(context.Creator()).result('john.doe')
        self.expect(self.portal_membership.getMemberById('john.doe')).result(
            member)
        self.expect(member.getProperty('phone_number', '&nbsp;')).result(
            '012 345 6789')

        self.replay()
        layout = DefaultLayout(context, request, builder)

        layout.show_organisation = True

        latex = layout.render_latex('LATEX CONTENT')
        self.assertIn(r'\begin{textblock}{58mm\TPHorizModule} '
                      r'(136mm\TPHorizModule',
                      latex)

        self.assertIn(r'\begin{textblock}{100mm\TPHorizModule} '
                      r'(35mm\TPHorizModule, 55mm\TPVertModule)',
                      latex)
