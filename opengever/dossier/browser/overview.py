from Products.ZCatalog.interfaces import ICatalogBrain
from five import grok
from opengever.base.browser.helper import get_css_class
from opengever.dossier import _ as _dossier
from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.globalindex.utils import indexed_task_link_helper
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.browser.tabs import OpengeverTab
from zope.component import getUtility


class DossierOverview(grok.View, OpengeverTab):

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

    def boxes(self):
        if not self.context.show_subdossier():
            items = [
                [dict(id='newest_tasks', content=self.tasks(), href='tasks'),
                 ],
                [dict(id='participants', content=self.sharing()), ],
                [dict(id='newest_documents', content=self.documents(),
                      href='documents'),
                 dict(id='description', content=self.description), ]
                ]
        else:
            items = [
                [dict(id='subdossiers', content=self.subdossiers()),
                 dict(id='participants', content=self.sharing()), ],
                [dict(id='newest_tasks', content=self.tasks(), href='tasks')],
                [dict(id='newest_documents', content=self.documents(),
                      href='documents'),
                 dict(id='description', content=self.description), ], ]
        return items

    def subdossiers(self):
        return self.context.get_subdossiers(
            sort_on='modified', sort_order='reverse')[:5]

    def tasks(self):
        return self.catalog(['opengever.task.task', ])[:5]

    def documents(self):
        documents = self.catalog(
            ['opengever.document.document', 'ftw.mail.mail', ])[:10]
        document_list = [{
                'Title': document.Title,
                'getURL': document.getURL,
                'alt': document.document_date and
                document.document_date.strftime('%d.%m.%Y') or '',
                'css_class': get_css_class(document),
                'portal_type': document.portal_type,
                } for document in documents]

        return document_list

    def sharing(self):

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

        info = getUtility(IContactInformation)

        return [{
            'Title': info.describe(xx.contact),
            'getURL': info.get_profile_url(xx.contact),
            'css_class':'function-user',
            }
            for xx in results]

    def description(self):
        return self.context.description

    def render_globalindex_task(self, item):
        return indexed_task_link_helper(item, item.title)

    def get_css_class(self, item):
        """Return the css classes
        """
        return "%s %s" % (
            "rollover-breadcrumb", self._get_css_icon_class(item))

    def _get_css_icon_class(self, item):
        """Return the rigth css-class for the icon.
        """
        return get_css_class(item)

    def get_type(self, item):
        """differ the object typ and return the type as string"""
        if isinstance(item, dict):
            return 'dict'
        elif ICatalogBrain.providedBy(item):
            return 'brain'
        else:
            return 'sqlalchemy_object'
