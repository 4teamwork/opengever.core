from Acquisition import aq_inner
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_filters
from opengever.base.browser.boxes_view import BoxesViewMixin
from opengever.base.browser.helper import get_css_class
from opengever.base.solr import OGSolrContentListing
from opengever.dossier import _
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplate
from opengever.globalindex.model.task import Task
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview import GeverTabMixin
from plone import api
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

    def boxes(self):
        return [[self.make_task_box(),
                 self.make_participation_box(),
                 self.make_reference_box()],
                [self.make_document_box(),
                 self.make_description_box(),
                 self.make_keyword_box()]]

    def make_participation_box(self):
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
        return self.solr_results(
            ['opengever.document.document', 'ftw.mail.mail'])

    def solr_results(self, types, depth=2, sort='modified desc'):
        solr = getUtility(ISolrSearch)
        filters = make_filters(
            trashed=False,
            portal_type=types,
            path={
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': depth,
            },
        )
        fieldlist = ['UID', 'Title', 'getIcon', 'portal_type', 'path']
        resp = solr.search(
            filters=filters, start=0, rows=self.document_limit, sort=sort,
            fl=fieldlist)
        return OGSolrContentListing(resp)

    def _get_participations(self):
        if not self.context.has_participation_support():
            return []

        phandler = IParticipationAware(self.context)
        return phandler.get_participations()

    def plone_participations(self):
        results = list(self._get_participations())

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
                if not rel.isBroken():
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

    @property
    def keywords(self):
        return IDossier(self.context).keywords

    def get_keywords(self):
        linked_keywords = []
        for keyword in self.keywords:
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
                 self.make_filing_prefix_box()],
                [self.make_document_box()]]

    @property
    def keywords(self):
        return IDossierTemplate(self.context).keywords

    def make_document_box(self):
        return dict(id='documents', content=self.documents(), href='documents',
                    label=_(u"label_documents", default="Documents"))

    def make_filing_prefix_box(self):
        return dict(id='filing_prefix', content=self.context.get_filing_prefix_label(),
                    label=_(u'filing_prefix', default="filing prefix"))

    def documents(self):
        return self.solr_results(
            ['opengever.document.document', 'ftw.mail.mail'],
            sort='sortable_title asc',
        )
