from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory
import os

_ = MessageFactory('opengever.readonly')


def readonly_env_var_is_set():
    return bool(os.environ.get('GEVER_READ_ONLY_MODE'))


def is_in_readonly_mode():
    """Checks whether the current instance is in readonly mode.
    """
    site = getSite()
    if site:
        conn = site._p_jar
        if conn:
            return conn.isReadOnly()
    return False
