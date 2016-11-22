from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from five import grok
from opengever.base.behaviors.lifecycle import ILifeCycle
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
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting.model import Proposal
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.task import OPEN_TASK_STATES
from opengever.task.task import ITask
from plone import api
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import Interface


DOSSIER_STATES_OPEN = [
    'dossier-state-active'
]

DOSSIER_STATES_CLOSED = [
    'dossier-state-archived',
    'dossier-state-inactive',
    'dossier-state-resolved'
]


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

    def show_subdossier(self):
        registry = queryUtility(IRegistry)
        reg_proxy = registry.forInterface(IDossierContainerTypes)
        depth = self._get_dossier_depth()

        if depth > getattr(reg_proxy, 'maximum_dossier_depth', 100):
            return False
        else:
            return True

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

        catalog = getToolByName(self, 'portal_catalog')
        subdossiers = catalog({
            'path': '/'.join(self.getPhysicalPath()),
            'object_provides': [
                'opengever.dossier.behaviors.dossier.IDossierMarker', ],
            'review_state': [
                'dossier-state-active',
                'dossier-state-resolved', ],
            })

        end_dates = []
        # main dossier
        if IDossier(self).start:
            end_dates.append(IDossier(self).start)

        for subdossier in subdossiers:
            if IDossier(subdossier.getObject()).end:
                temp_date = IDossier(subdossier.getObject()).end
                if not temp_date:
                    temp_date = IDossier(subdossier.getObject()).start

                if isinstance(temp_date, datetime):
                    end_dates.append(temp_date.date())
                else:
                    end_dates.append(temp_date)

            docs = subdossier.getObject().getFolderContents(
                {'object_provides': [
                    'opengever.document.behaviors.IBaseDocument', ],
                 })

            for doc in docs:
                # document or mails
                if doc.document_date:
                    if isinstance(doc.document_date, datetime):
                        end_dates.append(doc.document_date.date())
                    else:
                        end_dates.append(doc.document_date)

        if end_dates:
            end_dates.sort()
            return max(end_dates)
        return None

    def get_responsible_actor(self):
        return Actor.user(IDossier(self).responsible)

    @property
    def responsible_label(self):
        return self.get_responsible_actor().get_label()

    def get_sequence_number(self):
        return getUtility(ISequenceNumber).get_number(self)

    def has_participation_support(self):
        return IParticipationAwareMarker.providedBy(self)

    def get_retention_expiration_date(self):
        if IDossier(self).end:
            return IDossier(self).end + relativedelta(
                years=ILifeCycle(self).retention_period)

        return None

    def is_retention_period_expired(self):
        if IDossier(self).end:
            return self.get_retention_expiration_date() <= date.today()

        return False


class DefaultConstrainTypeDecider(grok.MultiAdapter):
    grok.provides(IConstrainTypeDecider)
    grok.adapts(Interface, IDossierMarker, IDexterityFTI)
    grok.name('')

    CONSTRAIN_CONFIGURATION = {
        'opengever.dossier.businesscasedossier': {
            'opengever.dossier.businesscasedossier': 2,
            'opengever.dossier.projectdossier': 1,
            },
        'opengever.private.dossier': {
            'opengever.private.dossier': 2
        },
        'opengever.dossier.projectdossier': {
            'opengever.dossier.projectdossier': 1,
            'opengever.dossier.businesscasedossier': 1,
            },
        }

    def __init__(self, request, context, fti):
        self.context = context
        self.request = request
        self.fti = fti

    def addable(self, depth):
        container_type = self.context.portal_type
        factory_type = self.fti.id
        mapping = self.constrain_type_mapping
        for const_ctype, const_depth, const_ftype in mapping:
            if const_ctype == container_type and const_ftype == factory_type:
                return depth < const_depth or const_depth == 0

        if factory_type in [u'opengever.meeting.proposal',
                            u'opengever.meeting.sablontemplate']:
            return is_meeting_feature_enabled()
        return True

    @property
    def constrain_type_mapping(self):
        conf = self.CONSTRAIN_CONFIGURATION
        for container_type, type_constr in conf.items():
            for factory_type, max_depth in type_constr.items():
                yield container_type, max_depth, factory_type
