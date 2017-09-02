from opengever.trash import _
from opengever.trash.trash import ITrashable
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage


class TrashView(BrowserView):
    """The trash view gets called via the `trash` action in a document listing.

    The selected documents are passed in via the `paths` request variable.
    """

    def __call__(self):
        paths = self.request.get('paths')
        catalog = getToolByName(self.context, 'portal_catalog')
        if paths:
            for item in paths:
                obj = self.context.restrictedTraverse(item)
                brains = catalog(path=item)

                # check that the object isn't already trashed
                if not brains:
                    msg = _(
                        u'could not trash the object ${obj}, '
                        'it is already trashed',
                        mapping={'obj': obj.Title().decode('utf-8')})
                    IStatusMessage(self.request).addStatusMessage(
                        msg, type='error')
                    continue
                # check that the document isn't checked_out
                if brains[0].checked_out:
                    msg = _(
                        u'could not trash the object ${obj}, it is checked out.',
                        mapping={'obj': obj.Title().decode('utf-8')})
                    IStatusMessage(self.request).addStatusMessage(
                        msg, type='error')
                    continue

                if not api.user.has_permission(
                        'opengever.trash: Trash content',
                        obj=obj):
                    msg = _(u'Trashing ${title} is forbidden',
                            mapping={'title': obj.Title().decode('utf-8')})
                    IStatusMessage(self.request).addStatusMessage(
                        msg, type='error')
                    continue

                trasher = ITrashable(obj)
                trasher.trash()
                msg = _(u'the object ${obj} trashed',
                    mapping={'obj': obj.Title().decode('utf-8')})
                IStatusMessage(self.request).addStatusMessage(
                    msg, type='info')

        else:
            msg = _(u'You have not selected any items.')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')

        return self.request.RESPONSE.redirect(
            '{}#documents'.format(self.context.absolute_url()))


class UntrashView(BrowserView):
    """The untrash view gets called via the `untrash` action in a trash
    listing.

    The selected documents are passed in via the `paths` request variable.
    """

    def __call__(self):
        paths = self.request.get('paths')
        if paths:
            for item in paths:
                obj = self.context.restrictedTraverse(item)
                if not api.user.has_permission(
                        'opengever.trash: Untrash content',
                        obj=obj):
                    msg = _(u'Untrashing ${title} is forbidden',
                            mapping={'title': obj.Title().decode('utf-8')})
                    IStatusMessage(self.request).addStatusMessage(
                        msg, type='error')
                    continue

                trasher = ITrashable(obj)
                trasher.untrash()

            return self.request.RESPONSE.redirect('%s#documents' % (
                self.context.absolute_url()))

        else:
            msg = _(u'You have not selected any items.')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')

            return self.request.RESPONSE.redirect(
                '%s#trash' % self.context.absolute_url())
