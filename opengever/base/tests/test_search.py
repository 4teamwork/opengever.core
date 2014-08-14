from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.testing import FunctionalTestCase
from zope.interface import alsoProvides


class TestOpengeverSearch(FunctionalTestCase):

    def setUp(self):
        super(TestOpengeverSearch, self).setUp()
        create(Builder('fixture').with_all_unit_setup())
        alsoProvides(self.portal.REQUEST, IOpengeverBaseLayer)

    def test_types_filters_list_is_limited_to_main_types(self):
        create(Builder('repository'))
        create(Builder('repository_root'))
        create(Builder('dossier'))
        create(Builder('document'))
        create(Builder('mail'))
        create(Builder('task'))
        create(Builder('inbox'))
        create(Builder('forwarding'))
        create(Builder('contactfolder'))
        create(Builder('contact'))

        self.assertItemsEqual(
            ['opengever.task.task', 'ftw.mail.mail',
             'opengever.document.document', 'opengever.inbox.forwarding',
             'opengever.dossier.businesscasedossier'],
            self.portal.unrestrictedTraverse('@@search').types_list())
