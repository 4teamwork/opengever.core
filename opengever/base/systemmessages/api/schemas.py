from zope.component import getUtility
from zope.interface import Interface
from zope.interface import invariant
from zope.interface import provider
from zope.interface.exceptions import Invalid
from zope.schema import Choice
from zope.schema import Datetime
from zope.schema import Text
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory


STATIC_TYPE_CHOICES = ["info", "warning", "error"]


@provider(IContextSourceBinder)
def validate_admin_unit(context):
    vocab = 'opengever.ogds.base.all_admin_units'
    vf = getUtility(IVocabularyFactory, name=vocab)
    return vf(context)


class ISystemMessageAPISchema(Interface):

    admin_unit = Choice(
        title=u'admin unit',
        required=False,
        source=validate_admin_unit,
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
    start = Datetime(
        title=u'start',
        required=True
    )
    end = Datetime(
        title=u'end',
        required=True,
    )
    type = Choice(
        title=u'type',
        values=STATIC_TYPE_CHOICES,
        required=True
    )

    @invariant
    def validate_end_data(self):
        """Validate that the end day is bigger than the start day"""
        if self.end < self.start:
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
