from ftw.bumblebee.viewlets.cookie import BumblebeeCookieViewlet
from zope.component.hooks import getSite


class BumblebeeCookieViewlet(BumblebeeCookieViewlet):
    """Don't send a bumblebee cookie in readonly mode.
    """

    def render(self):
        # XXX: Not sure whether this is the right approach
        site = getSite()
        conn = site._p_jar
        if conn.isReadOnly():
            return ''

        return super(BumblebeeCookieViewlet, self).render()
