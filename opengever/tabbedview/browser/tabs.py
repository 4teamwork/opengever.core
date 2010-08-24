import base64
import re
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from ftw.tabbedview.browser.listing import BaseListingView, ListingView
from ftw.tabbedview.interfaces import ITabbedView
from five import grok
from ftw.table import helper
from ftw.directoryservice.contact import IContact
from ftw.directoryservice.membership import Membership
from plone.directives import dexterity
from opengever.octopus.tentacle.interfaces import IContactInformation
from opengever.tabbedview import _
from opengever.tabbedview.helper import readable_ogds_author, linked, readable_date_set_invisibles, solr_linked
from opengever.task import _ as taskmsg

try:
    from opengever.globalsolr.interfaces import ISearch
    from collective.solr.flare import PloneFlare
except ImportError:
    pass


def datetime_compare(x, y):
    a = getattr(x, datetime_compare.index, None)
    b = getattr(y, datetime_compare.index, None)
    if a is None and b is None:
        return 0
    elif a is None:
        return -1
    elif b is None:
        return 1
    else:
        return cmp(a, b)
#XXX really ugly. Will be overwritten in datetime_sort
datetime_compare.index = 'modified'

def custom_sort(list_, index, dir_):

    datetime_compare.index = index
    reverse = 0
    if dir_ == 'reverse':
        reverse = 1
    return sorted(list_, cmp=datetime_compare, reverse=reverse)

class OpengeverListingTab(grok.View, BaseListingView):
    grok.context(ITabbedView)
    grok.template('generic')

    update = BaseListingView.update

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        ('modified', helper.readable_date),
        ('Creator', readable_ogds_author),
        )


    custom_sort_indexes = {'Products.PluginIndexes.DateIndex.DateIndex': custom_sort}

    def _custom_sort_method(self, contents, sort_on, sort_order):
        if BaseListingView._custom_sort_method is not None:
            contents = BaseListingView._custom_sort_method(self, contents, sort_on,
                                                           sort_order)
        if sort_on=='reference':
            splitter = re.compile('[/\., ]')
            def _sortable_data(brain):
                """ Converts the "reference" into a tuple containing integers, which are
                converted well. Sorting "10" and "2" as strings results in wrong order..
                """
                value = getattr(brain, sort_on, '')
                if not isinstance(value, str)  and not isinstance(value, unicode):
                    return value
                parts = []
                for part in splitter.split(value):
                    part = part.strip()
                    try:
                        part = int(part)
                    except ValueError:
                        pass
                    parts.append(part)
                return parts
            contents = list(contents)
            contents.sort(lambda a,b:cmp(_sortable_data(a), _sortable_data(b)))
            if sort_order!='asc':
                contents.reverse()
        elif sort_on in ('responsible', 'Creator', 'checked_out', 'issuer', 'contact'):
            info = getUtility(IContactInformation)
            def _sorter(a, b):
                av = (info.describe(getattr(a, sort_on, '')) or '').lower()
                bv = (info.describe(getattr(b, sort_on, '')) or '').lower()
                return cmp(av, bv)
            contents = list(contents)
            contents.sort(_sorter)
            if sort_order!='asc':
                contents.reverse()
        return contents

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


    search_index = 'SearchableText' #only 'SearchableText' is implemented for now
    sort_on = 'modified'
    sort_order = 'reverse'

class SolrListingView(ListingView):

    sort_on = ''

    def build_query(self):
        return self.search_util.buildQuery(**self._search_options)

    def update(self):
        self.search_util = queryUtility(ISearch)
        if not self.search_options.has_key('portal_type') and len(self.types):
            self.search_options.update({'portal_type':self.types[0]}) 

        self.search()

    def search(self, kwargs={}):

        parameters = {}
        self.sort_on = self.request.get('sort_on', self.sort_on)
        self.sort_order = self.request.get('sort_order', self.sort_order)

        parameters['sort'] = self.sort_on
        if self.sort_on:
            if self.sort_on.startswith('header-'):
                self.sort_on = self.sort_on.split('header-')[1]
                parameters['sort'] = self.sort_on

            if self.sort_order == 'reverse':
                parameters['sort'] = '%s desc' % parameters['sort']
            else:
                parameters['sort'] = '%s asc' % parameters['sort']

        query = self.build_query()
        flares = self.search_util(query, **parameters)
        self.contents = [PloneFlare(f) for f in flares]


