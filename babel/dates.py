# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

"""Locale dependent formatting and parsing of dates and times.

The default locale for the functions in this module is determined by the
following environment variables, in that order:

 * ``LC_TIME``,
 * ``LC_ALL``, and
 * ``LANG``
"""

from datetime import date, datetime, time, timedelta, tzinfo
import re

from babel.core import default_locale, Locale
from babel.util import UTC

__all__ = ['format_date', 'format_datetime', 'format_time', 'parse_date',
           'parse_datetime', 'parse_time']
__docformat__ = 'restructuredtext en'

LC_TIME = default_locale('LC_TIME')

# Aliases for use in scopes where the modules are shadowed by local variables
date_ = date
datetime_ = datetime
time_ = time

def get_period_names(locale=LC_TIME):
    """Return the names for day periods (AM/PM) used by the locale.
    
    >>> get_period_names(locale='en_US')['am']
    u'AM'
    
    :param locale: the `Locale` object, or a locale string
    :return: the dictionary of period names
    :rtype: `dict`
    """
    return Locale.parse(locale).periods

def get_day_names(width='wide', context='format', locale=LC_TIME):
    """Return the day names used by the locale for the specified format.
    
    >>> get_day_names('wide', locale='en_US')[1]
    u'Tuesday'
    >>> get_day_names('abbreviated', locale='es')[1]
    u'mar'
    >>> get_day_names('narrow', context='stand-alone', locale='de_DE')[1]
    u'D'
    
    :param width: the width to use, one of "wide", "abbreviated", or "narrow"
    :param context: the context, either "format" or "stand-alone"
    :param locale: the `Locale` object, or a locale string
    :return: the dictionary of day names
    :rtype: `dict`
    """
    return Locale.parse(locale).days[context][width]

def get_month_names(width='wide', context='format', locale=LC_TIME):
    """Return the month names used by the locale for the specified format.
    
    >>> get_month_names('wide', locale='en_US')[1]
    u'January'
    >>> get_month_names('abbreviated', locale='es')[1]
    u'ene'
    >>> get_month_names('narrow', context='stand-alone', locale='de_DE')[1]
    u'J'
    
    :param width: the width to use, one of "wide", "abbreviated", or "narrow"
    :param context: the context, either "format" or "stand-alone"
    :param locale: the `Locale` object, or a locale string
    :return: the dictionary of month names
    :rtype: `dict`
    """
    return Locale.parse(locale).months[context][width]

def get_quarter_names(width='wide', context='format', locale=LC_TIME):
    """Return the quarter names used by the locale for the specified format.
    
    >>> get_quarter_names('wide', locale='en_US')[1]
    u'1st quarter'
    >>> get_quarter_names('abbreviated', locale='de_DE')[1]
    u'Q1'
    
    :param width: the width to use, one of "wide", "abbreviated", or "narrow"
    :param context: the context, either "format" or "stand-alone"
    :param locale: the `Locale` object, or a locale string
    :return: the dictionary of quarter names
    :rtype: `dict`
    """
    return Locale.parse(locale).quarters[context][width]

def get_era_names(width='wide', locale=LC_TIME):
    """Return the era names used by the locale for the specified format.
    
    >>> get_era_names('wide', locale='en_US')[1]
    u'Anno Domini'
    >>> get_era_names('abbreviated', locale='de_DE')[1]
    u'n. Chr.'
    
    :param width: the width to use, either "wide" or "abbreviated"
    :param locale: the `Locale` object, or a locale string
    :return: the dictionary of era names
    :rtype: `dict`
    """
    return Locale.parse(locale).eras[width]

def get_date_format(format='medium', locale=LC_TIME):
    """Return the date formatting patterns used by the locale for the specified
    format.
    
    >>> get_date_format(locale='en_US')
    <DateTimePattern u'MMM d, yyyy'>
    >>> get_date_format('full', locale='de_DE')
    <DateTimePattern u'EEEE, d. MMMM yyyy'>
    
    :param format: the format to use, one of "full", "long", "medium", or
                   "short"
    :param locale: the `Locale` object, or a locale string
    :return: the date format pattern
    :rtype: `DateTimePattern`
    """
    return Locale.parse(locale).date_formats[format]

