from five import grok
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from z3c.form.converter import BaseDataConverter
from zope.schema.interfaces import IField
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITextAreaWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.component import adapts
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import ITextLine
from plone import api


@grok.implementer(IFieldWidget)
@grok.adapter(ISequence, ITextLine, IDefaultBrowserLayer)
def SequenceTextLinesFieldWidget(field, value_type, request):
    """ There is no default sequence widget for TextLine types
    """
    return TextLinesFieldWidget(field, request)


class ITrixWidget(ITextAreaWidget):
    """Text area widget with trix."""


class TrixWidget(Widget):
    """Textarea widget with trix implementation."""
    implementsOnly(ITrixWidget)


@adapter(ITrixWidget, IFormLayer)
@implementer(IFieldWidget)
def TrixFieldWidget(field, request):
    """IFieldWidget factory for TrixWidget."""

    return FieldWidget(field, TrixWidget(request))


class TrixDataConverter(BaseDataConverter):
    """Convert trix input to safe html."""

    adapts(IField, ITrixWidget)

    def __init__(self, field, widget):
        super(TrixDataConverter, self).__init__(field, widget)
        self.transformer = api.portal.get_tool('portal_transforms')

    def toFieldValue(self, value):
        safe_html = self.transformer.convert('safe_html', value).getData()
        return super(TrixDataConverter, self).toFieldValue(safe_html)
