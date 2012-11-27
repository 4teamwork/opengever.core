from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.base.interfaces import IRedirector
from opengever.document import _
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ogds.base.interfaces import IContactInformation
from opengever.task.task import ITask
from zope.component import getMultiAdapter, getUtility
from zope.interface import Interface


class EditingDocument(grok.View):
    """ The view for direct editing document. When they view is called,
    it checkouts the document if it's possible and necessary and
    redirect to the external_edit link"""

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('editing_document')

    def render(self):

        # have the document a file
        if not self.context.file:
            msg = _(
                u'The Document ${title} has no File',
                mapping={'title': self.context.Title().decode('utf-8')})

            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(self.get_redirect_url())

        # check out the document
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)

        # check if the document is allready checked out by the actual user
        userid = getToolByName(
            self.context, 'portal_membership').getAuthenticatedMember().getId()

        if manager.checked_out() == userid:
            #No checkout just open with the external edit
            pass

        elif manager.checked_out() is not None:
            info = getUtility(IContactInformation)
            msg = _(u"The Document is allready checked out by: ${userid}",
                    mapping={'userid': info.describe(userid)})
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(self.get_redirect_url())

        elif not manager.is_checkout_allowed():
            msg = _(
                u'Could not check out document ${title}',
                mapping={'title': self.context.Title().decode('utf-8')})
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(self.get_redirect_url())

        else:
            # check it out
            manager.checkout()

            # notify the user
            msg = _(
                u'Checked out: ${title}',
                mapping={'title': self.context.Title().decode('utf-8')})

            IStatusMessage(self.request).addStatusMessage(msg, type='info')

        # lets register a redirector for starting external
        # editor - if requested
        redirector = IRedirector(self.request)
        redirector.redirect(
            '%s/external_edit' % self.context.absolute_url(),
            target='_self',
            timeout=1000)

        # now lets redirect to an appropriate target..
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def get_redirect_url(self):
        """return the url where the editing_document view was called from
        It must be a document listing """

        referer = self.context.REQUEST.environ.get('HTTP_REFERER')
        portal_url = '/'.join(self.context.portal_url().split('/')[:-1])
        if referer:
            obj_path = referer[len(portal_url):]
            try:
                obj = self.context.restrictedTraverse(obj_path)
            except KeyError:
                return  '%s#documents' % self.context.absolute_url()

            # redirect to right tabbedview-tab
            if ITask.providedBy(obj):
                return '%s#relateddocuments' % (obj.absolute_url())
            elif IPloneSiteRoot.providedBy(obj):
                return '%s#mydocuments' % (obj.absolute_url())
            elif IDossierMarker.providedBy(obj):
                return '%s#documents' % (obj.absolute_url())
            else:
                return obj.absolute_url()

        else:
            return  '%s#overview' % self.context.absolute_url()
