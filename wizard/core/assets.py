# coding: utf-8
# This file uses UTF-8 encoding to ensure compatibility with a wide range of characters.
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
import os
import time
import json
import logging
import clipboard
import traceback
import uuid

# Wizard modules
from wizard.core import environment
from wizard.core import events
from wizard.core import project
from wizard.core import repository
from wizard.core import tools
from wizard.core import path_utils
from wizard.core import image
from wizard.core import game
from wizard.core import tags
from wizard.core import stats
from wizard.core import asset_tracking
from wizard.core import hooks
from wizard.core import user
from wizard.core import subtasks_library
from wizard.vars import assets_vars
from wizard.vars import game_vars
from wizard.vars import project_vars

logger = logging.getLogger(__name__)


def create_domain(name):
    """
    Creates a new domain in the project.

    Args:
        name (str): The name of the domain to be created.

    Returns:
        int: The ID of the created domain if successful, otherwise None.

    Behavior:
        - Validates the domain name to ensure it is safe.
        - Constructs the directory path for the new domain.
        - Adds the domain to the project database.
        - Creates the corresponding folder in the file system.
        - If folder creation fails, removes the domain from the database.
    """
    if not tools.is_safe(name):
        return
    dir_name = path_utils.clean_path(path_utils.join(environment.get_project_path(),
                                                     name))
    domain_id = project.add_domain(name)
    if not domain_id:
        return
    if not tools.create_folder(dir_name):
        project.remove_domain(domain_id)
        return
    return domain_id


def archive_domain(domain_id):
    """
    Archives a domain by creating a compressed archive of its directory, 
    removing the directory, and then deleting the domain from the project.

    Args:
        domain_id (int): The unique identifier of the domain to be archived.

    Returns:
        None

    Behavior:
        - Checks if the current user has admin privileges. If not, the function exits.
        - Retrieves the domain data using the provided domain ID. If the domain does not exist, the function exits.
        - Verifies if the domain directory exists. Logs a warning and exits if the directory is not found.
        - Creates a compressed archive of the domain directory. If the archive creation fails, the function exits.
        - Deletes the domain directory after successfully creating the archive.
        - Logs the deletion of the directory and records a progress event in the statistics.
        - Removes the domain from the project.
    """
    if not repository.is_admin():
        return
    domain_row = project.get_domain_data(domain_id)
    if not domain_row:
        return
    dir_name = get_domain_path(domain_id)
    if not path_utils.isdir(dir_name):
        logger.warning(f"{dir_name} not found")
        return
    if not tools.make_archive(dir_name):
        return
    path_utils.rmtree(dir_name)
    logger.info(f"{dir_name} deleted")
    stats.add_progress_event()
    return project.remove_domain(domain_id)


def create_category(name, domain_id):
    """
    Creates a new category within a specified domain.

    Args:
        name (str): The name of the category to be created.
        domain_id (int): The ID of the domain where the category will be created.

    Returns:
        int: The ID of the created category if successful, otherwise None.

    Behavior:
        - Validates the category name to ensure it is safe.
        - Retrieves the path of the domain where the category will be created.
        - Adds the category to the project database.
        - Creates the corresponding folder in the file system.
        - If folder creation fails, removes the category from the database.
        - Executes post-creation hooks and logs the creation event.
    """
    if not tools.is_safe(name):
        return
    domain_path = get_domain_path(domain_id)
    if not domain_path:
        logger.error("Can't create category")
        return
    category_id = project.add_category(name, domain_id)
    if not category_id:
        return
    dir_name = path_utils.clean_path(path_utils.join(domain_path, name))
    if not tools.create_folder(dir_name):
        project.remove_category(category_id, force=1)
        return
    category_row = project.get_category_data(category_id)
    hooks.after_category_creation_hook(category_row['string'], name)
    events.add_creation_event('category', category_id)
    game.add_xps(game_vars._creation_xp_)
    stats.add_progress_event()
    return category_id


def archive_category(category_id):
    """
    Archives a category by creating a compressed archive of its directory, 
    removing the directory, and then deleting the category from the project.

    Args:
        category_id (int): The unique identifier of the category to be archived.

    Returns:
        int: 1 if the category was successfully archived, otherwise None.

    Behavior:
        - Checks if the current user has admin privileges. If not, the function exits.
        - Retrieves the category data using the provided category ID. If the category does not exist, the function exits.
        - Verifies if the category directory exists. Logs a warning and exits if the directory is not found.
        - Creates a compressed archive of the category directory. If the archive creation fails, the function exits.
        - Deletes the category directory after successfully creating the archive.
        - Logs the deletion of the directory and records a progress event in the statistics.
        - Removes the category from the project.
    """
    if not repository.is_admin():
        return
    category_row = project.get_category_data(category_id)
    if not category_row:
        return
    dir_name = get_category_path(category_id)
    if path_utils.isdir(dir_name):
        archive_file = tools.make_archive(dir_name)
        if archive_file:
            path_utils.rmtree(dir_name)
            logger.info(f"{dir_name} deleted")
    else:
        logger.warning(f"{dir_name} not found")
        archive_file = ''
    if not project.remove_category(category_id):
        return
    events.add_archive_event(f"Archived {instance_to_string(('domain', category_row['domain_id']))}/{category_row['name']}",
                             archive_file)
    stats.add_progress_event()
    return 1


def create_asset(name, category_id, inframe=100, outframe=220, preroll=0, postroll=0):
    """
    Creates a new asset within a specified category.

    Args:
        name (str): The name of the asset to be created.
        category_id (int): The ID of the category where the asset will be created.
        inframe (int, optional): The starting frame of the asset. Defaults to 100.
        outframe (int, optional): The ending frame of the asset. Defaults to 220.
        preroll (int, optional): The number of preroll frames. Defaults to 0.
        postroll (int, optional): The number of postroll frames. Defaults to 0.

    Returns:
        int: The ID of the created asset if successful, otherwise None.

    Behavior:
        - Validates the asset name to ensure it is safe.
        - Retrieves the path of the category where the asset will be created.
        - Adds the asset to the project database.
        - Creates the corresponding folder in the file system.
        - If folder creation fails, removes the asset from the database.
        - Executes post-creation hooks and logs the creation event.
    """
    if not tools.is_safe(name):
        return
    category_path = get_category_path(category_id)
    if not category_path:
        logger.error("Can't create asset")
        return
    dir_name = path_utils.clean_path(path_utils.join(category_path, name))
    asset_id = project.add_asset(name,
                                 category_id,
                                 inframe,
                                 outframe,
                                 preroll,
                                 postroll)
    if not asset_id:
        return
    if not tools.create_folder(dir_name):
        project.remove_asset(asset_id, force=1)
        return
    asset_row = project.get_asset_data(asset_id)
    hooks.after_asset_creation_hook(asset_row['string'], name)
    events.add_creation_event('asset', asset_id)
    game.add_xps(game_vars._creation_xp_)
    game.add_coins(game_vars._creation_coins_)
    stats.add_progress_event()
    return asset_id


def modify_asset_frame_range(asset_id, inframe, outframe, preroll, postroll):
    """
    Modifies the frame range of an existing asset.

    Args:
        asset_id (int): The unique identifier of the asset to be modified.
        inframe (int): The new starting frame of the asset.
        outframe (int): The new ending frame of the asset.
        preroll (int): The new number of preroll frames.
        postroll (int): The new number of postroll frames.

    Returns:
        int: 1 if the frame range was successfully modified, otherwise None.

    Behavior:
        - Updates the frame range of the asset in the project database.
        - Logs a success message if the modification is successful.
    """
    if project.modify_asset_frame_range(asset_id,
                                        inframe,
                                        outframe,
                                        preroll,
                                        postroll):
        logger.info("Frame range modified")
        return 1
    else:
        return


def archive_asset(asset_id):
    """
    Archives an asset by creating a compressed archive of its directory, 
    removing the directory, and then deleting the asset from the project.

    Args:
        asset_id (int): The unique identifier of the asset to be archived.

    Returns:
        int: 1 if the asset was successfully archived, otherwise None.

    Behavior:
        - Checks if the current user has admin privileges. If not, the function exits.
        - Retrieves the asset data using the provided asset ID. If the asset does not exist, the function exits.
        - Verifies if the asset directory exists. Logs a warning and exits if the directory is not found.
        - Creates a compressed archive of the asset directory. If the archive creation fails, the function exits.
        - Deletes the asset directory after successfully creating the archive.
        - Logs the deletion of the directory and records a progress event in the statistics.
        - Removes the asset from the project.
    """
    if not repository.is_admin():
        return
    asset_row = project.get_asset_data(asset_id)
    if not asset_row:
        return
    dir_name = get_asset_path(asset_id)
    if path_utils.isdir(dir_name):
        archive_file = tools.make_archive(dir_name)
        if archive_file:
            path_utils.rmtree(dir_name)
            logger.info(f"{dir_name} deleted")
    else:
        logger.warning(f"{dir_name} not found")
        archive_file = ''
    if not project.remove_asset(asset_id):
        return
    events.add_archive_event(f"Archived {instance_to_string(('category', asset_row['category_id']))}/{asset_row['name']}",
                             archive_file)
    stats.add_progress_event()
    return 1


def get_asset_data_from_work_env_id(work_env_id, column='*'):
    """
    Retrieves asset data associated with a given work environment ID.

    Args:
        work_env_id (int): The ID of the work environment.
        column (str, optional): The specific column to retrieve. Defaults to '*' (all columns).

    Returns:
        dict or None: The asset data if found, otherwise None.

    Behavior:
        - Retrieves the variant ID associated with the work environment.
        - Retrieves the stage ID associated with the variant.
        - Retrieves the asset ID associated with the stage.
        - Fetches the asset data from the project database.
    """
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if not variant_id:
        return
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    if not stage_id:
        return
    asset_id = project.get_stage_data(stage_id, 'asset_id')
    if not asset_id:
        return
    return project.get_asset_data(asset_id, column)


def get_stage_data_from_work_env_id(work_env_id, column='*'):
    """
    Retrieves stage data associated with a given work environment ID.

    Args:
        work_env_id (int): The ID of the work environment.
        column (str, optional): The specific column to retrieve. Defaults to '*' (all columns).

    Returns:
        dict or None: The stage data if found, otherwise None.

    Behavior:
        - Retrieves the variant ID associated with the work environment.
        - Retrieves the stage ID associated with the variant.
        - Fetches the stage data from the project database.
    """
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if not variant_id:
        return
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    if not stage_id:
        return
    return project.get_stage_data(stage_id, column)


def get_domain_data_from_work_env_id(work_env_id, column='*'):
    """
    Retrieves domain data associated with a given work environment ID.

    Args:
        work_env_id (int): The ID of the work environment.
        column (str, optional): The specific column to retrieve. Defaults to '*' (all columns).

    Returns:
        dict or None: The domain data if found, otherwise None.

    Behavior:
        - Retrieves the variant ID associated with the work environment.
        - Retrieves the stage ID associated with the variant.
        - Retrieves the domain ID associated with the stage.
        - Fetches the domain data from the project database.
    """
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if not variant_id:
        return
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    if not stage_id:
        return
    domain_id = project.get_stage_data(stage_id, 'domain_id')
    if not domain_id:
        return
    return project.get_domain_data(domain_id, column)


def create_stage(name, asset_id):
    """
    Creates a new stage for a given asset in the project.
    This function performs several checks and operations to ensure the stage
    is valid and properly created. It validates the asset's category and domain,
    checks if the stage name is allowed based on predefined rules, creates the
    necessary directories, and sets up the stage with a default variant.
    Args:
        name (str): The name of the stage to be created.
        asset_id (int): The ID of the asset for which the stage is being created.
    Returns:
        int or None: The ID of the newly created stage if successful, or None
        if the stage creation fails at any step.
    Notes:
        - The function ensures that the stage name complies with the rules
          defined for the asset's domain.
        - If the stage creation fails at any point, any partially created
          data is cleaned up to maintain consistency.
        - Hooks and progress events are triggered after successful stage creation.
    Function Sections:
        1. **Asset and Category Validation**:
           - Retrieves and validates the asset's category and domain information.
           - Ensures that the category and domain data exist before proceeding.
        2. **Stage Name Validation**:
           - Checks if the provided stage name is allowed based on the domain's
             predefined rules.
           - Logs a warning and exits if the name does not comply.
        3. **Directory and Stage Creation**:
           - Constructs the directory path for the new stage.
           - Create an _EXPORTS subdirectory within the stage directory.
           - Creates the stage in the project database and ensures the directory
             is successfully created.
           - Cleans up partially created data if any step fails.
        4. **Post-Creation Setup**:
           - Creates a default variant for the stage and sets it as the default.
           - Triggers hooks and logs progress events to finalize the stage creation.
    """
    category_id = project.get_asset_data(asset_id, 'category_id')
    if not category_id:
        return
    category_name = project.get_category_data(category_id, 'name')
    if not category_name:
        return
    domain_id = project.get_category_data(category_id, 'domain_id')
    if not domain_id:
        return
    domain_name = project.get_domain_data(domain_id, 'name')
    if not domain_name:
        return

    allowed = None
    if domain_name == assets_vars._assets_:
        if name in assets_vars._assets_stages_list_:
            allowed = 1
    if domain_name == assets_vars._sequences_:
        if name in assets_vars._sequences_stages_list_:
            allowed = 1
    if domain_name == assets_vars._library_:
        if name in assets_vars._library_stages_list_:
            allowed = 1
    if not allowed:
        logger.warning(f"{name} doesn't match stages rules")
        return

    asset_path = get_asset_path(asset_id)
    if not asset_path:
        logger.error("Can't create stage")
        return
    dir_name = path_utils.clean_path(path_utils.join(asset_path, name))
    stage_id = project.add_stage(name, asset_id)
    if not stage_id:
        return
    if not tools.create_folder(dir_name):
        project.remove_stage(stage_id, force=1)
        return
    tools.create_folder(path_utils.clean_path(
        path_utils.join(dir_name, '_EXPORTS')))
    stage_row = project.get_stage_data(stage_id)
    hooks.after_stage_creation_hook(string_stage=stage_row['string'],
                                    stage_name=name)
    variant_id = create_variant('main', stage_id, 'default variant')
    if variant_id:
        project.set_stage_default_variant(stage_id, variant_id)
    stats.add_progress_event(new_stage=stage_id)
    return stage_id


