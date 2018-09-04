from AccessControl import Unauthorized
from opengever.trash import _
from opengever.trash.trash import ITrashable
from opengever.trash.trash import TrashError
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage


class TrashView(BrowserView):
    """The trash view gets called via the `trash` action in a document listing.

    The selected documents are passed in via the `paths` request variable.
    """

    def __call__(self):
        paths = self.request.get('paths')
        if paths:
            for item in paths:
                obj = self.context.restrictedTraverse(item)

                trasher = ITrashable(obj)
                try:
                    trasher.trash()
                except TrashError as exc:
                    if exc.message == 'Already trashed':
                        msg = _(
                            u'could not trash the object ${obj}, '
                            'it is already trashed',
                            mapping={'obj': obj.Title().decode('utf-8')})
                    elif exc.message == 'Document checked out':
                        msg = _(
                            u'could not trash the object ${obj}, it is checked'
                            ' out.',
                            mapping={'obj': obj.Title().decode('utf-8')})
                    elif exc.message == 'The document has been returned as excerpt':
                        msg = _(
                            u'could not trash the object ${obj}, it is an excerpt'
                            ' that has been returned to the proposal.',
                            mapping={'obj': obj.Title().decode('utf-8')})
                    IStatusMessage(self.request).addStatusMessage(
                        msg, type='error')
                except Unauthorized:
                    msg = _(u'Trashing ${title} is forbidden',
                            mapping={'title': obj.Title().decode('utf-8')})
                    IStatusMessage(self.request).addStatusMessage(
                        msg, type='error')

                else:
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
                trasher = ITrashable(obj)
                try:
                    trasher.untrash()
                except Unauthorized:
                    msg = _(u'Untrashing ${title} is forbidden',
                            mapping={'title': obj.Title().decode('utf-8')})
                    IStatusMessage(self.request).addStatusMessage(
                        msg, type='error')

            return self.request.RESPONSE.redirect('%s#documents' % (
                self.context.absolute_url()))

        else:
            msg = _(u'You have not selected any items.')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')

            return self.request.RESPONSE.redirect(
                '%s#trash' % self.context.absolute_url())
