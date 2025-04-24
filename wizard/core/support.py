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
This module provides support functionalities for the Wizard application.

It includes methods to:
- Fetch the latest build information from a remote server.
- Send log messages to a support server with user and application details.
- Submit user quotes to a predefined server.

The module handles network-related exceptions and logs errors or success messages
to ensure robustness and traceability.

Dependencies:
- Python modules: requests, traceback, logging
- Wizard modules: application, environment, ressources
"""

# Python modules
import requests
import traceback
import logging

# Wizard modules
from wizard.core import application
from wizard.core import environment
from wizard.vars import ressources

logger = logging.getLogger(__name__)


def get_latest_build():
    """
    Fetches the latest build information from a predefined web server URL.

    This function sends a POST request to the server's "latest_build" endpoint
    and attempts to retrieve the response in JSON format. It handles various
    exceptions to ensure robustness in case of network issues or other errors.

    Returns:
        dict: The JSON response from the server if the request is successful.
        None: If an exception occurs or the request fails.

    Exceptions Handled:
        - requests.Timeout: Logs an error if the connection times out.
        - requests.ConnectionError: Logs an error if there is no network connection.
        - Other exceptions: Logs the full traceback of the error.
    """
    URL = f"{ressources._web_server_url_}latest_build/"
    try:
        response = requests.post(URL, timeout=3)
        return response.json()
    except requests.Timeout:
        logger.error('Connection timed out')
        return
    except requests.ConnectionError:
        logger.error('No network connection')
        return
    except:
        logger.error(str(traceback.format_exc()))
        return


def send_log(log, type, additionnal_message=''):
    """
    Sends a log message along with additional information to a remote support server.

    Args:
        log (str): The log message to be sent.
        type (str): The type/category of the log (e.g., error, info, warning).
        additionnal_message (str, optional): An additional message provided by the user. 
            Defaults to 'No message from user' if not specified.

    Raises:
        requests.Timeout: If the connection to the server times out.
        requests.ConnectionError: If there is no network connection.
        Exception: For any other unexpected errors.

    Notes:
        - The function gathers user, project, repository, and application version information 
          to include in the log submission.
        - Logs are sent as a POST request to a predefined support server URL.
        - Logs the success or failure of the submission process.
    """
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
            logger.info(
                "Can't submit log, server error\nPlease contact the administrator")
    except requests.Timeout:
        logger.error('Connection timed out')
        return
    except requests.ConnectionError:
        logger.error('No network connection')
        return
    except:
        logger.error(str(traceback.format_exc()))
        return


def send_quote(quote):
    """
    Sends a quote to a predefined web server URL.

    This function constructs a dictionary containing user information and the
    quote content, then sends it as a POST request to the server. It handles
    various exceptions that may occur during the request and logs the outcome.

    Args:
        quote (str): The content of the quote to be sent.

    Raises:
        None: This function does not raise exceptions but logs errors instead.

    Logs:
        - Logs a success message if the quote is successfully submitted.
        - Logs an error message if the server returns an error, the connection
          times out, there is no network connection, or any other exception occurs.
    """
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
            logger.info(
                "Can't submit quote, server error\nPlease contact the administrator")
    except requests.Timeout:
        logger.error('Connection timed out')
        return
    except requests.ConnectionError:
        logger.error('No network connection')
        return
    except:
        logger.error(str(traceback.format_exc()))
        return
