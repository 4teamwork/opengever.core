from opengever.ogds.base.utils import get_current_admin_unit
from zope.interface import Interface
from zope.interface import invariant
from zope.interface.exceptions import Invalid
from zope.schema import ASCIILine
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Datetime
from zope.schema import List
from zope.schema import Text
from zope.schema import TextLine


class IDossierTransferAPISchema(Interface):
    """Schema to describe DossierTransfer API.
    """

    title = TextLine(
        title=u'Title',
        required=True,
    )
    message = Text(
        title=u'Message',
        default=u'',
        required=False,
    )
    created = Datetime(
        title=u'Created',
        required=False,
    )
    expires = Datetime(
        title=u'Expires',
        required=True,
    )
    target = Choice(
        title=u'Target admin unit',
        required=True,
        vocabulary='opengever.ogds.base.all_other_admin_units',
    )
    root = ASCIILine(
        title=u'Root dossier UID',
        required=True,
    )
    documents = List(
        title=u'List of document UIDs',
        required=False,
        value_type=ASCIILine(),
    )
    participations = List(
        title=u'List of participation IDs',
        required=False,
        value_type=ASCIILine(),
    )
    all_documents = Bool(
        title=u'Whether all documents should be transferred',
        required=True,
    )
    all_participations = Bool(
        title=u'Whether all participations should be transferred',
        required=True,
    )

    @invariant
    def source_and_target_unit_must_not_be_the_same(self):
        source = self.source
        if not source:
            source = get_current_admin_unit().unit_id

        if source == self.target:
            raise SourceSameAsTarget()


class SourceSameAsTarget(Invalid):
    """Source admin unit must not be the same as target.
    """
