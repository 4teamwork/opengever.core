from opengever.base.interfaces import IReferenceNumber
from plone.restapi.services import Service


class ReferenceNumber(object):
    """Return reference number information for an object."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        url = u"{}/@reference-number".format(self.context.absolute_url())
        result = {
            "reference-number": {
                "@id": url,
            },
        }

        if not expand:
            return result

        ref_num = IReferenceNumber(self.context)
        reference = {
            "parts": ref_num.get_numbers(),
            "reference_number": ref_num.get_number(),
            "sortable_reference_number": ref_num.get_sortable_number(),
        }

        result["reference-number"].update(reference)
        return result


class ReferenceNumberGet(Service):
    """API Endpoint to return reference number information.

    GET folder-1/@reference-number HTTP/1.1
    """

    def reply(self):
        reference_number = ReferenceNumber(self.context, self.request)
        return reference_number(expand=True)["reference-number"]