class OpengeverSolrListingTab(grok.View, SolrListingView):
    grok.context(ITabbedView)
    grok.template('generic')

    update = SolrListingView.update

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', solr_linked),
        ('modified', helper.readable_date),
        ('Creator', readable_ogds_author),
        )


    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


class OpengeverTab(object):
    show_searchform = False
    def get_css_classes(self):
        if self.show_searchform:
            return ['searchform-visible']
        else:
            return ['searchform-hidden']

class Documents(OpengeverListingTab):
    grok.name('tabbedview_view-documents')

    types = ['opengever.document.document', 'ftw.mail.mail']

    search_options = {'isWorkingCopy':0}

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        ('document_author', 'document_author'),
        ('document_date', 'document_date', helper.readable_date),
        ('receipt_date', 'receipt_date', helper.readable_date),
        ('delivery_date', 'delivery_date', helper.readable_date),
        ('checked_out', 'checked_out', readable_ogds_author)
        )

    enabled_actions = ['cut',
                       'copy',
                       'paste',
                       'send_as_email',
                       'checkout',
                       'checkin',
                       'cancel',
                       'create_task',
                       'trashed',
                       'copy_documents_to_remote_client',
                       ]

    major_actions = ['checkout',
                     'checkin',
                     'create_task',
                     ]

class Dossiers(OpengeverListingTab):
    grok.name('tabbedview_view-dossiers')

    types = ['opengever.dossier.projectdossier', 'opengever.dossier.businesscasedossier',]

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('reference'),
        ('Title', 'sortable_title', linked),
        ('review_state', 'review_state', helper.translated_string()),
        ('responsible', readable_ogds_author),
        ('start', helper.readable_date),
        ('end', helper.readable_date),

        )
    search_options = {'is_subdossier':False}

    enabled_actions = ['change_state',
                       'cut',
                       'copy',
                       'paste',
                       ]

    major_actions = ['change_state',
                     ]


class SubDossiers(Dossiers):
    grok.name('tabbedview_view-subdossiers')
    search_options = {'is_subdossier':True}

class Tasks(OpengeverListingTab):
    grok.name('tabbedview_view-tasks')

    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('review_state', 'review_state', helper.translated_string()),
        ('Title', 'sortable_title', linked),
        {'column' : 'task_type',
         'column_title' : taskmsg(u'label_task_type', 'Task Type')},
        ('deadline', helper.readable_date),
        ('date_of_completion', readable_date_set_invisibles), # erledigt am
        {'column' : 'responsible',
         'column_title' : taskmsg(u'label_responsible_task', 'Responsible'),
         'transform' : readable_ogds_author},
        ('issuer', readable_ogds_author), # zugewiesen von
        {'column' : 'created',
         'column_title' : taskmsg(u'label_issued_date', 'issued at'),
         'transform': helper.readable_date },
        )

    types = ['opengever.task.task',]

    enabled_actions = [
        'change_state',
        'cut',
        'paste',
        ]

class Events(OpengeverListingTab):
    grok.name('tabbedview_view-events')

    types = ['dummy.event',]


#code below might go to opengover.dossier..

from zope.annotation.interfaces import IAnnotations
from ftw.journal.interfaces import IAnnotationsJournalizable, IWorkflowHistoryJournalizable, IJournalizable
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.repository.interfaces import IRepositoryFolder
from opengever.inbox.inbox import IInbox
from ftw.table.interfaces import ITableGenerator
from zope.component import queryUtility
from ftw.table import helper


