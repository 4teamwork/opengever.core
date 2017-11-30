from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import date
from datetime import datetime
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.base.oguid import Oguid
from opengever.contact.models import Participation
from opengever.contact.participation import ParticipationWrapper
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from opengever.dossier.interfaces import IConstrainTypeDecider
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.dossier.utils import truncate_ellipsis
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting.model import Proposal
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.task import OPEN_TASK_STATES
from opengever.task.task import ITask
from plone import api
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zExceptions import Unauthorized
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


DOSSIER_STATES_OPEN = [
    'dossier-state-active'
]

DOSSIER_STATES_CLOSED = [
    'dossier-state-inactive',
    'dossier-state-resolved'
]

DOSSIER_STATES_OFFERABLE = DOSSIER_STATES_CLOSED + ['dossier-state-offered']


_marker = object()


class DossierContainer(Container):

    def _getOb(self, id_, default=_marker):
        """We extend `_getObj` in order to change the context for participation
        objects to the `ParticipationWrapper`. That allows us to register views
        and forms for Participations as regular BrowserViews.
        """

        obj = super(DossierContainer, self)._getOb(id_, default)
        if obj is not default:
            return obj

        if id_.startswith('participation-'):
            participation_id = int(id_.split('-')[-1])
            participation = Participation.query.get(participation_id)
            if participation:
                # Prevent cross injections
                if participation.dossier_oguid != Oguid.for_object(self):
                    raise Unauthorized

                return ParticipationWrapper.wrap(self, participation)

        if default is _marker:
            raise KeyError(id_)
        return default

    def allowedContentTypes(self, *args, **kwargs):
        types = super(
            DossierContainer, self).allowedContentTypes(*args, **kwargs)

        depth = self._get_dossier_depth()

        def filter_type(fti):
            # first we try the more specific one ...
            decider = queryMultiAdapter((self.REQUEST, self, fti),
                                        IConstrainTypeDecider,
                                        name=fti.portal_type)
            if not decider:
                # .. then we try the more general one
                decider = queryMultiAdapter((self.REQUEST, self, fti),
                                            IConstrainTypeDecider)
            if decider:
                return decider.addable(depth)
            # if we don't have an adapter, we just allow it
            return True

        return filter(filter_type, types)

    def _get_dossier_depth(self):
        # calculate depth
        depth = 0
        obj = self
        while IDossierMarker.providedBy(obj):
            depth += 1
            obj = aq_parent(aq_inner(obj))
            if IPloneSiteRoot.providedBy(obj):
                break
        return depth

    def is_open(self):
        wf_state = api.content.get_state(obj=self)
        return wf_state in DOSSIER_STATES_OPEN

    def get_main_dossier(self):
        """Return the root dossier for the current dossier.

        The root dossier is the dossier that has a repo-folder as its parent
        and thus forms the root of the local dossier hierarchy.

        """
        obj = self
        prev = self
        while IDossierMarker.providedBy(obj):
            prev = obj
            obj = aq_parent(aq_inner(obj))
            if IPloneSiteRoot.providedBy(obj):
                break
        return prev

    def is_subdossier_addable(self):
        """Only checks if the maximum dossier depth allows another level
        of subdossiers but not for permissions.
        """
        max_depth = api.portal.get_registry_record(
            name='maximum_dossier_depth',
            interface=IDossierContainerTypes, default=100)

        return self._get_dossier_depth() <= max_depth

    def has_subdossiers(self):
        return len(self.get_subdossiers()) > 0

    def get_subdossiers(self, sort_on='created',
                        sort_order='ascending',
                        review_state=None,
                        depth=-1):

        dossier_path = '/'.join(self.getPhysicalPath())
        query = {'path': dict(query=dossier_path, depth=depth),
                 'sort_on': sort_on,
                 'sort_order': sort_order,
                 'object_provides': IDossierMarker.__identifier__}

        if review_state:
            query['review_state'] = review_state

        subdossiers = self.portal_catalog(query)

        # Remove the object itself from the list of subdossiers
        subdossiers = [s for s in subdossiers
                       if not s.getPath() == dossier_path]

        return subdossiers

    def is_subdossier(self):
        return bool(self.get_parent_dossier())

    def get_parent_dossier(self):
        parent = aq_parent(aq_inner(self))
        if IDossierMarker.providedBy(parent):
            return parent

    def is_all_supplied(self):
        """Check if all tasks and all documents(incl. mails) are supplied in
        a subdossier provided there are any (active) subdossiers
        """

        subdossiers = self.getFolderContents({
            'object_provides':
            'opengever.dossier.behaviors.dossier.IDossierMarker'})

        active_dossiers = [d for d in subdossiers
                           if not d.review_state == 'dossier-state-inactive']

        if len(active_dossiers) > 0:
            results = self.getFolderContents({
                'object_provides': [ITask.__identifier__,
                                    IBaseDocument.__identifier__]})

            if len(results) > 0:
                return False

        return True

    def has_active_tasks(self):
        """Check if there are tasks inside the dossier, which
        are not in an end state.
        """
        active_tasks = api.content.find(
            context=self, depth=-1, object_provides=ITask,
            review_state=OPEN_TASK_STATES)

        return bool(active_tasks)

    def has_active_proposals(self):
        """Check if there are proposals inside the dossier, which
        are not in an end state.
        """
        query = Proposal.query.active().by_container(
            self, get_current_admin_unit())
        return bool(query.count())

    def is_all_checked_in(self):
        """ check if all documents in this path are checked in """

        docs = self.portal_catalog(
            portal_type="opengever.document.document",
            path=dict(depth=2,
                      query='/'.join(self.getPhysicalPath())))

        for doc in docs:
            if doc.checked_out:
                return False

        return True

    def has_valid_startdate(self):
        """check if a startdate is valid (if exist)."""

        return bool(IDossier(self).start)

    def has_valid_enddate(self):
        """Check if the enddate is valid.
        """
        dossier = IDossier(self)
        end_date = self.earliest_possible_end_date()

        # no enddate is valid because it would be overwritten
        # with the earliest_possible_end_date
        if dossier.end is None:
            return True

        if end_date:
            # Dossier end date needs to be older
            # than the earliest possible end_date
            if end_date > dossier.end:
                return False
        return True

    def earliest_possible_end_date(self):
        """The earliest possible end-date must be lather than all document dates and
        all dossier start and end dates.
        """
        dates = []
        catalog = getToolByName(self, 'portal_catalog')
        dossier_brains = catalog({
            'path': '/'.join(self.getPhysicalPath()),
            'object_provides': [
                'opengever.dossier.behaviors.dossier.IDossierMarker', ],
            'review_state': [
                'dossier-state-active',
                'dossier-state-resolved', ],
        })

        for dossier_brain in dossier_brains:
            dates.append(dossier_brain.end)
            dates.append(dossier_brain.start)

        document_brains = catalog({
            'path': '/'.join(self.getPhysicalPath()),
            'object_provides': [
                'opengever.document.behaviors.IBaseDocument'],
        })

        for document_brain in document_brains:
            dates.append(document_brain.document_date)

        dates = filter(None, dates)
        dates = map(self._convert_to_date, dates)

        return max(dates) if dates else None

    def get_responsible_actor(self):
        return Actor.user(IDossier(self).responsible)

    @property
    def responsible_label(self):
        return self.get_responsible_actor().get_label()

    def get_sequence_number(self):
        return getUtility(ISequenceNumber).get_number(self)

    def has_participation_support(self):
        return IParticipationAwareMarker.providedBy(self)

    def has_task_support(self):
        return self.portal_types['opengever.task.task'] in self.allowedContentTypes()

    def get_reference_number(self):
        return IReferenceNumber(self).get_number()

    def get_formatted_comments(self, threshold=400):
        """Returns the dossier's comment truncated to characters defined
        in `threshold` and transformed as web intelligent text.
        """
        comments = IDossier(self).comments
        if comments:
            if threshold:
                comments = truncate_ellipsis(comments, threshold)

            return api.portal.get_tool(name='portal_transforms').convertTo(
                'text/html', comments, mimetype='text/x-web-intelligent').getData()

    def get_retention_expiration_date(self):
        """Returns the date when the expiration date expires:

        The start of the next year (the first of january) after the
        retention period.
        """
        if IDossier(self).end:
            year = IDossier(self).end.year + \
                int(ILifeCycle(self).retention_period)
            return date(year + 1, 1, 1)

        return None

    def is_retention_period_expired(self):
        if IDossier(self).end:
            return self.get_retention_expiration_date() <= date.today()

        return False

    def offer(self):
        ILifeCycle(self).date_of_submission = date.today()
        api.content.transition(obj=self, transition='dossier-transition-offer')

    def retract(self):
        ILifeCycle(self).date_of_submission = None
        api.content.transition(obj=self, to_state=self.get_former_state())

    def activate(self):
        self.reset_end_date()
        api.content.transition(obj=self,
                               transition='dossier-transition-activate')

    def reset_end_date(self):
        IDossier(self).end = None

    def get_former_state(self):
        """Returns the end state of the active dossier lifecycle,
        so `dossier-state-resolved` for resolved dossiers or
        `dossier-state-inactive` for deactivated dossiers.
        """
        end_states = ['dossier-state-resolved', 'dossier-state-inactive']

        workflow = api.portal.get_tool('portal_workflow')
        workflow_id = workflow.getWorkflowsFor(self)[0].getId()
        history = workflow.getHistoryOf(workflow_id, self)
        for entry in reversed(history):
            if entry.get('review_state') in end_states:
                return entry.get('review_state')

        return None

    def _convert_to_date(self, datetime_obj):
        if isinstance(datetime_obj, datetime):
            return datetime_obj.date()

        # It is already a date-object
        return datetime_obj


