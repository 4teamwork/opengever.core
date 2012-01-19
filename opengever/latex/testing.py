from grokcore.component.testing import grok
from plone.testing import Layer
from plone.testing import zca
from zope.configuration import xmlconfig


class LatexZCMLLayer(Layer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def testSetUp(self):
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'))
        config = self['configurationContext']

        import ftw.pdfgenerator.tests
        xmlconfig.file('test.zcml', ftw.pdfgenerator.tests, config)
        import ftw.pdfgenerator
        xmlconfig.file('configure.zcml', ftw.pdfgenerator, config)

        import five.grok
        xmlconfig.file('meta.zcml', five.grok, config)

        grok('opengever.latex')

    def testTearDown(self):
        del self['configurationContext']


LATEX_ZCML_LAYER = LatexZCMLLayer()
