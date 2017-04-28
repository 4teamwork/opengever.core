from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldDeserializer
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import IFromUnicode


@implementer(IFieldDeserializer)
@adapter(IChoice, IDexterityContent, IBrowserRequest)
class ChoiceFieldDeserializer(object):

    def __init__(self, field, context, request):
        self.field = field
        self.context = context
        self.request = request

    def __call__(self, value):

        # Proper initialization of IContextSourceBinder
        # Check zope.schema IChoice field bind method.
        cloned_field = self.field.bind(self.context)

        if not isinstance(value, unicode):
            return value
        return IFromUnicode(cloned_field).fromUnicode(value)
