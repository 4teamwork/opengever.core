from AccessControl import Unauthorized
from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from datetime import datetime, timedelta
from ftw.table import helper
from ftw.table.interfaces import ITableGenerator
from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from opengever.ogds.base.utils import get_current_client
from opengever.ogds.base.interfaces import IContactInformation
from plone.dexterity.utils import createContent, addContentToContainer
from zope.component import queryUtility, getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectAddedEvent


def path_checkbox(item, value):
    preselected = item.getObject().preselected
    return """
            <input type="checkbox"
                    class="noborder"
                    name="paths:list"
                    id="%s" value="%s"
                    alt="Select %s"
                    title="Select %s"
                    %s
                    >""" % (item.id,
                            item.getPath(),
                            item.Title,
                            item.Title,
                            preselected and 'checked="checked"' or None
                            )

class AddForm(BrowserView):

    __call__ = ViewPageTemplateFile("form.pt")

    steps = {
        'templates': {
            'columns' : (('', helper.path_radiobutton), 'Title' ,'created'),
            'types': ('TaskTemplateFolder',)
            },
        'tasks': {
            'columns' : (('', path_checkbox), 'Title', 'created'),
            'types': ('TaskTemplate',)
            }
        }

    def listing(self, show='templates'):
        """returns a listing of either TaskTemplateFolders or TaskTemplates"""

        templates = self.context.portal_catalog(Type=self.steps[show]['types'])
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(templates,
                                  self.steps[show]['columns'],
                                  sortable = True,
                                  output='json'
                                  )

    def create(self, paths):
        """generate the task templates"""
        for path in paths:
            template = self.context.restrictedTraverse(path)
            deadline = datetime.today()+timedelta(template.deadline)


            data = dict(title=template.title,
                        issuer=self.replace_interactive_user(template.issuer),
                        responsible=\
                            self.replace_interactive_user(template.responsible),
                        task_type=template.task_type,
                        text=template.text,
                        deadline=deadline,
                        )

            if template.responsible_client == 'interactive_users':
                info = getUtility(IContactInformation)
                responsible_assigned_clients = tuple(
                    info.get_assigned_clients(data['responsible']))
                current_client = get_current_client()
                if not responsible_assigned_clients or \
                        current_client in responsible_assigned_clients:
                    data['responsible_client'] = current_client.client_id
                else:
                    data['responsible_client'] = \
                        responsible_assigned_clients[0].client_id
            else:
                data['responsible_client'] = template.responsible_client

            task = createContent('opengever.task.task', **data)
            notify(ObjectCreatedEvent(task))
            task = addContentToContainer(self.context,
                                         task,
                                         checkConstraints=True)
            notify(ObjectAddedEvent(task))
            task.reindexObject()

        IStatusMessage(self.request).addStatusMessage("tasks created",
                                                      type="info")
        return self.request.RESPONSE.redirect(self.context.absolute_url() + \
                                                  '#tasks')

    def replace_interactive_user(self, principal):
        """Replaces interactive users in the principal.
        """

        if principal == 'responsible':
            # find the dossier
            dossier = self.context
            while not IDossierMarker.providedBy(dossier):
                if IPloneSiteRoot.providedBy(dossier):
                    raise ValueError('Could not find dossier')
                dossier = aq_parent(aq_inner(dossier))
            # get the responsible of the dossier
            wrapped_dossier = IDossier(dossier)
            return wrapped_dossier.responsible

        elif principal == 'current_user':
            # get the current user
            mtool = getToolByName(self.context, 'portal_membership')
            member = mtool.getAuthenticatedMember()
            if not member:
                raise Unauthorized()
            return member.getId()

        else:
            return principal
