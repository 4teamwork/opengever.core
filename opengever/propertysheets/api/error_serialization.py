from opengever.propertysheets import _
from opengever.propertysheets.exceptions import AssignmentAlreadyInUse
from opengever.propertysheets.exceptions import AssignmentValidationError
from opengever.propertysheets.exceptions import FieldValidationError
from opengever.propertysheets.exceptions import SheetValidationError
from opengever.propertysheets.metaschema import IPropertySheetDefinition
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.interfaces import InvalidValue
from zope.schema.interfaces import TooLong
from zope.schema.interfaces import ValidationError


class IErrorInfos(Interface):
    pass


class ErrorSerializer(object):
    """Serialize exceptions for @propertysheets API responses in a
    frontend-friendly way.

    This mainly involves creating a multi-line string for 'translated_message'
    that contains enough context to be displayed at the top of the form,
    without any highlighting of the error field taking place. This message
    must therefore contain enough context to stand on its own, and allow
    the user to find and fix the error.

    Example:

    The form contains errors:
    Field 3 ('location'):
    Parameter 'title': Value is too long
    (Max: 128 characters, Actual length: 135 characters)
    """

    def __init__(self, exc, request):
        self.exc = exc
        self.request = request

    def __call__(self):
        error_adapter = queryMultiAdapter((self.exc, self.request), IErrorInfos)
        if not error_adapter:
            # No propertysheets specific error handling
            raise

        error_infos = error_adapter()

        # Prevent ZPublisher from setting wrong status code
        if isinstance(self.exc, BadRequest):
            self.request.response.setStatus(400, lock=1)

        serialized_error = {
            "message": str(self.exc).decode('utf-8'),
            "type": type(self.exc).__name__.decode('utf-8'),
            "translated_message": self.get_translated_message(**error_infos),
        }
        return serialized_error

    def get_translated_message(self, error_location, error_description, error_extras):
        error_string = '\n'.join([
            error_location,
            error_description,
            error_extras,
        ]).strip()

        message = _(
            u'msg_propertysheet_has_errors',
            default=u"The form contains errors:\n"
                    u"${error_string}",
            mapping={'error_string': error_string})

        return translate(message, context=self.request)


@implementer(IErrorInfos)
class ErrorInfosBase(object):

    def __init__(self, exc, request):
        self.exc = exc
        self.request = request

        self.validation_error = None
        self.unpack_error(exc)

    def __call__(self):
        error_infos = {
            'error_location': self.get_error_location(),
            'error_description': self.get_error_description(),
            'error_extras': self.get_error_extras(),
        }
        return error_infos

    def unpack_error(self, exc):
        """Unpack the given exception's data into a more standardized form.

        Subclasses must implement this, and know how their adapted exception's
        data is structured / nested.
        """
        raise NotImplementedError

    def get_error_location(self):
        """One-line summary of the error's location.
        """
        return u''

    def get_error_description(self):
        """One-line description of the error, with optional prefix for context.
        """
        short_text = self.get_error_short_text()
        prefix = self.get_error_description_prefix()
        return prefix + short_text

    def get_error_short_text(self):
        """Concise message describing only the error.

        For example, "Value too long".
        Defaults to extracting it from the zope.schema ValidationError.
        """
        validation_error = self.get_validation_error()
        return self.extract_error_description(validation_error)

    def get_error_description_prefix(self):
        """Short prefix providing context for the error description (optional).
        """
        return u''

    def get_error_extras(self):
        """One line of extra details about the error (optional).
        """
        return u''

    def get_first_error(self):
        return self.exc.message[0]

    def get_validation_error(self):
        return self.validation_error

    def extract_error_description(self, validation_error):
        """Get a translated, short description of the error from the inner
        exception (usually a zope.schema ValidationError).

        All subclasses of ValidationError have a .doc() method that returns a
        concise, translated error description, like "Value is too long".
        """

        if isinstance(validation_error, ValidationError):
            desc = validation_error.doc()
        else:
            # Otherwise default to the generic "Invalid value"
            desc = InvalidValue().doc()

        return translate(desc, context=self.request)

    def extract_extra_info(self, validation_error):
        """Return one line of extra info about a ValidationError, if more
        context is needed for the user to properly understand and fix the
        error.

        ValidationErrors usually contain information about the offending
        value and the failed constraint in a semi-structed way in exc.args.
        """
        extra_info = u''

        if isinstance(validation_error, TooLong):
            value, max_length = validation_error.args
            extra_info = translate(
                _(u'extra_info_max_length',
                  default=u'(Max: ${max_length} characters. '
                          u'Actual length: ${actual_length} characters)',
                  mapping={
                      'max_length': max_length,
                      'actual_length': len(value),
                  }),
                context=self.request,
            )

        return extra_info


@adapter(FieldValidationError, IBrowserRequest)
class FieldValidationErrorInfos(ErrorInfosBase):

    def unpack_error(self, exc):
        ps_field_no, ps_field_name, field_error = self.get_first_error()
        field_key, validation_error = field_error
        self.validation_error = validation_error
        self.field_key = field_key
        self.propertysheet_field_no = ps_field_no
        self.propertysheet_field_name = ps_field_name

    def get_error_location(self):
        """Location line with propertysheet field number and name.
        """
        error_location = _(
            u'msg_propertysheet_field_location',
            default=u"Field ${field_no} ('${field_name}'):",
            mapping={
                'field_no': self.propertysheet_field_no + 1,
                'field_name': self.propertysheet_field_name,
            })
        return translate(error_location, context=self.request)

    def get_error_description_prefix(self):
        """Prefix with the offending key of the propertysheet field dict.
        """
        if self.field_key is not None:
            prefix = _(
                u'msg_propertysheet_field_error_prefix',
                default=u"Parameter '${field_key}': ",
                mapping={
                    'field_key': self.field_key,
                })
            return translate(prefix, context=self.request)

        return u''

    def get_error_extras(self):
        return self.extract_extra_info(self.get_validation_error())


@adapter(AssignmentValidationError, IBrowserRequest)
class AssignmentValidationErrorInfos(ErrorInfosBase):

    def unpack_error(self, exc):
        self.validation_error = self.get_first_error()

    def get_error_location(self):
        field = IPropertySheetDefinition['assignments']
        error_location = translate(
            field.title,
            context=self.request,
        ) + u':'
        return error_location

    def get_error_short_text(self):
        validation_exc = self.get_validation_error()
        error_description = self.extract_error_description(validation_exc)

        if isinstance(validation_exc, AssignmentAlreadyInUse):
            # Provide a custom, more helpful error message for this
            error_description = translate(
                _(u'msg_assignment_already_in_use',
                  default=u"Assignment '${assignment}' is already in use.",
                  mapping={'assignment': validation_exc.message['assignment']}),
                context=self.request,
            )

        return error_description


@adapter(SheetValidationError, IBrowserRequest)
class SheetValidationErrorInfos(ErrorInfosBase):

    def unpack_error(self, exc):
        field_name, validation_error = self.get_first_error()
        self.validation_error = validation_error
        self.field_name = field_name

    def get_error_location(self):
        # We currently only raise SheetValidationError for ID field errors.
        field = IPropertySheetDefinition['id']
        error_location = translate(
            field.title,
            context=self.request,
        ) + u':'
        return error_location

    def get_error_extras(self):
        return self.extract_extra_info(self.get_validation_error())
