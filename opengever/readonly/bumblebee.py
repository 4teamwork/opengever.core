from ftw.bumblebee.interfaces import IBumblebeeUserSaltStore
from opengever.readonly import is_in_readonly_mode
from plone import api
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from zope.component import adapter


@adapter(IUserLoggedInEvent)
def create_user_salt_on_login(event):
    """Create the user's bumblebee salt during login, if one doesn't exist yet.

    This will make sure it's available when needed, and doesn't have to be
    calculated and persisted as part of an ad-hoc write-on-read.

    Like this we can ensure that users that have already logged in at least
    once have their salt ready, and will be able to see Bumblebee previews
    in read-only mode.

    (On a login during read-only mode this needs to be suppressed - the whole
    idea is that we won't have to generate any salts while in read-only mode)
    """
    if is_in_readonly_mode():
        return

    salt_store = IBumblebeeUserSaltStore(api.portal.get())
    storage = salt_store._get_storage()
    user_id = event.principal.getId()

    if user_id not in storage:
        # This will create the user salt (lazy init on get)
        salt_store.get_user_salt(user_id)
