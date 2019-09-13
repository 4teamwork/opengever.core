from opengever.examplecontent.contacts import ContactExampleContentCreator
from opengever.examplecontent.meeting import MeetingExampleContentCreator
from opengever.examplecontent.teams import TeamExampleContentCreator
from opengever.examplecontent.workspaces import WorkspaceResponseExampleContentCreator
from opengever.private import enable_opengever_private


def municipality_content_profile_installed(site):
    creator = MeetingExampleContentCreator(site)
    creator.create_content()

    creator = ContactExampleContentCreator()
    creator.create()

    creator = TeamExampleContentCreator()
    creator.create()

    enable_opengever_private()


def workspace_content_profile_installed(site):
    WorkspaceResponseExampleContentCreator(site)()