def get_datetime_format(format='medium', locale=LC_TIME):
    """Return the datetime formatting patterns used by the locale for the
    specified format.
    
    >>> get_datetime_format(locale='en_US')
    u'{1} {0}'
    
    :param format: the format to use, one of "full", "long", "medium", or
                   "short"
    :param locale: the `Locale` object, or a locale string
    :return: the datetime format pattern
    :rtype: `unicode`
    """
    patterns = Locale.parse(locale).datetime_formats
    if format not in patterns:
        format = None
    return patterns[format]

def get_time_format(format='medium', locale=LC_TIME):
    """Return the time formatting patterns used by the locale for the specified
    format.
    
    >>> get_time_format(locale='en_US')
    <DateTimePattern u'h:mm:ss a'>
    >>> get_time_format('full', locale='de_DE')
    <DateTimePattern u"H:mm' Uhr 'z">
    
    :param format: the format to use, one of "full", "long", "medium", or
                   "short"
    :param locale: the `Locale` object, or a locale string
    :return: the time format pattern
    :rtype: `DateTimePattern`
    """
    return Locale.parse(locale).time_formats[format]

def format_date(date=None, format='medium', locale=LC_TIME):
    """Return a date formatted according to the given pattern.
    
    >>> d = date(2007, 04, 01)
    >>> format_date(d, locale='en_US')
    u'Apr 1, 2007'
    >>> format_date(d, format='full', locale='de_DE')
    u'Sonntag, 1. April 2007'
    
    If you don't want to use the locale default formats, you can specify a
    custom date pattern:
    
    >>> format_date(d, "EEE, MMM d, ''yy", locale='en')
    u"Sun, Apr 1, '07"
    
    :param date: the ``date`` or ``datetime`` object; if `None`, the current
                 date is used
    :param format: one of "full", "long", "medium", or "short", or a custom
                   date/time pattern
    :param locale: a `Locale` object or a locale identifier
    :rtype: `unicode`
    
    :note: If the pattern contains time fields, an `AttributeError` will be
           raised when trying to apply the formatting. This is also true if
           the value of ``date`` parameter is actually a ``datetime`` object,
           as this function automatically converts that to a ``date``.
    """
    if date is None:
        date = date_.today()
    elif isinstance(date, datetime):
        date = date.date()

    locale = Locale.parse(locale)
    if format in ('full', 'long', 'medium', 'short'):
        format = get_date_format(format, locale=locale)
    pattern = parse_pattern(format)
    return parse_pattern(format).apply(date, locale)

def format_datetime(datetime=None, format='medium', tzinfo=None,
                    locale=LC_TIME):
    """Return a date formatted according to the given pattern.
    
    >>> dt = datetime(2007, 04, 01, 15, 30)
    >>> format_datetime(dt, locale='en_US')
    u'Apr 1, 2007 3:30:00 PM'
    
    For any pattern requiring the display of the time-zone, the third-party
    ``pytz`` package is needed to explicitly specify the time-zone:
    
    >>> from pytz import timezone
    >>> format_datetime(dt, 'full', tzinfo=timezone('Europe/Berlin'),
    ...                 locale='de_DE')
    u'Sonntag, 1. April 2007 17:30 Uhr MESZ'
    >>> format_datetime(dt, "yyyy.MM.dd G 'at' HH:mm:ss zzz",
    ...                 tzinfo=timezone('US/Eastern'), locale='en')
    u'2007.04.01 AD at 11:30:00 EDT'
    
    :param datetime: the `datetime` object; if `None`, the current date and
                     time is used
    :param format: one of "full", "long", "medium", or "short", or a custom
                   date/time pattern
    :param tzinfo: the timezone to apply to the time for display
    :param locale: a `Locale` object or a locale identifier
    :rtype: `unicode`
    """
    if datetime is None:
        datetime = datetime_.now()
    elif isinstance(datetime, (int, long)):
        datetime = datetime.fromtimestamp(datetime)
    elif isinstance(datetime, time):
        datetime = datetime_.combine(date.today(), datetime)
    if datetime.tzinfo is None:
        datetime = datetime.replace(tzinfo=UTC)
    if tzinfo is not None:
        datetime = datetime.astimezone(tzinfo)
        if hasattr(tzinfo, 'normalize'): # pytz
            datetime = tzinfo.normalize(datetime)

    locale = Locale.parse(locale)
    if format in ('full', 'long', 'medium', 'short'):
        return get_datetime_format(format, locale=locale) \
            .replace('{0}', format_time(datetime, format, tzinfo=None,
                                        locale=locale)) \
            .replace('{1}', format_date(datetime, format, locale=locale))
    else:
        return parse_pattern(format).apply(datetime, locale)