class RepositoryOverview(grok.View, OpengeverTab):
    grok.context(IRepositoryFolder)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    #TODO: refactor view using viewlets
    def catalog(self, types):
        return self.context.portal_catalog(portal_type=types ,
                                           path=dict(depth=1,
                                                     query='/'.join(self.context.getPhysicalPath())
                                                     ),
                                           sort_on='modified',
                                           sort_order='reverse')

    def boxes(self):
        items = [
            dict(id = 'repostories', content=self.repostories()),
            dict(id = 'dossiers', content=self.dossiers()),
            ]
        return items

    def repostories(self):
        return self.catalog(['opengever.repository.repositoryfolder',])[:5]

    def dossiers(self):
        return self.catalog(['opengever.dossier.projectdossier', 'opengever.dossier.businesscasedossier',])[:5]

class DossierOverview(grok.View, OpengeverTab):
    grok.context(IDossierMarker)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    #TODO: refactor view using viewlets
    def catalog(self, types, showTrashed=False, depth=2):
        return self.context.portal_catalog(portal_type=types ,
                                           path=dict(depth=depth,
                                                     query='/'.join(self.context.getPhysicalPath())
                                                     ),
                                           sort_on='modified',
                                           sort_order='reverse')

    def boxes(self):
        if not self.context.show_subdossier():
            items = [[dict(id = 'tasks', content=self.tasks()),
                      dict(id = 'journal', content=self.journal()),
                      dict(id = 'sharing', content=self.sharing())],
                     [dict(id = 'documents', content=self.documents()),]
                     ]
        else:
            items = [[dict(id = 'subdossiers', content=self.subdossiers()),
                      dict(id = 'tasks', content=self.tasks()),
                      dict(id = 'journal', content=self.journal()),
                      dict(id = 'sharing', content=self.sharing())],
                     [dict(id = 'documents', content=self.documents()),]
                     ]
        return items

    def subdossiers(self):
        return self.catalog(['opengever.dossier.projectdossier', 'opengever.dossier.businesscasedossier',], depth=1)[:5]

    def tasks(self):
        return self.catalog(['opengever.task.task', ])[:5]

    def documents(self):
        documents = self.catalog(['opengever.document.document','ftw.mail.mail',])[:10]
        return [{
            'Title': document.Title,
            'getURL': document.getURL,
            'alt': self.context.toLocalizedTime(document.modified, long_format=1),
            'getIcon': 'document_icon.gif',
        } for document in documents]
        return self.catalog(['opengever.document.document','ftw.mail.mail',])[:10]

    def events(self):
        return self.catalog(['dummy.event',] )[:5]

    def journal(self):
        if IAnnotationsJournalizable.providedBy(self.context):
            annotations = IAnnotations(self.context)
            entries = annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])[:5]
        elif IWorkflowHistoryJournalizable.providedBy(self.context):
            raise NotImplemented

        edict = [dict(Title=entry['action']['title'], getIcon=None) for entry in reversed(entries)]
        return edict

    def sharing(self):
        phandler = IParticipationAware(self.context)
        results = list(phandler.get_participations())
        
        dossier_adpt = IDossier(self.context)
        responsible_name = _(u'label_responsible', 'Responsible')
        results.append({'contact' : dossier_adpt.responsible,
                        'roles' : responsible_name,
                        'role_list' : responsible_name,
                        })
        return [{
            'Title':xx['contact'],
            'getIcon':'user.gif',
            }
            for xx in results
        ]
        
