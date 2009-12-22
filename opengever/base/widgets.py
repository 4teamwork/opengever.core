""" Commen widget stuff
"""

from five import grok
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from z3c.form.interfaces import IFieldWidget
from zope.schema.interfaces import ISequence, ITextLine
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


@grok.implementer(IFieldWidget)
@grok.adapter(ISequence, ITextLine, IDefaultBrowserLayer)
def SequenceTextLinesFieldWidget(field, value_type, request):
    """ There is no default sequence widget for TextLine types
    """
    return TextLinesFieldWidget(field, request)