def archive_stage(stage_id):
    """
    Archives a stage by creating a compressed archive of its directory, 
    removing the directory, and then deleting the stage from the project.

    Args:
        stage_id (int): The unique identifier of the stage to be archived.

    Returns:
        int: 1 if the stage was successfully archived, otherwise None.

    Behavior:
        - Checks if the current user has admin privileges. If not, the function exits.
        - Retrieves the stage data using the provided stage ID. If the stage does not exist, the function exits.
        - Verifies if the stage directory exists. Logs a warning and exits if the directory is not found.
        - Creates a compressed archive of the stage directory. If the archive creation fails, the function exits.
        - Deletes the stage directory after successfully creating the archive.
        - Logs the deletion of the directory and records a progress event in the statistics.
        - Removes the stage from the project.
    """
    if not repository.is_admin():
        return
    stage_row = project.get_stage_data(stage_id)
    if not stage_row:
        return
    dir_name = get_stage_path(stage_id)
    if path_utils.isdir(dir_name):
        archive_file = tools.make_archive(dir_name)
        if archive_file:
            path_utils.rmtree(dir_name)
            logger.info(f"{dir_name} deleted")
    else:
        logger.warning(f"{dir_name} not found")
        archive_file = ''
    if not project.remove_stage(stage_id):
        return
    events.add_archive_event(f"Archived {instance_to_string(('asset', stage_row['asset_id']))}/{stage_row['name']}",
                             archive_file)
    stats.add_progress_event(removed_stage=stage_row['name'])
    return 1


def create_variant(name, stage_id, comment=''):
    """
    Creates a new variant for a given stage in the project.

    Args:
        name (str): The name of the variant to be created.
        stage_id (int): The ID of the stage for which the variant is being created.
        comment (str, optional): A comment describing the variant. Defaults to an empty string.

    Returns:
        int or None: The ID of the newly created variant if successful, or None if the creation fails.

    Behavior:
        - Validates the variant name to ensure it is safe.
        - Constructs the directory path for the new variant.
        - Adds the variant to the project database and ensures the directory is successfully created.
        - Creates additional subdirectories (_SANDBOX and _VIDEOS) within the variant directory.
        - Executes post-creation hooks and logs the creation event.
        - Awards experience points for the creation.
    """
    if not tools.is_safe(name):
        return
    stage_path = get_stage_path(stage_id)
    if not stage_path:
        logger.error("Can't create variant")
        return
    dir_name = path_utils.clean_path(path_utils.join(stage_path, name))
    variant_id = project.add_variant(name, stage_id, comment)
    if not variant_id:
        return
    if not tools.create_folder(dir_name):
        project.remove_variant(variant_id, force=1)
        return
    tools.create_folder(path_utils.clean_path(
        path_utils.join(dir_name, '_SANDBOX')))
    tools.create_folder(path_utils.clean_path(
        path_utils.join(dir_name, '_VIDEOS')))
    variant_row = project.get_variant_data(variant_id)
    hooks.after_variant_creation_hook(variant_row['string'], name)
    events.add_creation_event('variant', variant_id)
    game.add_xps(game_vars._creation_xp_)
    return variant_id


def archive_variant(variant_id):
    """
    Archives a variant by its ID.

    Args:
        variant_id (int): The unique identifier of the variant to be archived.

    Returns:
        int or None: Returns 1 if the variant was successfully archived, otherwise returns None.

    Behavior:
        1. Checks if the current user has administrative privileges.
        2. Retrieves the variant data using the provided `variant_id`.
        3. If the variant exists, determines its directory path and creates an archive of the directory.
        4. Deletes the directory after successfully creating the archive.
        5. Logs the deletion or warns if the directory is not found.
        6. Removes the variant from the project.
        7. Logs an archive event with details about the archived variant.
    """
    if not repository.is_admin():
        return
    variant_row = project.get_variant_data(variant_id)
    if not variant_row:
        return
    dir_name = get_variant_path(variant_id)
    if path_utils.isdir(dir_name):
        archive_file = tools.make_archive(dir_name)
        if archive_file:
            path_utils.rmtree(dir_name)
            logger.info(f"{dir_name} deleted")
    else:
        logger.warning(f"{dir_name} not found")
        archive_file = ''
    if not project.remove_variant(variant_id):
        return
    events.add_archive_event(f"Archived {instance_to_string(('stage', variant_row['stage_id']))}/{variant_row['name']}",
                             archive_file)
    return 1


def modify_stage_state(stage_id, state, comment=''):
    """
    Modifies the state of a stage and optionally adds a comment.

    Args:
        stage_id (int): The unique identifier of the stage to be modified.
        state (str): The new state to set for the stage.
        comment (str, optional): A comment describing the state change. Defaults to an empty string.

    Returns:
        int: 1 if the state was successfully modified, otherwise None.

    Behavior:
        - Validates the provided state against a predefined list of allowed states.
        - Updates the stage's state and tracking comment in the project database.
        - Updates the stage's progress and logs a state switch event.
        - Awards coins to the assigned user if the state is set to "done".
        - Logs a progress event in the statistics.
    """
    if state not in assets_vars._asset_states_list_:
        logger.warning(f"Unknown state {state}")
        return
    project.set_stage_data(stage_id, 'state', state)
    if comment is not None and comment != '':
        project.set_stage_data(stage_id, 'tracking_comment', comment)
    project.update_stage_progress(stage_id)
    asset_tracking.add_state_switch_event(stage_id, state, comment)
    if state == assets_vars._asset_state_done_:
        stage_row = project.get_stage_data(stage_id)
        amount = int((stage_row['work_time']/400)*game_vars._task_done_coins_)
        repository.add_user_coins(stage_row['assignment'], amount)
    stats.add_progress_event()
    return 1


def modify_stage_priority(stage_id, priority):
    """
    Modifies the priority of a stage.

    Args:
        stage_id (int): The unique identifier of the stage to be modified.
        priority (str): The new priority to set for the stage.

    Returns:
        int: 1 if the priority was successfully modified, otherwise None.

    Behavior:
        - Validates the provided priority against a predefined list of allowed priorities.
        - Updates the stage's priority in the project database.
        - Logs a priority switch event in the asset tracking system.
    """
    if priority not in assets_vars._priority_list_:
        logger.warning(f"Unknown priority {priority}")
        return
    project.set_stage_data(stage_id, 'priority', priority)
    asset_tracking.add_priority_switch_event(stage_id, priority)
    return 1


def add_stage_comment(stage_id, comment):
    """
    Adds a comment to a stage's tracking data.

    Args:
        stage_id (int): The unique identifier of the stage.
        comment (str): The comment to be added.

    Returns:
        int: 1 if the comment was successfully added.

    Behavior:
        - Updates the stage's tracking comment in the project database.
        - Logs the comment addition as an asset tracking event.
    """
    project.set_stage_data(stage_id, 'tracking_comment', comment)
    asset_tracking.add_comment_event(stage_id, comment)
    return 1


def edit_stage_note(stage_id, note):
    """
    Edits the note associated with a stage.

    Args:
        stage_id (int): The unique identifier of the stage.
        note (str): The new note to be set.

    Returns:
        int: 1 if the note was successfully updated.

    Behavior:
        - Updates the stage's note in the project database.
    """
    project.set_stage_data(stage_id, 'note', note)
    return 1


def modify_stage_assignment(stage_id, user_name):
    """
    Modifies the assignment of a stage to a specific user.

    Args:
        stage_id (int): The unique identifier of the stage.
        user_name (str): The name of the user to assign the stage to.

    Returns:
        int: 1 if the assignment was successfully modified, otherwise None.

    Behavior:
        - Retrieves the user ID associated with the provided user name from the repository database.
        - Validates if the user has logged into the project.
        - Updates the stage's assignment in the project database.
        - Logs the assignment change as an asset tracking event.
    """
    user_id = repository.get_user_row_by_name(user_name, 'id')
    if user_id not in project.get_users_ids_list():
        logger.warning(f"{user_name} never logged into project")
        return
    project.set_stage_data(stage_id, 'assignment', user_name)
    asset_tracking.add_assignment_event(stage_id, user_name)
    return 1


def modify_stage_estimation(stage_id, days):
    """
    Modifies the estimated time for a stage.

    Args:
        stage_id (int): The unique identifier of the stage to be modified.
        days (int): The new estimated time in days.

    Returns:
        int: 1 if the estimation was successfully modified, otherwise None.

    Behavior:
        - Validates that the provided `days` argument is an integer.
        - Updates the stage's estimated time in the project database.
        - Logs the estimation change as an asset tracking event.
    """
    if type(days) != int:
        logger.warning(f'{days} is not a int')
        return
    project.set_stage_data(stage_id, 'estimated_time', days)
    asset_tracking.add_estimation_event(stage_id, days)
    return 1


def modify_stage_start_date(stage_id, start_date_in_seconds):
    """
    Modifies the start date of a stage.

    Args:
        stage_id (int): The unique identifier of the stage to be modified.
        start_date_in_seconds (float or int): The new start date in seconds since the epoch.

    Returns:
        int: 1 if the start date was successfully modified, otherwise None.

    Behavior:
        - Validates that the provided `start_date_in_seconds` argument is a number.
        - Updates the stage's start date in the project database.
        - Logs the start date change as an asset tracking event.
    """
    if type(start_date_in_seconds) not in [float, int]:
        logger.warning(f'{start_date_in_seconds} is not a number')
        return
    project.set_stage_data(stage_id, 'start_date', start_date_in_seconds)
    asset_tracking.add_start_date_event(stage_id, start_date_in_seconds)
    return 1


def add_work_time(work_env_id, work_time):
    """
    Adds work time to a specific work environment and updates related project and user data.

    Args:
        work_env_id (int): The ID of the work environment to which the work time is being added.
        work_time (float): The amount of work time to add, in seconds.

    Returns:
        int: Always returns 1 to indicate successful execution.

    Functionality:
        - Adds the specified work time to the given work environment.
        - Retrieves the associated variant ID and stage ID for the work environment.
        - Updates the stage's work time and logs the work session event.
        - Calculates and awards work coins to the user based on the work time.
    """
    project.add_work_time(work_env_id, work_time)
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    project.add_stage_work_time(stage_id, work_time)
    asset_tracking.add_work_session_event(stage_id, work_time)
    amount = int((work_time/200)*game_vars._work_coins_)
    repository.add_user_coins(environment.get_user(), amount)
    return 1


def get_software_id_by_name(software):
    """
    Retrieve the unique identifier (ID) of a software by its name.

    Args:
        software (str): The name of the software whose ID is to be retrieved.

    Returns:
        int: The unique identifier (ID) of the specified software.

    Note:
        This function relies on the `project.get_software_data_by_name` method
        to fetch the software data.
    """
    return project.get_software_data_by_name(software, 'id')


def create_work_env(software_id, variant_id):
    """
    Creates a work environment for a given software and variant.

    This function sets up a work environment by validating the software and 
    variant, creating necessary directories, and registering the environment 
    in the project database. It also triggers hooks and initializes a version 
    for the created work environment.

    Args:
        software_id (int): The ID of the software for which the work environment 
            is being created.
        variant_id (int): The ID of the variant associated with the work environment.

    Returns:
        int or None: The ID of the created work environment if successful, 
        otherwise None.

    Behavior:
        - Validates the software name and ensures it is handled by the project.
        - Retrieves the variant path and stage data.
        - Determines the export extension based on the stage and software.
        - Creates directories for the work environment and its screenshots.
        - Adds the work environment to the project database.
        - Executes a post-creation hook and initializes a version.
        - Cleans up and removes the work environment if directory creation fails.

    Raises:
        None: This function does not raise exceptions but logs errors and warnings 
        for invalid inputs or failures during execution.
    """
    name = project.get_software_data(software_id, 'name')
    if not name:
        return
    if name not in project.get_softwares_names_list():
        logger.warning(
            f"{name} is not a valid work environment ( software not handled )")
        return
    variant_path = get_variant_path(variant_id)
    if not variant_path:
        logger.error("Can't create work env")
        return
    stage_row = project.get_stage_data(
        project.get_variant_data(variant_id, 'stage_id'))
    if stage_row['name'] == assets_vars._custom_stage_:
        export_extension = assets_vars._ext_dic_[
            assets_vars._custom_stage_][name][0]
    else:
        export_extension = None
    dir_name = path_utils.clean_path(path_utils.join(variant_path, name))
    screenshots_dir_name = path_utils.clean_path(
        path_utils.join(dir_name, 'screenshots'))
    work_env_id = project.add_work_env(name,
                                       software_id,
                                       variant_id,
                                       export_extension)
    if not work_env_id:
        return
    if (not tools.create_folder(dir_name)) or (not tools.create_folder(screenshots_dir_name)):
        project.remove_work_env(work_env_id)
        return
    work_env_row = project.get_work_env_data(work_env_id)
    hooks.after_work_environment_creation_hook(work_env_row['string'], name)
    add_version(work_env_id, do_screenshot=0, fresh=1)
    return work_env_id


def force_unlock(work_env_id):
    """
    Forcefully unlocks a work environment by setting its lock status.

    Args:
        work_env_id (int): The identifier of the work environment to unlock.

    Returns:
        int: Always returns 1 to indicate the operation was performed.
    """
    project.set_work_env_lock(work_env_id, 0, 1)
    return 1


