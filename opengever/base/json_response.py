import json
from zope.i18n import translate
from opengever.base import _


class JSONResponse(object):
    """
    This class allows to generate a GEVER wide standardized JSON Response.
    JSONResponse can create messages or custom data. To get the client to
    know if something went wrong the response can get ended up with remain
    or proceed flags.
    JSONResponse is used as a builder.
    The client side implementation is done in
    opengever.base.browser.resources.MessageFactory
    """

    def __init__(self, request):
        self.request = request
        self.response = {}
        self.status = None

    def info(self, message):
        """
        Append a standardized info message with given message.
        """
        message = {
            'messageClass': 'info',
            'messageTitle': translate(_('message_title_info',
                                        default=u"Information"),
                                      context=self.request),
            'message': translate(message, context=self.request),
        }
        self.response['messages'] = self.response.get('messages', []) + [message]
        return self

    def warning(self, message):
        """
        Append a standardized warning message with given message.
        """
        message = {
            'messageClass': 'warning',
            'messageTitle': translate(_('message_title_warning',
                                        default=u"Warning"),
                                      context=self.request),
            'message': translate(message, context=self.request),
        }
        self.response['messages'] = self.response.get('messages', []) + [message]
        return self

    def error(self, message, status=None):
        """
        Append a standardized error message with given message.
        """
        self.status = status

        message = {
            'messageClass': 'error',
            'messageTitle': translate(_('message_title_error',
                                        default=u"Error"),
                                      context=self.request),
            'message': translate(message, context=self.request),
        }
        self.response['messages'] = self.response.get('messages', []) + [message]
        return self

    def data(self, **kwargs):
        """
        Append custom data as kwargs.
        """
        assert 'messages' not in kwargs, 'key message is not allowed for JSON responses'
        assert 'proceed' not in kwargs, 'key proceed is not allowed for JSON responses'
        self.response.update(kwargs)
        return self

    def redirect(self, redirect_url):
        """
        Define redirect_url
        """
        self.response['redirectUrl'] = redirect_url
        return self

    def proceed(self):
        """
        Set the proceed flag to True to say the client that everthing went okay.
        """
        self.response['proceed'] = True
        return self

    def remain(self):
        """
        Set the proceed flag to False to say the client that something went wrong.
        """
        self.response['proceed'] = False
        return self

    def dump(self, no_cache=True):
        """Return a JSON string for use as response, set response headers.

        The dump method sets the response headers.
        It expects that excatly this payload is returned in the response.
        By default, no-caching headers are set on the response.
        This can be disabled by setting ``no_cache`` to ``False``.
        """
        if self.status:
            self.request.response.setStatus(self.status)

        if no_cache:
            self.request.response.setHeader("Cache-Control", "no-store")
            self.request.response.setHeader("Pragma", "no-cache")
            self.request.response.setHeader("Expires", "0")

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(self.response)