def format_time(time=None, format='medium', tzinfo=None, locale=LC_TIME):
    """Return a time formatted according to the given pattern.
    
    >>> t = time(15, 30)
    >>> format_time(t, locale='en_US')
    u'3:30:00 PM'
    >>> format_time(t, format='short', locale='de_DE')
    u'15:30'
    
    If you don't want to use the locale default formats, you can specify a
    custom time pattern:
    
    >>> format_time(t, "hh 'o''clock' a", locale='en')
    u"03 o'clock PM"
    
    For any pattern requiring the display of the time-zone, the third-party
    ``pytz`` package is needed to explicitly specify the time-zone:
    
    >>> from pytz import timezone
    >>> t = time(15, 30)
    >>> format_time(t, format='full', tzinfo=timezone('Europe/Berlin'),
    ...             locale='de_DE')
    u'17:30 Uhr MESZ'
    >>> format_time(t, "hh 'o''clock' a, zzzz", tzinfo=timezone('US/Eastern'),
    ...             locale='en')
    u"11 o'clock AM, Eastern Daylight Time"
    
    :param time: the ``time`` or ``datetime`` object; if `None`, the current
                 time is used
    :param format: one of "full", "long", "medium", or "short", or a custom
                   date/time pattern
    :param tzinfo: the time-zone to apply to the time for display
    :param locale: a `Locale` object or a locale identifier
    :rtype: `unicode`
    
    :note: If the pattern contains date fields, an `AttributeError` will be
           raised when trying to apply the formatting. This is also true if
           the value of ``time`` parameter is actually a ``datetime`` object,
           as this function automatically converts that to a ``time``.
    """
    if time is None:
        time = datetime.now().time()
    elif isinstance(time, (int, long)):
        time = datetime.fromtimestamp(time).time()
    elif isinstance(time, datetime):
        time = time.timetz()
    if time.tzinfo is None:
        time = time.replace(tzinfo=UTC)
    if tzinfo is not None:
        dt = datetime.combine(date.today(), time).astimezone(tzinfo)
        if hasattr(tzinfo, 'normalize'): # pytz
            dt = tzinfo.normalize(dt)
        time = dt.timetz()

    locale = Locale.parse(locale)
    if format in ('full', 'long', 'medium', 'short'):
        format = get_time_format(format, locale=locale)
    return parse_pattern(format).apply(time, locale)

def parse_date(string, locale=LC_TIME):
    """Parse a date from a string.
    
    This function uses the date format for the locale as a hint to determine
    the order in which the date fields appear in the string.
    
    >>> parse_date('4/1/04', locale='en_US')
    datetime.date(2004, 4, 1)
    >>> parse_date('01.04.2004', locale='de_DE')
    datetime.date(2004, 4, 1)
    
    :param string: the string containing the date
    :param locale: a `Locale` object or a locale identifier
    :return: the parsed date
    :rtype: `date`
    """
    # TODO: try ISO format first?
    format = get_date_format(locale=locale).pattern.lower()
    year_idx = format.index('y')
    month_idx = format.index('m')
    if month_idx < 0:
        month_idx = format.index('l')
    day_idx = format.index('d')

    indexes = [(year_idx, 'Y'), (month_idx, 'M'), (day_idx, 'D')]
    indexes.sort()
    indexes = dict([(item[1], idx) for idx, item in enumerate(indexes)])

    # FIXME: this currently only supports numbers, but should also support month
    #        names, both in the requested locale, and english

    numbers = re.findall('(\d+)', string)
    year = numbers[indexes['Y']]
    if len(year) == 2:
        year = 2000 + int(year)
    else:
        year = int(year)
    month = int(numbers[indexes['M']])
    day = int(numbers[indexes['D']])
    if month > 12:
        month, day = day, month
    return date(year, month, day)

def parse_datetime(string, locale=LC_TIME):
    """Parse a date and time from a string.
    
    This function uses the date and time formats for the locale as a hint to
    determine the order in which the time fields appear in the string.
    
    :param string: the string containing the date and time
    :param locale: a `Locale` object or a locale identifier
    :return: the parsed date/time
    :rtype: `datetime`
    """
    raise NotImplementedError

