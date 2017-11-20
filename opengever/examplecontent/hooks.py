from opengever.examplecontent.contacts import ExampleContentCreator as ContactExampleContentCreator
from opengever.examplecontent.meeting import ExampleContentCreator as MeetingExampleContentCreator
from opengever.private import enable_opengever_private


def municipality_content_profile_installed(site):
    creator = MeetingExampleContentCreator(site)
    creator.create_content()

    creator = ContactExampleContentCreator()
    creator.create()

    enable_opengever_private()
