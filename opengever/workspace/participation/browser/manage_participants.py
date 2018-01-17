from plone import api
from Products.Five.browser import BrowserView
import json


class ManageParticipants(BrowserView):

    def __call__(self):
        return self.json_response(self.get_participants())

    def json_response(self, data):
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        response.enableHTTPCompression(REQUEST=self.request)
        return json.dumps(data)

    def get_participants(self):
        return self.get_user_role_mapping()

    def get_user_role_mapping(self):
        """Get local roles mapping for all local users.
        """
        entries = []

        for userid, roles in self.context.get_local_roles():
            member = api.user.get(userid=userid)
            if member is not None:
                email = member.getProperty('email', '').decode('utf-8')
                name = member.getProperty('fullname', '').decode('utf-8')
                item = dict(userid=userid,
                            roles=roles,
                            can_manage=self.can_manage_member(member),
                            type_='user')

                if name and email:
                    item['name'] = u'{} ({})'.format(name, email)
                elif name:
                    item['name'] = name
                else:
                    item['name'] = userid.decode('utf-8')
                entries.append(item)
        return entries

    def can_manage_member(self, member):

        if member.getId() == api.user.get_current().getId():
            return False
        else:
            return api.user.has_permission(
                'Sharing page: Delegate WorkspaceAdmin role',
                obj=self.context)
