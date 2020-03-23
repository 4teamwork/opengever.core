from opengever.base.model import create_session
from opengever.contact import contact_service
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.models.service import ogds_service
from opengever.ogds.models.user import User
from plone.memoize import ram
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.component import getUtility


def ogds_class_language_cachekey(method, self):
    """A cache key including the class' name, the preffered language
    and the actual ogds sync stamp.
    """

    return '%s.%s.%s:%s:%s' % (
        self.__class__.__module__,
        self.__class__.__name__,
        method.__name__,
        getToolByName(getSite(), 'portal_languages').getPreferredLanguage()[0],
        getUtility(ISyncStamp).get_sync_stamp())


class SortHelpers(object):

    @ram.cache(ogds_class_language_cachekey)
    def get_user_sort_dict(self):
        """Returns a dict presenting userid and the fullname,
        that allows correct sorting on the fullname.
        Including also every client inbox.
        """

        session = create_session()
        query = session.query(User.userid, User.lastname, User.firstname)
        query = query.order_by(User.lastname, User.firstname)
        results = query.all()

        sort_dict = {}
        for userid, lastname, firstname in results:
            sort_dict[userid] = u'%s %s' % (lastname, firstname)

        # includes every org-unit-inbox
        for unit in ogds_service().all_org_units():
            inbox_id = unit.inbox().id()
            sort_dict[inbox_id] = Actor.lookup(inbox_id).get_label()
        return sort_dict

    def get_user_contact_sort_dict(self):
        sort_dict = self.get_user_sort_dict()
        for contact in contact_service().all_contact_brains():
            sort_dict['contact:%s' % (contact.id)] = u'%s %s' % (
                contact.lastname, contact.firstname)
        return sort_dict
