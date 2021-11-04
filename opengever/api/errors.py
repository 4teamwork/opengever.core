from opengever.base import _
from plone.rest.errors import ErrorHandling
from plone.rest.interfaces import IAPIRequest
from zope.component import adapter
from zope.i18n import translate
from zope.i18nmessageid.message import Message


@adapter(Exception, IAPIRequest)
class GeverErrorHandling(ErrorHandling):

    def render_exception(self, exception):
        result = super(GeverErrorHandling, self).render_exception(exception)

        # Validation errors
        if isinstance(exception.message, list):
            fields = []
            for error in exception.message:
                fields.append({
                    'field': error['field'],
                    'type': str(error['error']).decode('utf-8'),
                    'translated_message': translate(
                        error['message'], context=self.request)
                })

            result['additional_metadata'] = {'fields': fields}
            result['translated_message'] = translate(
                _('msg_inputs_not_valid', default=u'Inputs not valid'),
                context=self.request)

        elif isinstance(exception.message, Message):
            result['additional_metadata'] = {}
            result['translated_message'] = translate(
                exception.message, context=self.request)

        return result
