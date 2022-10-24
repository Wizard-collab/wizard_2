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

# Python modules
import requests
import traceback
import json
import logging

# Wizard modules
from wizard.core import application
from wizard.core import environment
from wizard.vars import ressources

logger = logging.getLogger(__name__)

def get_latest_build():
    URL = f"{ressources._web_server_url_}latest_build/"
    try:
        response = requests.post(URL, timeout=3)
        return response.json()
    except requests.Timeout:
        logger.error('Connection timed out')
    except requests.ConnectionError:
        logger.error('No network connection')
    except:
        logger.error(str(traceback.format_exc()))

def send_log(log, type, additionnal_message=''):
    URL = f"{ressources._web_server_url_}support/"
    contact_dic = dict()
    contact_dic['username'] = environment.get_user()
    contact_dic['project'] = environment.get_project_name()
    contact_dic['repository'] = environment.get_repository()
    contact_dic['log'] = log
    if additionnal_message == '':
        additionnal_message = 'No message from user'
    contact_dic['additionnal_message'] = additionnal_message
    version_dic = application.get_version()
    contact_dic['wizard_version'] = f"{version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']}.{version_dic['builds']}"
    contact_dic['user_email'] = environment.get_user_email()
    contact_dic['type'] = type

    try:
        response = requests.post(URL, data=contact_dic)
        success = response.json()
        if success:
            logger.info("Log successfully submitted")
        else:
            logger.info("Can't submit log, server error\nPlease contact the administrator")
    except requests.Timeout:
        logger.error('Connection timed out')
    except requests.ConnectionError:
        logger.error('No network connection')
    except:
        logger.error(str(traceback.format_exc()))

def send_quote(quote):
    URL = f"{ressources._web_server_url_}quotes/"
    contact_dic = dict()
    contact_dic['username'] = environment.get_user()
    contact_dic['quote_content'] = quote
    contact_dic['user_email'] = environment.get_user_email()
    contact_dic['repository'] = environment.get_repository()

    try:
        response = requests.post(URL, data=contact_dic)
        success = response.json()
        if success:
            logger.info("Quote successfully submitted")
        else:
            logger.info("Can't submit quote, server error\nPlease contact the administrator")
    except requests.Timeout:
        logger.error('Connection timed out')
    except requests.ConnectionError:
        logger.error('No network connection')
    except:
        logger.error(str(traceback.format_exc()))

