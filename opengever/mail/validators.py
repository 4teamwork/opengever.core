import re

from plone.registry.interfaces import IRegistry
from z3c.form import validator
from zope import schema
from zope.component import queryUtility

from opengever.mail import _
from opengever.mail.interfaces import ISendDocumentConf
from ftw.mail.mail import IMail

EMAIL_REGEX = re.compile(
    r"^(\w&.%#$&'\*+-/=?^_`{}|~]+!)*[\w&.%#$&'\*+-/=?^_`{}|~]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$",
    re.IGNORECASE)


class FilesTooLarge(schema.interfaces.ValidationError):
    """ Total size of selected files is too large. """

    __doc__ = _(u"The files you selected are larger than the maximum size")


class DocumentSizeValidator(validator.SimpleFieldValidator):
    """ Check if the total size of the documents isn't larger than the
    `max_size` configured in the registry.
    """

    def validate(self, value):
        if value:
            if self.request.get(
                'form.widgets.documents_as_links') != ['selected']:
                registry = queryUtility(IRegistry)
                reg_proxy = registry.forInterface(ISendDocumentConf)
                total = 0
                for obj in value:
                    #check if its a mail
                    if IMail.providedBy(obj):
                        total += obj.message.getSize()
                    elif obj.file:
                        total += obj.file.getSize()
                if total > (reg_proxy.max_size * 1000000):
                    raise FilesTooLarge()
        else:
            raise schema.interfaces.RequiredMissing()


class AddressValidator(validator.SimpleFieldValidator):
    """ Check all e-mail addresses are valid/plausible according to
    the given regex."""

    def validate(self, value):
        """ validates the given email addresses """
        if value:
            for address in value:
                if not EMAIL_REGEX.match(address):
                    raise schema.interfaces.InvalidValue()