#        # TODO: move to util
#        role = 'Reader'
#        results = []
#        context = self.context
#        pas_tool = getToolByName(context, 'acl_users')
#        utils_tool = getToolByName(context, 'plone_utils')
#
#        inherited_and_local_roles = utils_tool.getInheritedLocalRoles(context) + pas_tool.getLocalRolesForDisplay(context)
#
#        for user_id_and_roles in inherited_and_local_roles:
#            if user_id_and_roles[2] == 'user':
#                if role in user_id_and_roles[1]:
#                    user = pas_tool.getUserById(user_id_and_roles[0])
#                    if user:
#                        results.append(dict(
#                                Title = '%s (%s)' % (user.getProperty('fullname', ''), user.getId()),
#                                getIcon='user.gif'
#                                ))
#            if user_id_and_roles[2] == 'group':
#                if role in user_id_and_roles[1]:
#                    for user in pas_tool.getGroupById(user_id_and_roles[0]).getGroupMembers():
#                        results.append(dict(
#                                Title = '%s (%s)' % (user.getProperty('fullname', ''), user.getId()),
#                                getIcon='user.gif'
#                                ))
#        import pdb; pdb.set_trace( )
#        return results

    def related_dossiers(self):
        results = []
        for item in IDossier(self.context).relatedDossier:
            results.append(self.object_to_brain(item.to_object))
        return results

    def object_to_brain(self, object):
        brains = self.context.portal_catalog({
                'path':{
                    'query':'/'.join(object.getPhysicalPath()),
                    'depth':0,
                    },
                })
        if len(brains)>0:
            return brains[0]
        else:
            return None


class InboxOverview(DossierOverview):
    grok.context(IInbox)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    def boxes(self):

        items = [[dict(id = 'tasks', content=self.tasks()),
                  dict(id = 'journal', content=self.journal()),
                  dict(id = 'sharing', content=self.sharing())],
                 [dict(id = 'documents', content=self.documents()),]
                 ]
        return items


class Journal(grok.View, OpengeverTab):
    grok.context(IJournalizable)
    grok.name('tabbedview_view-journal')
    grok.template('journal')

    def table(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        columns = (('title', lambda x,y: x['action']['title']),
                   'actor',
                   ('time', helper.readable_date_time),
                   'comments'
                   )
        return generator.generate(reversed(self.data()), columns, css_mapping={'table':'journal-listing'})

    def data(self):
        context = self.context
        history = []

        if IAnnotationsJournalizable.providedBy(self.context):
            annotations = IAnnotations(context)
            return annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
        elif IWorkflowHistoryJournalizable.providedBy(self.context):
            raise NotImplemented

class Trash(OpengeverListingTab):
    grok.name('tabbedview_view-trash')

    types = ['opengever.dossier.dossier', 'opengever.document.document', 'opengever.task.task', 'ftw.mail.mail', ]

    search_options = {'trashed':True}

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        )

    enabled_actions = ['untrashed',
                       ]


class Participants(OpengeverListingTab):
    """ Participants listing tab for dossiers using the
    IParticipantsAware behavior
    """
    grok.name('tabbedview_view-participants')
    grok.context(IParticipationAwareMarker)

    def base64_oid_checkbox(item, value):
        if not getattr(item, '_p_oid', False):
            return ''
        oid = base64.encodestring(item._p_oid)
        attrs = {
            'type' : 'checkbox',
            'class' : 'noborder',
            'name' : 'oids:list',
            'id' : 'item-%s' % oid,
            'value' : oid,
            }
        html = '<input %s />' % ' '.join(['%s="%s"' % (k, v)
                                          for k, v in attrs.items()])
        return html

    def icon_helper(item, value):
        return '<img src="user.gif" alt="" title="" border="0" />'

    sort_on = 'contact'
    columns = (
        ('', base64_oid_checkbox,),
        ('', icon_helper,),
        ('contact', 'contact', readable_ogds_author),
        ('role_list', 'roles',)
        )

    def update(self):
        self.pagesize = 20
        self.pagenumber =  int(self.request.get('pagenumber', 1))
        self.url = self.context.absolute_url()

        phandler = IParticipationAware(self.context)
        results = list(phandler.get_participations())

        dossier_adpt = IDossier(self.context)
        responsible_name = _(u'label_responsible', 'Responsible')
        results.append({'contact' : dossier_adpt.responsible,
                        'roles' : responsible_name,
                        'role_list' : responsible_name,
                        })

        # XXX implement searching
        #if self.request.has_key('searchable_text'):
        #    searchable_text = self.request.get('searchable_text', None)
        #    if len(searchable_text):
        #        searchable_text = searchable_text.endswith('*') and searchable_text[:-1] or searchable_text
        #        filter_condition = lambda p:searchable_text in p.Title()
        #        results = filter(filter_condition, results)

        if self.sort_on.startswith('header-'):
            self.sort_on = self.sort_on.split('header-')[1]
        if self.sort_on:
            sorter = lambda a,b:cmp(getattr(a, self.sort_on, ''),
                                    getattr(b, self.sort_on, ''))
            results.sort(sorter)

        if self.sort_order=='reverse':
            results.reverse()

        self.contents = results
        self.len_results = len(self.contents)

    enabled_actions = ['delete_participants',
                       'add_participant']


