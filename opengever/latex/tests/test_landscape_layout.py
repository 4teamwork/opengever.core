from ftw.pdfgenerator.builder import Builder as PDFBuilder
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.layouts.landscape import LandscapeLayout
from opengever.testing import IntegrationTestCase
from zope.component import adaptedBy


class TestLandscapeLayout(IntegrationTestCase):

    def test_adapts_landscape_request_layer(self):
        adapts = adaptedBy(LandscapeLayout)
        self.assertEqual(len(adapts), 3)
        self.assertEqual(adapts[1], ILandscapeLayer)

    def test_show_contact(self):
        self.login(self.regular_user)
        layout = LandscapeLayout(self.dossier, self.request, PDFBuilder())
        self.assertEqual(layout.get_render_arguments()['show_contact'],
                         False)

    def test_rendering(self):
        self.login(self.regular_user)

        layout = LandscapeLayout(self.dossier, self.request, PDFBuilder())
        latex = layout.render_latex('CONTENT LATEX')

        self.assertIn('CONTENT LATEX', latex)
        self.assertIn(layout.get_packages_latex(), latex)
        self.assertNotIn(r'T direkt ', latex)
        self.assertNotIn(r'\phantom{foo}\vspace{-2\baselineskip}', latex)

    def test_box_sizes_and_positions(self):
        self.login(self.regular_user)

        builder = PDFBuilder()
        builder.add_file('logo.pdf', 'Foo\nBar')

        layout = LandscapeLayout(self.dossier, self.request, builder)
        layout.show_contact = True
        layout.show_organisation = True

        latex = layout.render_latex('LATEX CONTENT')

        self.assertIn(r'begin{textblock}{58mm\TPHorizModule} '
                      r'(220mm\TPHorizModule',
                      latex)

        self.assertIn(r'\begin{textblock}{58mm\TPHorizModule}'
                      r' (220mm\TPHorizModule, 54mm\TPVertModule)',
                      latex)
