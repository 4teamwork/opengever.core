from opengever.base.adapters import ReferenceNumberPrefixAdpater
from opengever.base.exceptions import ReferenceNumberCannotBeFreed
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class ReferenceNumbersGet(Service):
    """API endpoint to get a list of repository numbers used or locked on the
    current context.

    GET /repository_folder/@reference-numbers
    """

    def reply(self):
        return ReferenceNumberPrefixAdpater(self.context).get_number_mapping(
            missing_title_as_none=True)


class ReferenceNumbersDelete(Service):
    """API endpoint to unlock a repository number on the current context.

    DELETE /repository_folder/@reference-numbers/1 HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ReferenceNumbersDelete, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, number):
        # Consume any path segments after /@reference-numbers as parameters
        self.params.append(number)
        return self

    def read_params(self):
        if len(self.params) == 0:
            raise BadRequest("Must supply a reference number as URL path parameter.")

        if len(self.params) > 1:
            raise BadRequest("Only reference number is supported as URL path parameter.")

        return self.params[0]

    def reply(self):
        number = self.read_params()
        manager = ReferenceNumberPrefixAdpater(self.context)
        try:
            manager.free_number(number)
        except ReferenceNumberCannotBeFreed:
            raise BadRequest("Number still in use.")
        return self.reply_no_content()
