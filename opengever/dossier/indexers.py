from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.base.response import IResponseContainer
from opengever.base.utils import ensure_str
from opengever.contact.sources import PloneSqlOrKubContactSourceBinder
from opengever.document.behaviors.name_from_title import DOCUMENT_NAME_PREFIX
from opengever.dossier import _
from opengever.dossier import is_dossier_checklist_feature_enabled
from opengever.dossier.behaviors.customproperties import IDossierCustomProperties
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.behaviors.filing import IFilingNumberMarker
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from opengever.dossier.browser.participants import translate_participation_role
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.dossier.participations import IParticipationData
from opengever.dossier.resolve import AfterResolveJobs
from opengever.dossier.utils import get_main_dossier
from opengever.inbox.inbox import IInbox
from opengever.private.dossier import IPrivateDossier
from plone import api
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.schema import getFields


@indexer(IDossierMarker)
def after_resolve_jobs_pending_indexer(obj):
    pending = AfterResolveJobs(obj).after_resolve_jobs_pending
    return pending


@indexer(IDossierMarker)
def DossierSubjectIndexer(obj):
    aobj = IDossier(obj)
    return aobj.keywords


@indexer(IDossierMarker)
def startIndexer(obj):
    aobj = IDossier(obj)
    if aobj.start is None:
        return None
    return aobj.start


@indexer(IDossierMarker)
def endIndexer(obj):
    aobj = IDossier(obj)
    if aobj.end is None:
        return None
    return aobj.end


@indexer(IDossierMarker)
def retention_expiration(obj):
    if IPrivateDossier.providedBy(obj):
        # Private dossiers don't have the Lifecycle behavior, and therefore
        # don't have a retention period, or expiration thereof
        return None
    return obj.get_retention_expiration_date()


@indexer(IDossierMarker)
def responsibleIndexer(obj):
    aobj = IDossier(obj)
    if aobj.responsible is None:
        return None
    return aobj.responsible


@indexer(IDossierMarker)
def external_reference(obj):
    """Return the external reference of a dossier."""
    context = aq_inner(obj)
    return IDossier(context).external_reference


@indexer(IDossierMarker)
def blocked_local_roles(obj):
    """Return whether acquisition is blocked or not."""
    return bool(getattr(aq_inner(obj), '__ac_local_roles_block__', False))


@indexer(IDossierMarker)
def has_sametype_children(obj):
    """Optimized indexer for dossiers that prevents loading documents.

    It skips all objects that are obviously documents based on their key.
    This potentially prevents loading all document objects of a dossier into
    memory.
    """
    for key in obj.objectIds(ordered=False):
        if key.startswith(DOCUMENT_NAME_PREFIX):
            continue
        if getattr(obj[key], "portal_type") == obj.portal_type:
            return True

    return False


@indexer(IDossierMarker)
def dossier_type(obj):
    return IDossier(obj).dossier_type


@indexer(IDossierMarker)
def progress(obj):
    """Returns the current progress of the dossier.

    We need to differ between a checklist without any closed items or
    a dossier without a checklist at all. We do this by returning "None"
    if there are no items and 0 if there are items but none of them are closed.

    The frontend is able to render different ui-elements for dossiers with or
    without checklists.
    """
    if not is_dossier_checklist_feature_enabled() or not obj.has_checklist_items():
        return None
    return obj.progress()


@indexer(IDossierMarker)
def document_count(obj):
    DOCUMENT_TYPES = (
        'opengever.document.document',
        'ftw.mail.mail',
    )
    catalog = getToolByName(obj, 'portal_catalog')
    brains = catalog.unrestrictedSearchResults(
        {
            'path': {'query': '/'.join(obj.getPhysicalPath()), 'depth': -1},
            'portal_type': DOCUMENT_TYPES,
            'trashed': False,
        }
    )

    return len(brains)


TYPES_WITH_CONTAINING_DOSSIER_INDEX = set(('opengever.dossier.businesscasedossier',
                                           'opengever.meeting.proposal',
                                           'opengever.workspace.folder',
                                           'opengever.document.document',
                                           'opengever.task.task',
                                           'opengever.private.dossier',
                                           'ftw.mail.mail',
                                           'opengever.meeting.meetingdossier',
                                           'opengever.workspace.workspace'))


