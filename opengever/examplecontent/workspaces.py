from opengever.base.model import create_session
from opengever.base.response import COMMENT_RESPONSE_TYPE
from opengever.base.response import IResponseContainer
from opengever.base.response import MOVE_RESPONSE_TYPE
from opengever.base.response import Response
from opengever.base.response import SCHEMA_FIELD_CHANGE_RESPONSE_TYPE
from opengever.setup import DEVELOPMENT_USERS_GROUP


class WorkspaceResponseExampleContentCreator(object):
    """Create Teams for example content.

    Creates one team per group.

    Predictably cycles through the existing org units.
    """

    def __init__(self, site):
        self.db_session = create_session()
        self.site = site

    def __call__(self):
        self.create_responses()
        self.grant_roles()

    def grant_roles(self):
        self.site.acl_users.portal_role_manager.assignRoleToPrincipal(
            'WorkspacesCreator', DEVELOPMENT_USERS_GROUP)
        self.site.acl_users.portal_role_manager.assignRoleToPrincipal(
            'WorkspacesUser', DEVELOPMENT_USERS_GROUP)

    def create_responses(self):
        todo = self.site.unrestrictedTraverse('workspaces/workspace-1/todo-1')
        responses = IResponseContainer(todo)

        response = Response(COMMENT_RESPONSE_TYPE)
        response.text = u"Wir m\xfcssen das Problem genauer analysieren\n\n" \
            u"Jeder einzelne Punkt ist sehr wichtig und muss genaustens angeschaut werden. " \
            u"Das Anw\xe4hlen muss \xfcber den Mauszeiger geschehen und darf nicht umgangen werden.\n\n" \
            u"Ich freue mich!"
        response.creator = u'david.erni'
        responses.add(response)

        response = Response(COMMENT_RESPONSE_TYPE)
        response.text = u"Danke f\xfcr deine schnelle Antwort."
        response.creator = u'philippe.gross'
        responses.add(response)

        response = Response(MOVE_RESPONSE_TYPE)
        response.creator = u'philippe.gross'
        response.add_change(u'', u'', u'Wichtig')
        responses.add(response)

        new_title = u'Wichtig!: {}'.format(todo.title)
        response = Response(SCHEMA_FIELD_CHANGE_RESPONSE_TYPE)
        response.creator = u'philippe.gross'
        response.add_change(u'title', todo.title, new_title)
        responses.add(response)
        todo.title = new_title

        response = Response(MOVE_RESPONSE_TYPE)
        response.creator = u'lukas.graf'
        response.add_change(u'', u'Wichtig', u'Projektleitung')
        responses.add(response)

        response = Response(MOVE_RESPONSE_TYPE)
        response.creator = u'lukas.graf'
        response.add_change(u'', u'Projektleitung', u'')
        responses.add(response)
