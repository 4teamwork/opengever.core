from datetime import date
from datetime import datetime
from opengever.dossier.base import as_date
from opengever.dossier.base import max_date
from unittest import TestCase
import pytz


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


class TestUnitDossierAsDate(TestCase):

    def test_handles_none_values(self):
        self.assertIsNone(as_date(None))

    def test_returns_date_unchanged(self):
        self.assertEquals(date(1950, 1, 1), as_date(date(1950, 1, 1)))

    def test_converts_datetime_to_date(self):
        self.assertEquals(date(1939, 9, 1), as_date(datetime(1939, 9, 1, 5, 45)))

    def test_handles_timezone_corretly(self):
        datetime_format = "%Y-%m-%d %H:%M"
        date_format = "%Y-%m-%d"

        utc_datetime = datetime(2017, 7, 16, 22, 15, tzinfo=pytz.utc)
        local_datetime = utc_datetime.astimezone(pytz.timezone('Europe/Zurich'))
        self.assertEqual('2017-07-16 22:15', utc_datetime.strftime(datetime_format))
        self.assertEqual('2017-07-17 00:15', local_datetime.strftime(datetime_format))
        self.assertEqual('2017-07-17', as_date(utc_datetime).strftime(date_format))
        self.assertEqual('2017-07-17', as_date(local_datetime).strftime(date_format))

        utc_datetime = datetime(2017, 11, 16, 23, 15, tzinfo=pytz.utc)
        local_datetime = utc_datetime.astimezone(pytz.timezone('Europe/Zurich'))
        self.assertEqual('2017-11-17 00:15', local_datetime.strftime(datetime_format))
        self.assertEqual('2017-11-16 23:15', utc_datetime.strftime(datetime_format))
        self.assertEqual('2017-11-17', as_date(utc_datetime).strftime(date_format))
        self.assertEqual('2017-11-17', as_date(local_datetime).strftime(date_format))

        utc_datetime = datetime(2017, 11, 16, 12, 15, tzinfo=pytz.utc)
        self.assertEqual('2017-11-16', as_date(utc_datetime).strftime(date_format))
