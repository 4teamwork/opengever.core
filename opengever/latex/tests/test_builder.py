from distutils.spawn import find_executable
from ftw.pdfgenerator.interfaces import IBuilderFactory
from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING
from opengever.core.testing import PDFLATEX_SERVICE_INTEGRATION_TESTING
from opengever.testing import IntegrationTestCase
from unittest import skipIf
from zope.component import getUtility


HAS_PDFLATEX = find_executable('pdflatex')


class TestPDFBuilderUsingService(IntegrationTestCase):

    layer = PDFLATEX_SERVICE_INTEGRATION_TESTING

    def test_pdfbuilder_produces_pdf_using_service(self):
        builder = getUtility(IBuilderFactory)()
        latex = r'\documentclass{article}\begin{document}Hello LaTeX\end{document}'
        pdf = builder.build(latex)
        self.assertTrue(
            pdf.startswith('%PDF-1.'), 'Does not look like a PDF document')

    def test_pdfbuilder_produces_zip_using_service(self):
        builder = getUtility(IBuilderFactory)()
        latex = r'\documentclass{article}\begin{document}Hello LaTeX\end{document}'
        archive = builder.build_zip(latex).read()
        self.assertTrue(
            archive.startswith('PK\x03\x04'), 'Does not look like a ZIP archive')


@skipIf(not HAS_PDFLATEX, 'pdflatex is required')
class TestPDFBuilderUsingExecutable(IntegrationTestCase):

    layer = OPENGEVER_INTEGRATION_TESTING

    def test_pdfbuilder_produces_pdf_using_executable(self):
        builder = getUtility(IBuilderFactory)()
        latex = r'\documentclass{article}\begin{document}Hello LaTeX\end{document}'
        pdf = builder.build(latex)
        self.assertTrue(
            pdf.startswith('%PDF-1.'), 'Does not look like a PDF document')

    def test_pdfbuilder_produces_zip_using_executable(self):
        builder = getUtility(IBuilderFactory)()
        latex = r'\documentclass{article}\begin{document}Hello LaTeX\end{document}'
        archive = builder.build_zip(latex).read()
        self.assertTrue(
            archive.startswith('PK\x03\x04'), 'Does not look like a ZIP archive')
