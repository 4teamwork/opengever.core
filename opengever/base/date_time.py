from DateTime import DateTime
from datetime import datetime
from DateTime.interfaces import IDateTime
from Products.CMFPlone.i18nl10n import _interp_regex
from Products.CMFPlone.i18nl10n import datetime_formatvariables
from Products.CMFPlone.i18nl10n import monthname_msgid
from Products.CMFPlone.i18nl10n import monthname_msgid_abbr
from Products.CMFPlone.i18nl10n import name_formatvariables
from Products.CMFPlone.i18nl10n import weekdayname_msgid
from Products.CMFPlone.i18nl10n import weekdayname_msgid_abbr
from Products.CMFPlone.utils import log
from zope.i18n import translate
import logging
import pytz


def utcnow_tz_aware():
    """Returns the utc now datetime timezone aware."""
    return datetime.now(pytz.UTC)


def as_utc(aware_dt):
    """Convert timezone aware datetime to UTC timezone."""

    return pytz.UTC.normalize(aware_dt.astimezone(pytz.UTC))


def format_string_to_message_string(formatstring):
    """python date format string (e.g. u"%A %d %B %Y") to
    translatable message string ("${A} ${d} ${B} ${Y}")
    """

    for key in datetime_formatvariables + name_formatvariables:
        formatstring = formatstring.replace("%" + key, "${{{}}}".format(key))
    return formatstring


def ulocalized_time(time, formatstring, request, target_language=None):
    """time localization method copied from Products.CMFPlone.i18nl10n.
    The method was modified to allow for a custom formatstring in the
    normal python format.

    From http://docs.python.org/lib/module-time.html

    %a        Locale's abbreviated weekday name.
    %A        Locale's full weekday name.
    %b        Locale's abbreviated month name.
    %B        Locale's full month name.
    %d        Day of the month as a decimal number [01,31].
    %H        Hour (24-hour clock) as a decimal number [00,23].
    %I        Hour (12-hour clock) as a decimal number [01,12].
    %m        Month as a decimal number [01,12].
    %M        Minute as a decimal number [00,59].
    %p        Locale's equivalent of either AM or PM.
    %S        Second as a decimal number [00,61].
    %y        Year without century as a decimal number [00,99].
    %Y        Year with century as a decimal number.
    %Z        Time zone name (no characters if no time zone exists).
    """

    domain = 'plonelocales'
    # map to a message string, to make easier reuse of original
    # method and _interp_regex.
    formatstring = format_string_to_message_string(formatstring)

    mapping = {}
    # convert to DateTime instances. Either a date string or
    # a DateTime instance needs to be passed.
    if not IDateTime.providedBy(time):
        try:
            time = DateTime(time)
        except Exception:
            log('Failed to convert %s to a DateTime object' % time,
                severity=logging.DEBUG)
            return None

    # get the format elements used in the formatstring
    formatelements = _interp_regex.findall(formatstring)

    # reformat the ${foo} to foo
    formatelements = [el[2:-1] for el in formatelements]

    # add used elements to mapping
    elements = [e for e in formatelements if e in datetime_formatvariables]

    # add weekday name, abbr. weekday name, month name, abbr month name
    week_included = True
    month_included = True

    name_elements = [e for e in formatelements if e in name_formatvariables]
    if not ('a' in name_elements or 'A' in name_elements):
        week_included = False
    if not ('b' in name_elements or 'B' in name_elements):
        month_included = False

    for key in elements:
        mapping[key] = time.strftime('%' + key)

    if week_included:
        weekday = int(time.strftime('%w'))  # weekday, sunday = 0
        if 'a' in name_elements:
            mapping['a'] = weekdayname_msgid_abbr(weekday)
        if 'A' in name_elements:
            mapping['A'] = weekdayname_msgid(weekday)
    if month_included:
        monthday = int(time.strftime('%m'))  # month, january = 1
        if 'b' in name_elements:
            mapping['b'] = monthname_msgid_abbr(monthday)
        if 'B' in name_elements:
            mapping['B'] = monthname_msgid(monthday)

    # translate translateable elements
    for key in name_elements:
        mapping[key] = translate(mapping[key], domain,
                                 context=request, default=mapping[key],
                                 target_language=target_language)

    # translate the time string
    return formatstring.replace("${", "{").format(**mapping)
