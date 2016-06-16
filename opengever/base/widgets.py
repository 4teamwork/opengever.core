from five import grok
from plone import api
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from z3c.form.converter import BaseDataConverter
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
from zope.schema.interfaces import IField
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import ITextLine
import re


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


# markup processed by trix is always wrapped in a single container div
RE_TRIX_LEADING_WHITESPACE = re.compile(
    ur"^<div>(&nbsp;|<br\s*/?>|\s)*", re.UNICODE)
RE_TRIX_TRAILING_WHITESPACE = re.compile(
    ur"(&nbsp;|<br\s*/?>|\s)*</div>$", re.UNICODE)


def trix_strip_whitespace(string):
    """Strip whitespace from a string.

    The string will contain markup supplied by trix, thus consecutive
    space characters will be encoded as &nbsp;.
    """
    if not string:
        return string

    lstripped = RE_TRIX_LEADING_WHITESPACE.sub(u"<div>", string)
    rstripped = RE_TRIX_TRAILING_WHITESPACE.sub(u"</div>", lstripped)
    return rstripped


class TrixDataConverter(BaseDataConverter):
    """Convert trix input to safe html."""

    adapts(IField, ITrixWidget)

    def __init__(self, field, widget):
        super(TrixDataConverter, self).__init__(field, widget)
        self.transformer = api.portal.get_tool('portal_transforms')

    def toFieldValue(self, value):
        safe_html = self.transformer.convert('trix_to_sablon', value).getData()
        # transform may return non-unicode empty string which raises validation
        # errors on the field
        safe_html = safe_html or u''
        field_value = self.field.fromUnicode(safe_html)
        return trix_strip_whitespace(field_value)
