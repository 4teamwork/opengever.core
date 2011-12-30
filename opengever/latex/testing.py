from ftw.pdfgenerator.testing import PDFGENERATOR_ZCML_LAYER
from plone.testing import Layer


class LatexZCMLLayer(Layer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (PDFGENERATOR_ZCML_LAYER,)


LATEX_ZCML_LAYER = LatexZCMLLayer()
