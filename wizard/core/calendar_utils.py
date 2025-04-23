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

# This module is the main instances management module
# You can create, get the path and archive the following instances
# /domains
# /categories
# /assets
# /stages
# /variants
# /work env
# /versions
# /export assets
# /export versions

# The creation of an instance basically log the instance
# in the project database and create the corresponding folders
# on the file system

# The archiving of an instance basically archive the corresponding
# folder, delete the original folder from the file
# system and remove the instance from the project database

# The path query of an instance will only access the database and
# construct the directory name, this modules doesn't
# query the file system

# Python modules
import datetime
from datetime import datetime, timedelta

# Define the year and month for which you want to get day names
year = 2023
month = 10  # For example, October


def get_current_day_id():
    today = datetime.today()
    today_id = today.strftime("%Y_%m_%W_%d")
    return today_id


def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp)


def get_days_in_range(start_date, end_date):
    days_dic = dict()
    years_dic = dict()
    months_dic = dict()
    weeks_dic = dict()

    # Calculate the number of days between the two dates
    delta = end_date - start_date
    # Iterate through the days and print each day
    for i in range(delta.days + 1):
        current_date = start_date + timedelta(days=i)
        year = current_date.strftime("%Y")
        month_number = current_date.strftime("%m")
        month_name = current_date.strftime("%B")
        day_number = current_date.strftime("%d")
        day_name = current_date.strftime("%A")
        week = current_date.strftime("%W")
        day_index = f"{year}_{month_number}_{week}_{day_number}"

        days_dic[day_index] = dict()
        days_dic[day_index]['year'] = year
        days_dic[day_index]['month_number'] = month_number
        days_dic[day_index]['month_name'] = month_name
        days_dic[day_index]['day_number'] = day_number
        days_dic[day_index]['day_name'] = day_name
        days_dic[day_index]['week'] = week

        if year not in years_dic.keys():
            years_dic[year] = []
        years_dic[year].append(day_index)

        month_key = f"{year}{month_name}"
        if month_key not in months_dic.keys():
            months_dic[month_key] = []
        months_dic[month_key].append(day_index)

        if week not in weeks_dic.keys():
            weeks_dic[week] = []
        weeks_dic[week].append(day_index)

    return years_dic, months_dic, weeks_dic, days_dic
