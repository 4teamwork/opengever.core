from five import grok
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITextAreaWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import ITextLine


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