def create_references_from_stage_id(work_env_id, stage_id):
    """
    Creates references for a given stage ID within a specified work environment.

    This function retrieves export rows associated with the given stage ID and 
    processes them to create references. If the stage corresponds to modeling 
    or layout, only the first export row is considered. References are created 
    using the default export version ID for each export row.

    Args:
        work_env_id (int): The ID of the work environment where references will be created.
        stage_id (int): The ID of the stage for which references are to be created.

    Returns:
        int or None: Returns 1 if at least one reference is successfully created, 
        otherwise returns None if no exports are found or no references are created.

    Logs:
        Logs a warning if no export rows are found or no references are created.
    """
    export_rows = project.get_stage_export_childs(stage_id)
    stage = project.get_stage_data(stage_id, 'name')
    if not export_rows:
        return
    if stage in [assets_vars._modeling_, assets_vars._layout_]:
        export_rows = [export_rows[0]]
    at_least_one = False
    for export_row in export_rows:
        export_version_id = project.get_default_export_version(
            export_row['id'], 'id')
        if export_version_id:
            at_least_one = 1
            create_reference(work_env_id, export_version_id)
    if not at_least_one:
        logger.warning('No export found')
        return
    return 1


def create_reference(work_env_id,
                     export_version_id,
                     namespace_and_count=None,
                     auto_update=None,
                     activated=1):
    """
    Creates a reference in the project with the specified parameters.

    Args:
        work_env_id (int): The ID of the work environment where the reference will be created.
        export_version_id (int): The ID of the export version to be referenced.
        namespace_and_count (tuple, optional): A tuple containing the namespace (str) and count (int).
            If not provided, a numbered namespace will be generated automatically.
        auto_update (bool, optional): Whether the reference should auto-update. If None, the default
            auto-update setting for the user will be used.
        activated (int, optional): Indicates whether the reference is activated. Defaults to 1 (activated).

    Returns:
        int: The ID of the created reference.

    Hooks:
        Executes the `after_reference_hook` with the work environment string, export version string,
        stage name, and reference stage after the reference is created.

    Notes:
        - The function interacts with the `project` module to create and retrieve data related to
            references, work environments, variants, stages, and export versions.
        - The `numbered_namespace` function is used to generate a namespace and count if not provided.
    """
    if auto_update is None:
        auto_update = user.user().get_reference_auto_update_default()
    if not namespace_and_count:
        namespace, count = numbered_namespace(work_env_id, export_version_id)
    else:
        namespace = namespace_and_count[0]
        count = namespace_and_count[1]
    reference_id = project.create_reference(work_env_id,
                                            export_version_id,
                                            namespace,
                                            count,
                                            int(auto_update),
                                            activated)
    work_env_row = project.get_work_env_data(work_env_id)
    variant_row = project.get_variant_data(work_env_row['variant_id'])
    stage_name = project.get_stage_data(variant_row['stage_id'], 'name')
    reference_row = project.get_reference_data(reference_id)
    export_version_row = project.get_export_version_data(
        reference_row['export_version_id'])
    hooks.after_reference_hook(work_env_row['string'],
                               export_version_row['string'],
                               stage_name,
                               reference_row['stage'])
    return reference_id


def quick_reference(work_env_id, stage):
    """
    Generates references for a specific stage within a work environment.

    This function retrieves and validates data related to a work environment, 
    variant, stage, and asset. It ensures that the specified stage exists 
    and has export versions available. If the conditions are met, it creates 
    references for the given stage.

    Args:
        work_env_id (int): The ID of the work environment.
        stage (str): The name of the stage to reference.

    Returns:
        None: If the variant, stage, or asset data is invalid, or if no export 
        versions are found for the specified stage.
        Any: The result of `create_references_from_stage_id` if the references 
        are successfully created.

    Logs:
        - A warning if no export versions are found for the specified stage.
        - A warning if the specified stage is not found for the asset.
    """
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if not variant_id:
        return
    variant_row = project.get_variant_data(variant_id)
    if not variant_row:
        return
    stage_row = project.get_stage_data(variant_row['stage_id'])
    if not stage_row:
        return
    asset_row = project.get_asset_data(stage_row['asset_id'])
    if not asset_row:
        return
    stages_rows = project.get_asset_childs(asset_row['id'])
    for stage_row in stages_rows:
        if stage_row['name'] != stage:
            continue
        if len(project.get_export_versions_by_stage(stage_row['id'], 'id')) == 0:
            logger.warning(f"No export found for {asset_row['name']}/{stage}")
            return
        return create_references_from_stage_id(work_env_id, stage_row['id'])
    logger.warning(f"Stage {stage} not found for {asset_row['name']}")


def numbered_namespace(work_env_id, export_version_id, namespace_to_update=None):
    """
    Generates a unique namespace by appending a numerical suffix if necessary.

    This function creates a namespace based on the provided `export_version_id` 
    and ensures it is unique within the list of existing namespaces for the 
    given `work_env_id`. If a `namespace_to_update` is provided, it is excluded 
    from the list of existing namespaces during the uniqueness check.

    Args:
        work_env_id (str): The identifier for the working environment.
        export_version_id (str): The identifier for the export version used to 
            build the base namespace.
        namespace_to_update (str, optional): A namespace to exclude from the 
            uniqueness check. Defaults to None.

    Returns:
        tuple: A tuple containing:
            - namespace (str): The unique namespace generated.
            - count (int): The numerical suffix appended to ensure uniqueness 
              (0 if no suffix was needed).
    """
    namespaces_list = project.get_references(work_env_id, 'namespace')
    if (namespace_to_update is not None) and namespace_to_update in namespaces_list:
        namespaces_list.remove(namespace_to_update)
    count = 0
    namespace_raw = build_namespace(export_version_id)
    namespace = f"{namespace_raw}"
    while namespace in namespaces_list:
        count += 1
        namespace = f"{namespace_raw}_{str(count)}"
    return namespace, count


def remove_reference(reference_id):
    """
    Removes a reference from the project by its identifier.

    Args:
        reference_id (str): The unique identifier of the reference to be removed.

    Returns:
        bool: True if the reference was successfully removed, False otherwise.
    """
    return project.remove_reference(reference_id)


def set_reference_last_version(reference_id):
    """
    Updates the reference to the latest default export version if it is outdated.

    This function checks the current export version associated with the given
    reference ID. If the export version is not the latest default version, it
    updates the reference to point to the latest default export version.

    Args:
        reference_id (int): The ID of the reference to be checked and updated.

    Returns:
        int or None: Returns 1 if the reference was updated successfully, 
        None if no update was necessary or if the reference/export data is invalid.

    Logs:
        Logs an informational message if the reference is already up to date.
    """
    export_version_id = project.get_reference_data(
        reference_id, 'export_version_id')
    if export_version_id is None:
        return
    export_version_row = project.get_export_version_data(export_version_id)
    export_row = project.get_export_data(export_version_row['export_id'])
    default_export_version_id = project.get_default_export_version(
        export_row['id'], 'id')
    if not default_export_version_id:
        return
    if default_export_version_id == export_version_id:
        logger.info("Reference is up to date")
        return
    project.update_reference(reference_id, default_export_version_id)
    return 1


def modify_reference_LOD(work_env_id, LOD, namespaces_list):
    """
    Modifies the Level of Detail (LOD) for specific references in a given work environment.

    This function iterates through the references associated with the provided work environment ID,
    filters them based on the given namespaces, and updates their LOD by modifying the reference export.

    Args:
        work_env_id (int): The ID of the work environment containing the references.
        LOD (str): The Level of Detail to be applied to the references.
        namespaces_list (list of str): A list of namespaces to filter the references.

    Returns:
        int: Always returns 1 upon successful execution.
    """
    references_rows = project.get_references(work_env_id)
    for reference_row in references_rows:
        if reference_row['namespace'] not in namespaces_list:
            continue
        export_row = project.get_export_data(reference_row['export_id'])
        export_rows = project.get_stage_export_childs(export_row['stage_id'])
        for export_row in export_rows:
            if LOD not in export_row['name']:
                continue
            project.modify_reference_export(
                reference_row['id'], export_row['id'])
    return 1


def get_references_files(work_env_id):
    """
    Retrieve a dictionary of reference files and their associated metadata for a given work environment.

    This function gathers references and grouped references associated with a specific work environment ID.
    It filters out deactivated references and processes their metadata, including file paths, namespaces,
    counts, category names, asset names, stage names, and stage strings. The references are organized by stage.

    Args:
        work_env_id (int): The ID of the work environment for which references are to be retrieved.

    Returns:
        dict: A dictionary where keys are stage identifiers and values are lists of dictionaries containing
              metadata about the references. Each reference dictionary includes:
              - 'files': List of file paths associated with the reference.
              - 'namespace': Namespace of the reference.
              - 'count': Count of the reference.
              - 'category_name': Name of the category the asset belongs to.
              - 'asset_name': Name of the asset.
              - 'stage_name': Name of the stage.
              - 'string_stage': String representation of the stage.

    Notes:
        - References and grouped references are filtered based on their activation status.
        - If no files are found for a reference, the function attempts to retrieve them using `get_export_files_list`.
        - Grouped references include additional namespace and count information derived from their parent group.
    """
    # Retrieve all references associated with the given work environment
    references_rows = project.get_references(work_env_id)
    references_dic = dict()

    # Process each reference row
    for reference_row in references_rows:
        if not reference_row['activated']:
            continue  # Skip deactivated references

        # Retrieve the list of files associated with the reference
        reference_files_list = json.loads(project.get_export_version_data(reference_row['export_version_id'],
                                                                          'files'))
        if reference_files_list == []:
            # If no files are found, fetch them from the export version
            reference_files_list = get_export_files_list(
                reference_row['export_version_id'])

        # Retrieve stage and asset details for the reference
        stage_id = project.get_export_data(
            reference_row['export_id'], 'stage_id')
        stage_row = project.get_stage_data(stage_id)
        stage_name = stage_row['name']
        string_stage = stage_row['string']
        asset_id = stage_row['asset_id']
        asset_row = project.get_asset_data(asset_id)
        asset_name = asset_row['name']
        category_name = project.get_category_data(
            asset_row['category_id'], 'name')

        # Build a dictionary for the reference metadata
        reference_dic = dict()
        reference_dic['files'] = reference_files_list
        reference_dic['namespace'] = reference_row['namespace']
        reference_dic['count'] = reference_row['count']
        reference_dic['category_name'] = category_name
        reference_dic['asset_name'] = asset_name
        reference_dic['stage_name'] = stage_name
        reference_dic['string_stage'] = string_stage

        # Group references by stage
        if reference_row['stage'] not in references_dic.keys():
            references_dic[reference_row['stage']] = []
        references_dic[reference_row['stage']].append(reference_dic)

    # Retrieve all referenced groups associated with the work environment
    referenced_groups_rows = project.get_referenced_groups(work_env_id)

    # Process each referenced group
    for referenced_group_row in referenced_groups_rows:
        if not referenced_group_row['activated']:
            continue  # Skip deactivated referenced groups

        # Retrieve grouped references within the referenced group
        grouped_references_rows = project.get_grouped_references(
            referenced_group_row['group_id'])

        # Process each grouped reference
        for grouped_reference_row in grouped_references_rows:
            if not grouped_reference_row['activated']:
                continue  # Skip deactivated grouped references

            # Retrieve the list of files associated with the grouped reference
            reference_files_list = json.loads(project.get_export_version_data(grouped_reference_row['export_version_id'],
                                                                              'files'))
            if reference_files_list == []:
                # If no files are found, fetch them from the export version
                reference_files_list = get_export_files_list(
                    grouped_reference_row['export_version_id'])

            # Retrieve stage and asset details for the grouped reference
            stage_id = project.get_export_data(
                grouped_reference_row['export_id'], 'stage_id')
            stage_row = project.get_stage_data(stage_id)
            stage_name = stage_row['name']
            string_stage = stage_row['string']
            asset_id = stage_row['asset_id']
            asset_row = project.get_asset_data(asset_id)
            asset_name = asset_row['name']
            category_name = project.get_category_data(
                asset_row['category_id'], 'name')

            # Build a dictionary for the grouped reference metadata
            reference_dic = dict()
            reference_dic['files'] = reference_files_list
            reference_dic['namespace'] = f"{referenced_group_row['namespace']}_{grouped_reference_row['namespace']}"
            reference_dic['count'] = f"{referenced_group_row['count']}_{grouped_reference_row['count']}"
            reference_dic['category_name'] = category_name
            reference_dic['asset_name'] = asset_name
            reference_dic['stage_name'] = stage_name
            reference_dic['string_stage'] = string_stage

            # Group grouped references by stage
            if grouped_reference_row['stage'] not in references_dic.keys():
                references_dic[grouped_reference_row['stage']] = []
            references_dic[grouped_reference_row['stage']].append(
                reference_dic)

    # Return the dictionary containing all references grouped by stage
    return references_dic


def get_export_files_list(export_version_id):
    """
    Retrieves a list of file paths for all files in the directory corresponding 
    to the given export version ID.

    Args:
        export_version_id (str): The identifier for the export version.

    Returns:
        list: A list of full file paths for all files in the export version directory.
    """
    export_version_path = get_export_version_path(export_version_id)
    files_list = []
    for file in path_utils.listdir(export_version_path):
        files_list.append(path_utils.join(export_version_path, file))
    return files_list


def merge_file_as_export_version(export_name, files, stage_id, comment='', analyse_comment=True):
    """
    Merges files into a new export version for a given stage.

    Args:
        export_name (str): The name of the export.
        files (list): A list of file paths to be included in the export version.
        stage_id (int): The ID of the stage where the export version will be created.
        comment (str, optional): A comment describing the export version. Defaults to an empty string.
        analyse_comment (bool, optional): Whether to analyze the comment for tags or penalties. Defaults to True.

    Returns:
        int or None: The ID of the created export version if successful, otherwise None.

    Behavior:
        - Calls the `add_export_version` function to create a new export version.
        - Skips temporary directory purging by setting `skip_temp_purge` to True.
    """
    return add_export_version(export_name, files, stage_id, version_id=None, comment=comment, analyse_comment=analyse_comment, skip_temp_purge=True)


