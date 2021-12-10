from opengever.base.model import create_session
from opengever.ogds.base import _
from opengever.ogds.models.substitute import Substitute
from zExceptions import BadRequest
from zExceptions import NotFound


class SubstituteManager(object):

    def delete(self, userid, substitute_userid):
        substitute = Substitute.query.by_userid_and_substitute_userid(userid, substitute_userid).first()
        if not substitute:
            raise NotFound(_(u'msg_substitute_does_not_exist',
                             default=u'This substitute does not exist.',
                             mapping={'userid': substitute_userid}))

        create_session().delete(substitute)

    def add(self, userid, substitute_userid):
        substitute = Substitute.query.by_userid_and_substitute_userid(userid, substitute_userid).first()
        if substitute:
            raise BadRequest(_(u'msg_substitute_already_exists',
                               default='This substitute already exists.',
                               mapping={'userid': substitute_userid}))
        substitute = Substitute(userid=userid, substitute_userid=substitute_userid)
        create_session().add(substitute)
        return substitute

    def list_substitutes_for(self, userid):
        return Substitute.query.by_userid(userid=userid)

    def list_active_substitutions_for(self, userid):
        return Substitute.query.by_substitute_userid(userid).by_absent_users()
