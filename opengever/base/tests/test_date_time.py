from datetime import datetime
from opengever.base.date_time import as_utc
from opengever.base.date_time import ulocalized_time
from opengever.testing import IntegrationTestCase
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


class TestDateTimeLocalisation(IntegrationTestCase):

    def test_ulocalized_time_translation(self):
        date = datetime(2011, 6, 17, 11, 30)
        frmt = "%A %a %B %b %H %I %m %d %M %p %S %Y %y"

        self.assertEqual('Friday Fri June Jun 11 11 06 17 30 AM 00 2011 11',
                         ulocalized_time(date, frmt, self.request))
        self.assertEqual('Friday Fri June Jun 11 11 06 17 30 AM 00 2011 11',
                         ulocalized_time(date, frmt, self.request, 'en'))
        self.assertEqual('Freitag Fre Juni Jun 11 11 06 17 30 AM 00 2011 11',
                         ulocalized_time(date, frmt, self.request, 'de'))
        self.assertEqual('Vendredi Ven Juin Jui 11 11 06 17 30 AM 00 2011 11',
                         ulocalized_time(date, frmt, self.request, 'fr'))

    def test_ulocalized_time_is_zero_padded(self):
        date = datetime(2011, 6, 3)
        frmt = "%d.%m.%y"
        self.assertEqual('03.06.11', ulocalized_time(date, frmt, self.request))
