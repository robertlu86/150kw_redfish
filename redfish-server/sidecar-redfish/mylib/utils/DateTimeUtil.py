import time
import datetime
from datetime import timedelta
from dateutil import relativedelta
from typing import Literal

class DateTimeUtil:
    @staticmethod
    def epoch_millisecond():
        # return int(datetime.datetime.now().timestamp() * 1000)
        return int( time.time()*1000 )

    @staticmethod
    def format_string(format_str='%Y%m%d%H%M%S') -> str:
        # return '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        # return format_str.format(datetime.datetime.now())
        # return time.strftime('%Y-%m-%d %H:%M:%S')
        # time.strftime('%Y%m%d%H%M%S')
        return time.strftime(format_str)

    @staticmethod
    def convert_format_string_to_another(format_datetime_str: str, src_format: str, dst_format: str="%Y-%m-%dT%H%M%SZ"):
        """
        @param format_datetime_str {str} datetime string, e.g., "2025-06-13 22:06:27"
        @param src_format {str} source format, e.g., "%Y-%m-%d %H:%M:%S"
        @param dst_format {str} destination format, e.g., "%Y-%m-%dT%H%M%SZ"
        @return {str} datetime string in destination format, e.g., "2025-06-13T220627Z"
        """
        return datetime.datetime.strptime(format_datetime_str, src_format).strftime(dst_format)

    @staticmethod
    def is_match_format(format_datetime_str: str, expected_format: str="%Y-%m-%dT%H%M%SZ"):
        """
        @param format_datetime_str {str} datetime string, e.g., "2025-06-13 22:06:27"
        @param expected_format {str} expected format, e.g., "%Y-%m-%dT%H%M%SZ"
        @return {bool} True if the datetime string matches the expected format, False otherwise
        """
        try:
            datetime.datetime.strptime(format_datetime_str, expected_format)
            return True
        except ValueError:
            return False

    ##
    # @return {datetime.datetime}
    # @note print now.year, now.month, now.day, now.hour, now.minute, now.second
    @staticmethod
    def now():
        now = datetime.datetime.now()
        return now

    @staticmethod
    # @param ts {int} time in millisecond
    def get_datetime_from_millisecond(ts):
        return datetime.datetime.fromtimestamp(ts / 1000)

    @staticmethod
    # @param dt {datetime.datetime}
    def get_millisecond_from_datetime(dt):
        return int(dt.timestamp() * 1000)

    ##
    # @param _datetime {datetime.datetime} 
    # @param years {int}
    # @return {datetime.datetime}
    @staticmethod
    def add_years(_datetime, years):
        return _datetime + relativedelta.relativedelta(years=years)

    ##
    # @param _datetime {datetime.datetime} 
    # @param months {int}
    # @return {datetime.datetime}
    @staticmethod
    def add_months(_datetime, months):
        return _datetime + relativedelta.relativedelta(months=months)

    ##
    # @param _datetime {datetime.datetime} 
    # @param days {int}
    # @return {datetime.datetime}
    @staticmethod
    def add_days(_datetime, days):
        return _datetime + timedelta(days=days)

    ##
    # @param _datetime {datetime.datetime} 
    # @param days {int}
    # @return {datetime.datetime}
    @staticmethod
    def add_hours(_datetime, hours):
        return _datetime + timedelta(hours=hours)

    @staticmethod
    def parse_timezone(_datetime: datetime.datetime, time_separator:Literal[':', ''] = '') -> str:
        """
        @param _datetime {datetime.datetime}
        @param time_separator {Literal[':', '']} default is ''
        @return {str} timezone in format of '+0800' or '+08:00'
        """
        ret = _datetime.astimezone().strftime("%z")
        if time_separator == ':':
            ret = ret[:3] + ':00'
        return ret
        