def add_export_version_from_version_id(export_name, files, version_id, comment='', analyse_comment=True):
    """
    Creates a new export version based on an existing work version.

    Args:
        export_name (str): The name of the export.
        files (list): A list of file paths to be included in the export version.
        version_id (int): The ID of the work version to base the export on.
        comment (str, optional): A comment describing the export version. Defaults to an empty string.
        analyse_comment (bool, optional): Whether to analyze the comment for tags or penalties. Defaults to True.

    Returns:
        int or None: The ID of the created export version if successful, otherwise None.

    Behavior:
        - Retrieves the work environment and stage associated with the given work version.
        - Calls the `add_export_version` function to create a new export version.
    """
    work_env_row = project.get_work_env_data(
        project.get_version_data(version_id, 'work_env_id'))
    if not work_env_row:
        return
    variant_id = work_env_row['variant_id']
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    return add_export_version(export_name,
                              files,
                              stage_id,
                              version_id,
                              comment,
                              analyse_comment)


def add_export_version(raw_export_name, files, stage_id, version_id, comment='', analyse_comment=True, skip_temp_purge=False):
    """
    Adds a new export version for a given stage.

    This function creates a new export version by validating file extensions, 
    generating a unique version name, copying files to the appropriate directory, 
    and updating the project database. It also triggers hooks and logs events 
    related to the export.

    Args:
        raw_export_name (str): The base name of the export.
        files (list): A list of file paths to be included in the export version.
        stage_id (int): The ID of the stage where the export version will be created.
        version_id (int or None): The ID of the work version to base the export on, if applicable.
        comment (str, optional): A comment describing the export version. Defaults to an empty string.
        analyse_comment (bool, optional): Whether to analyze the comment for tags or penalties. Defaults to True.
        skip_temp_purge (bool, optional): Whether to skip purging temporary directories. Defaults to False.

    Returns:
        int or None: The ID of the created export version if successful, otherwise None.

    Behavior:
        - Validates file extensions against the stage's export rules.
        - Generates a unique version name for the export.
        - Copies files to the export directory, using multithreading for large file sets.
        - Updates the project database with the new export version.
        - Awards experience points and coins for the export.
        - Analyzes the comment for tags or penalties, if enabled.
        - Triggers hooks and logs events related to the export.

    Logs:
        - Warnings for invalid file extensions or missing files.
        - Informational messages for large file sets or successful operations.
    """
    # Determine the export name based on the version ID and raw export name
    if version_id:
        version_row = project.get_version_data(version_id)
        work_env_row = project.get_work_env_data(version_row['work_env_id'])
        variant_row = project.get_variant_data(work_env_row['variant_id'])
        export_name = f"{variant_row['name']}_{raw_export_name}"
    else:
        export_name = raw_export_name

    # Retrieve stage data and validate file extensions
    stage_row = project.get_stage_data(stage_id)
    stage_name = stage_row['name']
    extension_errors = []

    # Collect allowed extensions for the stage
    extensions_rules = []
    for software in assets_vars._ext_dic_[stage_name].keys():
        extensions_rules += assets_vars._ext_dic_[stage_name][software]
    extensions_rules = list(dict.fromkeys(extensions_rules))

    # Check if files match the allowed extensions
    for file in files:
        if os.path.splitext(file)[-1].replace('.', '') not in extensions_rules:
            extension_errors.append(file)
    if extension_errors:
        for file in extension_errors:
            logger.warning(
                f"{file} format doesn't match the stage export rules ( {(', ').join(extensions_rules)} )")
        return
    if not stage_row:
        return

    # Get or create the export and determine the new version name
    export_id = get_or_add_export(export_name, stage_row['id'])
    if not export_id:
        return
    last_version_name = project.get_last_export_version(export_id, 'name')
    if last_version_name:
        new_version = str(int(last_version_name) + 1).zfill(4)
    else:
        new_version = '0001'

    # Create the directory for the new export version
    export_path = get_export_path(export_id)
    if not export_path:
        return
    dir_name = path_utils.clean_path(path_utils.join(export_path, new_version))
    while path_utils.isdir(dir_name):
        new_version = str(int(new_version) + 1).zfill(4)
        dir_name = path_utils.clean_path(
            path_utils.join(export_path, new_version))
    if not tools.create_folder(dir_name):
        return

    # Copy files to the export directory
    if (tools.get_files_list_size(files) > 5000000000) and (len(files) > 3):
        logger.info(
            f"Files list size over 5Gb, starting files copying as subtask.")
        subtasks_library.threaded_copy(files, dir_name, max_threads=16)
        copied_files = []
    else:
        copied_files = tools.copy_files(files, dir_name)
        if copied_files is None:
            if not tools.remove_folder(dir_name):
                logger.warning(
                    f"{dir_name} can't be removed, keeping export version {new_version} in database")
            return
        if (len(copied_files) == len(files) and len(files) > 0) and not skip_temp_purge:
            tools.remove_tree(os.path.dirname(files[0]))
        elif len(copied_files) != len(files):
            logger.warning(
                f"Missing files, keeping temp dir: {os.path.dirname(files[0])}")
        else:
            pass

    # Add the export version to the project database
    export_version_id = project.add_export_version(new_version,
                                                   copied_files,
                                                   export_id,
                                                   version_id,
                                                   comment)
    # Award experience points and coins for the export
    game.add_xps(game_vars._export_xp_)
    game.add_coins(game_vars._export_coins_)
    if analyse_comment:
        game.analyse_comment(comment, game_vars._export_penalty_)

    # Log events and analyze the comment
    events.add_export_event(export_version_id)
    tags.analyse_comment(comment, 'export_version', export_version_id)

    # Trigger hooks for the export
    export_version_string = instance_to_string(
        ('export_version', export_version_id))
    hooks.after_export_hook(export_version_string=export_version_string,
                            export_dir=dir_name,
                            stage_name=stage_name)
    return export_version_id


def modify_export_version_comment(export_version_id, comment):
    """
    Modifies the comment associated with a specific export version.

    Args:
        export_version_id (int): The unique identifier of the export version.
        comment (str): The new comment to be set for the export version.

    Returns:
        int: 1 if the comment was successfully modified, otherwise None.

    Behavior:
        - Updates the export version's comment in the project database.
        - Analyzes the comment for tags and logs the analysis.
    """
    if not project.modify_export_version_comment(export_version_id, comment):
        return
    tags.analyse_comment(comment, 'export_version', export_version_id)
    return 1


def modify_video_comment(video_id, comment):
    """
    Modifies the comment associated with a specific video.

    Args:
        video_id (int): The unique identifier of the video.
        comment (str): The new comment to be set for the video.

    Returns:
        int: 1 if the comment was successfully modified, otherwise None.

    Behavior:
        - Updates the video's comment in the project database.
        - Analyzes the comment for tags and logs the analysis.
    """
    if not project.modify_video_comment(video_id, comment):
        return
    tags.analyse_comment(comment, 'video', video_id)
    return 1


def request_export(work_env_id, raw_export_name, multiple=None, only_dir=None):
    """
    Handles the export request by creating a temporary directory and generating an export file path.

    Args:
        work_env_id (int): The ID of the work environment.
        raw_export_name (str): The base name for the export file.
        multiple (bool, optional): Indicates if multiple files are being exported. Defaults to None.
        only_dir (bool, optional): If True, only the directory path is returned. Defaults to None.

    Returns:
        str: The full path to the export file if `only_dir` is False.
        str: The path to the temporary directory if `only_dir` is True.
        None: If the export process cannot proceed due to missing or invalid data.

    Notes:
        - The function retrieves the variant and stage data associated with the given work environment ID.
        - A temporary directory is created for the export process, and its path is logged.
        - If `only_dir` is True, the function returns the temporary directory path.
        - If `only_dir` is False, the function returns the full path to the export file.
        - If the export process encounters an issue (e.g., missing variant or export ID), the function returns None.
    """
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if not variant_id:
        return
    variant_row = project.get_variant_data(variant_id)
    stage_id = project.get_stage_data(variant_row['stage_id'], 'id')
    export_name = f"{variant_row['name']}_{raw_export_name}"
    export_id = get_or_add_export(export_name, stage_id)
    if not export_id:
        return
    export_path = get_temp_export_path(export_id)
    path_utils.makedirs(export_path)
    dir_name = tools.temp_dir_in_dir(export_path)
    logger.info(
        f"Temporary directory created : {dir_name}, if something goes wrong in the export please go there to find your temporary export file")
    file_name = build_export_file_name(work_env_id, export_name, multiple)
    if file_name and not only_dir:
        return path_utils.clean_path(path_utils.join(dir_name, file_name))
    elif file_name and only_dir:
        return dir_name


def request_render(version_id, work_env_id, export_name, comment=''):
    """
    Requests the rendering of an export version based on the provided parameters.

    This function retrieves the necessary data for a rendering request, creates an 
    export version, and returns the path to the created export version.

    Args:
        version_id (int): The ID of the version to be rendered.
        work_env_id (int): The ID of the work environment associated with the request.
        export_name (str): The name of the export to be created.
        comment (str, optional): An optional comment to associate with the export version. 
            Defaults to an empty string.

    Returns:
        str: The file path of the created export version, if successful.
        None: If any required data is missing or the export version creation fails.
    """
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if not variant_id:
        return
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    if not stage_id:
        return
    export_version_id = add_export_version(
        export_name, [], stage_id, version_id, comment, analyse_comment=False)
    if not export_version_id:
        return
    export_version_path = get_export_version_path(export_version_id)
    return export_version_path


def archive_export(export_id):
    """
    Archives an export by creating a compressed archive of the export directory,
    removing the original directory, and logging the operation. Additionally,
    it removes the export record from the project and logs an archive event.

    Args:
        export_id (int): The unique identifier of the export to be archived.

    Returns:
        int: Returns 1 if the operation is successful, otherwise None.

    Behavior:
        - Checks if the user has administrative privileges.
        - Retrieves export data using the provided export_id.
        - If the export directory exists, creates an archive of the directory,
          deletes the original directory, and logs the deletion.
        - If the export directory does not exist, logs a warning.
        - Removes the export record from the project.
        - Logs an archive event with details of the archived export.
    """
    if not repository.is_admin():
        return
    export_row = project.get_export_data(export_id)
    if not export_row:
        return
    dir_name = get_export_path(export_id)
    if path_utils.isdir(dir_name):
        archive_file = tools.make_archive(dir_name)
        if archive_file:
            path_utils.rmtree(dir_name)
            logger.info(f"{dir_name} deleted")
    else:
        logger.warning(f"{dir_name} not found")
        archive_file = ''
    if not project.remove_export(export_id):
        return
    events.add_archive_event(f"Archived {instance_to_string(('stage', export_row['stage_id']))}/{export_row['name']}",
                             archive_file)
    return 1


def get_or_add_export(name, stage_id):
    """
    Retrieves the export ID for a given export name and stage ID, or creates a new export if it does not exist.

    Args:
        name (str): The name of the export. Must pass a safety check.
        stage_id (int): The ID of the stage associated with the export.

    Returns:
        int or None: The ID of the export if successful, or None if the operation fails.

    Behavior:
        - Validates the safety of the export name using `tools.is_safe`.
        - Retrieves the stage path using `get_stage_path`.
        - Constructs the directory path for the export.
        - Checks if the export already exists using `project.is_export`.
        - If the export does not exist:
            - Creates a new export entry using `project.add_export`.
            - Attempts to create the corresponding folder.
            - If folder creation fails, removes the newly created export entry.
        - If the export exists, retrieves its ID using `project.get_export_by_name`.

    Notes:
        - Logs an error if the stage path cannot be determined.
        - Returns `None` if any step in the process fails.
    """
    if not tools.is_safe(name):
        return
    stage_path = get_stage_path(stage_id)
    if not stage_path:
        logger.error("Can't create export")
        return
    dir_name = path_utils.clean_path(path_utils.join(stage_path,
                                                     '_EXPORTS',
                                                     name))
    is_export = project.is_export(name, stage_id)
    if not is_export:
        export_id = project.add_export(name, stage_id)
        if not tools.create_folder(dir_name):
            project.remove_export(export_id)
            return
    else:
        export_id = project.get_export_by_name(name, stage_id)['id']
    return export_id


def archive_export_version(export_version_id):
    """
    Archives an export version by creating an archive of its directory, 
    removing the directory, and logging the operation. If the export 
    version is the last one associated with an export, the export itself 
    is also archived.

    Args:
        export_version_id (int): The ID of the export version to be archived.

    Returns:
        int: Returns 1 if the operation is successful, otherwise None.

    Behavior:
        - Checks if the user has admin privileges.
        - Retrieves the export version data using the provided ID.
        - Creates an archive of the export version's directory if it exists.
        - Deletes the directory after archiving.
        - Logs the archiving operation and raises events.
        - Removes the export version from the project.
        - If no export versions remain for the associated export, archives the export itself.
    """
    if not repository.is_admin():
        return
    export_version_row = project.get_export_version_data(export_version_id)
    export_id = export_version_row['export_id']
    if not export_version_row:
        return
    dir_name = get_export_version_path(export_version_id)
    if path_utils.isdir(dir_name):
        archive_file = tools.make_archive(dir_name)
        if archive_file:
            path_utils.rmtree(dir_name)
            logger.info(f"{dir_name} deleted")
    else:
        logger.warning(f"{dir_name} not found")
        archive_file = ''
    if not project.remove_export_version(export_version_id):
        return
    events.add_archive_event(f"Archived{instance_to_string(('export', export_version_row['export_id']))}/{export_version_row['name']}",
                             archive_file)
    if len(project.get_export_versions(export_id)) == 0:
        archive_export(export_id)
    return 1


def screen_over_version(version_id):
    """
    Updates the screenshot and thumbnail for a specific version.

    This function retrieves version data using the provided version ID, generates
    a new screenshot and thumbnail based on the version's screenshot path, and
    updates the version's screen information in the project.

    Args:
        version_id (int): The unique identifier of the version to update.

    Returns:
        bool: True if the version screen was successfully updated, False otherwise.
              Returns None if the version data could not be retrieved.
    """
    version_row = project.get_version_data(version_id)
    if not version_row:
        return
    screenshot_file, thumbnail_file = image.screenshot(version_row['screenshot_path'],
                                                       version_row['thumbnail_path'])
    return project.modify_version_screen(version_id, screenshot_file, thumbnail_file)


