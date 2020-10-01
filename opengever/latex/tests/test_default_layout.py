from ftw.pdfgenerator.builder import Builder as PDFBuilder
from opengever.latex.layouts.default import DefaultLayout
from opengever.testing import IntegrationTestCase
from plone import api


class TestDefaultLayout(IntegrationTestCase):

    def test_configuration(self):
        self.login(self.regular_user)
        layout = DefaultLayout(self.dossier, self.request, PDFBuilder())

        self.assertEqual(layout.show_contact, False)
        self.assertEqual(layout.show_logo, False)
        self.assertEqual(layout.show_organisation, False)

    def test_before_render_hook(self):
        self.login(self.regular_user)
        layout = DefaultLayout(self.dossier, self.request, PDFBuilder())

        layout.before_render_hook()

        packages = '\n'.join([
                r'\usepackage[utf8]{inputenc}',
                r'\usepackage{ae,aecompl}',
                r'\usepackage[ngerman]{babel}',
                r'\usepackage{fancyhdr}',
                r'\usepackage{calc}',
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
        self.login(self.regular_user)

        layout = DefaultLayout(self.dossier, self.request, PDFBuilder())

        self.assertEqual(self.dossier.Creator(), 'robert.ziegler')

        portal_membership_tool = api.portal.get_tool('portal_membership')

        member = portal_membership_tool.getMemberById('robert.ziegler')
        member.phone_number = '012 345 6789'

        args = {
            'show_contact': False,
            'page_label': 'Page',
            'client_title': 'Hauptmandant',
            'location': 'Bern',
            'show_organisation': False,
            'member_phone': '012 345 6789',
            'show_logo': False
            }

        self.assertDictEqual(layout.get_render_arguments(), args)

    def test_get_render_arguments_non_owner(self):
        self.login(self.regular_user)
        self.dossier.creators = ('NonExistentUser',)

        layout = DefaultLayout(self.dossier, self.request, PDFBuilder())

        self.assertNotEqual(self.dossier.Creator(), 'robert.ziegler')

        args = {
            'show_contact': False,
            'page_label': 'Page',
            'client_title': 'Hauptmandant',
            'location': 'Bern',
            'show_organisation': False,
            'member_phone': '',
            'show_logo': False
            }

        self.assertEqual(layout.get_render_arguments(), args)

    def test_rendering(self):
        self.login(self.regular_user)

        layout = DefaultLayout(self.dossier, self.request, PDFBuilder())

        latex = layout.render_latex('LATEX CONTENT')
        self.assertIn('LATEX CONTENT', latex)
        self.assertIn(layout.get_packages_latex(), latex)
        self.assertIn(r'\phantom{foo}\vspace{-2\baselineskip}', latex)

    def test_box_sizes_and_positions(self):
        self.login(self.regular_user)

        builder = PDFBuilder()

        layout = DefaultLayout(self.dossier, self.request, builder)
        layout.show_organisation = True

        latex = layout.render_latex('LATEX CONTENT')

        self.assertIn(r'\begin{textblock}{58mm\TPHorizModule} '
                      r'(136mm\TPHorizModule',
                      latex)

        self.assertIn(r'\begin{textblock}{100mm\TPHorizModule} '
                      r'(100mm\TPHorizModule, 10mm\TPVertModule)',
                      latex)
