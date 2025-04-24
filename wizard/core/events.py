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
This module provides functions to log and manage various types of events 
within the Wizard project. Events include creation, export, video creation, 
archiving, tagging, and comment modification. Each event is logged with 
specific details such as titles, comments, and associated data.
Functions:
    - add_creation_event(instance_type, instance_id): Logs a creation event for a given instance.
    - add_export_event(export_version_id): Adds an export event to the project.
    - add_video_event(video_id, variant_id): Creates and logs an event for a newly created video.
    - add_archive_event(title, archive_path): Adds an archive event to the project.
    - add_tag_event(instance_type, instance_id, comment, user): Creates and adds a tagging event to the project.
    - modify_comment(event_id, comment): Modifies the comment associated with a specific event.
Dependencies:
    - Python modules: logging
    - Wizard modules: project, assets
This module is part of the Wizard project and is licensed under the MIT License.
"""

# Python modules
import logging

# Wizard modules
from wizard.core import project
from wizard.core import assets

logger = logging.getLogger(__name__)


def add_creation_event(instance_type, instance_id):
    """
    Logs a creation event for a given instance.

    Args:
        instance_type (str): The type of the instance being created (e.g., "file", "folder").
        instance_id (str): The unique identifier of the instance.

    Returns:
        bool: True if the event was successfully added, False otherwise.
    """
    data = (instance_type, instance_id)
    title = f"Created {assets.instance_to_string((instance_type, instance_id))}"
    return project.add_event('creation', title, '', data)


def add_export_event(export_version_id):
    """
    Adds an export event to the project.

    This function creates an event entry for an export operation, including
    details such as the export version ID, a title, a comment, and a thumbnail
    path associated with the export version.

    Args:
        export_version_id (int): The unique identifier for the export version.

    Returns:
        dict: A dictionary representing the newly added event, as returned by
        the `project.add_event` method.
    """
    title = f"Exported {assets.instance_to_string(('export_version', export_version_id))}"
    data = export_version_id
    export_version_row = project.get_export_version_data(export_version_id)
    return project.add_event('export', title, export_version_row['comment'], data, '', export_version_row['work_version_thumbnail_path'])


def add_video_event(video_id, variant_id):
    """
    Creates and logs an event for a newly created video.

    This function generates a descriptive title for the event based on the 
    provided variant ID, retrieves the video data, and adds the event to the 
    project's event log. The event includes details such as the video comment 
    and thumbnail path.

    Args:
        video_id (str): The unique identifier of the video.
        variant_id (str): The unique identifier of the variant used to create the video.

    Returns:
        dict: The event data added to the project's event log.
    """
    title = f"Created a video from {assets.instance_to_string(('variant', variant_id))}"
    data = video_id
    video_row = project.get_video_data(video_id)
    return project.add_event('video', title, video_row['comment'], data, '', video_row['thumbnail_path'])


def add_archive_event(title, archive_path):
    """
    Adds an archive event to the project.

    This function creates an event of type 'archive' with the specified title
    and archive path, and adds it to the project.

    Args:
        title (str): The title of the archive event.
        archive_path (str): The file path to the archive.

    Returns:
        bool: True if the event was successfully added, False otherwise.
    """
    data = archive_path
    return project.add_event('archive', title, '', data)


def add_tag_event(instance_type, instance_id, comment, user):
    """
    Creates and adds a tagging event to the project.

    This function generates an event to indicate that a user has been tagged
    in a comment associated with a specific instance. The event is then added
    to the project's event log.

    Args:
        instance_type (str): The type of the instance (e.g., "task", "issue").
        instance_id (int): The unique identifier of the instance.
        comment (str): The comment in which the user is tagged.
        user (str): The username of the tagged user.

    Returns:
        bool: True if the event was successfully added, False otherwise.
    """
    data_dic = dict()
    data_dic['instance'] = (instance_type, instance_id)
    data_dic['tagged_user'] = user
    title = f"Tagged {user} in a comment"
    return project.add_event('tag', title, comment, data_dic)


def modify_comment(event_id, comment):
    """
    Modifies the comment associated with a specific event.

    Args:
        event_id (int): The unique identifier of the event to be modified.
        comment (str): The new comment to associate with the event.

    Returns:
        bool: True if the modification was successful, False otherwise.
    """
    return project.modify_event_message(event_id, comment)
