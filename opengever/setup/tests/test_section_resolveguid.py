from opengever.setup.sections.resolveguid import DuplicateGuid
from opengever.setup.sections.resolveguid import MissingGuid
from opengever.setup.sections.resolveguid import ResolveGUIDSection
from opengever.setup.tests import MockTransmogrifier
from opengever.testing import FunctionalTestCase


class TestResolveGUID(FunctionalTestCase):

    def setup_section(self, previous=None):
        previous = previous or []
        transmogrifier = MockTransmogrifier()
        options = {'blueprint', 'opengever.setup.resolveguid'}

        return ResolveGUIDSection(transmogrifier, '', options, previous)

    def test_requires_guid(self):
        section = self.setup_section(
            previous=[{'foo': 1234}]
        )

        with self.assertRaises(MissingGuid):
            list(section)

    def test_prevents_duplicate_guid(self):
        section = self.setup_section(
            previous=[{'guid': 1234}, {'guid': 1234}]
        )

        with self.assertRaises(DuplicateGuid):
            list(section)
