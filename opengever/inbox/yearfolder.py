from datetime import datetime
from opengever.inbox import _
from opengever.inbox.utils import get_current_inbox
from plone.dexterity.utils import createContentInContainer
from plone.directives import form
from zope.i18n import translate
import AccessControl


class IYearFolder(form.Schema):
    """Base schema for a year folder.
    """


def get_current_yearfolder(context=None, inbox=None):
    """Returns the yearfolder for the current year (creates it if missing).
    """

    if context is None and inbox is None:
        raise ValueError('Context or the current inbox itself must be given.')

    if context:
        inbox = get_current_inbox(context)

    year = str(datetime.now().year)
    if inbox.get(year):
        return inbox.get(year)
    else:
        return _create_yearfolder(inbox, year)


def _create_yearfolder(inbox, year):
    """creates the yearfolder for the given year"""

    _sm = AccessControl.getSecurityManager()
    AccessControl.SecurityManagement.newSecurityManager(
        inbox.REQUEST,
        AccessControl.SecurityManagement.SpecialUsers.system)
    try:
        # for creating the folder, we need to be a superuser since
        # normal user should not be able to add year folders.
        # --- help i18ndude ---
        msg = _(u'yearfolder_title', default=u'Closed ${year}',
                mapping=dict(year=str(year)))
        # --- / help i18ndude ---
        folder_title = translate(str(msg), msg.domain, msg.mapping,
                                 context=inbox.REQUEST, default=msg.default)
        folder = createContentInContainer(
            inbox, 'opengever.inbox.yearfolder',
            title=folder_title, id=year)
    except:
        AccessControl.SecurityManagement.setSecurityManager(_sm)
        raise
    else:
        AccessControl.SecurityManagement.setSecurityManager(_sm)

    return folder
