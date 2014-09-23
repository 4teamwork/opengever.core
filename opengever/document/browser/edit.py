from five import grok
from opengever.base.interfaces import IRedirector
from opengever.document import _
from opengever.document.behaviors import IBaseDocument
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ogds.base.actor import Actor
from opengever.task.task import ITask
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from zope.interface import Interface


def get_redirect_url(context):
        """return the url where the editing_document view was called from
        It should be a document listing."""

        referer = context.REQUEST.environ.get('HTTP_REFERER')
        portal_url = '/'.join(context.portal_url().split('/')[:-1])
        if referer:
            obj_path = referer[len(portal_url):]
            try:
                obj = context.restrictedTraverse(obj_path)
            except KeyError:
                return  '%s#overview' % context.absolute_url()

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
            return  '%s#overview' % context.absolute_url()


class EditCheckerView(grok.View):
    """Short view wich only checks if the user has the required permissions.
    If not it returns with a statusmessages to the referer.
    Used in the documents extended tooltip."""

    grok.context(IBaseDocument)
    grok.name('edit_checker')
    grok.require('zope2.View')

    def render(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(
            'Modify portal content', self.context):
            return self.response.redirect(
                '%s/edit' % (self.context.absolute_url()))
        else:
            msg = _(
                u'You are not authorized to edit the document ${title}',
                mapping={'title': self.context.Title().decode('utf-8')})

            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(
                get_redirect_url(self.context))


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
            return self.request.RESPONSE.redirect(
                get_redirect_url(self.context))

        # check out the document
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)

        # check if the document is allready checked out by the actual user
        userid = getToolByName(
            self.context, 'portal_membership').getAuthenticatedMember().getId()

        if manager.get_checked_out_by() == userid:
            # check if the document is locked
            # otherwies only open with the ext. editor
            info = getMultiAdapter((self.context, self.request),
                        name="plone_lock_info")

            if info.is_locked():
                msg = _(u"Can't edit the document at moment, "
                        "beacuse it's locked.")
                IStatusMessage(
                        self.request).addStatusMessage(msg, type='error')

                return self.request.RESPONSE.redirect(
                    get_redirect_url(self.context))

        elif manager.get_checked_out_by() is not None:
            msg = _(u"The Document is allready checked out by: ${userid}",
                    mapping={'userid':
                             Actor.lookup(manager.get_checked_out_by()).get_label()})
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(
                get_redirect_url(self.context))

        elif not manager.is_checkout_allowed():
            msg = _(
                u'Could not check out document ${title}',
                mapping={'title': self.context.Title().decode('utf-8')})
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(
                get_redirect_url(self.context))

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