@indexer(IDexterityContent)
def main_dossier_title(obj):
    """Return the title of the main dossier."""
    if obj.portal_type not in TYPES_WITH_CONTAINING_DOSSIER_INDEX:
        return None

    dossier = get_main_dossier(obj)
    if not dossier:
        return None
    try:
        title = dossier.Title()
    except TypeError:
        # XXX: During upgrades, the odd case can happen that a mail inside a
        # forwarding inside the inbox wants to have its containing_dossier
        # reindexed. This can lead to a situation where we attempt to adapt
        # the Inbox to ITranslatedTitle, but it doesn't provide this behavior
        # yet because that behavior is going to be actived in the very same
        # upgrade.
        #
        # Account for this case, and fall back to inbox.title, which
        # will contain the original title (in unicode though).
        if IInbox.providedBy(dossier):
            title = dossier.title.encode('utf-8')
        else:
            raise
    return title


TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX = ('opengever.document.document',
                                          'opengever.task.task',
                                          'ftw.mail.mail')


@indexer(IDexterityContent)
def containing_subdossier(obj):
    """Returns the title of the subdossier the object is contained in,
    unless it's contained directly in the root of a dossier, in which
    case an empty string is returned.
    """
    if obj.portal_type not in TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX:
        return ''

    context = aq_inner(obj)

    parent = context
    parent_dossier = None
    parent_dossier_found = False
    while not parent_dossier_found:
        parent = aq_parent(parent)
        if ISiteRoot.providedBy(parent):
            # Shouldn't happen, just to be safe
            break
        if IDossierMarker.providedBy(parent) or IDossierTemplateMarker.providedBy(parent):
            parent_dossier_found = True
            parent_dossier = parent

    if parent_dossier and parent_dossier.is_subdossier():
        return parent_dossier.Title()
    return ''


TYPES_WITH_DOSSIER_REVIEW_STATE_INDEX = set(('opengever.dossier.businesscasedossier',
                                             'opengever.meeting.proposal',
                                             'opengever.ris.proposal',
                                             'opengever.document.document',
                                             'opengever.task.task',
                                             'opengever.private.dossier',
                                             'ftw.mail.mail',
                                             'opengever.meeting.meetingdossier'))


@indexer(IDexterityContent)
def dossier_review_state(obj):
    """Returns the review state of the current dossier or of the dossier of
    which the current content is contained in.
    """
    if obj.portal_type not in TYPES_WITH_DOSSIER_REVIEW_STATE_INDEX:
        return ''

    while obj and not ISiteRoot.providedBy(obj):
        if IDossierMarker.providedBy(obj):
            return api.content.get_state(obj)
        obj = aq_parent(aq_inner(obj))
    return ''


@indexer(IDossierMarker)
def is_subdossier(obj):
    return obj.is_subdossier()


@implementer(dexteritytextindexer.IDynamicTextIndexExtender)
@adapter(IDossierMarker)
class SearchableTextExtender(object):
    """Provide full text searching for dossiers."""

    def __init__(self, context):
        self.context = context

    def __call__(self):
        searchable = []
        # append some other attributes to the searchableText index
        # reference_number
        refNumb = getAdapter(self.context, IReferenceNumber)
        searchable.append(refNumb.get_number())

        # sequence_number
        seqNumb = getUtility(ISequenceNumber)
        searchable.append(str(seqNumb.get_number(self.context)))

        # responsible
        searchable.append(self.context.responsible_label.encode('utf-8'))

        # filing_no
        if IFilingNumberMarker.providedBy(self.context):
            filing_no = getattr(IFilingNumber(self.context), 'filing_no', None)
            if filing_no:
                searchable.append(filing_no.encode('utf-8'))

        # keywords
        keywords = IDossier(self.context).keywords
        if keywords:
            searchable.extend(
                keyword.encode('utf-8') if isinstance(keyword, unicode)
                else keyword
                for keyword in keywords)

        searchable_external_reference = IDossier(self.context).external_reference
        if searchable_external_reference:
            searchable.append(searchable_external_reference.encode('utf-8'))

        # comments stored in the response container
        for response in IResponseContainer(self.context):
            searchable.append(response.text.encode('utf-8'))

        # custom properties
        custom_properties = IDossierCustomProperties(self.context).custom_properties
        if custom_properties:
            field = getFields(IDossierCustomProperties).get('custom_properties')
            active_slot = field.get_active_assignment_slot(self.context)
            for slot in [active_slot, field.default_slot]:
                for value in custom_properties.get(slot, {}).values():
                    if isinstance(value, bool):
                        continue
                    elif isinstance(value, list):
                        searchable.extend([ensure_str(item) for item in value])
                    else:
                        searchable.append(ensure_str(value))

        return ' '.join(searchable)


