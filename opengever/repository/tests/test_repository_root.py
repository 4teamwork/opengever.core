from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase


class TestRepositoryRoot(FunctionalTestCase):

    def test_repository_root_name_from_title(self):
        root = create(Builder('repository_root').having(title_de=u'Foob\xe4r'))
        self.assertEqual('foobar', root.getId())
