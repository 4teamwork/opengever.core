from Acquisition import aq_inner
from opengever.base.browser.boxes_view import BoxesViewMixin
from opengever.base.browser.helper import get_css_class
from opengever.contact import is_contact_feature_enabled
from opengever.contact.models import Participation
from opengever.dossier import _
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.globalindex.model.task import Task
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview import GeverTabMixin
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from sqlalchemy import desc
from urllib import quote_plus
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission


class DossierOverview(BoxesViewMixin, BrowserView, GeverTabMixin):

    show_searchform = False
    document_limit = 10

    def catalog(self, types, showTrashed=False,
                depth=2, sort_on='modified', sort_order='reverse'):
        return self.context.portal_catalog(
            portal_type=types,
            path=dict(depth=depth,
                      query='/'.join(self.context.getPhysicalPath())),
            sort_on=sort_on,
            sort_order=sort_order)

    def boxes(self):
        can_modify = api.user.has_permission('Modify portal content',
                                             obj=self.context)
        has_empty_marker = (not can_modify and not self.get_comments())

        return [[self.make_task_box(),
                 self.make_comment_box(has_empty_marker=has_empty_marker),
                 self.make_participation_box(),
                 self.make_reference_box()],
                [self.make_document_box(),
                 self.make_description_box(),
                 self.make_keyword_box()]]

    def get_comments(self):
        return self.context.get_formatted_comments()

    def make_comment_box(self, has_empty_marker=True):
        return dict(id='comments', content=self.get_comments(),
                    label=_(u"label_comments", default="Comments"),
                    has_empty_marker=has_empty_marker, is_html=True)

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

    def make_task_box(self):
        return dict(id='newest_tasks', content=self.tasks(),
                    href='tasks', label=_("Newest tasks"),
                    available=self.context.has_task_support())

    def make_reference_box(self):
        return dict(
            id='references', content=self.linked_dossiers(),
            label=_('label_linked_dossiers', default='Linked Dossiers'))

    def make_document_box(self):
        return dict(id='newest_documents', content=self.documents(),
                    href='documents', label=_("Newest documents"))

    def make_description_box(self):
        return dict(id='description', content=self.description,
                    is_html=True, label=_("Description"))

    def description(self):
        return api.portal.get_tool(name='portal_transforms').convertTo(
            'text/html', self.context.description,
            mimetype='text/x-web-intelligent').getData()

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
        if not self.context.has_task_support():
            return []

        return Task.query.by_container(self.context, get_current_admin_unit())\
                         .in_pending_state()\
                         .order_by(desc('modified')).limit(5).all()

    def documents(self):
        return IContentListing(
            self.catalog(
                ['opengever.document.document',
                 'ftw.mail.mail', ])[:self.document_limit])

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
        responsible.roles = _(u'label_responsible', 'Responsible')
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

        return sorted(references, key=lambda reference: reference["Title"]().lower())

    def get_dossier_back_relations(self):
        """Returns a list of intids form all dossiers which relates to the
        current dossier.
        """

        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        relations = catalog.findRelations(
            {'to_id': intids.getId(aq_inner(self.context)),
             'from_attribute': 'relatedDossier'})
        return [relation.from_id for relation in relations if relation.from_object]

    def get_keywords(self):
        linked_keywords = []
        for keyword in IDossier(self.context).keywords:
            url = u'{}/@@search?Subject={}'.format(
                api.portal.get().absolute_url(),
                quote_plus(safe_unicode(keyword).encode('utf-8')))
            linked_keywords.append(
                {
                    'getURL': url,
                    'Title': keyword,
                    'css_class': '',
                }
            )
        return linked_keywords

    def make_keyword_box(self):
        return dict(id='keywords', content=self.get_keywords(),
                    label=_(u"label_keywords", default="Keywords"))


class DossierTemplateOverview(DossierOverview):

    def boxes(self):
        # Column 1 is hardcoded and used by the structure-tree.
        # Column 2 contains dossiertemplate metadata
        # Column 3 contains a listing of all documents within the template.
        return [[self.make_description_box(),
                 self.make_keyword_box(),
                 self.make_comment_box(),
                 self.make_filing_prefix_box()],
                [self.make_document_box()]]

    def make_document_box(self):
        return dict(id='documents', content=self.documents(), href='documents',
                    label=_(u"label_documents", default="Documents"))

    def make_filing_prefix_box(self):
        return dict(id='filing_prefix', content=self.context.get_filing_prefix_label(),
                    label=_(u'filing_prefix', default="filing prefix"))

    def documents(self):
        return IContentListing(self.catalog(
            ['opengever.document.document', 'ftw.mail.mail', ],
            sort_on='sortable_title', sort_order='asc')[:self.document_limit])
