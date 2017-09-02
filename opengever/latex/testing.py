from ftw.testing.layer import ComponentRegistryLayer
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

        import Products.GenericSetup
        self.load_zcml_file('meta.zcml', Products.GenericSetup)

        import opengever.latex
        self.load_zcml_file('configure.zcml', opengever.latex)


LATEX_ZCML_LAYER = LatexZCMLLayer()
