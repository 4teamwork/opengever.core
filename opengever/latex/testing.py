from ftw.testing.layer import ComponentRegistryLayer
from grokcore.component.testing import grok
from plone.testing import zca


class LatexZCMLLayer(ComponentRegistryLayer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def setUp(self):
        super(LatexZCMLLayer, self).testSetUp()

        import ftw.pdfgenerator.tests
        self.load_zcml_file('test.zcml', ftw.pdfgenerator.tests)
        import ftw.pdfgenerator
        self.load_zcml_file('configure.zcml', ftw.pdfgenerator)

        import five.grok
        self.load_zcml_file('meta.zcml', five.grok)

        grok('opengever.latex')


LATEX_ZCML_LAYER = LatexZCMLLayer()
