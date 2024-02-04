from datetime import timedelta
from opengever.base.date_time import utcnow_tz_aware
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.base import DOSSIER_STATE_RESOLVED
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import invariant
from zope.interface import provider
from zope.interface.exceptions import Invalid
from zope.schema import ASCIILine
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Datetime
from zope.schema import List
from zope.schema import Text
from zope.schema import TextLine
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import os


@provider(IContextSourceBinder)
def valid_target_admin_units(context):
    if allow_same_unit():
        vocab = 'opengever.ogds.base.all_admin_units'
    else:
        vocab = 'opengever.ogds.base.all_other_admin_units'

    vf = getUtility(IVocabularyFactory, name=vocab)
    return vf(context)


def valid_root_dossier(root_uid):
    obj = api.content.uuidToObject(root_uid)
    if IDossierMarker.providedBy(obj):
        if api.content.get_state(obj) == DOSSIER_STATE_RESOLVED:
            return True
    raise InvalidRootDossier()


@provider(IContextSourceBinder)
def valid_document_uids(context):
    valid_uids = []
    root_uid = context.get('root')
    if root_uid:
        root_dossier = api.content.uuidToObject(root_uid)
        valid_docs = api.content.find(
            context=root_dossier,
            object_provides=IBaseDocument,
        )
        valid_uids = [doc.UID for doc in valid_docs]

    return SimpleVocabulary([SimpleTerm(uid, uid) for uid in valid_uids])


def valid_expires(expires):
    if expires < utcnow_tz_aware():
        raise ExpiresInPast()

    if expires > (utcnow_tz_aware() + timedelta(days=31)):
        raise ExpiresTooFarInFuture()

    return True


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
        constraint=valid_expires,
    )
    target = Choice(
        title=u'Target admin unit',
        required=True,
        source=valid_target_admin_units,
    )
    root = ASCIILine(
        title=u'Root dossier UID',
        required=True,
        constraint=valid_root_dossier,
    )
    documents = List(
        title=u'List of document UIDs',
        required=False,
        value_type=Choice(
            title=u'Document UID',
            source=valid_document_uids,
        ),
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
        if allow_same_unit():
            return

        source = self.source
        if not source:
            source = get_current_admin_unit().unit_id

        if source == self.target:
            raise SourceSameAsTarget()

    @invariant
    def all_docs_and_docs_list(self):
        if self.all_documents:
            if getattr(self, 'documents', None) is not None:
                raise AllDocsAndDocsListMutuallyExclusive()
        else:
            if getattr(self, 'documents', None) is None:
                raise DocsListRequired()

    @invariant
    def all_participations_and_participations_list(self):
        if self.all_participations:
            if getattr(self, 'participations', None) is not None:
                raise AllParticipationsAndParticipationsListMutuallyExclusive()
        else:
            if getattr(self, 'participations', None) is None:
                raise ParticipationsListRequired()


class SourceSameAsTarget(Invalid):
    """Source admin unit must not be the same as target.
    """


class AllDocsAndDocsListMutuallyExclusive(Invalid):
    """'all_documents == true' and 'documents' list are mutually exclusive.
    """


class DocsListRequired(Invalid):
    """'documents' list is required if 'all_documents' is false.
    """


class AllParticipationsAndParticipationsListMutuallyExclusive(Invalid):
    """'all_participations == true' and 'participations' list are mutually exclusive.
    """


class ParticipationsListRequired(Invalid):
    """'participations' list is required if 'all_participations' is false.
    """


class InvalidRootDossier(ConstraintNotSatisfied):
    """Root dossier with that UID does not exist or is not resolved.
    """


class ExpiresInPast(ConstraintNotSatisfied):
    """'expires' must not be in the past.
    """


class ExpiresTooFarInFuture(ConstraintNotSatisfied):
    """'expires' must not be more than 30 days in the future.
    """


def allow_same_unit():
    """This flag is used to simplify (human and software) testing:

    It allows to select the current admin unit as target, and
    lifts the requirement that target and source are not the same.
    """
    return bool(os.environ.get('GEVER_DOSSIER_TRANSFERS_ALLOW_SAME_AU', False))
