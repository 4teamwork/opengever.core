from zope.component.hooks import getSite


def is_in_readonly_mode():
    """Checks whether the current instance is in readonly mode.
    """
    site = getSite()
    conn = site._p_jar
    return conn.isReadOnly()
