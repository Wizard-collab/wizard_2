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
This module provides functionality for analyzing comments to identify and process
user mentions and tag groups. It includes the following:

- Parsing comments to extract words starting with '@', which are treated as user mentions
    or tag group references.
- Checking if mentioned users exist in the repository and are part of the project.
- Handling special cases like '@all' to trigger events for all users.
- Verifying if mentioned tag groups exist in the project and triggering events accordingly.

Dependencies:
- Python's logging module for logging messages.
- Wizard's core modules: events, project, and repository for handling project-specific
    operations and events.

Functions:
- analyse_comment: Analyzes a comment to identify user mentions and tag groups, and
    triggers appropriate events.

This module is part of the Wizard project and adheres to the MIT License.
"""

# Python modules
import logging

# Wizard modules
from wizard.core import events
from wizard.core import project
from wizard.core import repository

logger = logging.getLogger(__name__)


def analyse_comment(comment, instance_type, instance_id):
    """
    Analyzes a comment to identify and process user mentions and tag groups.

    This function parses a given comment to extract words that start with '@',
    which are treated as user mentions or tag group references. It performs
    the following actions:
    - Checks if the mentioned user exists in the repository and is part of the
      project. If so, it triggers a tag event.
    - Handles the special case where '@all' is mentioned, triggering a tag event.
    - Checks if the mentioned tag group exists in the project and triggers a
      tag event if a match is found.

    Args:
        comment (str): The comment text to analyze.
        instance_type (str): The type of the instance associated with the comment.
        instance_id (int): The ID of the instance associated with the comment.

    Returns:
        None
    """
    # Split the comment into words, replacing newlines and carriage returns with spaces
    comment_words = comment.replace('\n', ' ').replace('\r', ' ').split(' ')

    # Iterate through each word in the comment
    for word in comment_words:
        # Skip words that do not start with '@'
        if not word.startswith('@'):
            continue

        # Extract the user or tag group name by removing '@' and any newline or carriage return characters
        user = word.replace('@', '').replace('\r', '').replace('\n', '')

        # Check if the extracted name is a valid user in the repository
        if user in repository.get_user_names_list():
            # Retrieve the user ID from the repository
            user_id = repository.get_user_row_by_name(user, 'id')

            # Verify if the user ID is part of the current project
            if user_id in project.get_users_ids_list():
                # Trigger a tag event for the identified user
                events.add_tag_event(instance_type, instance_id, comment, user)

        # Handle the special case where '@all' is mentioned
        elif user == 'all':
            # Trigger a tag event for all users
            events.add_tag_event(instance_type, instance_id, comment, user)

        # Retrieve all tag groups in the project
        all_tag_groups = project.get_all_tag_groups()

        # Check if the extracted name matches any tag group name
        for tag_group_row in all_tag_groups:
            if user in tag_group_row['name']:
                # Trigger a tag event for the matching tag group
                events.add_tag_event(instance_type, instance_id, comment, user)