def add_version(work_env_id, comment="", do_screenshot=1, fresh=None, analyse_comment=None):
    """
    Creates a new version of a work environment, optionally capturing a screenshot, 
    analyzing comments, and updating asset previews.

    Args:
        work_env_id (str): The ID of the work environment for which the version is being created.
        comment (str, optional): A comment describing the version. Defaults to an empty string.
        do_screenshot (int, optional): Flag to determine whether to capture a screenshot. 
                                        Defaults to 1 (enabled).
        fresh (bool, optional): If True, creates a fresh version starting at '0001'. 
                                If False or None, increments the last version. Defaults to None.
        analyse_comment (bool, optional): If True, analyzes the comment for penalties. 
                                          Defaults to None.

    Returns:
        str: The ID of the newly created version, or None if the version creation failed.

    Side Effects:
        - Captures and saves screenshots and thumbnails if `do_screenshot` is enabled.
        - Updates the asset preview with the new thumbnail.
        - Adds the new version to the project database.
        - Executes hooks after version creation.
        - Updates user activity and recent scenes.
        - Analyzes the comment for tags and penalties if applicable.

    Raises:
        None: This function does not explicitly raise exceptions but may propagate 
              exceptions from called functions.
    """
    # Determine the new version number
    if fresh:
        new_version = '0001'  # Start fresh with version '0001'
    else:
        # Retrieve the last version and increment it
        last_version_list = project.get_last_work_version(work_env_id, 'name')
        if len(last_version_list) == 1:
            last_version = last_version_list[0]
            new_version = str(int(last_version)+1).zfill(4)
        else:
            new_version = '0001'  # Default to '0001' if no previous version exists

    # Construct paths for the new version
    dirname = get_work_env_path(work_env_id)
    screenshot_dir_name = path_utils.join(dirname, 'screenshots')
    file_name = path_utils.clean_path(path_utils.join(dirname,
                                                      build_version_file_name(work_env_id, new_version)))
    file_name_ext = os.path.splitext(file_name)[-1]
    basename = os.path.basename(file_name)
    screenshot_file = path_utils.join(screenshot_dir_name,
                                      basename.replace(file_name_ext, '.jpg'))
    thumbnail_file = path_utils.join(screenshot_dir_name,
                                     basename.replace(file_name_ext, '.thumbnail.jpg'))

    # Capture screenshot and update asset preview if enabled
    if do_screenshot:
        screenshot_file, thumbnail_file = image.screenshot(
            screenshot_file, thumbnail_file)
        variant_id = project.get_work_env_data(work_env_id, 'variant_id')
        stage_id = project.get_variant_data(variant_id, 'stage_id')
        asset_id = project.get_stage_data(stage_id, 'asset_id')
        project.modify_asset_preview(asset_id, thumbnail_file)

    # Add the new version to the project database
    version_id = project.add_version(new_version,
                                     file_name,
                                     work_env_id,
                                     comment,
                                     screenshot_file,
                                     thumbnail_file)
    if not version_id:
        return

    # Trigger hooks and log the creation of the new version
    version_row = project.get_version_data(version_id)
    hooks.after_work_version_creation_hook(
        version_row['string'], new_version, file_name)

    # Award experience points for saving
    game.add_xps(game_vars._save_xp_)

    # Analyze the comment for penalties if applicable
    if analyse_comment and not fresh:
        game.analyse_comment(comment, game_vars._save_penalty_)

    # Update the user's recent scenes
    user.user().add_recent_scene((work_env_id, time.time()))

    # Analyze the comment for tags
    tags.analyse_comment(comment, 'work_version', version_id)

    # Return the ID of the newly created version
    return version_id


def add_video(variant_id, comment="", analyse_comment=None):
    """
    Adds a new video entry to the project, generates necessary directories and files, 
    and handles associated events, rewards, and tags.

    Args:
        variant_id (str): The identifier for the video variant.
        comment (str, optional): A comment associated with the video. Defaults to an empty string.
        analyse_comment (bool, optional): If True, analyzes the comment for penalties. Defaults to None.

    Returns:
        int or None: The ID of the newly added video if successful, otherwise None.

    Functionality:
        - Determines the new version number for the video based on the last version.
        - Creates necessary directories for storing the video and its thumbnails.
        - Constructs the file name and thumbnail file path for the video.
        - Adds the video to the project database and triggers associated events.
        - Awards experience points for adding the video.
        - Tags and optionally analyzes the comment for penalties.
    """
    # Retrieve the last video version for the given variant and determine the new version number
    last_version_list = project.get_last_video_version(variant_id, 'name')
    if len(last_version_list) == 1:
        last_version = last_version_list[0]
        # Increment the version number
        new_version = str(int(last_version)+1).zfill(4)
    else:
        new_version = '0001'  # Default to '0001' if no previous version exists

    # Get the directory path for storing videos and ensure it exists
    dirname = get_video_path(variant_id)
    if not path_utils.isdir(dirname):
        path_utils.mkdir(dirname)

    # Create a directory for storing video thumbnails if it doesn't exist
    screenshot_dir_name = path_utils.join(dirname, 'thumbnails')
    if not path_utils.isdir(screenshot_dir_name):
        path_utils.mkdir(screenshot_dir_name)

    # Construct the file name and thumbnail file path for the new video
    file_name = path_utils.clean_path(path_utils.join(dirname,
                                                      build_video_file_name(variant_id, new_version)))
    file_name_ext = os.path.splitext(file_name)[-1]
    basename = os.path.basename(file_name)
    thumbnail_file = path_utils.join(screenshot_dir_name,
                                     basename.replace(file_name_ext, '.thumbnail.jpg'))

    # Add the new video entry to the project database
    video_id = project.add_video(new_version,
                                 file_name,
                                 variant_id,
                                 comment,
                                 thumbnail_file)
    if not video_id:
        return  # Exit if the video creation fails

    # Log the video creation event and award experience points
    events.add_video_event(video_id, variant_id)
    game.add_xps(game_vars._video_xp_)

    # Analyze the comment for tags and penalties if applicable
    tags.analyse_comment(comment, 'video', video_id)
    if analyse_comment:
        game.analyse_comment(comment, game_vars._video_penalty_)

    # Return the ID of the newly created video
    return video_id


def save_playlist(playlist_id, data, thumbnail_temp_path=None):
    """
    Save playlist data and optionally update its thumbnail.

    This function updates the playlist data, last save user, and last save time
    in the project. If a temporary thumbnail path is provided, it saves the 
    thumbnail to the project's thumbnails folder and updates the playlist's 
    thumbnail path.

    Args:
        playlist_id (str): The unique identifier of the playlist to update.
        data (dict): The playlist data to save, which will be serialized to JSON.
        thumbnail_temp_path (str, optional): The temporary file path of the 
            thumbnail image. If provided, the thumbnail will be copied to the 
            project's thumbnails folder.

    Returns:
        int: Returns 1 upon successful completion.

    Raises:
        OSError: If there is an error creating the thumbnails directory or 
            copying the thumbnail file.
    """
    project.update_playlist_data(playlist_id, ('data', json.dumps(data)))
    project.update_playlist_data(
        playlist_id, ('last_save_user', environment.get_user()))
    project.update_playlist_data(playlist_id, ('last_save_time', time.time()))
    if thumbnail_temp_path is not None:
        ext = path_utils.splitext(thumbnail_temp_path)[-1]
        thumbnail_path = path_utils.join(
            environment.get_project_path(), project_vars._thumbnails_folder_)
        if not path_utils.isdir(thumbnail_path):
            path_utils.makedirs(thumbnail_path)
        thumbnail_path = path_utils.join(
            thumbnail_path, f"{str(uuid.uuid4())}{ext}")
        path_utils.copyfile(thumbnail_temp_path, thumbnail_path)
        project.update_playlist_data(
            playlist_id, ('thumbnail_path', thumbnail_path))
    return 1


def create_playlist(name, data='{}', thumbnail_temp_path=None):
    """
    Creates a new playlist with the specified name, data, and optional thumbnail.

    Args:
        name (str): The name of the playlist to be created.
        data (str, optional): The playlist data in JSON format. Defaults to an empty JSON string '{}'.
        thumbnail_temp_path (str, optional): The temporary file path of the thumbnail image. 
                                             If provided, the thumbnail will be copied to the project's thumbnails folder.

    Returns:
        int or None: The ID of the newly created playlist if successful, otherwise None.

    Behavior:
        - If a thumbnail is provided, it is copied to the project's thumbnails folder.
        - The playlist is added to the project database with the provided name, data, and thumbnail path.
    """
    thumbnail_path = None
    if thumbnail_temp_path is not None:
        ext = path_utils.splitext(thumbnail_temp_path)[-1]
        thumbnail_path = path_utils.join(
            environment.get_project_path(), project_vars._thumbnails_folder_)
        if not path_utils.isdir(thumbnail_path):
            path_utils.makedirs(thumbnail_path)
        thumbnail_path = path_utils.join(
            thumbnail_path, f"{str(uuid.uuid4())}{ext}")
        path_utils.copyfile(thumbnail_temp_path, thumbnail_path)
    return project.add_playlist(name=name, data=data, thumbnail_path=thumbnail_path)


def copy_work_version(work_version_id):
    """
    Copies the specified work version ID to the clipboard.

    Args:
        work_version_id (int): The ID of the work version to be copied.

    Returns:
        int: Always returns 1 to indicate successful execution.

    Behavior:
        - Creates a dictionary containing the work version ID.
        - Serializes the dictionary to JSON and copies it to the clipboard.
        - Logs a message indicating that the version ID has been copied.
    """
    clipboard_dic = dict()
    clipboard_dic['work_version_id'] = work_version_id
    clipboard.copy(json.dumps(clipboard_dic))
    logger.info("Version ID copied to clipboard")
    return 1


def copy_references(references_dic):
    """
    Copies a dictionary of references to the clipboard.

    Args:
        references_dic (dict): A dictionary containing references to be copied.

    Returns:
        int: Always returns 1 to indicate successful execution.

    Behavior:
        - Serializes the references dictionary to JSON format.
        - Copies the serialized JSON to the clipboard.
        - Logs a message indicating that the references have been copied.
    """
    clipboard_dic = dict()
    clipboard_dic['references_dic'] = references_dic
    clipboard.copy(json.dumps(clipboard_dic))
    logger.info("References copied to clipboard")
    return 1


def paste_work_version(destination_work_env_id, mirror_work_env_references=False):
    """
    Pastes a work version from the clipboard into a specified work environment.

    Args:
        destination_work_env_id (int): The ID of the destination work environment.
        mirror_work_env_references (bool, optional): If True, mirrors references 
                                                     from the source work environment 
                                                     to the destination. Defaults to False.

    Returns:
        int or None: Returns 1 if the operation is successful, otherwise None.

    Behavior:
        - Retrieves the clipboard content and parses it as JSON.
        - Checks if the clipboard contains a valid work version ID.
        - Duplicates the work version into the destination work environment.
        - If `mirror_work_env_references` is True, mirrors references from the source 
          work environment to the destination.
        - Logs warnings if the clipboard content is invalid or the operation fails.
    """
    clipboard_json = clipboard.paste()
    try:
        clipboard_dic = json.loads(clipboard_json)
    except json.decoder.JSONDecodeError:
        logger.warning("No valid work version found in clipboard")
        return
    if 'work_version_id' not in clipboard_dic.keys():
        logger.warning("No valid work version found in clipboard")
        return
    work_version_id = clipboard_dic['work_version_id']
    if not duplicate_version(work_version_id, work_env_id=destination_work_env_id):
        return
    if mirror_work_env_references:
        work_version_row = project.get_version_data(work_version_id)
        work_env_id = work_version_row['work_env_id']
        mirror_references(work_env_id, destination_work_env_id)
    return 1


def paste_references(context, destination_instance_id):
    """
    Paste references from the clipboard into the specified destination instance.

    This function retrieves reference data from the clipboard, validates it, and
    processes it to create references, grouped references, or referenced groups
    in the specified destination instance based on the provided context.

    Args:
        context (str): The context in which the references are being pasted.
            Expected values are 'work_env' or other contexts.
        destination_instance_id (int): The ID of the destination instance where
            the references will be created.

    Returns:
        int: Returns 1 upon successful execution.

    Notes:
        - The clipboard must contain valid JSON data with a 'references_dic' key.
        - The 'references_dic' key should include 'references', 'grouped_references',
          and 'referenced_groups' keys, each containing lists of IDs.
        - Depending on the context, the function creates references, grouped references,
          or referenced groups using the provided data.

    Warnings:
        - Logs a warning if the clipboard does not contain valid JSON data or
          if the required 'references_dic' key is missing.
    """
    # Retrieve clipboard content and parse it as JSON
    clipboard_json = clipboard.paste()
    try:
        clipboard_dic = json.loads(clipboard_json)
    except json.decoder.JSONDecodeError:
        logger.warning("No valid references found in clipboard")
        return

    # Check if the clipboard contains valid references data
    if 'references_dic' not in clipboard_dic.keys():
        logger.warning("No valid references found in clipboard")
        return

    # Extract references data from the clipboard
    references_dic = clipboard_dic['references_dic']
    references_rows = []
    referenced_groups_rows = []
    grouped_references_rows = []

    # Retrieve reference rows from the project database
    for reference_id in references_dic['references']:
        references_rows.append(project.get_reference_data(reference_id))

    # Retrieve grouped reference rows from the project database
    for grouped_reference_id in references_dic['grouped_references']:
        grouped_references_rows.append(
            project.get_grouped_reference_data(grouped_reference_id))

    # Retrieve referenced group rows from the project database
    for referenced_group_id in references_dic['referenced_groups']:
        referenced_groups_rows.append(
            project.get_referenced_group_data(referenced_group_id))

    # Process and create references based on the context
    for reference_row in references_rows:
        if context == 'work_env':
            # Create a reference in the work environment
            create_reference(destination_instance_id,
                             reference_row['export_version_id'],
                             auto_update=reference_row['auto_update'],
                             activated=reference_row['activated'])
        else:
            # Create a grouped reference in the specified group
            create_grouped_reference(destination_instance_id,
                                     reference_row['export_version_id'],
                                     auto_update=reference_row['auto_update'],
                                     activated=reference_row['activated'])

    # Process and create grouped references based on the context
    for grouped_reference_row in grouped_references_rows:
        if context == 'work_env':
            # Create a reference in the work environment
            create_reference(destination_instance_id,
                             grouped_reference_row['export_version_id'],
                             auto_update=grouped_reference_row['auto_update'],
                             activated=grouped_reference_row['activated'])
        else:
            # Create a grouped reference in the specified group
            create_grouped_reference(destination_instance_id,
                                     grouped_reference_row['export_version_id'],
                                     auto_update=grouped_reference_row['auto_update'],
                                     activated=grouped_reference_row['activated'])

    # Process and create referenced groups only for work environments
    for referenced_group_row in referenced_groups_rows:
        if context != 'work_env':
            continue
        # Create a referenced group in the work environment
        create_referenced_group(destination_instance_id,
                                referenced_group_row['group_id'],
                                activated=referenced_group_row['activated'])

    return 1


