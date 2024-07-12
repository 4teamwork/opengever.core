from opengever.globalindex.browser.report import UserReport
from opengever.ogds.models.service import ogds_service
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.workspace')


class WorkspaceParticipantsReport(UserReport):
    """View that generate an excel spreadsheet which list all selected users
    """

    @property
    def filename(self):
        participants = translate(_("Participants"), context=self.request)
        return "{participants}_{workspace_title}.xlsx".format(
            participants=participants,
            workspace_title=self.context.title
        )

    def check_permissions(self):
        pass

    def fetch_users(self):
        user_ids = self.extract_user_ids_from_request()
        users = set()

        for user_id in user_ids:
            group_members = ogds_service().fetch_group(user_id)
            if group_members:
                users.update(group_members.users)
            else:
                user = ogds_service().fetch_user(user_id)
                if user:
                    users.add(user)

        return list(users)
