# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This module provides utility functions for working with calendar-related data, 
including generating unique day identifiers, converting timestamps to datetime objects, 
and extracting detailed information about days, months, weeks, and years within a specified date range.

Functions:
    - get_current_day_id(): Generates a unique identifier for the current day.
    - timestamp_to_datetime(timestamp): Converts a UNIX timestamp to a datetime object.
    - get_days_in_range(start_date, end_date): Generates dictionaries containing detailed 
      information about days, months, weeks, and years within a specified date range.
"""

# Python modules
import datetime
from datetime import datetime, timedelta

# Define the year and month for which you want to get day names
year = 2023
month = 10  # For example, October


def get_current_day_id():
    """
    Generates a unique identifier for the current day based on the current date.

    The identifier is formatted as a string in the format "YYYY_MM_WW_DD", where:
    - YYYY is the 4-digit year.
    - MM is the 2-digit month.
    - WW is the ISO week number of the year.
    - DD is the 2-digit day of the month.

    Returns:
        str: A string representing the unique identifier for the current day.
    """
    today = datetime.today()
    today_id = today.strftime("%Y_%m_%W_%d")
    return today_id


def timestamp_to_datetime(timestamp):
    """
    Convert a UNIX timestamp to a datetime object.

    Args:
        timestamp (float): The UNIX timestamp to convert. This is the number 
            of seconds since January 1, 1970 (UTC).

    Returns:
        datetime.datetime: A datetime object representing the given timestamp.
    """
    return datetime.fromtimestamp(timestamp)


def get_days_in_range(start_date, end_date):
    """
    Generates dictionaries containing detailed information about days, months, weeks, 
    and years within a specified date range.
    Args:
        start_date (datetime.date): The starting date of the range.
        end_date (datetime.date): The ending date of the range.
    Returns:
        tuple: A tuple containing four dictionaries:
            - years_dic (dict): A dictionary where keys are years (as strings) and 
              values are lists of day indices within that year.
            - months_dic (dict): A dictionary where keys are month identifiers 
              (formatted as "YYYYMonthName") and values are lists of day indices 
              within that month.
            - weeks_dic (dict): A dictionary where keys are week numbers (as strings) 
              and values are lists of day indices within that week.
            - days_dic (dict): A dictionary where keys are day indices 
              (formatted as "YYYY_MM_WeekNumber_DayNumber") and values are dictionaries 
              containing detailed information about each day, including:
                - 'year': The year as a string.
                - 'month_number': The month number as a string (e.g., "01" for January).
                - 'month_name': The full name of the month (e.g., "January").
                - 'day_number': The day of the month as a string (e.g., "01").
                - 'day_name': The full name of the day (e.g., "Monday").
                - 'week': The week number as a string.
    Note:
        - The function assumes that `start_date` and `end_date` are valid `datetime.date` 
          objects and that `start_date` is earlier than or equal to `end_date`.
        - The week numbers are based on the ISO week date system.
    """
    # Initialize dictionaries to store information about days, years, months, and weeks
    days_dic = dict()
    years_dic = dict()
    months_dic = dict()
    weeks_dic = dict()

    # Calculate the number of days between the start and end dates
    delta = end_date - start_date

    # Iterate through each day in the range
    for i in range(delta.days + 1):
        current_date = start_date + timedelta(days=i)

        # Extract year, month, day, and week information for the current date
        year = current_date.strftime("%Y")
        month_number = current_date.strftime("%m")
        month_name = current_date.strftime("%B")
        day_number = current_date.strftime("%d")
        day_name = current_date.strftime("%A")
        week = current_date.strftime("%W")
        day_index = f"{year}_{month_number}_{week}_{day_number}"

        # Populate the days dictionary with detailed information about the current day
        days_dic[day_index] = dict()
        days_dic[day_index]['year'] = year
        days_dic[day_index]['month_number'] = month_number
        days_dic[day_index]['month_name'] = month_name
        days_dic[day_index]['day_number'] = day_number
        days_dic[day_index]['day_name'] = day_name
        days_dic[day_index]['week'] = week

        # Add the current day index to the years dictionary
        if year not in years_dic.keys():
            years_dic[year] = []
        years_dic[year].append(day_index)

        # Add the current day index to the months dictionary
        month_key = f"{year}{month_name}"
        if month_key not in months_dic.keys():
            months_dic[month_key] = []
        months_dic[month_key].append(day_index)

        # Add the current day index to the weeks dictionary
        if week not in weeks_dic.keys():
            weeks_dic[week] = []
        weeks_dic[week].append(day_index)

    # Return the populated dictionaries
    return years_dic, months_dic, weeks_dic, days_dic
