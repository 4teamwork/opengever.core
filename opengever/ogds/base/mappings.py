from opengever.ogds.base.sync.import_stamp import get_ogds_sync_stamp
from plone.memoize import ram
from opengever.ogds.models.user import User


@ram.cache(lambda m, userid: u'{}-{}'.format(userid, get_ogds_sync_stamp()))
def userid_to_username(userid):
    user = User.query.get_by_userid(userid)
    if user:
        return user.username


@ram.cache(lambda m, username: u'{}-{}'.format(username, get_ogds_sync_stamp()))
def username_to_userid(username):
    user = User.query.get_by_username(username)
    if user:
        return user.userid
