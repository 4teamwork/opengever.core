from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import applyProfile


class TestHooks(FunctionalTestCase):

    def test_execute_examplecontent_hooks(self):
        applyProfile(api.portal.get(), 'opengever.setup:default_content')
        applyProfile(api.portal.get(), 'opengever.setup:empty_templates')
        applyProfile(api.portal.get(), 'opengever.examplecontent:init')
