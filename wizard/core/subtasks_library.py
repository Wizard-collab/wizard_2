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
This module provides a library of functions for managing subtasks in the Wizard software.
Each function is designed to perform a specific operation, such as exporting versions,
creating videos, archiving assets, or copying files, by executing Python commands as subtasks.

The module includes the following functionalities:
- Exporting versions and creating videos as subtasks.
- Submitting export tasks to a Deadline render farm.
- Archiving various entities like versions, videos, assets, categories, stages, and variants.
- Performing multithreaded file copy operations.
- Creating videos from renders with customizable parameters.

Each function logs the start and completion of the task, updates progress percentages,
and refreshes the team UI as needed. The tasks are executed as subtasks, allowing users
to monitor their progress through the subtask manager.
"""

# Python modules
import logging

# Wizard modules
from wizard.core import assets
from wizard.core import subtask
from wizard.core import deadline
from wizard.core import environment

logger = logging.getLogger(__name__)


def batch_export(version_id, settings_dic=None, print_stdout=False):
    """
    Starts a subtask to export a version using the provided settings.

    Args:
        version_id (int): The ID of the version to export.
        settings_dic (dict, optional): A dictionary containing export settings. Defaults to None.
        print_stdout (bool, optional): Whether to print the subtask's standard output. Defaults to False.

    This function creates a Python command string that performs the export operation,
    waits for any child processes to complete, and refreshes the team UI. The command
    is executed as a subtask, and the user is notified that the export has started.
    """
    asset_string = assets.instance_to_string(('work_version', version_id))
    command = "# coding: utf-8\n"
    command += "from wizard.core import launch_batch\n"
    command += "from wizard.core import tools\n"
    command += "from wizard.core import team_client\n"
    command += "from wizard.core import environment\n"
    command += f"print('wizard_task_name:Exporting {asset_string}')\n"
    command += f"launch_batch.batch_export({version_id}, {settings_dic})\n"
    command += "tools.wait_for_child_processes()\n"
    command += "team_client.refresh_team(environment.get_team_dns())\n"
    command += "print('wizard_task_status:done')\n"
    task = subtask.subtask(pycmd=command, print_stdout=print_stdout)
    task.start()
    logger.info(
        'Export started as subtask, open the subtask manager to get more informations')


def batch_video(version_id, settings_dic=None, print_stdout=False):
    """
    Starts a subtask to create a video for a specific version using the provided settings.

    Args:
        version_id (int): The ID of the version for which the video is to be created.
        settings_dic (dict, optional): A dictionary containing video creation settings. Defaults to None.
        print_stdout (bool, optional): Whether to print the subtask's standard output. Defaults to False.

    This function creates a Python command string that performs the video creation operation,
    refreshes the team UI, and marks the task as done. The command is executed as a subtask,
    and the user is notified that the video creation has started.
    """
    asset_string = assets.instance_to_string(('work_version', version_id))
    command = "# coding: utf-8\n"
    command += "from wizard.core import launch_batch\n"
    command += "from wizard.core import team_client\n"
    command += "from wizard.core import environment\n"
    command += f"print('wizard_task_name:Creating video for {asset_string}')\n"
    command += f"launch_batch.batch_export({version_id}, {settings_dic})\n"
    command += "team_client.refresh_team(environment.get_team_dns())\n"
    command += "print('wizard_task_status:done')\n"
    task = subtask.subtask(pycmd=command, print_stdout=print_stdout)
    task.start()
    logger.info(
        'Video creation started as subtask, open the subtask manager to get more informations')


def deadline_batch_export(version_id, settings_dic=None, print_stdout=False):
    """
    Submits a Deadline job to export a version using the provided settings.

    Args:
        version_id (int): The ID of the version to export.
        settings_dic (dict, optional): A dictionary containing export settings. Defaults to None.
        print_stdout (bool, optional): Whether to print the subtask's standard output. Defaults to False.

    This function creates a Python command string that performs the export operation,
    refreshes the team UI, and marks the task as done. The command is submitted as a
    Deadline job, allowing the export to be processed in a render farm environment.
    """
    asset_string = assets.instance_to_string(('work_version', version_id))
    command = "# coding: utf-8\n"
    command += "from wizard.core import launch_batch\n"
    command += "from wizard.core import team_client\n"
    command += "from wizard.core import environment\n"
    command += f"print('wizard_task_name:Exporting {asset_string}')\n"
    command += f"launch_batch.batch_export({version_id}, {settings_dic})\n"
    command += "team_client.refresh_team(environment.get_team_dns())\n"
    command += "print('wizard_task_status:done')\n"
    deadline.submit_job(
        pycmd=command, name=f'{environment.get_project_name()} - {asset_string} export')


def archive_versions(version_ids, print_stdout=False):
    """
    Starts a subtask to archive multiple versions.

    Args:
        version_ids (list): A list of version IDs to archive.
        print_stdout (bool, optional): Whether to print the subtask's standard output. Defaults to False.

    This function creates a Python command string that iterates through the provided version IDs,
    archives each version, updates the progress percentage, and refreshes the team UI. The command
    is executed as a subtask, and the user is notified that the archiving process has started.
    """
    command = "# coding: utf-8\n"
    command += "from wizard.core import assets\n"
    command += "from wizard.gui import gui_server\n"
    command += "print('wizard_task_name:Version archiving')\n"
    command += f"percent_step=100.0/len({version_ids})\n"
    command += "percent=0.0\n"
    command += "print(f'wizard_task_percent:{percent}')\n"
    command += f"for version_id in {version_ids}:\n"
    command += "	assets.archive_version(version_id)\n"
    command += "	percent+=percent_step\n"
    command += "	print(f'wizard_task_percent:{percent}')\n"
    command += "gui_server.refresh_team_ui()\n"
    command += "print('wizard_task_status:done')\n"
    task = subtask.subtask(pycmd=command, print_stdout=print_stdout)
    task.start()
    logger.info(
        'Archiving started as subtask, open the subtask manager to get more informations')


def archive_videos(videos_ids, print_stdout=False):
    """
    Starts a subtask to archive multiple videos.

    Args:
        videos_ids (list): A list of video IDs to archive.
        print_stdout (bool, optional): Whether to print the subtask's standard output. Defaults to False.

    This function creates a Python command string that iterates through the provided video IDs,
    archives each video, updates the progress percentage, and refreshes the team UI. The command
    is executed as a subtask, and the user is notified that the archiving process has started.
    """
    command = "# coding: utf-8\n"
    command += "from wizard.core import assets\n"
    command += "from wizard.gui import gui_server\n"
    command += "print('wizard_task_name:Video archiving')\n"
    command += f"percent_step=100.0/len({videos_ids})\n"
    command += "percent=0.0\n"
    command += "print(f'wizard_task_percent:{percent}')\n"
    command += f"for video_id in {videos_ids}:\n"
    command += "	assets.archive_video(video_id)\n"
    command += "	percent+=percent_step\n"
    command += "	print(f'wizard_task_percent:{percent}')\n"
    command += "gui_server.refresh_team_ui()\n"
    command += "print('wizard_task_status:done')\n"
    task = subtask.subtask(pycmd=command, print_stdout=print_stdout)
    task.start()
    logger.info(
        'Archiving started as subtask, open the subtask manager to get more informations')


def archive_export_versions(export_version_ids, print_stdout=False):
    """
    Archives a list of export versions by creating and executing a subtask.

    This function generates a Python command script that iterates through the 
    provided export version IDs, archives each version, and updates the progress 
    percentage. The task is executed as a subtask, and the UI is refreshed after 
    each version is archived.

    Args:
        export_version_ids (list): A list of export version IDs to be archived.
        print_stdout (bool, optional): If True, the subtask will print its output 
            to the standard output. Defaults to False.

    Behavior:
        - Logs the start of the archiving process.
        - Iterates through the provided export version IDs.
        - Archives each export version using the `assets.archive_export_version` method.
        - Updates and prints the progress percentage for each archived version.
        - Refreshes the team UI using `gui_server.refresh_team_ui`.
        - Logs the completion of the task.

    Note:
        The task is executed as a subtask, and users can monitor its progress 
        through the subtask manager.
    """
    command = "# coding: utf-8\n"
    command += "from wizard.core import assets\n"
    command += "from wizard.gui import gui_server\n"
    command += "print('wizard_task_name:Export version archiving')\n"
    command += f"percent_step=100.0/len({export_version_ids})\n"
    command += "percent=0.0\n"
    command += "print(f'wizard_task_percent:{percent}')\n"
    command += f"for export_version_id in {export_version_ids}:\n"
    command += "	assets.archive_export_version(export_version_id)\n"
    command += "	percent+=percent_step\n"
    command += "	print(f'wizard_task_percent:{percent}')\n"
    command += "gui_server.refresh_team_ui()\n"
    command += "print('wizard_task_status:done')\n"
    task = subtask.subtask(pycmd=command, print_stdout=print_stdout)
    task.start()
    logger.info(
        'Archiving started as subtask, open the subtask manager to get more informations')


def archive_exports(export_ids, print_stdout=False):
    """
    Starts a subtask to archive multiple exports.

    Args:
        export_ids (list): A list of export IDs to archive.
        print_stdout (bool, optional): Whether to print the subtask's standard output. Defaults to False.

    This function creates a Python command string that iterates through the provided export IDs,
    archives each export, updates the progress percentage, and refreshes the team UI. The command
    is executed as a subtask, and the user is notified that the archiving process has started.

    Behavior:
        - Logs the start of the archiving process.
        - Iterates through the provided export IDs.
        - Archives each export using the `assets.archive_export` method.
        - Updates and prints the progress percentage for each archived export.
        - Refreshes the team UI using `gui_server.refresh_team_ui`.
        - Logs the completion of the task.

    Note:
        The task is executed as a subtask, and users can monitor its progress 
        through the subtask manager.
    """
    command = "# coding: utf-8\n"
    command += "from wizard.core import assets\n"
    command += "from wizard.gui import gui_server\n"
    command += "print('wizard_task_name:Export archiving')\n"
    command += f"percent_step=100.0/len({export_ids})\n"
    command += "percent=0.0\n"
    command += "print(f'wizard_task_percent:{percent}')\n"
    command += f"for export_id in {export_ids}:\n"
    command += "	assets.archive_export(export_id)\n"
    command += "	percent+=percent_step\n"
    command += "	print(f'wizard_task_percent:{percent}')\n"
    command += "gui_server.refresh_team_ui()\n"
    command += "print('wizard_task_status:done')\n"
    task = subtask.subtask(pycmd=command, print_stdout=print_stdout)
    task.start()
    logger.info(
        'Archiving started as subtask, open the subtask manager to get more informations')


def archive_asset(asset_id, print_stdout=False):
    """
    Starts a subtask to archive a specific asset.

    Args:
        asset_id (int): The ID of the asset to archive.
        print_stdout (bool, optional): Whether to print the subtask's standard output. Defaults to False.

    This function creates a Python command string that performs the asset archiving operation,
    updates the progress percentage, and refreshes the team UI. The command is executed as a subtask,
    and the user is notified that the archiving process has started.

    Behavior:
        - Logs the start of the archiving process.
        - Archives the specified asset using the `assets.archive_asset` method.
        - Updates and prints the progress percentage.
        - Refreshes the team UI using `gui_server.refresh_team_ui`.
        - Logs the completion of the task.

    Note:
        The task is executed as a subtask, and users can monitor its progress 
        through the subtask manager.
    """
    command = "# coding: utf-8\n"
    command += "from wizard.core import assets\n"
    command += "from wizard.gui import gui_server\n"
    command += "print('wizard_task_name:Asset archiving')\n"
    command += "print('wizard_task_percent:0')\n"
    command += f"assets.archive_asset({asset_id})\n"
    command += "print('wizard_task_percent:100')\n"
    command += "gui_server.refresh_team_ui()\n"
    command += "print('wizard_task_status:done')\n"
    task = subtask.subtask(pycmd=command, print_stdout=print_stdout)
    task.start()
    logger.info(
        'Archiving started as subtask, open the subtask manager to get more informations')


def archive_category(category_id, print_stdout=False):
    """
    Starts a subtask to archive a specific category.

    Args:
        category_id (int): The ID of the category to archive.
        print_stdout (bool, optional): Whether to print the subtask's standard output. Defaults to False.

    This function creates a Python command string that performs the category archiving operation,
    updates the progress percentage, and refreshes the team UI. The command is executed as a subtask,
    and the user is notified that the archiving process has started.

    Behavior:
        - Logs the start of the archiving process.
        - Archives the specified category using the `assets.archive_category` method.
        - Updates and prints the progress percentage.
        - Refreshes the team UI using `gui_server.refresh_team_ui`.
        - Logs the completion of the task.

    Note:
        The task is executed as a subtask, and users can monitor its progress 
        through the subtask manager.
    """
    command = "# coding: utf-8\n"
    command += "from wizard.core import assets\n"
    command += "from wizard.gui import gui_server\n"
    command += "print('wizard_task_name:Category archiving')\n"
    command += "print('wizard_task_percent:0')\n"
    command += f"assets.archive_category({category_id})\n"
    command += "print('wizard_task_percent:100')\n"
    command += "gui_server.refresh_team_ui()\n"
    command += "print('wizard_task_status:done')\n"
    task = subtask.subtask(pycmd=command, print_stdout=print_stdout)
    task.start()
    logger.info(
        'Archiving started as subtask, open the subtask manager to get more informations')


def archive_stage(stage_id, print_stdout=False):
    """
    Starts a subtask to archive a specific stage.

    Args:
        stage_id (int): The ID of the stage to archive.
        print_stdout (bool, optional): Whether to print the subtask's standard output. Defaults to False.

    This function creates a Python command string that performs the stage archiving operation,
    updates the progress percentage, and refreshes the team UI. The command is executed as a subtask,
    and the user is notified that the archiving process has started.

    Behavior:
        - Logs the start of the archiving process.
        - Archives the specified stage using the `assets.archive_stage` method.
        - Updates and prints the progress percentage.
        - Refreshes the team UI using `gui_server.refresh_team_ui`.
        - Logs the completion of the task.

    Note:
        The task is executed as a subtask, and users can monitor its progress 
        through the subtask manager.
    """
    command = "# coding: utf-8\n"
    command += "from wizard.core import assets\n"
    command += "from wizard.gui import gui_server\n"
    command += "print('wizard_task_name:Stage archiving')\n"
    command += "print('wizard_task_percent:0')\n"
    command += f"assets.archive_stage({stage_id})\n"
    command += "print('wizard_task_percent:100')\n"
    command += "gui_server.refresh_team_ui()\n"
    command += "print('wizard_task_status:done')\n"
    task = subtask.subtask(pycmd=command, print_stdout=print_stdout)
    task.start()
    logger.info(
        'Archiving started as subtask, open the subtask manager to get more informations')


def archive_variant(variant_id, print_stdout=False):
    """
    Starts a subtask to archive a specific variant.

    Args:
        variant_id (int): The ID of the variant to archive.
        print_stdout (bool, optional): Whether to print the subtask's standard output. Defaults to False.

    This function creates a Python command string that performs the variant archiving operation,
    updates the progress percentage, and refreshes the team UI. The command is executed as a subtask,
    and the user is notified that the archiving process has started.

    Behavior:
        - Logs the start of the archiving process.
        - Archives the specified variant using the `assets.archive_variant` method.
        - Updates and prints the progress percentage.
        - Refreshes the team UI using `gui_server.refresh_team_ui`.
        - Logs the completion of the task.

    Note:
        The task is executed as a subtask, and users can monitor its progress 
        through the subtask manager.
    """
    command = "# coding: utf-8\n"
    command += "from wizard.core import assets\n"
    command += "from wizard.gui import gui_server\n"
    command += "print('wizard_task_name:Variant archiving')\n"
    command += "print('wizard_task_percent:0')\n"
    command += f"assets.archive_variant({variant_id})\n"
    command += "print('wizard_task_percent:100')\n"
    command += "gui_server.refresh_team_ui()\n"
    command += "print('wizard_task_status:done')\n"
    task = subtask.subtask(pycmd=command, print_stdout=print_stdout)
    task.start()
    logger.info(
        'Archiving started as subtask, open the subtask manager to get more informations')


def threaded_copy(files_list, destination, max_threads=16, print_stdout=False):
    """
    Starts a subtask to copy multiple files to a destination using multithreading.

    Args:
        files_list (list): A list of file paths to copy.
        destination (str): The destination directory where files will be copied.
        max_threads (int, optional): The maximum number of threads to use for copying. Defaults to 16.
        print_stdout (bool, optional): Whether to print the subtask's standard output. Defaults to False.

    This function creates a Python command string that performs a multithreaded copy operation
    using the `threaded_copy` module. The task is executed as a subtask, and the user is notified
    that the copy process has started.

    Behavior:
        - Logs the start of the threaded copy process.
        - Copies the specified files to the destination directory using multiple threads.
        - Marks the task as done upon completion.

    Note:
        The task is executed as a subtask, and users can monitor its progress through the subtask manager.
    """
    command = "# coding: utf-8\n"
    command += "from wizard.core import threaded_copy\n"
    command += f"threaded_copy.threaded_copy({files_list}, '{destination}', {max_threads}).copy()\n"
    command += "print('wizard_task_status:done')\n"
    task = subtask.subtask(pycmd=command, print_stdout=print_stdout)
    task.start()
    logger.info(
        'Threaded copy started as subtask, open the subtask manager to get more informations')


def create_video_from_render(export_version_id, ics, ocs, channel, frame_rate, comment='', overlay=True, print_stdout=False):
    """
    Starts a subtask to create a video from a render.

    Args:
        export_version_id (int): The ID of the export version to create the video from.
        ics (str): The input color space for the render.
        ocs (str): The output color space for the video.
        frame_rate (float): The frame rate of the resulting video.
        comment (str, optional): A comment to include in the video metadata. Defaults to an empty string.
        overlay (bool, optional): Whether to include an overlay in the video. Defaults to True.
        print_stdout (bool, optional): Whether to print the subtask's standard output. Defaults to False.

    This function creates a Python command string that performs the video creation operation
    using the `video.video_from_render` method. It refreshes the team UI upon completion
    and marks the task as done. The task is executed as a subtask, and the user is notified
    that the video creation process has started.

    Behavior:
        - Logs the start of the video creation process.
        - Creates a video from the specified render using the provided parameters.
        - Refreshes the team UI using `gui_server.refresh_team_ui`.
        - Logs the completion of the task.

    Note:
        The task is executed as a subtask, and users can monitor its progress through the subtask manager.
    """
    command = "# coding: utf-8\n"
    command += "from wizard.gui import gui_server\n"
    command += "from wizard.core import video\n"
    command += f"video.video_from_render({export_version_id}, '{ics}', '{ocs}', '{channel}', {frame_rate}, comment='''{comment}''', overlay={overlay})\n"
    command += "gui_server.refresh_team_ui()\n"
    command += "print('wizard_task_status:done')\n"
    task = subtask.subtask(pycmd=command, print_stdout=print_stdout)
    task.start()
    logger.info(
        'Render to video started as subtask, open the subtask manager to get more informations')