def mirror_references(work_env_id, destination_work_env_id):
    """
    Mirrors the references from one work environment to another by first removing
    all existing references in the destination work environment and then recreating
    them based on the references in the source work environment.

    Args:
        work_env_id (str): The ID of the source work environment from which references
                           will be mirrored.
        destination_work_env_id (str): The ID of the destination work environment where
                                        references will be recreated.

    Behavior:
        - Removes all references in the destination work environment.
        - Recreates references in the destination work environment using the data
          from the source work environment, including export version, namespace,
          count, auto-update status, and activation status.
    """
    for reference_id in project.get_references(destination_work_env_id, 'id'):
        remove_reference(reference_id)
    for reference_row in project.get_references(work_env_id):
        create_reference(destination_work_env_id,
                         reference_row['export_version_id'],
                         namespace_and_count=[
                             reference_row['namespace'], reference_row['count']],
                         auto_update=reference_row['auto_update'],
                         activated=reference_row['activated'])


def duplicate_reference(reference_id):
    """
    Duplicates a reference by creating a new reference with the same properties.

    Args:
        reference_id (int): The ID of the reference to duplicate.

    Behavior:
        - Retrieves the reference data using the provided reference ID.
        - Creates a new reference in the same work environment with the same export version,
          auto-update status, and activation status.
    """
    reference_row = project.get_reference_data(reference_id)
    create_reference(reference_row['work_env_id'],
                     reference_row['export_version_id'],
                     auto_update=reference_row['auto_update'],
                     activated=reference_row['activated'])


def duplicate_grouped_reference(grouped_reference_id):
    """
    Duplicates a grouped reference by creating a new grouped reference with the same properties.

    Args:
        grouped_reference_id (int): The ID of the grouped reference to duplicate.

    Behavior:
        - Retrieves the grouped reference data using the provided grouped reference ID.
        - Creates a new grouped reference in the same group with the same export version,
          auto-update status, and activation status.
    """
    grouped_reference_row = project.get_grouped_reference_data(
        grouped_reference_id)
    create_grouped_reference(grouped_reference_row['group_id'],
                             grouped_reference_row['export_version_id'],
                             auto_update=grouped_reference_row['auto_update'],
                             activated=grouped_reference_row['activated'])


def duplicate_referenced_group(referenced_group_id):
    """
    Duplicates a referenced group by creating a new referenced group with the same properties.

    Args:
        referenced_group_id (int): The ID of the referenced group to duplicate.

    Behavior:
        - Retrieves the referenced group data using the provided referenced group ID.
        - Creates a new referenced group in the same work environment with the same group ID
          and activation status.
    """
    referenced_group_row = project.get_referenced_group_data(
        referenced_group_id)
    create_referenced_group(referenced_group_row['work_env_id'],
                            referenced_group_row['group_id'],
                            activated=referenced_group_row['activated'])


def modify_version_comment(version_id, comment=''):
    """
    Modifies the comment associated with a specific version.

    Args:
        version_id (int): The unique identifier of the version to be modified.
        comment (str): The new comment to set for the version. Defaults to an empty string.

    Returns:
        int: 1 if the comment was successfully modified, otherwise None.

    Behavior:
        - Updates the version's comment in the project database.
        - Analyzes the comment for tags and logs the analysis.
    """
    if not project.modify_version_comment(version_id, comment):
        return
    tags.analyse_comment(comment, 'work_version', version_id)
    return 1


def set_asset_preview(asset_id, image_file):
    """
    Sets a preview image for a specific asset.

    Args:
        asset_id (int): The unique identifier of the asset.
        image_file (str): The file path of the image to be used as the preview.

    Returns:
        str or None: The file path of the resized preview image if successful, otherwise None.

    Behavior:
        - Creates a 'preview' directory within the asset's path if it does not exist.
        - Resizes the provided image file and saves it in the 'preview' directory.
        - Updates the asset's manual preview path in the project database.
    """
    preview_file = None
    if image_file is not None:
        preview_path = path_utils.join(get_asset_path(asset_id), 'preview')
        if not path_utils.isdir(preview_path):
            path_utils.mkdir(preview_path)
        destination = path_utils.join(preview_path,
                                      f"{project.get_asset_data(asset_id, 'name')}.jpg")
        preview_file = image.resize_preview(image_file, destination)
    return project.modify_asset_manual_preview(asset_id, preview_file)


def merge_file(file, work_env_id, comment="", do_screenshot=1):
    """
    Merges a file into a new version of a work environment.

    Args:
        file (str): The file path to be merged.
        work_env_id (int): The ID of the work environment where the file will be merged.
        comment (str, optional): A comment describing the merge. Defaults to an empty string.
        do_screenshot (int, optional): Flag to determine whether to capture a screenshot. Defaults to 1 (enabled).

    Returns:
        int or None: The ID of the newly created version if successful, otherwise None.

    Behavior:
        - Validates the existence of the file and its extension against the work environment's rules.
        - Creates a new version in the specified work environment.
        - Copies the file to the new version's file path.
        - Logs the merge operation and returns the new version ID.
    """
    if not path_utils.isfile(file):
        logger.warning(f"{file} doesn't exists")
        return
    software_extension = project.get_software_data(project.get_work_env_data(work_env_id, 'software_id'),
                                                   'extension')
    file_extension = os.path.splitext(file)[-1].replace('.', '')
    if software_extension != file_extension:
        logger.warning(
            f"{file} doesn't match the work environment extension rules ( .ma )")
        return None
    version_id = add_version(work_env_id, comment, do_screenshot)
    version_row = project.get_version_data(version_id)
    path_utils.copyfile(file, version_row['file_path'])
    logger.info(f"{file} merged in new version {version_row['name']}")
    return version_id


def duplicate_version(version_id, work_env_id=None, comment=None):
    """
    Duplicates a version into the same or a different work environment.

    Args:
        version_id (int): The ID of the version to be duplicated.
        work_env_id (int, optional): The ID of the destination work environment. Defaults to the source version's work environment.
        comment (str, optional): A comment describing the duplication. Defaults to the source version's comment.

    Returns:
        int or None: The ID of the newly duplicated version if successful, otherwise None.

    Behavior:
        - Retrieves the source version's data and determines the destination work environment and comment.
        - Merges the source version's file into the destination work environment as a new version.
        - Copies the source version's screenshot and thumbnail to the new version.
        - Returns the ID of the newly created version.
    """
    version_row = project.get_version_data(version_id)
    if not version_row:
        return
    if comment is None:
        comment = version_row['comment']
    if work_env_id is None:
        work_env_id = version_row['work_env_id']
    new_version_id = merge_file(version_row['file_path'],
                                work_env_id,
                                comment, 0)
    if new_version_id is None:
        return
    new_version_row = project.get_version_data(new_version_id)
    if path_utils.isfile(version_row['screenshot_path']):
        path_utils.copyfile(version_row['screenshot_path'],
                            new_version_row['screenshot_path'])
    if path_utils.isfile(version_row['thumbnail_path']):
        path_utils.copyfile(version_row['thumbnail_path'],
                            new_version_row['thumbnail_path'])
    return new_version_id


def archive_version(version_id):
    """
    Archives a specific version by compressing its file into a zip archive 
    and removing the original file. The version is then removed from the project.

    Args:
        version_id (int): The unique identifier of the version to be archived.

    Returns:
        int or None: Returns 1 if the version was successfully archived and removed, 
        otherwise None.

    Behavior:
        - Checks if the current user has administrative privileges.
        - Retrieves the version data using the provided version ID.
        - Prevents archiving of the default version (0001).
        - Compresses the version file into a zip archive if it exists.
        - Deletes the original version file after archiving.
        - Removes the version from the project database.
    """
    if not repository.is_admin():
        return
    version_row = project.get_version_data(version_id)
    if version_row['name'] == '0001':
        logger.warning("You can't archive the default version (0001)")
        return
    if not version_row:
        return
    if path_utils.isfile(version_row['file_path']):
        zip_file = path_utils.join(os.path.split(version_row['file_path'])[0],
                                   'archives.zip')
        if tools.zip_files([version_row['file_path']], zip_file):
            path_utils.remove(version_row['file_path'])
            logger.info(f"{version_row['file_path']} deleted")
    else:
        logger.warning(f"{version_row['file_path']} not found")
    return project.remove_version(version_row['id'])


def archive_video(video_id):
    """
    Archives a specific video by compressing its file into a zip archive 
    and removing the original file and its thumbnail. The video is then 
    removed from the project.

    Args:
        video_id (int): The unique identifier of the video to be archived.

    Returns:
        int or None: Returns 1 if the video was successfully archived and removed, 
        otherwise None.

    Behavior:
        - Checks if the current user has administrative privileges.
        - Retrieves the video data using the provided video ID.
        - Compresses the video file into a zip archive if it exists.
        - Deletes the original video file and its thumbnail after archiving.
        - Removes the video from the project database.
    """
    if not repository.is_admin():
        return
    video_row = project.get_video_data(video_id)
    if not video_row:
        return
    if path_utils.isfile(video_row['file_path']):
        zip_file = path_utils.join(os.path.split(video_row['file_path'])[0],
                                   'archives.zip')
        if tools.zip_files([video_row['file_path']], zip_file):
            path_utils.remove(video_row['file_path'])
            path_utils.remove(video_row['thumbnail_path'])
            logger.info(f"{video_row['file_path']} deleted")
    else:
        logger.warning(f"{video_row['file_path']} not found")
    return project.remove_video(video_row['id'])


def get_video_folder(version_id):
    """
    Retrieves the folder path for storing video files associated with a specific version.
    If the folder does not exist, it is created.

    Args:
        version_id (int): The unique identifier of the version.

    Returns:
        str: The absolute path to the video folder.

    Raises:
        KeyError: If the 'work_env_id' key is not found in the version data.
        OSError: If there is an error creating the directory.
    """
    version_row = project.get_version_data(version_id)
    work_env_path = get_work_env_path(version_row['work_env_id'])
    playblast_folder = path_utils.join(work_env_path, 'video')
    if not path_utils.isdir(playblast_folder):
        path_utils.mkdir(playblast_folder)
    return playblast_folder


def create_group(name, color='#798fe8'):
    """
    Creates a new group with the specified name and color.

    Args:
        name (str): The name of the group to be created.
        color (str, optional): The color associated with the group. Defaults to '#798fe8'.

    Returns:
        int or None: The ID of the newly created group if successful, otherwise None.

    Behavior:
        - Validates the group name to ensure it is safe.
        - Creates the group in the project database with the specified name and color.
    """
    if not tools.is_safe(name):
        return
    return project.create_group(name, color)


def remove_group(group_id):
    """
    Removes a group by its unique identifier.

    Args:
        group_id (int): The ID of the group to be removed.

    Returns:
        int or None: Returns 1 if the group was successfully removed, otherwise None.

    Behavior:
        - Deletes the group from the project database using the provided group ID.
    """
    return project.remove_group(group_id)


def create_referenced_group(work_env_id, group_id, activated=1):
    """
    Creates a referenced group in a specified work environment.

    This function generates a unique namespace for the referenced group by appending
    a numerical suffix if necessary. It then creates the referenced group in the
    project database with the specified parameters.

    Args:
        work_env_id (int): The ID of the work environment where the referenced group will be created.
        group_id (int): The ID of the group to be referenced.
        activated (int, optional): Indicates whether the referenced group is activated. Defaults to 1 (activated).

    Returns:
        int or None: The ID of the newly created referenced group if successful, otherwise None.

    Behavior:
        - Retrieves the list of existing namespaces in the work environment.
        - Generates a unique namespace for the referenced group.
        - Creates the referenced group in the project database with the generated namespace.
    """
    namespaces_list = project.get_referenced_groups(work_env_id, 'namespace')
    count = 0
    namespace_raw = project.get_group_data(group_id, 'name')
    namespace = f"{namespace_raw}"
    while namespace in namespaces_list:
        count += 1
        namespace = f"{namespace_raw}_{str(count)}"
    return project.create_referenced_group(work_env_id,
                                           group_id,
                                           namespace,
                                           count,
                                           activated)


def remove_referenced_group(referenced_group_id):
    """
    Removes a referenced group by its unique identifier.

    Args:
        referenced_group_id (int): The ID of the referenced group to be removed.

    Returns:
        int or None: Returns 1 if the referenced group was successfully removed, otherwise None.

    Behavior:
        - Deletes the referenced group from the project database using the provided ID.
    """
    return project.remove_referenced_group(referenced_group_id)


