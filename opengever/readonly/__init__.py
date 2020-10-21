from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('opengever.readonly')


def is_in_readonly_mode():
    """Checks whether the current instance is in readonly mode.
    """
    site = getSite()
    if site:
        conn = site._p_jar
        return conn.isReadOnly()
    return False
