from zope.interface import Interface
from zope.schema import TextLine


class IAddressBlockData(Interface):

    salutation = TextLine()
    academic_title = TextLine()
    first_name = TextLine()
    last_name = TextLine()

    org_name = TextLine()

    street_and_no = TextLine()
    po_box = TextLine()

    postal_code = TextLine()
    city = TextLine()
