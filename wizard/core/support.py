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
import json
import logging

# Wizard modules
from wizard.core import application
from wizard.core import environment

logger = logging.getLogger(__name__)

URL = "http://93.19.210.30/support/"

def send_log(log, type, additionnal_message=''):
    contact_dic = dict()
    contact_dic['username'] = environment.get_user()
    contact_dic['log'] = log
    contact_dic['additionnal_message'] = additionnal_message
    version_dic = application.get_version()
    contact_dic['wizard_version'] = f"{version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']}.{version_dic['builds']}"
    contact_dic['user_email'] = environment.get_user_email()
    contact_dic['type'] = type

    try:
        response = requests.post(URL, data=contact_dic)
        response_dic = response.json()
        if response_dic['success']:
            logger.info(response_dic['messages_list'][0])
        else:
            for message in response_dic['messages_list']:
                logger.error(message)
    except requests.Timeout:
        logger.error('Connection timed out')
    except requests.ConnectionError:
        logger.error('No network connection')
