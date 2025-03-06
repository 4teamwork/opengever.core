from opengever.api import _
from plone.rest.errors import ErrorHandling
from plone.rest.interfaces import IAPIRequest
from zope.component import adapter
from zope.i18n import translate
from zope.i18nmessageid.message import Message


@adapter(Exception, IAPIRequest)
class GeverErrorHandling(ErrorHandling):

    def render_exception(self, exception):
        result = super(GeverErrorHandling, self).render_exception(exception)
        try:
            result = self.extend_with_translation(result, exception.message)
        except Exception:
            pass

        return result

    def extend_with_translation(self, result, message):
        if isinstance(message, list):
            # Handle TUS error
            if len(message) and not message[0].get('field'):
                result['additional_metadata'] = {}
                result['translated_message'] = translate(
                    message[0].get('message'), context=self.request)
                return result

            # Validation errors
            fields = []
            for error in message:
                fields.append({
                    'field': error.get('field'),
                    'type': str(error.get('error', '')).decode('utf-8'),
                    'translated_message': translate(
                        error.get('message'), context=self.request)
                })
                # bundle validation
                if error.get("item_title"):
                    fields[-1]["item_title"] = error.get("item_title")

            result['additional_metadata'] = {'fields': fields}

            result['translated_message'] = translate(
                message[0].get('message'),
                context=self.request)

        elif isinstance(message, Message):
            result['additional_metadata'] = {}
            result['translated_message'] = translate(
                message, context=self.request)

        return result