def parse_time(string, locale=LC_TIME):
    """Parse a time from a string.
    
    This function uses the time format for the locale as a hint to determine
    the order in which the time fields appear in the string.
    
    >>> parse_time('15:30:00', locale='en_US')
    datetime.time(15, 30)
    
    :param string: the string containing the time
    :param locale: a `Locale` object or a locale identifier
    :return: the parsed time
    :rtype: `time`
    """
    # TODO: try ISO format first?
    format = get_time_format(locale=locale).pattern.lower()
    hour_idx = format.index('h')
    if hour_idx < 0:
        hour_idx = format.index('k')
    min_idx = format.index('m')
    sec_idx = format.index('s')

    indexes = [(hour_idx, 'H'), (min_idx, 'M'), (sec_idx, 'S')]
    indexes.sort()
    indexes = dict([(item[1], idx) for idx, item in enumerate(indexes)])

    # FIXME: support 12 hour clock, and 0-based hour specification
    #        and seconds should be optional, maybe minutes too
    #        oh, and time-zones, of course

    numbers = re.findall('(\d+)', string)
    hour = int(numbers[indexes['H']])
    minute = int(numbers[indexes['M']])
    second = int(numbers[indexes['S']])
    return time(hour, minute, second)


class DateTimePattern(object):

    def __init__(self, pattern, format):
        self.pattern = pattern
        self.format = format

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.pattern)

    def __unicode__(self):
        return self.pattern

    def __mod__(self, other):
        assert type(other) is DateTimeFormat
        return self.format % other

    def apply(self, datetime, locale):
        return self % DateTimeFormat(datetime, locale)