def create_grouped_references_from_stage_id(group_id, stage_id):
    """
    Creates grouped references for a given stage ID within a specified group.

    This function retrieves export rows associated with the given stage ID and processes
    them to create grouped references. If the stage corresponds to modeling, only the
    first export row is considered.

    Args:
        group_id (int): The ID of the group where grouped references will be created.
        stage_id (int): The ID of the stage for which grouped references are to be created.

    Returns:
        int or None: Returns 1 if at least one grouped reference is successfully created,
        otherwise returns None if no exports are found.

    Behavior:
        - Retrieves export rows associated with the stage ID.
        - If the stage corresponds to modeling, only the first export row is considered.
        - For each export row, retrieves the default export version ID and creates a grouped reference.
    """
    export_rows = project.get_stage_export_childs(stage_id)
    stage = project.get_stage_data(stage_id, 'name')
    if not export_rows:
        return
    if stage == assets_vars._modeling_:
        export_rows = [export_rows[0]]
    for export_row in export_rows:
        export_version_id = project.get_default_export_version(
            export_row['id'], 'id')
        if export_version_id:
            create_grouped_reference(group_id, export_version_id)
    return 1


def create_grouped_reference(group_id, export_version_id, auto_update=0, activated=1):
    """
    Creates a grouped reference in a specified group.

    This function generates a unique namespace for the grouped reference by appending
    a numerical suffix if necessary. It then creates the grouped reference in the
    project database with the specified parameters.

    Args:
        group_id (int): The ID of the group where the grouped reference will be created.
        export_version_id (int): The ID of the export version to be referenced.
        auto_update (int, optional): Indicates whether the grouped reference should auto-update.
                                     Defaults to 0 (disabled).
        activated (int, optional): Indicates whether the grouped reference is activated.
                                   Defaults to 1 (activated).

    Returns:
        int or None: The ID of the newly created grouped reference if successful, otherwise None.

    Behavior:
        - Retrieves the list of existing namespaces in the group.
        - Generates a unique namespace for the grouped reference.
        - Creates the grouped reference in the project database with the generated namespace.
    """
    namespaces_list = project.get_grouped_references(group_id, 'namespace')
    count = 0
    namespace_raw = build_namespace(export_version_id)
    namespace = f"{namespace_raw}"
    while namespace in namespaces_list:
        count += 1
        namespace = f"{namespace_raw}_{str(count)}"
    return project.create_grouped_reference(group_id,
                                            export_version_id,
                                            namespace,
                                            count,
                                            auto_update,
                                            activated)


def remove_grouped_reference(grouped_reference_id):
    """
    Removes a grouped reference by its unique identifier.

    Args:
        grouped_reference_id (int): The ID of the grouped reference to be removed.

    Returns:
        int or None: Returns 1 if the grouped reference was successfully removed, otherwise None.

    Behavior:
        - Deletes the grouped reference from the project database using the provided ID.
    """
    return project.remove_grouped_reference(grouped_reference_id)


def set_grouped_reference_last_version(grouped_reference_id):
    """
    Updates the grouped reference to the latest default export version if it is outdated.

    This function checks the current export version associated with the given
    grouped reference ID. If the export version is not the latest default version, it
    updates the grouped reference to point to the latest default export version.

    Args:
        grouped_reference_id (int): The ID of the grouped reference to be checked and updated.

    Returns:
        int or None: Returns 1 if the grouped reference was updated successfully, 
        None if no update was necessary or if the reference/export data is invalid.

    Logs:
        - Logs an informational message if the grouped reference is already up to date.
    """
    export_version_id = project.get_grouped_reference_data(grouped_reference_id,
                                                           'export_version_id')
    if not export_version_id:
        return
    export_version_row = project.get_export_version_data(export_version_id)
    export_row = project.get_export_data(export_version_row['export_id'])
    default_export_version_id = project.get_default_export_version(
        export_row['id'], 'id')
    if not default_export_version_id:
        logger.info("Grouped reference is up to date")
        return
    if default_export_version_id == export_version_id:
        return
    project.update_grouped_reference(
        grouped_reference_id, default_export_version_id)
    return 1


def create_or_get_camera_work_env(work_env_id):
    """
    Creates or retrieves a camera work environment associated with the given work environment ID.

    This function checks if a camera stage exists for the asset associated with the given work 
    environment. If the camera stage does not exist, it creates one. It then ensures that a 
    work environment for the specified software exists within the camera stage's default variant. 
    If it does not exist, it creates one.

    Args:
        work_env_id (int): The ID of the work environment to process.

    Returns:
        int: The ID of the camera work environment.
    """
    # Retrieve the work environment data and software name
    work_env_row = project.get_work_env_data(work_env_id)
    software = work_env_row['name']

    # Retrieve the stage ID and asset ID associated with the work environment
    stage_id = project.get_variant_data(work_env_row['variant_id'], 'stage_id')
    asset_id = project.get_stage_data(stage_id, 'asset_id')

    # Check if a 'camera' stage exists for the asset
    stages = project.get_asset_childs(asset_id, 'name')
    if 'camera' in stages:
        # If the 'camera' stage exists, retrieve its ID
        camera_stage_id = project.get_asset_child_by_name(
            asset_id, 'camera', 'id')
    else:
        # If the 'camera' stage does not exist, create it
        camera_stage_id = create_stage('camera', asset_id)

    # Retrieve the default variant ID for the 'camera' stage
    camera_default_variant_id = project.get_stage_data(
        camera_stage_id, 'default_variant_id')

    # Check if a work environment for the specified software exists in the 'camera' stage's default variant
    work_envs = project.get_variant_work_envs_childs(
        camera_default_variant_id, 'name')
    if software in work_envs:
        # If the work environment exists, retrieve its ID
        camera_work_env_id = project.get_variant_work_env_child_by_name(
            camera_default_variant_id, software, 'id')
    else:
        # If the work environment does not exist, create it
        software_id = project.get_software_data_by_name(software, 'id')
        camera_work_env_id = create_work_env(
            software_id, camera_default_variant_id)

    # Return the ID of the camera work environment
    return camera_work_env_id


def create_or_get_rendering_work_env(work_env_id):
    """
    Creates or retrieves a rendering work environment associated with the given work environment ID.

    This function ensures that a rendering stage exists for the asset associated with the given 
    work environment. If the rendering stage does not exist, it creates one. It then ensures that 
    a work environment for the specified software exists within the rendering stage's default variant. 
    If it does not exist, it creates one.

    Args:
        work_env_id (int): The ID of the work environment to process.

    Returns:
        int: The ID of the rendering work environment.
    """
    # Retrieve the work environment data and software name
    work_env_row = project.get_work_env_data(work_env_id)
    software = work_env_row['name']

    # Retrieve the stage ID and asset ID associated with the work environment
    stage_id = project.get_variant_data(work_env_row['variant_id'], 'stage_id')
    asset_id = project.get_stage_data(stage_id, 'asset_id')

    # Check if a 'rendering' stage exists for the asset
    stages = project.get_asset_childs(asset_id, 'name')
    if 'rendering' in stages:
        # If the 'rendering' stage exists, retrieve its ID
        rendering_stage_id = project.get_asset_child_by_name(
            asset_id, 'rendering', 'id')
    else:
        # If the 'rendering' stage does not exist, create it
        rendering_stage_id = create_stage('rendering', asset_id)

    # Retrieve the default variant ID for the 'rendering' stage
    rendering_default_variant_id = project.get_stage_data(
        rendering_stage_id, 'default_variant_id')

    # Check if a work environment for the specified software exists in the 'rendering' stage's default variant
    work_envs = project.get_variant_work_envs_childs(
        rendering_default_variant_id, 'name')
    if software in work_envs:
        # If the work environment exists, retrieve its ID
        rendering_work_env_id = project.get_variant_work_env_child_by_name(
            rendering_default_variant_id, software, 'id')
    else:
        # If the work environment does not exist, create it
        software_id = project.get_software_data_by_name(software, 'id')
        rendering_work_env_id = create_work_env(
            software_id, rendering_default_variant_id)

    # Return the ID of the rendering work environment
    return rendering_work_env_id


def add_asset_tracking_event(stage_id, event_type, data, comment=''):
    """
    Adds an asset tracking event for a specific stage.

    Args:
        stage_id (int): The unique identifier of the stage.
        event_type (str): The type of the event to be added.
        data (dict): Additional data associated with the event.
        comment (str, optional): A comment describing the event. Defaults to an empty string.

    Returns:
        int: 1 if the event was successfully added, otherwise None.

    Behavior:
        - Adds the asset tracking event to the project database.
        - Analyzes the comment for tags and logs the analysis.
    """
    if not project.add_asset_tracking_event(stage_id, event_type, data, comment):
        return
    tags.analyse_comment(comment, 'stage', stage_id)
    return 1


def get_default_extension(work_env_id):
    """
    Retrieves the default file extension for a given work environment.

    Args:
        work_env_id (int): The unique identifier of the work environment.

    Returns:
        str: The default file extension for the work environment.

    Behavior:
        - Retrieves the work environment and variant data.
        - Determines the stage name associated with the variant.
        - Checks if a custom export extension is set for the work environment.
        - If no custom extension is set, retrieves the default extension based on the stage and software.
    """
    work_env_row = project.get_work_env_data(work_env_id)
    variant_row = project.get_variant_data(work_env_row['variant_id'])
    stage_name = project.get_stage_data(variant_row['stage_id'], 'name')
    if not work_env_row['export_extension']:
        extension = project.get_default_extension(
            stage_name, work_env_row['software_id'])
    else:
        extension = work_env_row['export_extension']
    return extension


def get_domain_path(domain_id):
    """
    Retrieves the file system path for a specific domain.

    Args:
        domain_id (int): The unique identifier of the domain.

    Returns:
        str or None: The file system path of the domain if successful, otherwise None.

    Behavior:
        - Retrieves the domain name using the provided domain ID.
        - Constructs the path by joining the project path with the domain name.
    """
    domain_name = project.get_domain_data(domain_id, 'name')
    if not domain_name:
        return
    return path_utils.join(environment.get_project_path(), domain_name)


def get_category_path(category_id):
    """
    Retrieves the file system path for a specific category.

    Args:
        category_id (int): The unique identifier of the category.

    Returns:
        str or None: The file system path of the category if successful, otherwise None.

    Behavior:
        - Retrieves the category name and its associated domain ID using the provided category ID.
        - Constructs the path by joining the domain path with the category name.
    """
    category_row = project.get_category_data(category_id)
    if not category_row:
        return
    category_name = category_row['name']
    domain_path = get_domain_path(category_row['domain_id'])
    if not domain_path:
        return
    return path_utils.join(domain_path, category_name)


def get_asset_path(asset_id):
    """
    Retrieves the file system path for a specific asset.

    Args:
        asset_id (int): The unique identifier of the asset.

    Returns:
        str or None: The file system path of the asset if successful, otherwise None.

    Behavior:
        - Retrieves the asset name and its associated category ID using the provided asset ID.
        - Constructs the path by joining the category path with the asset name.
    """
    asset_row = project.get_asset_data(asset_id)
    if not asset_row:
        return
    asset_name = asset_row['name']
    category_path = get_category_path(asset_row['category_id'])
    if not category_path:
        return
    return path_utils.join(category_path, asset_name)


def get_stage_path(stage_id):
    """
    Retrieves the file system path for a specific stage.

    Args:
        stage_id (int): The unique identifier of the stage.

    Returns:
        str or None: The file system path of the stage if successful, otherwise None.

    Behavior:
        - Retrieves the stage name and its associated asset ID using the provided stage ID.
        - Constructs the path by joining the asset path with the stage name.
    """
    stage_row = project.get_stage_data(stage_id)
    if not stage_row:
        return
    stage_name = stage_row['name']
    asset_path = get_asset_path(stage_row['asset_id'])
    if not asset_path:
        return
    return path_utils.join(asset_path, stage_name)


def get_variant_path(variant_id):
    """
    Retrieves the file system path for a specific variant.

    Args:
        variant_id (int): The unique identifier of the variant.

    Returns:
        str or None: The file system path of the variant if successful, otherwise None.

    Behavior:
        - Retrieves the variant name and its associated stage ID using the provided variant ID.
        - Constructs the path by joining the stage path with the variant name.
    """
    variant_row = project.get_variant_data(variant_id)
    if not variant_row:
        return
    variant_name = variant_row['name']
    stage_path = get_stage_path(variant_row['stage_id'])
    if not stage_path:
        return
    return path_utils.join(stage_path, variant_name)


def get_stage_export_path(stage_id):
    """
    Retrieves the file system path for the export directory of a specific stage.

    Args:
        stage_id (int): The unique identifier of the stage.

    Returns:
        str or None: The file system path of the stage's export directory if successful, otherwise None.

    Behavior:
        - Retrieves the stage name and its associated path using the provided stage ID.
        - Constructs the path by appending '_EXPORTS' to the stage path.
    """
    stage_row = project.get_stage_data(stage_id)
    if not stage_row:
        return
    stage_path = get_stage_path(stage_id)
    if not stage_path:
        return
    return path_utils.join(stage_path, '_EXPORTS')


def get_work_env_path(work_env_id):
    """
    Retrieves the file system path for a specific work environment.

    Args:
        work_env_id (int): The unique identifier of the work environment.

    Returns:
        str or None: The file system path of the work environment if successful, otherwise None.

    Behavior:
        - Retrieves the work environment name and its associated variant ID using the provided work_env_id.
        - Constructs the path by joining the variant path with the work environment name.
    """
    work_env_row = project.get_work_env_data(work_env_id)
    if not work_env_row:
        return
    work_env_name = work_env_row['name']
    variant_path = get_variant_path(work_env_row['variant_id'])
    if not variant_path:
        return
    return path_utils.join(variant_path, work_env_name)


def get_video_path(variant_id):
    """
    Retrieves the file system path for the video directory of a specific variant.

    Args:
        variant_id (int): The unique identifier of the variant.

    Returns:
        str: The file system path of the variant's video directory.

    Behavior:
        - Retrieves the variant path using the provided variant_id.
        - Constructs the path by appending '_VIDEOS' to the variant path.
        - Ensures the video directory exists by creating it if it does not already exist.
    """
    variant_path = get_variant_path(variant_id)
    if not variant_path:
        return
    dir_name = path_utils.join(variant_path, '_VIDEOS')
    if not path_utils.isdir(dir_name):
        path_utils.mkdir(dir_name)
    return dir_name