@implementer(IConstrainTypeDecider)
@adapter(Interface, IDossierMarker, IDexterityFTI)
class DefaultConstrainTypeDecider(object):

    def __init__(self, request, context, fti):
        self.context = context
        self.request = request
        self.fti = fti

        max_dossier_depth = api.portal.get_registry_record(
            'maximum_dossier_depth',
            interface=IDossierContainerTypes) + 1

        self.constrain_configuration = {
            'opengever.dossier.businesscasedossier': {
                'opengever.dossier.businesscasedossier': max_dossier_depth,
            },
            'opengever.private.dossier': {
                'opengever.private.dossier': max_dossier_depth
            },
        }

    def addable(self, depth):
        container_type = self.context.portal_type
        factory_type = self.fti.id
        mapping = self.constrain_type_mapping
        for const_ctype, const_depth, const_ftype in mapping:
            if const_ctype == container_type and const_ftype == factory_type:
                return depth < const_depth or const_depth == 0

        if factory_type in [u'opengever.meeting.proposal']:
            return is_meeting_feature_enabled()

        return True

    @property
    def constrain_type_mapping(self):
        conf = self.constrain_configuration
        for container_type, type_constr in conf.items():
            for factory_type, max_depth in type_constr.items():
                yield container_type, max_depth, factory_type