class DateTimeFormat(object):

    def __init__(self, value, locale):
        assert isinstance(value, (date, datetime, time))
        if isinstance(value, (datetime, time)) and value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        self.value = value
        self.locale = Locale.parse(locale)

    def __getitem__(self, name):
        # TODO: a number of fields missing here
        char = name[0]
        num = len(name)
        if char == 'G':
            return self.format_era(char, num)
        elif char in ('y', 'Y'):
            return self.format_year(char, num)
        elif char in ('Q', 'q'):
            return self.format_quarter(char, num)
        elif char in ('M', 'L'):
            return self.format_month(char, num)
        elif char == 'd':
            return self.format(self.value.day, num)
        elif char in ('E', 'e', 'c'):
            return self.format_weekday(char, num)
        elif char == 'a':
            return self.format_period(char)
        elif char == 'h':
            return self.format(self.value.hour % 12, num)
        elif char == 'H':
            return self.format(self.value.hour, num)
        elif char == 'K':
            return self.format(self.value.hour % 12 - 1, num)
        elif char == 'k':
            return self.format(self.value.hour + 1, num)
        elif char == 'm':
            return self.format(self.value.minute, num)
        elif char == 's':
            return self.format(self.value.second, num)
        elif char in ('z', 'Z', 'v'):
            return self.format_timezone(char, num)
        else:
            raise KeyError('Unsupported date/time field %r' % char)

    def format_era(self, char, num):
        width = {3: 'abbreviated', 4: 'wide', 5: 'narrow'}[max(3, num)]
        era = int(self.value.year >= 0)
        return get_era_names(width, self.locale)[era]

    def format_year(self, char, num):
        if char.islower():
            value = self.value.year
        else:
            value = self.value.isocalendar()[0]
        year = self.format(value, num)
        if num == 2:
            year = year[-2:]
        return year

    def format_month(self, char, num):
        if num <= 2:
            return ('%%0%dd' % num) % self.value.month
        width = {3: 'abbreviated', 4: 'wide', 5: 'narrow'}[num]
        context = {3: 'format', 4: 'format', 5: 'stand-alone'}[num]
        return get_month_names(width, context, self.locale)[self.value.month]

    def format_weekday(self, char, num):
        if num < 3:
            if char.islower():
                value = 7 - self.locale.first_week_day + self.value.weekday()
                return self.format(value % 7 + 1, num)
            num = 3
        weekday = self.value.weekday()
        width = {3: 'abbreviated', 4: 'wide', 5: 'narrow'}[num]
        context = {3: 'format', 4: 'format', 5: 'stand-alone'}[num]
        return get_day_names(width, context, self.locale)[weekday]

    def format_period(self, char):
        period = {0: 'am', 1: 'pm'}[int(self.value.hour > 12)]
        return get_period_names(locale=self.locale)[period]

    def format_timezone(self, char, num):
        if char in ('z', 'v'):
            if hasattr(self.value.tzinfo, 'zone'):
                zone = self.value.tzinfo.zone
            else:
                zone = self.value.tzinfo.tzname(self.value)

            # Get the canonical time-zone code
            zone = self.locale.zone_aliases.get(zone, zone)

            # Try explicitly translated zone names first
            display = self.locale.time_zones.get(zone)
            if display:
                if 'long' in display:
                    width = {3: 'short', 4: 'long'}[max(3, num)]
                    if char == 'v':
                        dst = 'generic'
                    else:
                        dst = self.value.dst() and 'daylight' or 'standard'
                    return display[width][dst]
                elif 'city' in display:
                    return display['city']

            else:
                return zone.split('/', 1)[1]

        elif char == 'Z':
            offset = self.value.utcoffset()
            seconds = offset.days * 24 * 60 * 60 + offset.seconds
            hours, seconds = divmod(seconds, 3600)
            pattern = {3: '%+03d%02d', 4: 'GMT %+03d:%02d'}[max(3, num)]
            return pattern % (hours, seconds // 60)


    def format(self, value, length):
        return ('%%0%dd' % length) % value


PATTERN_CHARS = {
    'G': [1, 2, 3, 4, 5],                                           # era
    'y': None, 'Y': None, 'u': None,                                # year
    'Q': [1, 2, 3, 4], 'q': [1, 2, 3, 4],                           # quarter
    'M': [1, 2, 3, 4, 5], 'L': [1, 2, 3, 4, 5],                     # month
    'w': [1, 2], 'W': [1],                                          # week
    'd': [1, 2], 'D': [1, 2, 3], 'F': [1], 'g': None,               # day
    'E': [1, 2, 3, 4, 5], 'e': [1, 2, 3, 4, 5], 'c': [1, 3, 4, 5],  # week day
    'a': [1],                                                       # period
    'h': [1, 2], 'H': [1, 2], 'K': [1, 2], 'k': [1, 2],             # hour
    'm': [1, 2],                                                    # minute
    's': [1, 2], 'S': None, 'A': None,                              # second
    'z': [1, 2, 3, 4], 'Z': [1, 2, 3, 4], 'v': [1, 4]               # zone
}

def parse_pattern(pattern):
    """Parse date, time, and datetime format patterns.
    
    >>> parse_pattern("MMMMd").format
    u'%(MMMM)s%(d)s'
    >>> parse_pattern("MMM d, yyyy").format
    u'%(MMM)s %(d)s, %(yyyy)s'
    
    Pattern can contain literal strings in single quotes:
    
    >>> parse_pattern("H:mm' Uhr 'z").format
    u'%(H)s:%(mm)s Uhr %(z)s'
    
    An actual single quote can be used by using two adjacent single quote
    characters:
    
    >>> parse_pattern("hh' o''clock'").format
    u"%(hh)s o'clock"
    
    :param pattern: the formatting pattern to parse
    """
    if type(pattern) is DateTimePattern:
        return pattern

    result = []
    quotebuf = None
    charbuf = []
    fieldchar = ['']
    fieldnum = [0]

    def append_chars():
        result.append(''.join(charbuf).replace('%', '%%'))
        del charbuf[:]

    def append_field():
        limit = PATTERN_CHARS[fieldchar[0]]
        if limit and fieldnum[0] not in limit:
            raise ValueError('Invalid length for field: %r'
                             % (fieldchar[0] * fieldnum[0]))
        result.append('%%(%s)s' % (fieldchar[0] * fieldnum[0]))
        fieldchar[0] = ''
        fieldnum[0] = 0

    for idx, char in enumerate(pattern.replace("''", '\0')):
        if quotebuf is None:
            if char == "'": # quote started
                if fieldchar[0]:
                    append_field()
                elif charbuf:
                    append_chars()
                quotebuf = []
            elif char in PATTERN_CHARS:
                if charbuf:
                    append_chars()
                if char == fieldchar[0]:
                    fieldnum[0] += 1
                else:
                    if fieldchar[0]:
                        append_field()
                    fieldchar[0] = char
                    fieldnum[0] = 1
            else:
                if fieldchar[0]:
                    append_field()
                charbuf.append(char)

        elif quotebuf is not None:
            if char == "'": # end of quote
                charbuf.extend(quotebuf)
                quotebuf = None
            else: # inside quote
                quotebuf.append(char)

    if fieldchar[0]:
        append_field()
    elif charbuf:
        append_chars()

    return DateTimePattern(pattern, u''.join(result).replace('\0', "'"))
