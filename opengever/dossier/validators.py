import re
from zope import schema
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from z3c.form import validator

from opengever.document import _
from opengever.document.interfaces import ISendDocumentConf

EMAIL_REGEX = re.compile(
    r"^(\w&.%#$&'\*+-/=?^_`{}|~]+!)*[\w&.%#$&'\*+-/=?^_`{}|~]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$",
    re.IGNORECASE)


class ToBigFiles(schema.interfaces.ValidationError):
    """ The to big Files Exception. """
    
    __doc__= _(
        u"The Files you selected are bigger than the maximal Size"
    )



class DocumentSizeValidator(validator.SimpleFieldValidator):
    """ Check if the Total size of the documents isn't bigger than the 

    max_size was configured in the registry
    
    """

    def validate(self, value):
        if value:
            registry = queryUtility(IRegistry)
            reg_proxy = registry.forInterface(ISendDocumentConf)
            total = 0

            for doc in value:
                if doc.file:
                    total += doc.file.getSize()
            if total > (reg_proxy.max_size * 1000000):
                raise ToBigFiles()
        else:
            raise schema.interfaces.RequiredMissing()

class AddressValidator(validator.SimpleFieldValidator):
    """ Check all Mail addresses in the given list. """

    def validate(self, value):
        """ validates the given email addresses """
        if value:
            for address in value:
                if not EMAIL_REGEX.match(address):
                    raise schema.interfaces.InvalidValue()