from plone.app.workflow.interfaces import ISharingPageRole
from zope.component import getUtilitiesFor
from plone.app.workflow.browser.sharing import SharingView
from Acquisition import aq_inner

class Sharing(SharingView):

    template = ViewPageTemplateFile('tabs_templates/sharing.pt')

    def roles(self):
        """Get a list of roles that can be managed.

        Returns a list of dicts with keys:

        - id
        - title
        """
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')

        pairs = []
        has_manage_portal = context.portal_membership.checkPermission('ManagePortal', context)
        aviable_roles_for_users = [ u'Editor',u'Reader', u'Contributor', u'Reviewer']
        for name, utility in getUtilitiesFor(ISharingPageRole):
            if not has_manage_portal and name not in aviable_roles_for_users:
                continue
            pairs.append(dict(id = name, title = utility.title))

        pairs.sort(key=lambda x: x["id"])
        return pairs


    def role_settings(self):
        context = self.context
        results = super(Sharing, self).role_settings()

        if not context.portal_membership.checkPermission('ManagePortal', context):
            results = [r for r in results if r['type']!='group']

        return results


    # @memoize
    # def roles(self):
    #     """Get a list of roles that can be managed.
    #
    #     Returns a list of dicts with keys:
    #
    #         - id
    #         - title
    #     """
    #     return [
    #         {
    #             'id'        : 'Reader',
    #             'title'     : 'read',
    #         },
    #         {
    #             'id'        : 'Editor',
    #             'title'     : 'write',
    #         },
    #     ]


#Client Views
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


class ContactsView(OpengeverListingTab):
    grok.name('tabbedview_view-all_contacts')

    types = ['ftw.directoryservice.contact',]

    sort_on = 'sortable_title'
    sort_order='asc'

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        ('email'),
        ('phone_office'),
        )

class OrgunitView(OpengeverListingTab):
    grok.name('tabbedview_view-all_orgunits')

    types = ['ftw.directoryservice.orgunit']

    sort_on = 'sortable_title'
    sort_order='asc'

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        )

class ContactImportantView(dexterity.DisplayForm, OpengeverTab):
    grok.context(IContact)
    grok.name('tabbedview_view-important_contact')
    grok.template('important_contact')

    def showAttributes(self):
        items = ['firstname', 'lastname','email', 'phone_office', 'phone_fax', 'phone_mobile','directorate']
        return items

class ContactAdditionalView(dexterity.DisplayForm, OpengeverTab):
    grok.context(IContact)
    grok.name('tabbedview_view-additional_contact')
    grok.template('additional_contact')

class ContactOrgunitView(dexterity.DisplayForm, OpengeverTab):
    grok.context(IContact)
    grok.name('tabbedview_view-orgunit_contact')
    grok.template('orgunit_contact')

    def get_units(self):
        intids = getUtility( IIntIds )
        og = []
        memberships = Membership.get_memberships(contact=self.context)
        for rel in memberships:
            og.append(intids.getObject(rel.to_id))
        return og