def get_export_path(export_id):
    """
    Retrieves the file system path for a specific export.

    Args:
        export_id (int): The unique identifier of the export.

    Returns:
        str or None: The file system path of the export if successful, otherwise None.

    Behavior:
        - Retrieves the export name and its associated stage ID using the provided export ID.
        - Constructs the path by joining the stage path, '_EXPORTS', and the export name.
    """
    export_row = project.get_export_data(export_id)
    if not export_row:
        return
    export_name = export_row['name']
    stage_path = get_stage_path(export_row['stage_id'])
    if not stage_path:
        return
    return path_utils.join(stage_path,
                           '_EXPORTS',
                           export_name)


def get_temp_export_path(export_id):
    """
    Retrieves the temporary file system path for a specific export.

    Args:
        export_id (int): The unique identifier of the export.

    Returns:
        str: The temporary file system path of the export.

    Behavior:
        - Retrieves the local path of the user and the project path.
        - If the local path is not set, creates a temporary directory and logs a warning.
        - Retrieves the export name and its associated stage ID using the provided export ID.
        - Constructs the temporary path by appending 'temp' to the export path and adjusting it for the local path.
    """
    # Retrieve the local path and project path
    local_path = user.user().get_local_path()
    project_path = environment.get_project_path()

    # If the local path is not set, create a temporary directory and log a warning
    if local_path is None or local_path == '':
        dir_name = tools.temp_dir()
        logger.warning(
            "Your local path is not setted, exporting in default temp dir.")
        return dir_name

    # Retrieve export data using the provided export ID
    export_row = project.get_export_data(export_id)
    if not export_row:
        return

    # Retrieve the export name and stage path
    export_name = export_row['name']
    stage_path = get_stage_path(export_row['stage_id'])
    if not stage_path:
        return

    # Construct the temporary export directory path
    dir_name = path_utils.join(stage_path, '_EXPORTS', export_name, 'temp')

    # Adjust the path for the local path and return it
    dir_name = local_path + dir_name[len(project_path):]
    return dir_name


def get_temp_video_path(variant_id):
    """
    Generates and returns a temporary directory path for storing video files 
    associated with a given variant ID. The function ensures that the directory 
    exists and creates it if necessary.

    Args:
        variant_id (str): The identifier for the video variant.

    Returns:
        str: The path to the temporary directory for the video variant. 
             If the video path cannot be determined, returns None.

    Notes:
        - If the user's local path is not set, a default temporary directory 
          is used, and a warning is logged.
        - The temporary directory is created within the user's local path, 
          relative to the project path.
    """
    local_path = user.user().get_local_path()
    project_path = environment.get_project_path()
    if local_path is None or local_path == '':
        dir_name = tools.temp_dir()
        logger.warning(
            "Your local path is not setted, exporting in default temp dir.")
        return dir_name
    video_path = get_video_path(variant_id)
    if not video_path:
        return
    dir_name = path_utils.join(video_path, 'temp')
    dir_name = local_path+dir_name[len(project_path):]
    if not path_utils.isdir(dir_name):
        path_utils.makedirs(dir_name)
    dir_name = tools.temp_dir_in_dir(dir_name)
    return dir_name


def get_export_version_path(export_version_id):
    """
    Retrieves the full file path for a specific export version.

    Args:
        export_version_id (int): The unique identifier of the export version.

    Returns:
        str: The full path to the export version file, or None if the export version
             or its associated export path cannot be found.

    Notes:
        - This function depends on `project.get_export_version_data` to fetch
          export version details and `get_export_path` to retrieve the base export path.
        - The resulting path is constructed by joining the base export path with
          the export version name.
    """
    export_version_row = project.get_export_version_data(export_version_id)
    if not export_version_row:
        return
    export_version_name = export_version_row['name']
    export_path = get_export_path(export_version_row['export_id'])
    if not export_path:
        return
    return path_utils.join(export_path, export_version_name)


def build_version_file_name(work_env_id, name):
    """
    Constructs a file name for a specific version in a work environment.

    Args:
        work_env_id (int): The unique identifier of the work environment.
        name (str): The name of the version.

    Returns:
        str: The constructed file name for the version.

    Behavior:
        - Retrieves data for the work environment, variant, stage, asset, and category.
        - Constructs the file name using the category, asset, stage, variant, version name, and software extension.
    """
    work_env_row = project.get_work_env_data(work_env_id)
    variant_row = project.get_variant_data(work_env_row['variant_id'])
    stage_row = project.get_stage_data(variant_row['stage_id'])
    asset_row = project.get_asset_data(stage_row['asset_id'])
    category_row = project.get_category_data(asset_row['category_id'])
    extension = project.get_software_data(
        work_env_row['software_id'], 'extension')

    file_name = f"{category_row['name']}"
    file_name += f"_{asset_row['name']}"
    file_name += f"_{stage_row['name']}"
    file_name += f"_{variant_row['name']}"
    file_name += f".{name}"
    file_name += f".{extension}"
    return file_name


def build_video_file_name(variant_id, name):
    """
    Constructs a file name for a video associated with a specific variant.

    Args:
        variant_id (int): The unique identifier of the variant.
        name (str): The name of the video version.

    Returns:
        str: The constructed file name for the video.

    Behavior:
        - Retrieves data for the variant, stage, asset, and category.
        - Constructs the file name using the category, asset, stage, variant, video version name, and a fixed 'mp4' extension.
    """
    variant_row = project.get_variant_data(variant_id)
    stage_row = project.get_stage_data(variant_row['stage_id'])
    asset_row = project.get_asset_data(stage_row['asset_id'])
    category_row = project.get_category_data(asset_row['category_id'])
    extension = 'mp4'

    file_name = f"{category_row['name']}"
    file_name += f"_{asset_row['name']}"
    file_name += f"_{stage_row['name']}"
    file_name += f"_{variant_row['name']}"
    file_name += f".{name}"
    file_name += f".{extension}"
    return file_name


def build_export_file_name(work_env_id, export_name, multiple=None):
    """
    Constructs an export file name based on the provided work environment ID, export name, 
    and optional multiple file indicator.
    The function retrieves data from various entities such as work environment, variant, 
    stage, asset, and category to build a structured file name. It also determines the 
    appropriate file extension based on the work environment or default settings.
    Args:
        work_env_id (int): The ID of the work environment.
        export_name (str): The name of the export to include in the file name.
        multiple (str, optional): An optional indicator for multiple files (e.g., a sequence number). 
                                  Defaults to None.
    Returns:
        str: The constructed file name including category, asset, stage, variant, export name, 
             and extension. Returns None if the file extension cannot be determined.
    """
    work_env_row = project.get_work_env_data(work_env_id)
    variant_row = project.get_variant_data(work_env_row['variant_id'])
    stage_row = project.get_stage_data(variant_row['stage_id'])
    asset_row = project.get_asset_data(stage_row['asset_id'])
    category_row = project.get_category_data(asset_row['category_id'])
    if not work_env_row['export_extension']:
        extension = project.get_default_extension(
            stage_row['name'], work_env_row['software_id'])
    else:
        extension = work_env_row['export_extension']

    if not extension:
        logger.error("Can't build file name")
        return
    file_name = f"{category_row['name']}"
    file_name += f"_{asset_row['name']}"
    file_name += f"_{stage_row['name']}"
    file_name += f"_{variant_row['name']}"
    file_name += f"_{export_name}"
    if multiple:
        file_name += f".{multiple}"
    file_name += f".{extension}"
    return file_name


def build_namespace(export_version_id):
    """
    Constructs a namespace string based on hierarchical project data.

    The namespace is built using data retrieved from various project entities
    such as export version, export, stage, asset, category, and domain. The
    structure of the namespace depends on the domain, category, asset, export,
    and stage names.

    Args:
        export_version_id (int): The ID of the export version used to retrieve
                                 hierarchical project data.

    Returns:
        str: A formatted namespace string based on the project data.

    Notes:
        - If the domain name is 'assets', the category name is truncated to the
          first 5 characters.
        - The namespace includes the asset name and, for specific stages
          ('animation' or 'cfx'), the export name.
        - The stage name is truncated to the first 3 characters and appended
          to the namespace.
    """
    export_version_row = project.get_export_version_data(export_version_id)
    export_row = project.get_export_data(export_version_row['export_id'])
    stage_row = project.get_stage_data(export_row['stage_id'])
    asset_row = project.get_asset_data(stage_row['asset_id'])
    category_row = project.get_category_data(asset_row['category_id'])
    domain_row = project.get_domain_data(category_row['domain_id'])
    if domain_row['name'] == 'assets':
        namespace = f"{category_row['name'][:5]}"
    else:
        namespace = f"{category_row['name']}"
    namespace += f"_{asset_row['name']}"
    if stage_row['name'] == 'animation' or stage_row['name'] == 'cfx':
        namespace += f"_{export_row['name']}"
    namespace += f"_{stage_row['name'][:3]}"
    return namespace


def instance_to_string(instance_tuple):
    """
    Converts an instance tuple into a string representation based on its type.

    Args:
        instance_tuple (tuple): A tuple where the first element represents the 
            type of the instance (e.g., 'export_version', 'export', etc.), and 
            the last element represents the instance ID.

    Returns:
        str: A string representation of the instance based on its type, or 
            None if the type is not recognized.

    Supported instance types:
        - 'export_version': Retrieves export version data as a string.
        - 'export': Retrieves export data as a string.
        - 'work_version': Retrieves work version data as a string.
        - 'work_env': Retrieves work environment data as a string.
        - 'variant': Retrieves variant data as a string.
        - 'stage': Retrieves stage data as a string.
        - 'asset': Retrieves asset data as a string.
        - 'category': Retrieves category data as a string.
        - 'domain': Retrieves domain data as a string.
    """
    instance_type = instance_tuple[0]
    instance_id = instance_tuple[-1]
    string = None
    if instance_type == 'export_version':
        string = project.get_export_version_data(instance_id, 'string')
    elif instance_type == 'export':
        string = project.get_export_data(instance_id, 'string')
    elif instance_type == 'work_version':
        string = project.get_version_data(instance_id, 'string')
    elif instance_type == 'work_env':
        string = project.get_work_env_data(instance_id, 'string')
    elif instance_type == 'variant':
        string = project.get_variant_data(instance_id, 'string')
    elif instance_type == 'stage':
        string = project.get_stage_data(instance_id, 'string')
    elif instance_type == 'asset':
        string = project.get_asset_data(instance_id, 'string')
    elif instance_type == 'category':
        string = project.get_category_data(instance_id, 'string')
    elif instance_type == 'domain':
        string = project.get_domain_data(instance_id, 'string')
    return string


def string_to_instance(string):
    """
    Converts a string representation of an instance into its corresponding type and ID.
    The function determines the type of instance (e.g., domain, category, asset, stage, or variant)
    based on the number of segments in the input string, which are separated by '/'.
    It then retrieves the corresponding instance ID using project-specific methods.
    Args:
        string (str): The string representation of the instance, with segments separated by '/'.
    Returns:
        tuple: A tuple containing:
            - instance_type (str): The type of the instance ('domain', 'category', 'asset', 'stage', or 'variant').
            - instance_id: The ID of the instance, retrieved using the appropriate project method.
    """
    instances_list = string.split('/')

    if len(instances_list) == 1:
        instance_type = 'domain'
        instance_id = project.get_domain_data_by_string(string, 'id')
    elif len(instances_list) == 2:
        instance_type = 'category'
        instance_id = project.get_category_data_by_string(string, 'id')
    elif len(instances_list) == 3:
        instance_type = 'asset'
        instance_id = project.get_asset_data_by_string(string, 'id')
    elif len(instances_list) == 4:
        instance_type = 'stage'
        instance_id = project.get_stage_data_by_string(string, 'id')
    elif len(instances_list) == 5:
        instance_type = 'variant'
        instance_id = project.get_variant_data_by_string(string, 'id')

    return (instance_type, instance_id)


def string_to_work_instance(string):
    """
    Converts a string representation of a work instance into its corresponding type and ID.

    This function determines whether the input string represents a work environment or a work version
    based on the number of segments in the string, which are separated by '/'.

    Args:
        string (str): The string representation of the work instance.

    Returns:
        tuple: A tuple containing:
            - instance_type (str or None): The type of the instance ('work_env' or 'work_version').
            - instance_id (int or None): The ID of the instance, retrieved using the appropriate project method.

    Notes:
        - If the string contains 6 segments, it is assumed to represent a work environment.
        - If the string contains 7 segments, it is assumed to represent a work version.
        - Logs a warning and returns (None, None) if the string does not match either case.
    """
    instances_list = string.split('/')
    if len(instances_list) == 6:
        instance_type = 'work_env'
        instance_id = project.get_work_env_data_by_string(string, 'id')
    elif len(instances_list) == 7:
        instance_type = 'work_version'
        instance_id = project.get_work_version_data_by_string(string, 'id')
    else:
        logger.warning('The given string is not a work instance')
        return (None, None)
    return (instance_type, instance_id)


def string_to_export_instance(string):
    """
    Converts a string representation of an export instance into its corresponding type and ID.

    This function determines whether the input string represents an export or an export version
    based on the number of segments in the string, which are separated by '/'.

    Args:
        string (str): The string representation of the export instance.

    Returns:
        tuple: A tuple containing:
            - instance_type (str or None): The type of the instance ('export' or 'export_version').
            - instance_id (int or None): The ID of the instance, retrieved using the appropriate project method.

    Notes:
        - If the string contains 5 segments, it is assumed to represent an export.
        - If the string contains 6 segments, it is assumed to represent an export version.
        - Logs a warning and returns (None, None) if the string does not match either case.
    """
    instances_list = string.split('/')
    if len(instances_list) == 5:
        instance_type = 'export'
        instance_id = project.get_export_data_by_string(string, 'id')
    elif len(instances_list) == 6:
        instance_type = 'export_version'
        instance_id = project.get_export_version_data_by_string(string, 'id')
    else:
        logger.warning('The given string is not an export instance')
        return (None, None)
    return (instance_type, instance_id)
