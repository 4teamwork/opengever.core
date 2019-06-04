from plone.memoize.view import memoize_contextless
from zope.component.hooks import getSite


def gever_is_readonly():
    site = getSite()
    conn = site._p_jar
    return conn.isReadOnly()
