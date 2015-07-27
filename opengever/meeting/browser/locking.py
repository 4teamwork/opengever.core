from plone.locking.browser.locking import LockingInformation
from plone.locking.browser.locking import LockingOperations
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import IRefreshableLockable
from Products.CMFCore.utils import getToolByName
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('plone')


class SQLRepresenterLockingOperations(LockingOperations):
    """Lock acquisition and stealing operations
    """

    @property
    def lockable(self):
        return ILockable(self.context)

    @property
    def refreshable_lockable(self):
        model = self.model
        if self.model:
            return IRefreshableLockable(model)
        return IRefreshableLockable(self.context)

    def force_unlock(self, redirect=True):
        """Steal the lock.

        If redirect is True, redirect back to the context URL, i.e. reload
        the page.
        """
        self.lockable.unlock()
        if redirect:
            url = self.context.absolute_url()
            props_tool = getToolByName(self.context, 'portal_properties')
            if props_tool:
                types_use_view = props_tool.site_properties.typesUseViewActionInListings
                if self.context.portal_type in types_use_view:
                    url += '/view'

            self.request.RESPONSE.redirect(url)

    def safe_unlock(self):
        """Unlock the object if the current user has the lock
        """
        if self.lockable.can_safely_unlock():
            self.lockable.unlock()

    def refresh_lock(self):
        """Reset the lock start time
        """
        lockable = self.refreshable_lockable
        if lockable is not None:
            lockable.refresh_lock()


class SQLRepresenterLockingInformation(LockingInformation):

    @property
    def lockable(self):
        return ILockable(self.context)

    def is_locked(self):
        return self.lockable.locked()

    def is_locked_for_current_user(self):
        """True if this object is locked for the current user (i.e. the
        current user is not the lock owner)
        """
        # Faster version - we rely on the fact that can_safely_unlock() is
        # True even if the object is not locked
        return not self.lockable.can_safely_unlock()
        # return self.lockable.locked() and not self.lockable.can_safely_unlock()

    def lock_is_stealable(self):
        """Find out if the lock is stealable
        """
        return self.lockable.stealable()

    def lock_info(self):
        """Get information about the current lock, a dict containing:

        creator - the id of the user who created the lock
        fullname - the full name of the lock creator
        author_page - a link to the home page of the author
        time - the creation time of the lock
        time_difference - a string representing the time since the lock was
        acquired.
        """

        portal_membership = getToolByName(self.context, 'portal_membership')
        portal_url = getToolByName(self.context, 'portal_url')
        url = portal_url()
        for info in self.lockable.lock_info():
            creator = info['creator']
            time = info['time']
            token = info['token']
            lock_type = info['type']
            # Get the fullname, but remember that the creator may not
            # be a member, but only Authenticated or even anonymous.
            # Same for the author_page
            fullname = ''
            author_page = ''
            member = portal_membership.getMemberById(creator)
            if member:
                fullname = member.getProperty('fullname', '')
                author_page = "%s/author/%s" % (url, creator)
            if fullname == '':
                fullname = creator or _('label_an_anonymous_user',
                                        u'an anonymous user')
            time_difference = self._getNiceTimeDifference(time)

            return {
                'creator': creator,
                'fullname': fullname,
                'author_page': author_page,
                'time': time,
                'time_difference': time_difference,
                'token': token,
                'type': lock_type,
            }
