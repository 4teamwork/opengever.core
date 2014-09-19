from collections import namedtuple
from DateTime import DateTime
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.base.indexes import modified_seconds
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for


Dummy = namedtuple('Dummy', ['modified'])


class TestModifiedSecondsIndex(FunctionalTestCase):

    def test_index_preciseness_is_seconds(self):
        date = datetime(2000, 10, 20, 8, 45, 10)
        with freeze(date):
            repo = create(Builder('repository'))
        indexdate_created = index_data_for(repo)['modified_seconds']

        with freeze(date + timedelta(seconds=1)):
            repo.reindexObject()  # updates modified date
        indexdate_updated = index_data_for(repo)['modified_seconds']

        self.assertLess(indexdate_created, indexdate_updated,
                        'The date should be newer.')

    def test_indexer_does_not_fail_when_object_has_no_date(self):
        self.assertEqual(None, modified_seconds(object())())

    def test_indexer_supports_python_datetime(self):
        obj = Dummy(modified=datetime(2000, 12, 30, 10, 55, 50))
        self.assertEquals(978170150, modified_seconds(obj)())

    def test_indexer_supports_zope_datetime(self):
        obj = Dummy(modified=DateTime(2000, 12, 30, 10, 55, 50))
        self.assertEquals(978170150, modified_seconds(obj)())
