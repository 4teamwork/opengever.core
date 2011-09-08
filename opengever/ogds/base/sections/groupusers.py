from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from z3c.saconfig import named_scoped_session
from zope.interface import classProvides, implements
import logging


Session = named_scoped_session("opengever")
SQLSOURCE_KEY = 'transmogrify.sqlinserter.sqlinsertersection'


class GroupUsersSection(object):
    """This section write all relations beetwen users and groups,
    import all users of all LDAP groups
    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])
        self.context = transmogrifier.context

        self.session = Session()

    def __iter__(self):

        for item in self.previous:
            groups = self.session.query(Group).filter_by(
                groupid=item.get('groupid')).all()
            if len(groups):

                #first remove all actuall relations
                temp_user = [user for user in groups[0].users]
                for user in temp_user:
                    groups[0].users.remove(user)

                # get all userobjects and append it to the group
                users = self.session.query(User).filter(
                    User.userid.in_(item.get('_users'))).all()
                for user in users:
                    groups[0].users.append(user)

            else:
                self.logger.warn("Couldn't find group with the id %s" % (
                        item.get('groupid')))

            yield item
