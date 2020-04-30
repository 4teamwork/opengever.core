from datetime import date
from datetime import datetime
from DateTime import DateTime
from opengever.dossier.base import as_date
from opengever.dossier.base import max_date
from unittest import TestCase


class TestUnitDossierMaxDate(TestCase):

    def test_handles_none_values(self):
        self.assertIsNone(max_date(None))
        self.assertIsNone(max_date(None, None))

    def test_handles_none_date_comparison(self):
        self.assertEquals(
            date(2010, 12, 13), max_date(None, date(2010, 12, 13))
        )
        self.assertEquals(
            date(2010, 12, 31), max_date(date(2010, 12, 31), None)
        )

    def test_returns_max_value(self):
        self.assertEquals(
            date(2019, 8, 13), max_date(date(2019, 8, 13), date(2018, 1, 3))
        )

    def test_handles_mixed_types(self):
        self.assertEquals(
            date(2017, 9, 19),
            max_date(datetime(2017, 9, 19, 1, 2, 3),
                     date(1997, 1, 3),
                     DateTime(2016, 1, 1, 7, 40))
        )


class TestUnitDossierAsDate(TestCase):

    def test_handles_none_values(self):
        self.assertIsNone(as_date(None))

    def test_returns_date_unchanged(self):
        self.assertEquals(date(1950, 1, 1), as_date(date(1950, 1, 1)))

    def test_converts_datetime_to_date(self):
        self.assertEquals(date(1939, 9, 1), as_date(datetime(1939, 9, 1, 5, 45)))

    def test_converts_zope_datetime_to_date(self):
        self.assertEquals(date(1989, 9, 9), as_date(DateTime(1989, 9, 9, 7, 3)))