class ParticipationIndexHelper(object):
    """This helper class is used to convert data back and forth between
    participations, participants and roles on one side and index values
    on the other. It is in charge of creating and parsing participations
    index values as well as convert them to human readable labels.

    The index is a multivalued string field in Solr and takes the form
    'participant_id|role', with additional entries of the types
    'any-participant|role' and 'participant_id|any-role' used to allow
    querying only by participant_id or only by role (i.e. all dossiers
    where a given participant has a participation with any role,
    as well as all dossiers where any participant has a participation
    with a given role).

    """
    any_participant_marker = 'any-participant'
    any_role_marker = 'any-role'

    def index_value_to_participant_id_and_role(self, value):
        """Takes a single index value of the form 'participant_id|role'
        and returns the participant_id and role.
        """
        participant_id, role = value.rsplit("|", 1)
        return participant_id, role

    def index_value_to_participant_id(self, value):
        """Takes a single index value of the form 'participant_id|role'
        and returns the participant_id.
        """
        participant_id, role = self.index_value_to_participant_id_and_role(value)
        return participant_id

    def index_value_to_role(self, value):
        """Takes a single index value of the form 'participant_id|role'
        and returns the role.
        """
        participant_id, role = self.index_value_to_participant_id_and_role(value)
        return role

    def participant_id_and_role_to_index_value(self, participant_id=None, role=None):
        """Creates an index value of the form 'participant_id|role' from
        a participant_id and/or a role, filling in the markers for any-role
        or any-participant if necessary.
        """
        if role is None:
            role = self.any_role_marker
        if participant_id is None:
            participant_id = self.any_participant_marker
        return u"{}|{}".format(participant_id, role)

    def participations_to_index_value_list(self, participations):
        """From a list of participations, this method creates the list of
        index values of the form ['participant_id|role', ...] that will be
        stored in solr.
        """
        index_value = set()

        for participation in participations:
            data = IParticipationData(participation)
            index_value.add(self.participant_id_and_role_to_index_value(
                participant_id=data.participant_id))
            for role in data.roles:
                index_value.add(self.participant_id_and_role_to_index_value(
                    role=role))
                index_value.add(self.participant_id_and_role_to_index_value(
                    participant_id=data.participant_id, role=role))
        return list(index_value)

    def role_to_label(self, role):
        """Returns a translated label for a given role.
        """
        if role == self.any_role_marker:
            return translate(_(u'any_role'), context=getRequest())
        return translate_participation_role(role)

    def participant_id_to_label(self, participant_id):
        """Returns a translated label for a given participant_id.
        """
        if participant_id == self.any_participant_marker:
            return translate(_(u'any_participant'), context=getRequest())
        source = PloneSqlOrKubContactSourceBinder()(api.portal.get())
        try:
            term = source.getTermByToken(participant_id)
            return term.title
        except LookupError:
            return translate(_(u'unknown_id', default=u'Unknown ID'), context=getRequest())

    def index_value_to_label(self, value):
        """Returns a translated label of the form 'participant label|role label'
        for a given index value ('participant_id|role').
        """
        participant_id, role = self.index_value_to_participant_id_and_role(value)
        role_label = self.role_to_label(role)
        participant_label = self.participant_id_to_label(participant_id)
        return u"{}|{}".format(participant_label, role_label)


@indexer(IParticipationAwareMarker)
def participations(obj):
    phandler = IParticipationAware(obj)
    helper = ParticipationIndexHelper()
    participations = phandler.get_participations()
    return helper.participations_to_index_value_list(participations)
