from five import grok
from ftw.pdfgenerator.interfaces import IBuilder
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.layouts.default import DefaultLayout
from zope.interface import Interface


class LandscapeLayout(DefaultLayout):
    grok.adapts(Interface, ILandscapeLayer, IBuilder)

    template_name = 'landscape.tex'

    def __init__(self, context, request, builder):
        super(LandscapeLayout, self).__init__(context, request, builder)
        self.show_contact = False
