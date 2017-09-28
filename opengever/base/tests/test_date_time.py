from datetime import datetime
from opengever.base.date_time import as_utc
from unittest import TestCase
import pytz


class TestDateTime(TestCase):

    def test_as_utc_fails_for_naive_datetime(self):
        with self.assertRaises(ValueError):
            as_utc(datetime(2010, 1, 1))

    def test_as_utc_converts_to_utc_winter(self):
        zurich = pytz.timezone('Europe/Zurich')
        zurich_dt_winter = zurich.localize(datetime(2011, 11, 29, 11, 30))
        self.assertEqual(
            pytz.UTC.localize(datetime(2011, 11, 29, 10, 30)),
            as_utc(zurich_dt_winter))

    def test_as_utc_converts_to_utc_summer(self):
        zurich = pytz.timezone('Europe/Zurich')
        zurich_dt_summer = zurich.localize(datetime(2011, 6, 17, 11, 30))
        self.assertEqual(
            pytz.UTC.localize(datetime(2011, 6, 17, 9, 30)),
            as_utc(zurich_dt_summer))
