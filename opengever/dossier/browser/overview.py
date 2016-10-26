from Acquisition import aq_inner
from five import grok
from opengever.base.browser.boxes_view import BoxesViewMixin
from opengever.base.browser.helper import get_css_class
from opengever.contact import is_contact_feature_enabled
from opengever.contact.models import Participation
from opengever.dossier import _
from opengever.dossier import _ as _dossier
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.globalindex.model.task import Task
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview import GeverTabMixin
from plone.app.contentlisting.interfaces import IContentListing
from sqlalchemy import desc
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission


class DossierOverview(BoxesViewMixin, grok.View, GeverTabMixin):

    show_searchform = False

    grok.context(IDossierMarker)
    grok.name('tabbedview_view-overview')
    grok.require('zope2.View')
    grok.template('overview')

    def catalog(self, types, showTrashed=False, depth=2):
        return self.context.portal_catalog(
            portal_type=types,
            path=dict(depth=depth,
                      query='/'.join(self.context.getPhysicalPath())),
            sort_on='modified',
            sort_order='reverse')

    def make_participation_box(self):
        if is_contact_feature_enabled():
            return dict(id='participations',
                        content=self.sql_participations(),
                        href='participations',
                        label=_("Participations"),
                        available=self.context.has_participation_support())

        else:
            return dict(id='participants',
                        content=self.plone_participations(),
                        href='participants',
                        label=_("Participants"),
                        available=self.context.has_participation_support())

    def boxes(self):
        return [
            [
                dict(id='newest_tasks', content=self.tasks(),
                     href='tasks', label=_("Newest tasks")),
                self.make_participation_box(),
                dict(id='references', content=self.linked_dossiers(),
                     label=_('label_linked_dossiers',
                             default='Linked Dossiers')),
            ], [
                dict(id='newest_documents', content=self.documents(),
                     href='documents', label=_("Newest documents")),
                dict(id='description', content=self.description,
                     label=_("Description")),
            ]
        ]

    def is_subdossier_navigation_available(self):
        main_dossier = self.context.get_main_dossier()
        return main_dossier.has_subdossiers()

    def navigation_json_url(self):
        return '{}/dossier_navigation.json'.format(
            self.context.get_main_dossier().absolute_url())

    def subdossiers(self):
        return self.context.get_subdossiers(
            sort_on='modified', sort_order='reverse',
            review_state=DOSSIER_STATES_OPEN)[:5]

    def tasks(self):
        return Task.query.by_container(self.context, get_current_admin_unit())\
                         .in_pending_state()\
                         .order_by(desc('modified')).limit(5).all()

    def documents(self):
        return IContentListing(self.catalog(
            ['opengever.document.document', 'ftw.mail.mail', ])[:10])

    def sql_participations(self):
        participations = []
        for participation in Participation.query.by_dossier(self.context):
            participant = participation.participant
            participations.append({
                'getURL': participant.get_url(),
                'Title': participant.get_title(),
                'css_class': participant.get_css_class(),
            })

        return sorted(participations,
                      key=lambda participation: participation.get('Title'))

    def plone_participations(self):
        if not self.context.has_participation_support():
            return []

        # get the participants
        phandler = IParticipationAware(self.context)
        results = list(phandler.get_participations())

        # also append the responsible
        class ResponsibleParticipant(object):
            pass

        responsible = ResponsibleParticipant()
        responsible.roles = _dossier(u'label_responsible', 'Responsible')
        responsible.role_list = responsible.roles

        dossier_adpt = IDossier(self.context)
        responsible.contact = dossier_adpt.responsible
        results.append(responsible)

        users = []
        for dossier in results:
            actor = Actor.lookup(dossier.contact)
            users.append({
                'Title': actor.get_label(),
                'getURL': actor.get_profile_url(),
                'css_class': 'function-user',
            })
        return users

    def description(self):
        return self.context.description

    def linked_dossiers(self):
        """Returns a list of dicts representing incoming and outgoing
        references to/from other dossiers.
        """

        references = []
        intids = getUtility(IIntIds)

        ids = self.get_dossier_back_relations()
        if IDossier(self.context).relatedDossier:
            for rel in IDossier(self.context).relatedDossier:
                ids.append(rel.to_id)

        for iid in ids:
            obj = intids.queryObject(iid)
            if obj is not None and checkPermission('zope2.View', obj):
                references.append(
                    {'Title': obj.Title,
                     'getURL': obj.absolute_url(),
                     'css_class': get_css_class(obj)})

        return references

    def get_dossier_back_relations(self):
        """Returns a list of intids form all dossiers which relates to the
        current dossier.
        """

        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        relations = catalog.findRelations(
            {'to_id': intids.getId(aq_inner(self.context)),
             'from_attribute': 'relatedDossier'})
        return [relation.from_id for relation in relations]
