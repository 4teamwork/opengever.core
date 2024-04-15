from zope.interface import Interface
from zope.interface import invariant
from zope.interface.exceptions import Invalid
from zope.schema import Choice
from zope.schema import Datetime
from zope.schema import Text


STATIC_TYPE_CHOICES = ["info", "warning", "error"]


class ISystemMessageAPISchema(Interface):

    admin_unit = Choice(
        title=u'admin unit',
        required=False,
        vocabulary='opengever.ogds.base.all_admin_units',
    )
    text_en = Text(
        title=u'text_en',
        required=False,
        max_length=200
    )
    text_de = Text(
        title=u'text_de',
        required=False,
        max_length=200
    )
    text_fr = Text(
        title=u'text_fr',
        required=False,
        max_length=200
    )
    start_ts = Datetime(
        title=u'start',
        required=True
    )
    end_ts = Datetime(
        title=u'end',
        required=True,
    )
    type = Choice(
        title=u'type',
        values=STATIC_TYPE_CHOICES,
        required=True
    )

    @invariant
    def validate_end_date(self):
        """Validate that the end day is bigger than the start_ts day"""
        if self.end_ts < self.start_ts:
            raise InvalidEndDate()
        return True

    @invariant
    def validate_text_fields(self):
        """Make sure at least one of the text fields has a value"""
        if not any([self.text_en, self.text_de, self.text_fr]):
            raise TextFieldMissing()
        return True


class InvalidEndDate(Invalid):
    """The message end date must be bigger than the start date"""


class TextFieldMissing(Invalid):
    """"At least one of the text fields (text_en, text_de, text_fr) must have a value"""
