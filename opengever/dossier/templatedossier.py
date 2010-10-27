import re
import urllib

from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface
from zope.component import getUtility
from zope.lifecycleevent import ObjectAddedEvent, ObjectModifiedEvent
from zope.event import notify

from five import grok
from Acquisition import aq_inner, aq_parent
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from datetime import datetime
from DateTime import DateTime

from opengever.dossier import _
from opengever.base.interfaces import ISequenceNumber

from ftw.table import helper
from ftw.table.interfaces import ITableGenerator
from opengever.document.staging.manager import ICheckinCheckoutManager
from opengever.tabbedview.helper import linked


class ITemplateDossier(Interface):
    pass


class ITemplateUtility(Interface):
    pass


class TemplateDocumentFormView(grok.View):
    """ Show the "Document with Tempalte"-Form
        A Form wich show all static templates.
    """

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('document_with_template')
    grok.template('template_form')
    label = _('create_document_with_template',
        default="create document with template")

    def __call__(self):
        self.errors = {'title': None, 'paths': None}
        self.title = ''
        self.edit = False
        if self.request.get('form.buttons.save'):
            path = None
            if self.request.get('paths'):
                path = self.request.get('paths')[0]
            self.title = self.request.get('form.widgets.title').decode('utf8')
            self.edit = self.request.get('form.widgets.edit_form') == ['on']

            if path and self.title:
                #create document
                doc = self.context.restrictedTraverse(path)
                clibboard = aq_parent(aq_inner(doc)).manage_copyObjects(
                    [doc.getId()])
                result = self.context.manage_pasteObjects(clibboard)
                newdoc = self.context.get(result[0].get('new_id'))
                annotations = IAnnotations(newdoc)
                for a in list(annotations.keys()):
                    del annotations[a]
                # change attributes: id, title, owner, creation_date ect.
                name = "document-%s" % getUtility(ISequenceNumber).get_number(
                    newdoc)
                member = self.context.portal_membership.getAuthenticatedMember()
                self.context.manage_renameObject(newdoc.getId(), name)
                event = ObjectAddedEvent(newdoc, newParent=self.context, newName=newdoc.getId())
                notify(event)
                newdoc.setTitle(self.title)
                newdoc.changeOwnership(member)
                newdoc.creation_date = DateTime()
                newdoc.document_date = datetime.now()
                newdoc.creators = (member.title_or_id(), )
                newdoc.document_author = member.title_or_id()
                newdoc.manage_delLocalRoles([u for u, r in newdoc.get_local_roles()])
                newdoc.manage_setLocalRoles(member.getId(), ('Owner', ))
                event = ObjectModifiedEvent(newdoc)
                notify(event)
                # check if the direct-edit-mode is selected
                if self.edit:
                    # redirect to the parent Dossier of the new document 
                    # and set the redirectTo parameter, which start the 
                    # zem-file download. See startredirect.js
                    manager = ICheckinCheckoutManager(newdoc)
                    wc = manager.checkout('', show_status_message=False)
                    portal = self.context.portal_url.getPortalObject()
                    xpr = re.compile('href="(.*?)"')
                    html = portal.externalEditLink_(wc)
                    url = xpr.search(html).groups()[0]
                    url = url.replace(portal.absolute_url(),'')
                    get = urllib.urlencode({'redirectTo':url})

                    redirect_url = '%s?%s#documents_overview' % (self.context.absolute_url(), get)
                    return self.request.RESPONSE.redirect(redirect_url)
                else:
                    return self.request.RESPONSE.redirect(self.context.absolute_url()+'#documents_overview')
            else:
                if path == None:
                    self.errors['paths'] = True
                if not self.title:
                    self.errors['title'] = True

        elif self.request.get('form.buttons.cancel'):
            return self.request.RESPONSE.redirect(self.context.absolute_url())
        else:
            templateUtil = getUtility(ITemplateUtility, 'opengever.templatedossier')
            self.templatedossier = templateUtil.templateFolder(self.context)
            if self.templatedossier is None:
                status = IStatusMessage(self.request)
                status.addStatusMessage(_("Not found the templatedossier"), type="error")
                return self.context.request.RESPONSE.redirect(self.context.absolute_url())
            return super(TemplateDocumentFormView, self).__call__()

    def templates(self):
        generator = getUtility(ITableGenerator, 'ftw.tablegenerator')
        catalog = getToolByName(self.context, 'portal_catalog')
        templates = catalog(path=dict(depth=1, query=self.templatedossier), portal_type="opengever.document.document")
        generator = getUtility(ITableGenerator, 'ftw.tablegenerator')

        columns = (
            (''),
            ('', helper.path_radiobutton),
            ('Title', 'sortable_title', linked),
            ('Creator', 'document_author'),
            ('modified', helper.readable_date),
            )

        return generator.generate(templates, columns)


class TemplateFolder(grok.GlobalUtility):
    grok.provides(ITemplateUtility)
    grok.name('opengever.templatedossier')

    def templateFolder(self, context):
        catalog = getToolByName(context, 'portal_catalog')
        result = catalog(portal_type="opengever.dossier.templatedossier")
        if result:
            brain = result[0]
            if brain:
                return brain.getPath()
        return None
