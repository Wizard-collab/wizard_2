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
This module provides a comprehensive set of functions for managing a project database.
It includes functionality for handling domains, categories, assets, stages, variants,
work environments, export versions, references, and more. The module interacts with
the database to perform CRUD operations and manage project settings, user permissions,
and other project-related data.

Key Features:
- Domain and Category Management: Functions to add, retrieve, and remove domains and categories.
- Asset Management: Functions to add, retrieve, and remove assets, including frame range modifications.
- Stage and Variant Management: Functions to manage stages and their associated variants.
- Work Environment Management: Functions to handle work environments, including locking and unlocking.
- Export and Version Management: Functions to manage export versions, work versions, and their relationships.
- User and Permission Management: Functions to manage user permissions and project settings.
- Event and Progress Tracking: Functions to log events and track progress within the project.
- Shelf Script Management: Functions to manage shelf scripts and separators for project tools.
- Settings and Configuration: Functions to manage project settings, such as frame rate, image format, and OCIO configuration.

Dependencies:
- Python standard libraries: re, os, time, json, logging
- Wizard modules: db_utils, tools, path_utils, repository, environment, image, tags
- Wizard variables: softwares_vars, project_vars, ressources

Logging:
- The module uses the `logging` library to log warnings, errors, and informational messages.

Usage:
- Import the module and call the desired functions to interact with the project database.
- Ensure that the database utilities (`db_utils`) and environment settings are properly configured.

Note:
- The module assumes the existence of a database schema with specific tables and columns.
- Some functions rely on external modules and variables for additional functionality.
"""

# Python modules
import re
import os
import time
import json
import logging

# Wizard modules
from wizard.core import db_utils
from wizard.core import tools
from wizard.core import path_utils
from wizard.core import repository
from wizard.core import environment
from wizard.core import image
from wizard.core import tags
from wizard.vars import softwares_vars
from wizard.vars import project_vars
from wizard.vars import ressources

logger = logging.getLogger(__name__)


def add_domain(name):
    """
    Adds a new domain to the project.

    This function creates a new entry in the 'domains_data' table of the 'project' database
    with the provided domain name, the current timestamp, the current user, and the domain name
    as a string identifier. If the domain is successfully added, its ID is returned. Otherwise,
    a warning is logged.

    Args:
        name (str): The name of the domain to be added.

    Returns:
        int or None: The ID of the newly added domain if successful, or None if the operation fails.

    Logs:
        - Logs a warning if the domain could not be added.
        - Logs an info message if the domain is successfully added.
    """
    domain_id = db_utils.create_row('project',
                                    'domains_data',
                                    ('name', 'creation_time',
                                     'creation_user', 'string'),
                                    (name, time.time(), environment.get_user(), name))
    if not domain_id:
        logger.warning(f"{name} not added to project")
        return
    logger.info(f"Domain {name} added to project")
    return domain_id


def get_domains(column='*'):
    """
    Retrieve domain data from the 'domains_data' table in the 'project' database.

    Args:
        column (str): The specific column(s) to retrieve from the table. 
                      Defaults to '*' to retrieve all columns.

    Returns:
        list: A list of rows containing the requested domain data.
    """
    domain_rows = db_utils.get_rows('project', 'domains_data', column=column)
    return domain_rows


def get_domain_data(domain_id, column='*'):
    """
    Retrieve data for a specific domain from the 'domains_data' table.

    Args:
        domain_id (int): The ID of the domain to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary containing the domain data if found, or None if the domain 
                      is not found.

    Logs:
        Logs an error message if the domain is not found.
    """
    domain_rows = db_utils.get_row_by_column_data('project',
                                                  'domains_data',
                                                  ('id', domain_id),
                                                  column)
    if len(domain_rows) >= 1:
        return domain_rows[0]
    else:
        logger.error("Domain not found")
        return


def get_domain_childs(domain_id, column='*'):
    """
    Retrieve child categories for a given domain ID from the 'categories' table.

    Args:
        domain_id (int): The ID of the domain whose child categories are to be retrieved.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', which retrieves all columns.

    Returns:
        list: A list of rows representing the child categories for the given domain ID.
    """
    categories_rows = db_utils.get_row_by_column_data('project',
                                                      'categories',
                                                      ('domain_id', domain_id),
                                                      column)
    return categories_rows


def get_domain_child_by_name(domain_id, category_name, column='*'):
    """
    Retrieve a specific category row from the 'categories' table in the 'project' database
    based on the provided domain ID and category name.

    Args:
        domain_id (int): The ID of the domain to filter the categories.
        category_name (str): The name of the category to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', which retrieves all columns.

    Returns:
        dict or None: The first matching category row as a dictionary if found, or None if no match is found.

    Logs:
        Logs an error message if no matching category is found.
    """
    categories_rows = db_utils.get_row_by_multiple_data('project',
                                                        'categories',
                                                        ('domain_id', 'name'),
                                                        (domain_id, category_name),
                                                        column)
    if len(categories_rows) >= 1:
        return categories_rows[0]
    else:
        logger.error("Category not found")
        return


def get_domain_by_name(name, column='*'):
    """
    Retrieve a domain record from the 'domains_data' table in the 'project' database
    by its name.

    Args:
        name (str): The name of the domain to search for.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*',
                                which retrieves all columns.

    Returns:
        dict or None: The first matching domain record as a dictionary if found,
                      or None if no matching record is found.

    Logs:
        Logs an error message if the domain is not found.
    """
    domain_rows = db_utils.get_row_by_column_data('project',
                                                  'domains_data',
                                                  ('name', name),
                                                  column)
    if domain_rows and len(domain_rows) >= 1:
        return domain_rows[0]
    else:
        logger.error("Domain not found")
        return


def get_domain_data_by_string(string, column='*'):
    """
    Retrieve domain data from the 'domains_data' table in the 'project' database 
    based on a specific string value.

    Args:
        string (str): The string value to search for in the 'string' column of the table.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' 
                                to retrieve all columns.

    Returns:
        dict or None: The first row of the matching domain data as a dictionary if found, 
                      or None if no matching data is found.

    Logs:
        Logs an error message if no matching domain data is found.
    """
    domain_rows = db_utils.get_row_by_column_data('project',
                                                  'domains_data',
                                                  ('string', string),
                                                  column)
    if domain_rows and len(domain_rows) >= 1:
        return domain_rows[0]
    else:
        logger.error("Domain not found")
        return


def remove_domain(domain_id):
    """
    Removes a domain from the project.

    This function deletes a domain and its associated categories from the project.
    It first checks if the user has administrative privileges. If the user is not
    an admin, the function exits without performing any action. It then retrieves
    all child categories of the specified domain and removes them. Finally, it
    attempts to delete the domain from the database.

    Args:
        domain_id (int): The ID of the domain to be removed.

    Returns:
        int or None: Returns 1 if the domain is successfully removed, or None if
        the user is not an admin or the domain could not be deleted.

    Logs:
        - Logs a warning if the domain could not be removed from the project.
        - Logs an info message if the domain is successfully removed.
    """
    if not repository.is_admin():
        return
    for category_id in get_domain_childs(domain_id, 'id'):
        remove_category(category_id)
    if not db_utils.delete_row('project', 'domains_data', domain_id):
        logger.warning(f"Domain NOT removed from project")
        return
    logger.info(f"Domain removed from project")
    return 1


def get_all_categories(column='*'):
    """
    Retrieve all categories from the 'categories' table in the 'project' database.

    Args:
        column (str): The specific column(s) to retrieve from the table. 
                      Defaults to '*' to retrieve all columns.

    Returns:
        list: A list of rows representing the categories retrieved from the database.
    """
    categories_rows = db_utils.get_rows('project',
                                        'categories',
                                        column)
    return categories_rows


def add_category(name, domain_id):
    """
    Adds a new category to the project if it does not already exist.

    Args:
        name (str): The name of the category to be added. Must not be empty or None.
        domain_id (int): The ID of the domain to which the category belongs.

    Returns:
        int or None: The ID of the newly created category if successful, or None if the category
        already exists or if an error occurs during creation.

    Logs:
        - A warning if the category name is invalid or if the category already exists.
        - An info message when a category is successfully added.

    Notes:
        - The function checks for the existence of the category in the database using the
          combination of `name` and `domain_id`.
        - The `string` field for the category is generated using the domain name and category name.
        - The category is created with additional metadata such as creation time and user.
    """
    # Check if the category name is valid
    if name == '' or name is None:
        logger.warning(f"Please provide a valid category name")
        return

    # Check if the category already exists in the database
    if (db_utils.check_existence_by_multiple_data('project',
                                                  'categories',
                                                  ('name', 'domain_id'),
                                                  (name, domain_id))):
        logger.warning(f"{name} already exists")
        return

    # Retrieve the domain name for constructing the string identifier
    domain_name = get_domain_data(domain_id, 'name')
    string_asset = f"{domain_name}/{name}"

    # Create a new category row in the database
    category_id = db_utils.create_row('project',
                                      'categories',
                                      ('name', 'creation_time',
                                       'creation_user', 'string', 'domain_id'),
                                      (name, time.time(), environment.get_user(), string_asset, domain_id))
    # Check if the category creation was successful
    if not category_id:
        return

    # Log the successful addition of the category
    logger.info(f"Category {name} added to project")
    return category_id


def remove_category(category_id, force=0):
    """
    Removes a category from the project database.

    This function deletes a category and its associated child assets from the 
    project database. If the `force` parameter is not set, the function checks 
    if the user has administrative privileges before proceeding.

    Args:
        category_id (int): The ID of the category to be removed.
        force (int, optional): If set to a non-zero value, forces the removal 
            without checking for administrative privileges. Defaults to 0.

    Returns:
        int or None: Returns 1 if the category was successfully removed, 
        otherwise returns None.

    Notes:
        - The function first removes all child assets associated with the 
          category before attempting to delete the category itself.
        - If the category cannot be removed, a warning is logged.
        - If the category is successfully removed, an informational log is created.
    """
    if not force:
        if not repository.is_admin():
            return
    for asset_id in get_category_childs(category_id, 'id'):
        remove_asset(asset_id, force)
    success = db_utils.delete_row('project', 'categories', category_id)
    if not db_utils.delete_row('project', 'categories', category_id):
        logger.warning(f"Category NOT removed from project")
        return
    logger.info(f"Category removed from project")
    return 1


def get_category_childs(category_id, column="*"):
    """
    Retrieve child assets of a given category from the database.

    Args:
        category_id (int): The ID of the category whose child assets are to be retrieved.
        column (str, optional): The specific column(s) to retrieve from the database. 
                                Defaults to "*" (all columns).

    Returns:
        list: A list of rows representing the child assets of the specified category.
    """
    assets_rows = db_utils.get_row_by_column_data('project',
                                                  'assets',
                                                  ('category_id', category_id),
                                                  column)
    return assets_rows


def get_category_child_by_name(category_id, asset_name, column='*'):
    """
    Retrieve a child asset from a specific category by its name.

    Args:
        category_id (int): The ID of the category to search within.
        asset_name (str): The name of the asset to retrieve.
        column (str, optional): The specific column(s) to retrieve from the database. 
                                Defaults to '*' (all columns).

    Returns:
        dict or None: The first matching asset row as a dictionary if found, 
                      otherwise None.

    Logs:
        Logs an error message if no asset is found.
    """
    assets_rows = db_utils.get_row_by_multiple_data('project',
                                                    'assets',
                                                    ('category_id', 'name'),
                                                    (category_id, asset_name),
                                                    column)
    if len(assets_rows) >= 1:
        return assets_rows[0]
    else:
        logger.error("Asset not found")
        return


def get_category_data(category_id, column='*'):
    """
    Retrieve data for a specific category from the database.

    Args:
        category_id (int): The ID of the category to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary containing the category data if found, or None if 
                      the category does not exist.

    Logs:
        Logs an error message if the category is not found.
    """
    category_rows = db_utils.get_row_by_column_data('project',
                                                    'categories',
                                                    ('id', category_id),
                                                    column)
    if category_rows and len(category_rows) >= 1:
        return category_rows[0]
    else:
        logger.error("Category not found")
        return


def get_category_data_by_name(name, column='*'):
    """
    Retrieve category data from the 'categories' table in the 'project' database 
    by matching the specified category name.

    Args:
        name (str): The name of the category to search for.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary containing the data of the first matching category 
                      row if found, or None if no matching category is found.

    Logs:
        Logs an error message if the category is not found.
    """
    category_rows = db_utils.get_row_by_column_data('project',
                                                    'categories',
                                                    ('name', name),
                                                    column)
    if category_rows and len(category_rows) >= 1:
        return category_rows[0]
    else:
        logger.error("Category not found")
        return


def get_category_data_by_string(string, column='*'):
    """
    Retrieve category data from the database based on a given string.

    This function queries the 'categories' table in the 'project' database
    for rows where the 'string' column matches the provided string. It 
    returns the first matching row if one or more rows are found.

    Args:
        string (str): The string value to search for in the 'string' column.
        column (str, optional): The specific column(s) to retrieve from the 
            database. Defaults to '*' (all columns).

    Returns:
        dict or None: A dictionary representing the first matching row if 
        found, or None if no matching rows are found.

    Logs:
        Logs an error message if no matching category is found.
    """
    category_rows = db_utils.get_row_by_column_data('project',
                                                    'categories',
                                                    ('string', string),
                                                    column)
    if category_rows and len(category_rows) >= 1:
        return category_rows[0]
    else:
        logger.error("Category not found")
        return


def add_asset(name, category_id, inframe=100, outframe=220, preroll=0, postroll=0):
    """
    Adds a new asset to the project database.

    Args:
        name (str): The name of the asset. Must be a non-empty string.
        category_id (int): The ID of the category to which the asset belongs.
        inframe (int, optional): The starting frame of the asset. Defaults to 100.
        outframe (int, optional): The ending frame of the asset. Defaults to 220.
        preroll (int, optional): The number of preroll frames. Defaults to 0.
        postroll (int, optional): The number of postroll frames. Defaults to 0.

    Returns:
        int or None: The ID of the newly created asset if successful, or None if the asset
        could not be created or already exists.

    Logs:
        - A warning if the asset name is invalid or the asset already exists.
        - An info message if the asset is successfully added.

    Notes:
        - The function checks for the existence of the asset in the database before creating it.
        - The asset's string representation is constructed using its domain and category names.
        - A preview for the asset is added after successful creation.
    """
    if name == '' or name is None:
        logger.warning(f"Please provide a valid asset name")
        return
    if (db_utils.check_existence_by_multiple_data('project',
                                                  'assets',
                                                  ('name', 'category_id'),
                                                  (name, category_id))):
        logger.warning(f"{name} already exists")
        return
    category_row = get_category_data(category_id)
    domain_name = get_domain_data(category_row['domain_id'], 'name')
    category_name = category_row['name']
    string_asset = f"{domain_name}/{category_name}/{name}"
    asset_id = db_utils.create_row('project',
                                   'assets',
                                   ('name',
                                    'creation_time',
                                    'creation_user',
                                    'inframe',
                                    'outframe',
                                    'preroll',
                                    'postroll',
                                    'string',
                                    'category_id'),
                                   (name,
                                    time.time(),
                                    environment.get_user(),
                                    inframe,
                                    outframe,
                                    preroll,
                                    postroll,
                                    string_asset,
                                    category_id))
    if not asset_id:
        return
    add_asset_preview(asset_id)
    logger.info(f"Asset {name} added to project")
    return asset_id


def modify_asset_frame_range(asset_id, inframe, outframe, preroll, postroll):
    """
    Updates the frame range and roll values for a specific asset in the database.

    Args:
        asset_id (int): The unique identifier of the asset to be updated.
        inframe (int): The starting frame of the asset.
        outframe (int): The ending frame of the asset.
        preroll (int): The number of preroll frames for the asset.
        postroll (int): The number of postroll frames for the asset.

    Returns:
        int: Returns 1 if all updates are successful, otherwise returns 0.
    """
    success = 1
    if not db_utils.update_data('project',
                                'assets',
                                ('inframe', inframe),
                                ('id', asset_id)):
        success = 0
    if not db_utils.update_data('project',
                                'assets',
                                ('outframe', outframe),
                                ('id', asset_id)):
        success = 0
    if not db_utils.update_data('project',
                                'assets',
                                ('preroll', preroll),
                                ('id', asset_id)):
        success = 0
    if not db_utils.update_data('project',
                                'assets',
                                ('postroll', postroll),
                                ('id', asset_id)):
        success = 0
    return success


def get_asset_data_by_string(string, column='*'):
    """
    Retrieve asset data from the 'assets' table in the 'project' database 
    by matching a specific string value in the 'string' column.

    Args:
        string (str): The value to search for in the 'string' column.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary representing the first matching asset row if found, 
                      or None if no matching asset is found.

    Logs:
        Logs an error message if no matching asset is found.
    """
    asset_rows = db_utils.get_row_by_column_data('project',
                                                 'assets',
                                                 ('string', string),
                                                 column)
    if not asset_rows or len(asset_rows) < 1:
        logger.error("Asset not found")
        return
    return asset_rows[0]


def add_asset_preview(asset_id):
    """
    Adds an asset preview entry to the 'assets_preview' table in the database.

    This function creates a new row in the 'assets_preview' table with the 
    specified asset ID. The 'manual_override' and 'preview_path' fields are 
    set to None by default. If the row creation is successful, the function 
    logs the operation and returns the ID of the newly created asset preview. 
    If the operation fails, it returns None.

    Args:
        asset_id (int): The ID of the asset for which the preview is being added.

    Returns:
        int or None: The ID of the newly created asset preview if successful, 
        otherwise None.
    """
    asset_preview_id = db_utils.create_row('project',
                                           'assets_preview',
                                           ('manual_override',
                                            'preview_path',
                                            'asset_id'),
                                           (None,
                                            None,
                                            asset_id))
    if not asset_preview_id:
        return
    logger.info(f"Asset preview added to project")
    return asset_preview_id


def get_all_assets_preview(column='*'):
    """
    Retrieve all rows from the 'assets_preview' table in the 'project' database.

    Args:
        column (str): The column(s) to retrieve from the table. Defaults to '*', 
                      which selects all columns.

    Returns:
        list: A list of rows retrieved from the 'assets_preview' table.
    """
    assets_preview_rows = db_utils.get_rows('project',
                                            'assets_preview',
                                            column)
    return assets_preview_rows


def modify_asset_preview(asset_id, preview_path):
    """
    Update the preview path of an asset in the project database.

    This function modifies the preview path of a specific asset identified
    by its asset ID in the 'project' database table. If the update is
    successful, it logs a debug message and returns 1. If the update fails,
    the function returns without performing any further actions.

    Args:
        asset_id (int): The unique identifier of the asset to be updated.
        preview_path (str): The new file path for the asset's preview.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise None.
    """
    if not db_utils.update_data('project',
                                'assets_preview',
                                ('preview_path', preview_path),
                                ('asset_id', asset_id)):
        return
    logger.debug('Asset preview modified')
    return 1


def remove_asset_preview(asset_id):
    """
    Removes the preview of an asset from the project database.

    This function deletes the row corresponding to the given asset ID
    from the 'assets_preview' table in the 'project' database. If the
    deletion is successful, it logs an informational message and returns 1.
    If the deletion fails, the function exits without performing further actions.

    Args:
        asset_id (int): The unique identifier of the asset whose preview
                        is to be removed.

    Returns:
        int or None: Returns 1 if the asset preview is successfully removed,
                     otherwise returns None.
    """
    if not db_utils.delete_row('project',
                               'assets_preview',
                               asset_id,
                               'asset_id'):
        return
    logger.info(f"Asset preview removed from project")
    return 1


def modify_asset_manual_preview(asset_id, preview_path):
    """
    Updates the manual preview of an asset in the project database.

    This function modifies the preview of a specific asset by updating the
    'manual_override' field in the 'assets_preview' table of the 'project' database.
    If the update operation fails, the function returns without making any changes.

    Args:
        asset_id (int): The unique identifier of the asset to be updated.
        preview_path (str): The file path to the new preview image.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.

    Logs:
        Logs a debug message indicating that the asset preview was modified
        if the update operation is successful.
    """
    if not db_utils.update_data('project',
                                'assets_preview',
                                ('manual_override', preview_path),
                                ('asset_id', asset_id)):
        return
    logger.debug('Asset preview modified')
    return 1


def get_all_assets(column='*'):
    """
    Retrieve all asset records from the 'assets' table in the 'project' database.

    Args:
        column (str): The specific column(s) to retrieve from the table. 
                      Defaults to '*' to select all columns.

    Returns:
        list: A list of rows representing the assets retrieved from the database.
    """
    assets_rows = db_utils.get_rows('project',
                                    'assets',
                                    column)
    return assets_rows


def get_all_sequence_assets(column='*'):
    """
    Retrieves all sequence assets from the database.

    This function fetches all assets associated with the "sequences" domain
    by first obtaining the domain ID for "sequences" and then retrieving
    the IDs of its child categories. It then collects all assets belonging
    to these categories.

    Args:
        column (str): The column(s) to retrieve for each asset. Defaults to '*'.

    Returns:
        list: A list of assets belonging to the "sequences" domain.
    """
    domain_id = get_domain_by_name('sequences', 'id')
    categories_ids = get_domain_childs(domain_id, 'id')
    assets_rows = []
    for category_id in categories_ids:
        assets_rows += (get_category_childs(category_id))
    return assets_rows


def remove_asset(asset_id, force=0):
    """
    Removes an asset from the project, including its associated stages and preview.

    Args:
        asset_id (int): The unique identifier of the asset to be removed.
        force (int, optional): If set to a non-zero value, forces the removal 
            regardless of user permissions. Defaults to 0.

    Returns:
        int: Returns 1 if the asset was successfully removed.

    Notes:
        - If `force` is not set, the function checks if the user has admin 
          permissions before proceeding.
        - All child stages of the asset are recursively removed.
        - Logs a warning if the asset could not be removed from the database.
        - Logs an info message upon successful removal.
    """
    if not force:
        if not repository.is_admin():
            return
    for stage_id in get_asset_childs(asset_id, 'id'):
        remove_stage(stage_id, force)
    remove_asset_preview(asset_id)
    if not db_utils.delete_row('project', 'assets', asset_id):
        logger.warning(f"Asset NOT removed from project")
    logger.info(f"Asset removed from project")
    return 1


def get_asset_childs(asset_id, column='*'):
    """
    Retrieve child stages of a given asset from the 'project' database table.

    Args:
        asset_id (int): The ID of the asset whose child stages are to be retrieved.
        column (str, optional): The specific column(s) to retrieve from the database. 
                                Defaults to '*' to retrieve all columns.

    Returns:
        list: A list of rows representing the child stages of the specified asset.
    """
    stages_rows = db_utils.get_row_by_column_data('project',
                                                  'stages',
                                                  ('asset_id', asset_id),
                                                  column)
    return stages_rows


def get_asset_child_by_name(asset_id, stage_name, column='*', ignore_warning=False):
    """
    Retrieve a specific child stage of an asset by its name.

    This function queries the 'project' database table to find a stage
    associated with a given asset ID and stage name. If no matching stage
    is found, it either logs an error or silently returns, depending on
    the `ignore_warning` flag.

    Args:
        asset_id (int): The unique identifier of the asset.
        stage_name (str): The name of the stage to retrieve.
        column (str, optional): The database column(s) to retrieve. Defaults to '*'.
        ignore_warning (bool, optional): If True, suppresses the error log when
            no stage is found. Defaults to False.

    Returns:
        dict or None: A dictionary representing the first matching stage row
        if found, or None if no match is found and `ignore_warning` is True.

    Logs:
        Logs an error message if no stage is found and `ignore_warning` is False.
    """
    stages_rows = db_utils.get_row_by_multiple_data('project',
                                                    'stages',
                                                    ('asset_id', 'name'),
                                                    (asset_id, stage_name),
                                                    column)
    if stages_rows is None or len(stages_rows) < 1:
        if ignore_warning:
            return
        logger.error("Stage not found")
        return
    return stages_rows[0]


def get_asset_data(asset_id, colmun='*'):
    """
    Retrieve asset data from the database based on the given asset ID.

    Args:
        asset_id (int): The unique identifier of the asset to retrieve.
        colmun (str, optional): The column(s) to retrieve from the database. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary containing the asset data if found, or None if the asset 
                      is not found.

    Logs:
        Logs an error message if the asset is not found in the database.
    """
    assets_rows = db_utils.get_row_by_column_data('project',
                                                  'assets',
                                                  ('id', asset_id),
                                                  colmun)
    if assets_rows is None or len(assets_rows) < 1:
        logger.error("Asset not found")
        return
    return assets_rows[0]


def add_stage(name, asset_id):
    """
    Adds a new stage to the project if it does not already exist.
    This function checks if a stage with the given name and asset ID already exists
    in the database. If it does not exist, it creates a new stage entry in the
    database with the provided details and associated metadata.
    Args:
        name (str): The name of the stage to be added.
        asset_id (int): The ID of the asset associated with the stage.
    Returns:
        int or None: The ID of the newly created stage if successful, or None if
        the stage already exists or the creation fails.
    Raises:
        None: This function does not raise any exceptions directly.
    Side Effects:
        - Logs a warning if the stage already exists.
        - Logs an informational message when a stage is successfully added.
        - Interacts with the database to check existence and create a new stage.
    Notes:
        - The function constructs a string representation of the stage using
          domain, category, asset, and stage names.
        - The stage is initialized with default values for state, assignment,
          work time, estimated time, progress, priority, and note.
    """
    if (db_utils.check_existence_by_multiple_data('project',
                                                  'stages',
                                                  ('name', 'asset_id'),
                                                  (name, asset_id))):
        logger.warning(f"{name} already exists")
        return
    asset_row = get_asset_data(asset_id)
    category_row = get_category_data(asset_row['category_id'])
    domain_name = get_domain_data(category_row['domain_id'], 'name')
    string_asset = f"{domain_name}/{category_row['name']}/{asset_row['name']}/{name}"

    category_id = category_row['id']
    domain_id = category_row['domain_id']
    stage_id = db_utils.create_row('project',
                                   'stages',
                                   ('name',
                                    'creation_time',
                                    'creation_user',
                                    'state',
                                    'assignment',
                                    'work_time',
                                    'estimated_time',
                                    'start_date',
                                    'progress',
                                    'string',
                                    'asset_id',
                                    'domain_id',
                                    'priority',
                                    'note'),
                                   (name,
                                    time.time(),
                                    environment.get_user(),
                                    'todo',
                                    environment.get_user(),
                                    0.0,
                                    3,
                                    time.time(),
                                    0.0,
                                    string_asset,
                                    asset_id,
                                    domain_id,
                                    'normal',
                                    ''))
    if not stage_id:
        return
    logger.info(f"Stage {name} added to project")
    return stage_id


def get_stage_data_by_string(string, column='*'):
    """
    Retrieve stage data from the 'stages' table in the 'project' database 
    based on a specific string value.

    Args:
        string (str): The string value to search for in the 'string' column.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary representing the first row of the result if found, 
                      or None if no matching stage is found.

    Logs:
        Logs an error message if no stage is found.
    """
    stage_rows = db_utils.get_row_by_column_data('project',
                                                 'stages',
                                                 ('string', string),
                                                 column)
    if stage_rows is None or len(stage_rows) < 1:
        logger.error("Stage not found")
        return
    return stage_rows[0]


def get_all_stages(column='*'):
    """
    Retrieve all stages from the 'stages' table in the 'project' database.

    Args:
        column (str): The column(s) to retrieve from the 'stages' table. 
                      Defaults to '*' to select all columns.

    Returns:
        list: A list of rows representing the stages retrieved from the database.
    """
    stages_rows = db_utils.get_rows('project',
                                    'stages',
                                    column)
    return stages_rows


def remove_stage(stage_id, force=0):
    """
    Removes a stage from the project, including its associated variants, exports, 
    and asset tracking events.

    Args:
        stage_id (int): The unique identifier of the stage to be removed.
        force (int, optional): If set to a non-zero value, forces the removal 
            without checking for admin privileges. Defaults to 0.

    Returns:
        int: Returns 1 if the stage is successfully removed.

    Notes:
        - If `force` is not set, the function checks if the user has admin 
          privileges before proceeding.
        - The function recursively removes all child variants, exports, and 
          asset tracking events associated with the stage.
        - Logs a message indicating whether the stage was successfully removed 
          or not.
    """
    if not force:
        if not repository.is_admin():
            return
    for variant_id in get_stage_childs(stage_id, 'id'):
        remove_variant(variant_id, force)
    for export_id in get_stage_export_childs(stage_id, 'id'):
        remove_export(export_id, force)
    for asset_tracking_event_id in get_asset_tracking_events(stage_id, 'id'):
        remove_asset_tracking_event(asset_tracking_event_id)
    if not db_utils.delete_row('project', 'stages', stage_id):
        logger.info(f"Stage NOT removed from project")
    logger.info(f"Stage removed from project")
    return 1


def set_stage_default_variant(stage_id, variant_id):
    """
    Updates the default variant for a given stage in the project database.

    This function modifies the 'default_variant_id' field of a specific stage
    in the 'stages' table of the 'project' database. If the update operation
    fails, the function returns without making any changes. On success, it logs
    a debug message indicating that the default variant has been modified.

    Args:
        stage_id (int): The unique identifier of the stage to update.
        variant_id (int): The unique identifier of the variant to set as default.

    Returns:
        int or None: Returns 1 if the operation is successful, otherwise None.
    """
    if not db_utils.update_data('project',
                                'stages',
                                ('default_variant_id', variant_id),
                                ('id', stage_id)):
        return
    logger.debug('Default variant modified')
    return 1


def get_stage_data(stage_id, column='*'):
    """
    Retrieve data for a specific stage from the 'stages' table in the 'project' database.

    Args:
        stage_id (int): The ID of the stage to retrieve.
        column (str, optional): The column(s) to retrieve. Defaults to '*', which retrieves all columns.

    Returns:
        dict or None: A dictionary representing the first row of the stage data if found, 
                      or None if the stage is not found.

    Logs:
        Logs an error message if the stage is not found.
    """
    stages_rows = db_utils.get_row_by_column_data('project',
                                                  'stages',
                                                  ('id', stage_id),
                                                  column)
    if stages_rows is None or len(stages_rows) < 1:
        logger.error("Stage not found")
        return
    return stages_rows[0]


def get_stage_childs(stage_id, column='*'):
    """
    Retrieve child variants associated with a specific stage ID from the database.

    Args:
        stage_id (int): The ID of the stage for which child variants are to be retrieved.
        column (str, optional): The specific column(s) to retrieve from the database. 
                                Defaults to '*' to retrieve all columns.

    Returns:
        list: A list of rows representing the child variants for the given stage ID.
    """
    variants_rows = db_utils.get_row_by_column_data('project',
                                                    'variants',
                                                    ('stage_id', stage_id),
                                                    column)
    return variants_rows


def get_stage_child_by_name(stage_id, variant_name, column='*'):
    """
    Retrieve a specific variant row from the 'variants' table in the 'project' database 
    based on the given stage ID and variant name.

    Args:
        stage_id (int): The ID of the stage to filter the variants.
        variant_name (str): The name of the variant to retrieve.
        column (str, optional): The specific column(s) to retrieve from the database. 
                                Defaults to '*' (all columns).

    Returns:
        dict or None: The first matching variant row as a dictionary if found, 
                      or None if no matching row is found.

    Logs:
        Logs an error message if no matching variant is found.
    """
    variants_rows = db_utils.get_row_by_multiple_data('project',
                                                      'variants',
                                                      ('stage_id', 'name'),
                                                      (stage_id, variant_name),
                                                      column)
    if variants_rows is None or len(variants_rows) < 1:
        logger.error("Variant not found")
        return
    return variants_rows[0]


def add_variant(name, stage_id, comment):
    """
    Adds a new variant to the project database.

    This function creates a new variant entry in the database if the provided
    variant name and stage ID combination does not already exist. It constructs
    a string representation of the variant's hierarchy and stores it along with
    other metadata.

    Args:
        name (str): The name of the variant to be added. Must not be empty or None.
        stage_id (int): The ID of the stage to which the variant belongs.
        comment (str): A comment or description for the variant.

    Returns:
        int: The ID of the newly created variant if successful.
        None: If the variant already exists or if the creation fails.

    Logs:
        - A warning if the variant name is invalid or if the variant already exists.
        - An info message upon successful creation of the variant.
    """
    if name == '' or name is None:
        logger.warning(f"Please provide a valid variant name")
        return
    if (db_utils.check_existence_by_multiple_data('project',
                                                  'variants',
                                                  ('name', 'stage_id'),
                                                  (name, stage_id))):
        logger.warning(f"{name} already exists")
        return
    stage_row = get_stage_data(stage_id)
    asset_row = get_asset_data(stage_row['asset_id'])
    category_row = get_category_data(asset_row['category_id'])
    domain_name = get_domain_data(category_row['domain_id'], 'name')
    string_asset = f"{domain_name}/{category_row['name']}/{asset_row['name']}/{stage_row['name']}/{name}"
    variant_id = db_utils.create_row('project',
                                     'variants',
                                     ('name',
                                      'creation_time',
                                      'creation_user',
                                      'comment',
                                      'default_work_env_id',
                                      'string',
                                      'stage_id'),
                                     (name,
                                      time.time(),
                                      environment.get_user(),
                                      comment,
                                      None,
                                      string_asset,
                                      stage_id))
    if not variant_id:
        return
    logger.info(f"Variant {name} added to project")
    return variant_id


def get_variant_data_by_string(string, column='*'):
    """
    Retrieve variant data from the 'variants' table in the 'project' database 
    based on a specific string value.

    Args:
        string (str): The string value to search for in the 'string' column.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary representing the first row of the matching variant 
                      data if found, or None if no matching data is found.

    Logs:
        Logs an error message if no matching variant is found.
    """
    variant_rows = db_utils.get_row_by_column_data('project',
                                                   'variants',
                                                   ('string', string),
                                                   column)
    if variant_rows is None or len(variant_rows) < 1:
        logger.error("Variant not found")
        return
    return variant_rows[0]


def get_variant_by_name(stage_id, name, column='*'):
    """
    Retrieve a variant from the 'variants' table in the 'project' database 
    by matching the specified stage ID and name.

    Args:
        stage_id (int): The ID of the stage to filter the variants.
        name (str): The name of the variant to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        Any: The first row of the matching variant if found, or None if no match is found.

    Logs:
        Logs a debug message if no variant is found.
    """
    variant_row = db_utils.get_row_by_multiple_data('project',
                                                    'variants',
                                                    ('name', 'stage_id'),
                                                    (name, stage_id),
                                                    column)
    if variant_row is None or len(variant_row) < 1:
        logger.debug("Variant not found")
        return
    return variant_row[0]


def get_all_variants(column='*'):
    """
    Retrieve all variant rows from the 'variants' table in the 'project' database.

    Args:
        column (str): The column(s) to retrieve from the 'variants' table. 
                      Defaults to '*' to select all columns.

    Returns:
        list: A list of rows from the 'variants' table based on the specified column(s).
    """
    variants_rows = db_utils.get_rows('project',
                                      'variants',
                                      column)
    return variants_rows


def search_variant_by_column_data(data_tuple, column='*'):
    """
    Searches for variant rows in the 'variants' table of the 'project' database
    based on partial column data.

    Args:
        data_tuple (tuple): A tuple containing the partial data to search for.
                            Typically, this includes two elements corresponding
                            to the column values to match.
        column (str, optional): The specific column(s) to retrieve from the 
                                'variants' table. Defaults to '*' (all columns).

    Returns:
        list: A list of rows from the 'variants' table that match the given 
              partial data in the specified column(s).
    """
    variants_rows = db_utils.get_row_by_column_part_data('project',
                                                         'variants',
                                                         (data_tuple[0],
                                                          data_tuple[1]),
                                                         column)
    return variants_rows


def get_variant_work_env_child_by_name(variant_id, work_env_name, column='*'):
    """
    Retrieve a specific work environment child record by its variant ID and name.

    Args:
        variant_id (int): The ID of the variant to search for.
        work_env_name (str): The name of the work environment to search for.
        column (str, optional): The specific column(s) to retrieve from the database. Defaults to '*'.

    Returns:
        dict or None: The first matching work environment record as a dictionary if found, 
                      or None if no matching record exists.

    Logs:
        Logs an error message if no matching work environment is found.
    """
    work_envs_rows = db_utils.get_row_by_multiple_data('project',
                                                       'work_envs',
                                                       ('variant_id', 'name'),
                                                       (variant_id, work_env_name),
                                                       column)
    if work_envs_rows is None or len(work_envs_rows) < 1:
        logger.error("Work env not found")
        return
    return work_envs_rows[0]


def check_work_env_existence(work_env_id):
    """
    Check if a work environment exists in the database.

    This function verifies the existence of a work environment in the 
    'work_envs' table of the 'project' database by checking for a matching ID.

    Args:
        work_env_id (int): The ID of the work environment to check.

    Returns:
        bool: True if the work environment exists, False otherwise.
    """
    return db_utils.check_existence('project', 'work_envs', 'id', work_env_id)


def remove_variant(variant_id, force=0):
    """
    Removes a variant from the project, along with its associated work environments,
    videos, and updates to related stages. The removal process can be forced or
    restricted based on user permissions.

    Args:
        variant_id (int): The unique identifier of the variant to be removed.
        force (int, optional): If set to a non-zero value, forces the removal
            regardless of user permissions. Defaults to 0.

    Returns:
        int: Returns 1 if the variant is successfully removed.

    Notes:
        - If `force` is not set and the user is not an admin, the function will
          terminate without performing any action.
        - Associated work environments and videos are removed recursively.
        - Stages referencing the variant as their default are updated to remove
          the reference.
        - Logs a warning if the variant could not be removed from the database.
        - Logs an info message upon successful removal.
    """
    if not force:
        if not repository.is_admin():
            return
    for work_env_id in get_variant_work_envs_childs(variant_id, 'id'):
        remove_work_env(work_env_id, force)
    for video_id in get_videos(variant_id, 'id'):
        remove_video(video_id)
    for stage_id in db_utils.get_row_by_column_data('project',
                                                    'stages',
                                                    ('default_variant_id',
                                                     variant_id),
                                                    'id'):
        db_utils.update_data('project',
                             'stages',
                             ('default_variant_id', None),
                             ('id', stage_id))
    if not db_utils.delete_row('project', 'variants', variant_id):
        logger.warning(f"Variant NOT removed from project")
    logger.info(f"Variant removed from project")
    return 1


def get_variant_data(variant_id, column='*'):
    """
    Retrieve data for a specific variant from the 'variants' table in the 'project' database.

    Args:
        variant_id (int): The ID of the variant to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' (all columns).

    Returns:
        dict or None: A dictionary containing the data for the specified variant if found,
                      or None if the variant is not found.

    Logs:
        Logs an error message if the variant is not found.
    """
    variants_rows = db_utils.get_row_by_column_data('project',
                                                    'variants',
                                                    ('id', variant_id),
                                                    column)
    if variants_rows is None or len(variants_rows) < 1:
        logger.error("Variant not found")
        return
    return variants_rows[0]


def set_variant_data(variant_id, column, data):
    """
    Updates the data of a specific variant in the 'variants' table of the 'project' database.

    Args:
        variant_id (int): The unique identifier of the variant to be updated.
        column (str): The name of the column to be updated.
        data (Any): The new data to be set in the specified column.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.

    Logs:
        Logs a debug message indicating that the variant was modified if the update is successful.
    """
    if not db_utils.update_data('project',
                                'variants',
                                (column, data),
                                ('id', variant_id)):
        return
    logger.debug('Variant modified')
    return 1


def set_stage_data(stage_id, column, data):
    """
    Updates a specific column of a stage in the 'stages' table of the 'project' database.

    Args:
        stage_id (int): The ID of the stage to be updated.
        column (str): The name of the column to update.
        data (Any): The new data to set for the specified column.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.

    Logs:
        Logs a debug message indicating that the stage was modified if the update is successful.
    """
    if not db_utils.update_data('project',
                                'stages',
                                (column, data),
                                ('id', stage_id)):
        return
    logger.debug('Stage modified')
    return 1


def add_asset_tracking_event(stage_id, event_type, data, comment=''):
    """
    Adds an asset tracking event to the database.

    This function creates a new row in the 'asset_tracking_events' table of the 'project' database.
    It logs the event details, including the user who created it, the event type, associated data,
    and an optional comment.

    Args:
        stage_id (int): The ID of the stage associated with the event.
        event_type (str): The type of the event being tracked.
        data (str): The data associated with the event.
        comment (str, optional): An optional comment describing the event. Defaults to an empty string.

    Returns:
        int: The ID of the newly created asset tracking event if successful.
        None: If the event creation fails.
    """
    asset_tracking_event_id = db_utils.create_row('project',
                                                  'asset_tracking_events',
                                                  ('creation_user',
                                                   'creation_time',
                                                   'event_type',
                                                   'data',
                                                   'comment',
                                                   'stage_id'),
                                                  (environment.get_user(),
                                                   time.time(),
                                                      event_type,
                                                      data,
                                                      comment,
                                                      stage_id))
    if not asset_tracking_event_id:
        return
    logger.debug("Asset tracking event added")
    return asset_tracking_event_id


def remove_asset_tracking_event(asset_tracking_event_id):
    """
    Removes an asset tracking event from the project.

    This function deletes an asset tracking event from the 'asset_tracking_events' table
    in the 'project' database. It first checks if the user has administrative privileges.
    If the user is not an admin, the function exits without performing any action.

    Args:
        asset_tracking_event_id (int): The ID of the asset tracking event to be removed.

    Returns:
        int or None: Returns 1 if the asset tracking event was successfully removed.
                     Returns None if the user is not an admin or if the deletion fails.

    Logs:
        - Logs a warning if the asset tracking event could not be removed.
        - Logs an info message if the asset tracking event was successfully removed.
    """
    if not repository.is_admin():
        return
    if not db_utils.delete_row('project', 'asset_tracking_events', asset_tracking_event_id):
        logger.warning(f"Asset tracking event NOT removed from project")
        return
    logger.info(f"Asset tracking event removed from project")
    return 1


def remove_progress_event(progress_event_id):
    """
    Removes a progress event from the project.

    This function deletes a progress event identified by its ID from the 
    'progress_events' table in the 'project' database. The operation is 
    only performed if the user has administrative privileges.

    Args:
        progress_event_id (int): The ID of the progress event to be removed.

    Returns:
        int: Returns 1 if the progress event was successfully removed.

    Logs:
        - Logs a warning if the progress event could not be removed.
        - Logs an info message when the progress event is successfully removed.
    """
    if not repository.is_admin():
        return
    if not db_utils.delete_row('project', 'progress_events', progress_event_id):
        logger.warning(f"Stage progress event NOT removed from project")
    logger.info(f"Stage progress event removed from project")
    return 1


def get_asset_tracking_event_data(asset_tracking_event_id, column='*'):
    """
    Retrieve data for a specific asset tracking event from the database.

    This function queries the 'asset_tracking_events' table in the 'project' database
    for a row matching the given asset_tracking_event_id. By default, it retrieves all
    columns, but a specific column can be requested by providing its name.

    Args:
        asset_tracking_event_id (int): The ID of the asset tracking event to retrieve.
        column (str, optional): The column(s) to retrieve from the database. Defaults to '*'.

    Returns:
        dict or None: A dictionary containing the data for the asset tracking event if found,
                      or None if no matching event is found.

    Logs:
        Logs an error message if the asset tracking event is not found.
    """
    asset_tracking_events_rows = db_utils.get_row_by_column_data('project',
                                                                 'asset_tracking_events',
                                                                 ('id', asset_tracking_event_id),
                                                                 column)
    if asset_tracking_events_rows is None or len(asset_tracking_events_rows) < 1:
        logger.error("Asset tracking event not found")
        return
    return asset_tracking_events_rows[0]


def get_asset_tracking_events(stage_id, column='*'):
    """
    Retrieve asset tracking events from the database for a specific stage.

    Args:
        stage_id (int): The ID of the stage for which to retrieve asset tracking events.
        column (str, optional): The specific column(s) to retrieve from the database. 
                                Defaults to '*' to retrieve all columns.

    Returns:
        list: A list of rows representing the asset tracking events for the given stage.
    """
    asset_tracking_events_rows = db_utils.get_row_by_column_data('project',
                                                                 'asset_tracking_events',
                                                                 ('stage_id',
                                                                  stage_id),
                                                                 column)
    return asset_tracking_events_rows


def get_all_progress_events(column='*'):
    """
    Retrieve all progress events from the 'progress_events' table in the database.

    Args:
        column (str): The column(s) to retrieve from the table. Defaults to '*', 
                      which selects all columns.

    Returns:
        list: A list of rows representing progress events, ordered by the 'id' column.
    """
    progress_events_rows = db_utils.get_rows('project',
                                             'progress_events',
                                             column, order='id')
    return progress_events_rows


def get_variant_work_envs_childs(variant_id, column='*'):
    """
    Retrieve work environment rows associated with a specific variant ID.

    This function queries the 'work_envs' table in the 'project' database
    to fetch rows where the 'variant_id' matches the provided value. By default,
    it retrieves all columns unless a specific column is specified.

    Args:
        variant_id (int): The ID of the variant to filter work environments.
        column (str, optional): The column(s) to retrieve from the table. Defaults to '*'.

    Returns:
        list: A list of rows from the 'work_envs' table that match the given variant ID.
    """
    work_envs_rows = db_utils.get_row_by_column_data('project',
                                                     'work_envs',
                                                     ('variant_id', variant_id),
                                                     column)
    return work_envs_rows


def get_work_env_variant_child_by_name(variant_id, work_env_name, column='*'):
    """
    Retrieve a specific work environment variant child by its name.

    This function queries the database to find a row in the 'work_envs' table
    that matches the given `variant_id` and `work_env_name`. If no matching
    row is found, an error is logged, and the function returns None.

    Args:
        variant_id (int): The ID of the variant to search for.
        work_env_name (str): The name of the work environment to search for.
        column (str, optional): The specific column(s) to retrieve from the 
            database. Defaults to '*' (all columns).

    Returns:
        dict or None: A dictionary representing the first matching row if found,
        or None if no match is found.
    """
    work_envs_rows = db_utils.get_row_by_multiple_data('project',
                                                       'work_envs',
                                                       ('variant_id', 'name'),
                                                       (variant_id, work_env_name),
                                                       column)
    if work_envs_rows is None or len(work_envs_rows) < 1:
        logger.error("Work env not found")
        return
    return work_envs_rows[0]


def get_stage_export_childs(stage_id, column='*'):
    """
    Retrieve export rows associated with a specific stage ID from the 'exports' table.

    Args:
        stage_id (int): The ID of the stage for which export rows are to be retrieved.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        list: A list of rows from the 'exports' table that match the given stage ID.
    """
    exports_rows = db_utils.get_row_by_column_data('project',
                                                   'exports',
                                                   ('stage_id', stage_id),
                                                   column)
    return exports_rows


def get_export_by_name(name, stage_id):
    """
    Retrieve an export record by its name and stage ID.

    This function queries the 'exports' table in the 'project' database
    to find a row that matches the given name and stage_id. If no matching
    row is found or the result is empty, an error is logged, and the function
    returns None.

    Args:
        name (str): The name of the export to retrieve.
        stage_id (int): The ID of the stage associated with the export.

    Returns:
        dict or None: The first matching export row as a dictionary if found,
                      otherwise None.
    """
    export_row = db_utils.get_row_by_multiple_data('project',
                                                   'exports',
                                                   ('name', 'stage_id'),
                                                   (name, stage_id))
    if export_row is None and len(export_row) < 1:
        logger.error("Export not found")
        return
    return export_row[0]


def get_export_data(export_id, column='*'):
    """
    Retrieve export data from the 'exports' table in the 'project' database.

    Args:
        export_id (int): The ID of the export to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary representing the first row of the export data 
                      if found, or None if no matching export is found.

    Logs:
        Logs an error message if the export is not found.
    """
    export_rows = db_utils.get_row_by_column_data('project',
                                                  'exports',
                                                  ('id', export_id),
                                                  column)
    if export_rows is None or len(export_rows) < 1:
        logger.error("Export not found")
        return
    return export_rows[0]


def get_export_childs(export_id, column='*'):
    """
    Retrieve child rows from the 'export_versions' table in the 'project' database
    that are associated with a specific export ID.

    Args:
        export_id (int): The ID of the export whose child rows are to be retrieved.
        column (str, optional): The specific column(s) to retrieve from the table.
            Defaults to '*' to retrieve all columns.

    Returns:
        list: A list of rows from the 'export_versions' table that match the given export ID.
    """
    exports_versions_rows = db_utils.get_row_by_column_data('project',
                                                            'export_versions',
                                                            ('export_id',
                                                             export_id),
                                                            column)
    return exports_versions_rows


def is_export(name, stage_id):
    """
    Check if an export exists in the 'project' database table.

    This function verifies the existence of an export entry in the 'project'
    database table by checking the 'exports' column for a match with the
    provided 'name' and 'stage_id' values.

    Args:
        name (str): The name of the export to check.
        stage_id (int): The stage ID associated with the export.

    Returns:
        bool: True if the export exists, False otherwise.
    """
    return db_utils.check_existence_by_multiple_data('project',
                                                     'exports',
                                                     ('name', 'stage_id'),
                                                     (name, stage_id))


def add_export(name, stage_id):
    """
    Adds a new export entry to the project database if it does not already exist.

    This function checks if an export with the given name and stage ID already exists
    in the database. If it does, a warning is logged, and the function returns without
    making any changes. Otherwise, it creates a new export entry in the database with
    the provided name and stage ID, along with additional metadata.

    Args:
        name (str): The name of the export to be added.
        stage_id (int): The ID of the stage associated with the export.

    Returns:
        int or None: The ID of the newly created export entry if successful, or None
        if the export could not be created or already exists.

    Logs:
        - Logs a warning if the export already exists.
        - Logs an info message when a new export is successfully added.

    Notes:
        - The function relies on several helper functions to retrieve data about
          stages, assets, categories, and domains.
        - The `string_asset` is constructed as a hierarchical path based on domain,
          category, asset, stage, and export name.
        - The `db_utils.create_row` function is used to insert the new export entry
          into the database.
    """
    if (db_utils.check_existence_by_multiple_data('project',
                                                  'exports',
                                                  ('name', 'stage_id'),
                                                  (name, stage_id))):
        logger.warning(f"{name} already exists")
        return
    # variant_row = get_variant_data(variant_id)
    stage_row = get_stage_data(stage_id)
    asset_row = get_asset_data(stage_row['asset_id'])
    category_row = get_category_data(asset_row['category_id'])
    domain_name = get_domain_data(category_row['domain_id'], 'name')
    string_asset = f"{domain_name}/{category_row['name']}/{asset_row['name']}/{stage_row['name']}/{name}"
    export_id = db_utils.create_row('project',
                                    'exports',
                                    ('name',
                                     'creation_time',
                                     'creation_user',
                                     'string',
                                     'stage_id',
                                     'default_export_version'),
                                    (name,
                                     time.time(),
                                     environment.get_user(),
                                     string_asset,
                                     stage_id,
                                     None))
    if not export_id:
        return
    logger.info(f"Export root {name} added to project")
    return export_id


def get_export_data_by_string(string, column='*'):
    """
    Retrieve export data from the 'exports' table in the 'project' database 
    based on a specific string value.

    Args:
        string (str): The string value to search for in the 'string' column.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: The first row of the export data as a dictionary if found, 
                      or None if no matching data is found.

    Logs:
        Logs an error message if no export data is found.
    """
    export_rows = db_utils.get_row_by_column_data('project',
                                                  'exports',
                                                  ('string', string),
                                                  column)
    if export_rows is None and len(export_rows) < 1:
        logger.error("Export not found")
        return
    return export_rows[0]


def remove_export(export_id, force=0):
    """
    Removes an export from the project.

    This function deletes an export and its associated child export versions 
    from the project database. It performs an admin check unless the `force` 
    parameter is set to a non-zero value.

    Args:
        export_id (int): The unique identifier of the export to be removed.
        force (int, optional): If set to a non-zero value, bypasses the admin 
            check. Defaults to 0.

    Returns:
        int or None: Returns 1 if the export is successfully removed, 
        otherwise returns None.

    Notes:
        - The function first checks if the user has admin privileges unless 
          `force` is enabled.
        - It recursively removes all child export versions associated with 
          the given export ID.
        - Logs a warning if the export could not be removed from the project.
    """
    if not force:
        if not repository.is_admin():
            return
    for export_version_id in get_export_childs(export_id, 'id'):
        remove_export_version(export_version_id, force)
    if not db_utils.delete_row('project', 'exports', export_id):
        logger.warning("Export NOT removed from project")
        return
    logger.info("Export removed from project")
    return 1


def get_export_versions(export_id, column='*'):
    """
    Retrieve export version information from the 'project' database table.

    Args:
        export_id (int): The unique identifier for the export whose versions are to be retrieved.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' (all columns).

    Returns:
        list: A list of rows containing the export version information based on the specified column(s).
    """
    export_versions_rows = db_utils.get_row_by_column_data('project',
                                                           'export_versions',
                                                           ('export_id',
                                                            export_id),
                                                           column)
    return export_versions_rows


def get_export_versions_by_work_version_id(work_version_id, column='*'):
    """
    Retrieve export version records associated with a specific work version ID.

    This function queries the 'export_versions' table in the 'project' database
    to fetch rows where the 'work_version_id' matches the provided value. By default,
    all columns are retrieved, but a specific column can be selected by passing its name.

    Args:
        work_version_id (int): The ID of the work version to filter export versions.
        column (str, optional): The column(s) to retrieve from the table. Defaults to '*'.

    Returns:
        list: A list of rows matching the specified work version ID. Each row is represented
              as a dictionary or tuple, depending on the database utility implementation.
    """
    export_versions_rows = db_utils.get_row_by_column_data('project',
                                                           'export_versions',
                                                           ('work_version_id',
                                                            work_version_id),
                                                           column)
    return export_versions_rows


def get_export_versions_by_user_name(creation_user, column='*'):
    """
    Retrieve export version data for a specific user from the 'project' table.

    Args:
        creation_user (str): The username of the user whose export versions are to be retrieved.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' (all columns).

    Returns:
        list: A list of rows containing the export version data for the specified user.
    """
    export_versions_rows = db_utils.get_row_by_column_data('project',
                                                           'export_versions',
                                                           ('creation_user',
                                                            creation_user),
                                                           column)
    return export_versions_rows


def get_all_export_versions(column='*'):
    """
    Retrieve all export versions from the 'project' database table.

    Args:
        column (str): The specific column(s) to retrieve from the 'export_versions' table.
                      Defaults to '*' to retrieve all columns.

    Returns:
        list: A list of rows representing the export versions retrieved from the database.
    """
    export_versions_rows = db_utils.get_rows('project',
                                             'export_versions',
                                             column)
    return export_versions_rows


def get_default_export_version(export_id, column='*'):
    """
    Retrieves the default export version data for a given export ID.

    This function first attempts to fetch the default export version
    associated with the provided export ID. If a default export version
    exists, it retrieves the corresponding data for the specified column(s).
    If no default export version is found, it fetches the most recent export
    version data from the 'project' table based on the export ID.

    Args:
        export_id (int): The ID of the export to retrieve the version for.
        column (str, optional): The column(s) to retrieve from the export version
            data. Defaults to '*' (all columns).

    Returns:
        dict or None: The export version data as a dictionary if found, or None
        if no data is available.
    """
    default_export_version = get_export_data(
        export_id, 'default_export_version')
    if default_export_version:
        data = get_export_version_data(default_export_version, column)
    else:
        datas = db_utils.get_last_row_by_column_data('project',
                                                     'export_versions',
                                                     ('export_id', export_id),
                                                     column)
        if datas is None or datas == []:
            return
        data = datas[0]
    return data


def get_last_export_version(export_id, column='*'):
    """
    Retrieve the last export version for a given export ID from the database.

    Args:
        export_id (int or str): The unique identifier for the export.
        column (str, optional): The specific column to retrieve from the database. 
                                Defaults to '*' to retrieve all columns.

    Returns:
        Any: The value of the specified column from the last export version, 
             or None if no data is found.
    """
    datas = db_utils.get_last_row_by_column_data('project',
                                                 'export_versions',
                                                 ('export_id', export_id),
                                                 column)
    if datas is None or datas == []:
        return
    return datas[0]


def set_default_export_version(export_id, export_version_id):
    """
    Updates the default export version for a given export and propagates the change.

    This function updates the 'default_export_version' field in the 'exports' table
    for the specified export ID. If the update is successful, it triggers the 
    propagation of the auto-update and logs the modification.

    Args:
        export_id (int): The unique identifier of the export to update.
        export_version_id (int): The version ID to set as the default export version.

    Returns:
        int or None: Returns 1 if the operation is successful, otherwise None.
    """
    if not db_utils.update_data('project',
                                'exports',
                                ('default_export_version', export_version_id),
                                ('id', export_id)):
        return
    propagate_auto_update(export_id, export_version_id)
    logger.info(f'Default export version modified')
    return 1


def add_export_version(name, files, export_id, work_version_id=None, comment=''):
    """
    Adds a new export version to the project database.

    This function creates a new export version entry in the database if the provided
    export version name and export ID combination does not already exist. It constructs
    a string representation of the export version's hierarchy and stores it along with
    other metadata.

    Args:
        name (str): The name of the export version to be added. Must not be empty or None.
        files (list): A list of file paths associated with the export version.
        export_id (int): The ID of the export to which the version belongs.
        work_version_id (int, optional): The ID of the associated work version. Defaults to None.
        comment (str, optional): A comment or description for the export version. Defaults to an empty string.

    Returns:
        int: The ID of the newly created export version if successful.
        None: If the export version already exists or if the creation fails.

    Logs:
        - A warning if the export version name is invalid or if the export version already exists.
        - An info message upon successful creation of the export version.

    Notes:
        - The function checks for the existence of the export version in the database before creating it.
        - The export version's string representation is constructed using its domain, category, asset, stage, and export names.
        - If a work version is provided, additional metadata such as the software name and thumbnail path are included.
        - The function propagates auto-update changes to references after creating the export version.
    """
    # Check if the export version already exists in the database
    if (db_utils.check_existence_by_multiple_data('project',
                                                  'export_versions',
                                                  ('name', 'export_id'),
                                                  (name, export_id))):
        logger.warning(f"{name} already exists")
        return

    # Retrieve the stage ID associated with the export
    stage_id = get_export_data(export_id, 'stage_id')

    # If a work version is provided, retrieve additional metadata
    if work_version_id is not None:
        version_row = get_version_data(work_version_id)
        work_version_thumbnail = version_row['thumbnail_path']
        work_env_id = version_row['work_env_id']
        software_id = get_work_env_data(work_env_id, 'software_id')
        software = get_software_data(software_id, 'name')
    else:
        software = None
        work_version_thumbnail = None

    # Retrieve data for constructing the string representation
    export_row = get_export_data(export_id)
    stage_row = get_stage_data(export_row['stage_id'])
    asset_row = get_asset_data(stage_row['asset_id'])
    category_row = get_category_data(asset_row['category_id'])
    domain_name = get_domain_data(category_row['domain_id'], 'name')

    # Construct the string representation of the export version
    string_asset = f"{domain_name}/"
    string_asset += f"{category_row['name']}/"
    string_asset += f"{asset_row['name']}/"
    string_asset += f"{stage_row['name']}/"
    string_asset += f"{export_row['name']}/"
    string_asset += f"{name}"

    # Create a new export version row in the database
    export_version_id = db_utils.create_row('project',
                                            'export_versions',
                                            ('name',
                                             'creation_time',
                                             'creation_user',
                                             'comment',
                                             'files',
                                             'stage_id',
                                             'work_version_id',
                                             'work_version_thumbnail_path',
                                             'software',
                                             'string',
                                             'export_id'),
                                            (name,
                                             time.time(),
                                             environment.get_user(),
                                             comment,
                                             json.dumps(files),
                                             stage_id,
                                             work_version_id,
                                             work_version_thumbnail,
                                             software,
                                             string_asset,
                                             export_id))
    # Check if the export version creation was successful
    if not export_version_id:
        return

    # Log the successful addition of the export version
    logger.info(f"Export version {name} added to project")

    # Analyze the comment for tags and propagate auto-update changes
    tags.analyse_comment(comment, 'export_version', export_version_id)
    propagate_auto_update(export_id, export_version_id)

    return export_version_id


def get_export_version_data_by_string(string, column='*'):
    """
    Retrieves export version data from the 'exports_versions' table in the 'project' database
    based on a specified string value.

    Args:
        string (str): The string value to search for in the 'string' column of the table.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' (all columns).

    Returns:
        dict or None: The first row of the retrieved export version data as a dictionary if found,
                      or None if no matching data is found.

    Logs:
        Logs an error message if no export version data is found.
    """
    export_version_rows = db_utils.get_row_by_column_data('project',
                                                          'exports_versions',
                                                          ('string', string),
                                                          column)
    if export_version_rows is None or len(export_version_rows) < 1:
        logger.error("Export version not found")
        return
    return export_version_rows[0]


def propagate_auto_update(export_id, export_version_id):
    """
    Updates the export version ID for references and grouped references in the 
    project database if the provided export version ID matches the default 
    export version ID or is None.

    This function retrieves rows from the 'references_data' and 
    'grouped_references_data' tables where the export ID matches and the 
    'auto_update' flag is set to 1. It then updates the 'export_version_id' 
    for these rows to the default export version ID if they differ.

    Args:
        export_id (int): The ID of the export to process.
        export_version_id (int or None): The export version ID to check against 
            the default export version ID. If None, the function will use the 
            default export version ID.

    Returns:
        None
    """
    default_export_version_id = get_default_export_version(export_id, 'id')
    if (export_version_id == default_export_version_id) or (export_version_id is None):
        references_rows = db_utils.get_row_by_multiple_data('project',
                                                            'references_data',
                                                            ('export_id',
                                                             'auto_update'),
                                                            (export_id, 1))
        grouped_references_rows = db_utils.get_row_by_multiple_data('project',
                                                                    'grouped_references_data',
                                                                    ('export_id',
                                                                     'auto_update'),
                                                                    (export_id, 1))
        for reference_row in references_rows:
            if reference_row['export_version_id'] != default_export_version_id:
                update_reference_data(reference_row['id'],
                                      ('export_version_id', default_export_version_id))
        for grouped_reference_row in grouped_references_rows:
            if grouped_reference_row['export_version_id'] != default_export_version_id:
                update_grouped_reference_data(grouped_reference_row['id'],
                                              ('export_version_id', default_export_version_id))


def get_export_version_destinations(export_version_id, column='*'):
    """
    Retrieve rows from the 'project' table in the database where the 
    'references_data' column matches the specified export_version_id.

    Args:
        export_version_id (int): The ID of the export version to filter rows by.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' 
                                to select all columns.

    Returns:
        list: A list of rows from the 'project' table that match the given 
              export_version_id.
    """
    references_rows = db_utils.get_row_by_column_data('project',
                                                      'references_data',
                                                      ('export_version_id',
                                                       export_version_id),
                                                      column)
    return references_rows


def get_grouped_export_version_destination(export_version_id, column='*'):
    """
    Retrieves grouped reference data for a specific export version from the 'project' table.

    Args:
        export_version_id (int): The ID of the export version to retrieve data for.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', which retrieves all columns.

    Returns:
        list: A list of rows containing the grouped reference data for the specified export version.
    """
    grouped_references_rows = db_utils.get_row_by_column_data('project',
                                                              'grouped_references_data',
                                                              ('export_version_id',
                                                               export_version_id),
                                                              column)
    return grouped_references_rows


def get_export_versions_by_stage(stage_id, column='*'):
    """
    Retrieve export version data for a specific stage from the 'project' table.

    Args:
        stage_id (int): The ID of the stage for which export version data is to be retrieved.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' (all columns).

    Returns:
        list: A list of rows containing the export version data for the specified stage.
    """
    export_versions_rows = db_utils.get_row_by_column_data('project',
                                                           'export_versions',
                                                           ('stage_id', stage_id),
                                                           column)
    return export_versions_rows


def remove_export_version(export_version_id, force=0):
    """
    Removes an export version from the project.

    Args:
        export_version_id (int): The ID of the export version to be removed.
        force (int, optional): If set to a non-zero value, forces the removal 
            regardless of admin privileges. Defaults to 0.

    Returns:
        int: Returns 1 if the export version is successfully removed.

    Behavior:
        - If `force` is not set and the user is not an admin, the function exits without performing any action.
        - Retrieves the export data associated with the given export version ID.
        - If the export version is the default for the export, it unsets the default export version.
        - Removes references and grouped references associated with the export version.
        - Deletes the export version from the database.
        - Logs warnings if the export version could not be removed and logs info upon successful removal.
    """
    if not force:
        if not repository.is_admin():
            return
    export_row = get_export_data(
        get_export_version_data(export_version_id, 'export_id'))
    if export_row['default_export_version'] == export_version_id:
        set_default_export_version(export_row['id'], None)
    for reference_id in get_export_version_destinations(export_version_id, 'id'):
        # remove_reference(reference_id)
        lower_or_remove_reference(reference_id)
    for grouped_reference_id in get_grouped_export_version_destination(export_version_id, 'id'):
        remove_grouped_reference(grouped_reference_id)
    if not db_utils.delete_row('project', 'export_versions', export_version_id):
        logger.warning("Export version NOT removed from project")
    logger.info("Export version removed from project")
    return 1


def search_export_version(data_to_search, variant_id=None, column_to_search='name', column='*'):
    """
    Searches for export version records in the 'export_versions' table of the 'project' database.

    Args:
        data_to_search (str): The value to search for in the specified column.
        variant_id (Optional[Any]): The variant ID to filter the search by. If None, the search is not filtered by variant ID.
        column_to_search (str): The column name to search within. Defaults to 'name'.
        column (str): The column(s) to retrieve from the database. Defaults to '*' (all columns).

    Returns:
        Any: The rows retrieved from the database that match the search criteria.
    """
    if variant_id:
        export_versions_rows = db_utils.get_row_by_column_part_data_and_data('project',
                                                                             'export_versions',
                                                                             (column_to_search,
                                                                              data_to_search),
                                                                             ('variant_id',
                                                                              variant_id),
                                                                             column)
    else:
        export_versions_rows = db_utils.get_row_by_column_part_data('project',
                                                                    'export_versions',
                                                                    (column_to_search,
                                                                     data_to_search),
                                                                    column)
    return export_versions_rows


def get_export_version_data(export_version_id, column='*'):
    """
    Retrieve data for a specific export version from the 'export_versions' table.

    Args:
        export_version_id (int): The ID of the export version to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary representing the first row of the export version data 
                      if found, or None if no matching data is found.

    Logs:
        Logs an error message if the export version is not found.
    """
    export_versions_rows = db_utils.get_row_by_column_data('project',
                                                           'export_versions',
                                                           ('id', export_version_id),
                                                           column)
    if export_versions_rows is None or len(export_versions_rows) < 1:
        logger.error("Export version not found")
        return
    return export_versions_rows[0]


def update_export_version_data(export_version_id, data_tuple):
    """
    Updates the data of a specific export version in the 'export_versions' table of the 'project' database.

    Args:
        export_version_id (int): The ID of the export version to update.
        data_tuple (tuple): A tuple containing the data to update in the export version.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    return db_utils.update_data('project',
                                'export_versions',
                                data_tuple,
                                ('id', export_version_id))


def modify_export_version_comment(export_version_id, comment):
    """
    Modifies the comment of an export version if the current user is the creator of the export version.

    Args:
        export_version_id (int): The unique identifier of the export version to be modified.
        comment (str): The new comment to be set for the export version.

    Returns:
        int or None: Returns 1 if the comment was successfully modified, None otherwise.

    Logs:
        - Logs a warning if the current user is not the creator of the export version.
        - Logs an info message if the comment is successfully modified.

    Notes:
        - The function checks if the current user is the creator of the export version before allowing the modification.
        - If the database update fails, the function returns without making any changes.
    """
    if environment.get_user() != get_export_version_data(export_version_id, 'creation_user'):
        logger.warning("You did not created this file, modification forbidden")
        return
    if not db_utils.update_data('project',
                                'export_versions',
                                ('comment', comment),
                                ('id', export_version_id)):
        return
    logger.info('Export version comment modified')
    return 1


def modify_video_comment(video_id, comment):
    """
    Modifies the comment of a video in the database if the current user is the creator of the video.

    Args:
        video_id (int): The unique identifier of the video whose comment is to be modified.
        comment (str): The new comment to be set for the video.

    Returns:
        int or None: Returns 1 if the comment was successfully modified. Returns None if the modification
        is forbidden or if the database update operation fails.

    Logs:
        - Logs a warning if the current user is not the creator of the video.
        - Logs an informational message if the comment is successfully modified.
    """
    if environment.get_user() != get_video_data(video_id, 'creation_user'):
        logger.warning("You did not created this file, modification forbidden")
        return
    if not db_utils.update_data('project',
                                'videos',
                                ('comment', comment),
                                ('id', video_id)):
        return
    logger.info('Video comment modified')
    return 1


def add_work_env(name, software_id, variant_id, export_extension=None):
    """
    Adds a new work environment to the project database.
    This function creates a new work environment entry in the database if it 
    does not already exist. It constructs a string representation of the 
    work environment based on its associated domain, category, asset, stage, 
    and variant data. If the work environment is successfully created, its 
    ID is returned.
    Args:
        name (str): The name of the work environment to be added.
        software_id (int): The ID of the software associated with the work environment.
        variant_id (int): The ID of the variant associated with the work environment.
        export_extension (str, optional): The file extension for exports. Defaults to None.
    Returns:
        int or None: The ID of the newly created work environment if successful, 
                     or None if the creation failed or the work environment already exists.
    Logs:
        - A warning if the work environment already exists.
        - An info message if the work environment is successfully added.
    """
    if (db_utils.check_existence_by_multiple_data('project',
                                                  'work_envs',
                                                  ('name', 'variant_id'),
                                                  (name, variant_id))):
        logger.warning(f"{name} already exists")
        return
    variant_row = get_variant_data(variant_id)
    stage_row = get_stage_data(variant_row['stage_id'])
    asset_row = get_asset_data(stage_row['asset_id'])
    category_row = get_category_data(asset_row['category_id'])
    domain_name = get_domain_data(category_row['domain_id'], 'name')
    string_asset = f"{domain_name}/{category_row['name']}/{asset_row['name']}/{stage_row['name']}/{variant_row['name']}/{name}"

    work_env_id = db_utils.create_row('project',
                                      'work_envs',
                                      ('name',
                                       'creation_time',
                                       'creation_user',
                                       'variant_id',
                                       'lock_id',
                                       'export_extension',
                                       'work_time',
                                       'string',
                                       'software_id'),
                                      (name,
                                       time.time(),
                                          environment.get_user(),
                                          variant_id,
                                          None,
                                          export_extension,
                                          0.0,
                                          string_asset,
                                          software_id))
    if not work_env_id:
        return
    logger.info(f"Work env {name} added to project")
    return work_env_id


def get_work_env_data_by_string(string, column='*'):
    """
    Retrieve work environment data from the database based on a given string.

    This function queries the 'work_envs' table in the 'project' database
    for rows where the 'string' column matches the provided string. It 
    returns the first matching row or logs an error if no matches are found.

    Args:
        string (str): The string value to search for in the 'string' column.
        column (str, optional): The specific column(s) to retrieve from the 
            database. Defaults to '*' (all columns).

    Returns:
        dict or None: A dictionary representing the first matching row if 
        found, or None if no matches are found.

    Logs:
        Logs an error message if no matching rows are found.
    """
    work_env_rows = db_utils.get_row_by_column_data('project',
                                                    'work_envs',
                                                    ('string', string),
                                                    column)
    if work_env_rows is None or len(work_env_rows) < 1:
        logger.error("Work env not found")
        return
    return work_env_rows[0]


def create_reference(work_env_id, export_version_id, namespace, count=None, auto_update=0, activated=1):
    """
    Creates a reference entry in the database for a given work environment and export version.

    Args:
        work_env_id (int): The ID of the work environment where the reference will be created.
        export_version_id (int): The ID of the export version to associate with the reference.
        namespace (str): The namespace for the reference.
        count (int, optional): An optional count value for the reference. Defaults to None.
        auto_update (int, optional): Flag indicating whether the reference should auto-update (1 for True, 0 for False). Defaults to 0.
        activated (int, optional): Flag indicating whether the reference is activated (1 for True, 0 for False). Defaults to 1.

    Returns:
        int or None: The ID of the created reference if successful, or None if the creation failed or the namespace already exists.

    Logs:
        - A warning if the namespace already exists in the database.
        - An info message if the reference is successfully created.
    """
    export_id = get_export_version_data(export_version_id, 'export_id')
    stage_name = get_stage_data(get_export_data(export_id, 'stage_id'),
                                'name')
    if (db_utils.check_existence_by_multiple_data('project',
                                                  'references_data',
                                                  ('namespace', 'work_env_id'),
                                                  (namespace, work_env_id))):
        logger.warning(f"{namespace} already exists")
        return
    reference_id = db_utils.create_row('project',
                                       'references_data',
                                       ('creation_time',
                                        'creation_user',
                                        'namespace',
                                        'count',
                                        'stage',
                                        'work_env_id',
                                        'export_id',
                                        'export_version_id',
                                        'auto_update',
                                        'activated'),
                                       (time.time(),
                                        environment.get_user(),
                                        namespace,
                                        count,
                                        stage_name,
                                        work_env_id,
                                        export_id,
                                        export_version_id,
                                        auto_update,
                                        activated))
    if not reference_id:
        return
    logger.info(f"Reference created")
    return reference_id


def lower_or_remove_reference(reference_id):
    """
    Adjusts the export version of a reference or removes the reference if no valid export version exists.

    This function retrieves the reference data associated with the given `reference_id`. It then determines
    the export version associated with the reference and attempts to lower it to the previous export version
    in the list. If the previous export version is not valid, it tries to move to the next export version.
    If neither is valid, the reference is removed.

    Args:
        reference_id (int): The unique identifier of the reference to be adjusted or removed.

    Returns:
        int: Always returns 1 after processing the reference.

    Behavior:
        - If the reference data cannot be found, the function exits without making changes.
        - If the reference's export version can be lowered to a valid previous version, it updates the reference.
        - If the reference's export version can be moved to a valid next version, it updates the reference.
        - If no valid export version exists, the reference is removed.
    """
    reference_row = get_reference_data(reference_id)
    if not reference_row:
        return
    export_version_row = get_export_version_data(
        reference_row['export_version_id'])
    export_versions = get_export_childs(reference_row['export_id'])
    index = export_versions.index(export_version_row)
    if index - 1 in range(0, len(export_versions)-1):
        update_reference_data(
            reference_id, ('export_version_id', export_versions[index-1]['id']))
    elif index + 1 in range(0, len(export_versions)-1):
        update_reference_data(
            reference_id, ('export_version_id', export_versions[index+1]['id']))
    else:
        remove_reference(reference_id)
    return 1


def remove_reference(reference_id):
    """
    Removes a reference from the 'references_data' table in the 'project' database.

    Args:
        reference_id (int): The ID of the reference to be removed.

    Returns:
        int: Returns 1 if the reference was successfully deleted.
        None: Returns None if the deletion failed.

    Logs:
        - Logs a warning if the reference could not be deleted.
        - Logs an info message if the reference was successfully deleted.
    """
    if not db_utils.delete_row('project', 'references_data', reference_id):
        logger.warning("Reference NOT deleted")
        return
    logger.info("Reference deleted")
    return 1


def get_references(work_env_id, column='*'):
    """
    Retrieve reference data from the 'project' table based on the given work environment ID.

    Args:
        work_env_id (int): The ID of the work environment to filter the references.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        list: A list of rows containing the reference data that matches the given work environment ID.
    """
    references_rows = db_utils.get_row_by_column_data('project',
                                                      'references_data',
                                                      ('work_env_id',
                                                       work_env_id),
                                                      column)
    return references_rows


def get_references_by_export_version(export_version_id, column='*'):
    """
    Retrieve references data from the 'project' table based on the specified export version ID.

    Args:
        export_version_id (int): The ID of the export version to filter the references data.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' (all columns).

    Returns:
        list: A list of rows containing the references data matching the given export version ID.
    """
    references_rows = db_utils.get_row_by_column_data('project',
                                                      'references_data',
                                                      ('export_version_id',
                                                       export_version_id),
                                                      column)
    return references_rows


def get_grouped_references_by_export_version(export_version_id, column='*'):
    """
    Retrieve grouped references data from the 'project' table based on the specified export version ID.

    Args:
        export_version_id (int): The ID of the export version to filter the grouped references data.
        column (str, optional): The specific column(s) to retrieve from the database. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        list: A list of rows containing the grouped references data that match the given export version ID.
    """
    references_rows = db_utils.get_row_by_column_data('project',
                                                      'grouped_references_data',
                                                      ('export_version_id',
                                                       export_version_id),
                                                      column)
    return references_rows


def get_references_by_export(export_id, column='*'):
    """
    Retrieve references data from the 'project' database table based on the given export ID.

    Args:
        export_id (str or int): The ID of the export to filter the references data.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        list or None: A list of rows matching the export ID, or None if no matching rows are found.
    """
    references_rows = db_utils.get_row_by_column_data('project',
                                                      'references_data',
                                                      ('export_id', export_id),
                                                      column)
    return references_rows


def get_reference_data(reference_id, column='*'):
    """
    Retrieve reference data from the 'references_data' table in the 'project' database.

    Args:
        reference_id (int): The ID of the reference to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary representing the first row of the reference data if found, 
                      or None if no matching reference is found.

    Logs:
        Logs an error message if the reference is not found.
    """
    reference_rows = db_utils.get_row_by_column_data('project',
                                                     'references_data',
                                                     ('id', reference_id),
                                                     column)
    if reference_rows is None or len(reference_rows) < 1:
        logger.error("Reference not found")
        return
    return reference_rows[0]


def get_reference_by_namespace(work_env_id, namespace, column='*'):
    """
    Retrieve a reference row from the 'references_data' table in the 'project' database
    based on the provided work environment ID and namespace.

    Args:
        work_env_id (int): The ID of the work environment to filter by.
        namespace (str): The namespace to filter by.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: The first matching reference row as a dictionary if found, 
                      or None if no matching row exists.

    Logs:
        Logs an error message if no reference is found.
    """
    reference_rows = db_utils.get_row_by_multiple_data('project',
                                                       'references_data',
                                                       ('work_env_id',
                                                        'namespace'),
                                                       (work_env_id, namespace),
                                                       column)
    if reference_rows is None or len(reference_rows) < 1:
        logger.error("Reference not found")
        return
    return reference_rows[0]


def modify_reference_export(reference_id, export_id):
    """
    Updates the reference data with the provided export ID and its default export version ID.

    This function retrieves the default export version ID for the given export ID and updates
    the reference data with both the export ID and the export version ID. If the export version
    ID is not found, no updates are performed.

    Args:
        reference_id (int): The ID of the reference to be updated.
        export_id (int): The ID of the export to associate with the reference.

    Returns:
        int: Always returns 1 to indicate the function executed successfully.
    """
    export_version_id = get_default_export_version(export_id, 'id')
    if export_version_id:
        update_reference_data(reference_id, ('export_id', export_id))
        update_reference_data(
            reference_id, ('export_version_id', export_version_id))
    return 1


def modify_reference_auto_update(reference_id, auto_update):
    """
    Modifies the auto-update setting for a reference and updates related data.

    If the `auto_update` parameter is set to True, it enables auto-update for 
    the reference by setting it to 1. Additionally, it retrieves the export ID 
    and default export version ID associated with the reference. If a valid 
    export version ID is found, it updates the reference with this version ID.

    Args:
        reference_id (int): The unique identifier of the reference to modify.
        auto_update (bool): A flag indicating whether to enable or disable 
            auto-update for the reference.

    Returns:
        int: Always returns 1, indicating successful execution.
    """
    if auto_update:
        auto_update = 1
    update_reference_data(reference_id, ('auto_update', auto_update))
    if auto_update:
        export_id = get_reference_data(reference_id, 'export_id')
        export_version_id = get_default_export_version(export_id, 'id')
        if not export_version_id:
            return 1
        update_reference_data(
            reference_id, ('export_version_id', export_version_id))
    return 1


def modify_reference_activation(reference_id, activated):
    """
    Modify the activation status of a reference.

    This function updates the activation status of a reference in the database.
    If the `activated` parameter is True, it converts it to an integer value of 1
    before passing it to the update function.

    Args:
        reference_id (int): The unique identifier of the reference to be updated.
        activated (bool): The desired activation status. True for activated, False for deactivated.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    if activated:
        activated = 1
    return update_reference_data(reference_id, ('activated', activated))


def update_reference_data(reference_id, data_tuple):
    """
    Updates the reference data in the 'project' database table.

    This function updates a record in the 'references_data' table of the 
    'project' database using the provided reference ID and data tuple. 
    If the update is successful, it logs a message indicating that the 
    reference was modified. If the update fails, the function returns 
    without performing any further actions.

    Args:
        reference_id (int): The ID of the reference to be updated.
        data_tuple (tuple): A tuple containing the data to update the reference with.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise None.
    """
    if not db_utils.update_data('project',
                                'references_data',
                                data_tuple,
                                ('id', reference_id)):
        return
    logger.info('Reference modified')
    return 1


def update_referenced_group_data(referenced_group_id, data_tuple):
    """
    Updates the data of a referenced group in the 'project' database.

    This function modifies the 'referenced_groups_data' table in the database
    for the specified referenced group ID with the provided data tuple. If the
    update is successful, it logs the modification and returns 1. Otherwise,
    it returns None.

    Args:
        referenced_group_id (int): The ID of the referenced group to update.
        data_tuple (tuple): The data to update in the referenced group.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise None.
    """
    if not db_utils.update_data('project',
                                'referenced_groups_data',
                                data_tuple,
                                ('id', referenced_group_id)):
        return
    logger.info('Referenced group modified')
    return 1


def update_reference(reference_id, export_version_id):
    """
    Updates the export version ID of a reference in the 'references_data' table.

    This function modifies the 'export_version_id' field of a specific reference
    identified by its reference ID in the 'project' database. If the update is
    successful, it logs a message indicating that the reference was modified.

    Args:
        reference_id (int): The ID of the reference to be updated.
        export_version_id (int): The new export version ID to be set.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.
    """
    if not db_utils.update_data('project',
                                'references_data',
                                ('export_version_id', export_version_id),
                                ('id', reference_id)):
        return
    logger.info('Reference modified')
    return 1


def remove_work_env(work_env_id, force=0):
    """
    Remove a work environment from the project.

    This function deletes a work environment and its associated data, such as 
    versions, references, and referenced groups, from the project database. 
    It also ensures that only administrators can perform this action unless 
    the `force` parameter is set.

    Args:
        work_env_id (int): The ID of the work environment to be removed.
        force (int, optional): If set to a non-zero value, bypasses the 
            administrator check. Defaults to 0.

    Returns:
        int or None: Returns 1 if the work environment is successfully removed. 
        Returns None if the operation is not performed or fails.

    Notes:
        - The function checks if the user is an administrator unless `force` 
          is enabled.
        - Associated data such as versions, references, and referenced groups 
          are removed before deleting the work environment.
        - Logs warnings if the deletion fails and logs info upon successful 
          removal.
    """
    if not force:
        if not repository.is_admin():
            return
    for version_id in get_work_versions(work_env_id, 'id'):
        remove_version(version_id)
    for reference_id in get_references(work_env_id, 'id'):
        remove_reference(reference_id)
    for referenced_group_id in get_referenced_groups(work_env_id, 'id'):
        remove_referenced_group(referenced_group_id)
    if not db_utils.delete_row('project', 'work_envs', work_env_id):
        logger.warning("Work env NOT removed from project")
        return
    logger.info("Work env removed from project")
    return 1


def get_work_versions(work_env_id, column='*'):
    """
    Retrieve version rows from the 'versions' table in the 'project' database 
    based on the specified work environment ID.

    Args:
        work_env_id (int): The ID of the work environment to filter the versions.
        column (str, optional): The column(s) to retrieve from the database. 
                                Defaults to '*' (all columns).

    Returns:
        list: A list of rows matching the specified work environment ID, 
              with the selected columns.
    """
    versions_rows = db_utils.get_row_by_column_data('project',
                                                    'versions',
                                                    ('work_env_id',
                                                     work_env_id),
                                                    column)
    return versions_rows


def get_work_version_by_name(work_env_id, name, column='*'):
    """
    Retrieve a specific version row from the 'versions' table in the 'project' database
    based on the provided work environment ID and version name.

    Args:
        work_env_id (int): The ID of the work environment to filter by.
        name (str): The name of the version to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        tuple or None: The first matching version row as a tuple if found, or None 
                       if no matching row exists.

    Logs:
        Logs a debug message if no matching version is found.
    """
    version_row = db_utils.get_row_by_multiple_data('project',
                                                    'versions',
                                                    ('name', 'work_env_id'),
                                                    (name, work_env_id),
                                                    column)
    if version_row is None or len(version_row) < 1:
        logger.debug("Version not found")
        return
    return version_row[0]


def get_work_versions_by_user(creation_user, column='*'):
    """
    Retrieve work versions from the 'versions' table in the 'project' database
    filtered by the specified creation user.

    Args:
        creation_user (str): The username of the user whose work versions are to be retrieved.
        column (str, optional): The specific column(s) to retrieve from the table. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        list: A list of rows from the 'versions' table that match the specified creation user.
    """
    versions_rows = db_utils.get_row_by_column_data('project',
                                                    'versions',
                                                    ('creation_user',
                                                     creation_user),
                                                    column)
    return versions_rows


def get_all_work_versions(column='*'):
    """
    Retrieve all work versions from the 'project' database table.

    Args:
        column (str): The specific column(s) to retrieve from the 'versions' table.
                      Defaults to '*' to select all columns.

    Returns:
        list: A list of rows representing the work versions retrieved from the database.
    """
    work_versions_rows = db_utils.get_rows('project',
                                           'versions',
                                           column)
    return work_versions_rows


def get_last_work_version(work_env_id, column='*'):
    """
    Retrieve the last work version for a given work environment ID.

    This function queries the 'project' database table to fetch the last row
    from the 'versions' column that matches the specified work environment ID.
    By default, it retrieves all columns unless a specific column is provided.

    Args:
        work_env_id (int): The ID of the work environment to filter by.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*'.

    Returns:
        Any: The last row(s) matching the criteria from the 'versions' column.
    """
    versions_rows = db_utils.get_last_row_by_column_data('project',
                                                         'versions',
                                                         ('work_env_id',
                                                          work_env_id),
                                                         column)
    return versions_rows


def get_last_video_version(variant_id, column='*'):
    """
    Retrieve the last video version for a given variant ID from the database.

    Args:
        variant_id (int): The ID of the variant to query.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        list: A list of rows representing the last video version(s) for the given variant ID.
    """
    videos_rows = db_utils.get_last_row_by_column_data('project',
                                                       'videos',
                                                       ('variant_id', variant_id),
                                                       column)
    return videos_rows


def get_work_env_data(work_env_id, column='*'):
    """
    Retrieve data for a specific work environment from the database.

    Args:
        work_env_id (int): The ID of the work environment to retrieve.
        column (str, optional): The specific column(s) to retrieve from the database.
            Defaults to '*' to retrieve all columns.

    Returns:
        dict or None: A dictionary containing the data for the specified work environment
            if found, or None if no matching work environment is found.

    Logs:
        Logs an error message if the specified work environment is not found.
    """
    work_env_rows = db_utils.get_row_by_column_data('project',
                                                    'work_envs',
                                                    ('id', work_env_id),
                                                    column)
    if work_env_rows is None or len(work_env_rows) < 1:
        logger.error("Work env not found")
        return
    return work_env_rows[0]


def get_all_work_envs(column='*'):
    """
    Retrieve all work environment records from the 'work_envs' table in the 'project' database.

    Args:
        column (str): The specific column(s) to retrieve from the table. Defaults to '*', 
                      which retrieves all columns.

    Returns:
        list: A list of rows representing the work environment records.
    """
    work_env_rows = db_utils.get_rows('project',
                                      'work_envs',
                                      column)
    return work_env_rows


def get_work_env_by_name(variant_id, name, column='*'):
    """
    Retrieve a work environment row from the database by its name and variant ID.

    Args:
        variant_id (int): The ID of the variant to filter the work environment.
        name (str): The name of the work environment to retrieve.
        column (str, optional): The specific column(s) to retrieve from the database. 
                                Defaults to '*' (all columns).

    Returns:
        dict or None: The first row of the work environment matching the criteria 
                      as a dictionary if found, or None if no match is found.

    Logs:
        Logs a debug message if the work environment is not found.
    """
    work_env_row = db_utils.get_row_by_multiple_data('project',
                                                     'work_envs',
                                                     ('name', 'variant_id'),
                                                     (name, variant_id),
                                                     column)
    if work_env_row is None or len(work_env_row) < 1:
        logger.debug("Work env not found")
        return
    return work_env_row[0]


def set_work_env_extension(work_env_id, export_extension):
    """
    Updates the export extension for a specific work environment in the database.

    Args:
        work_env_id (int): The unique identifier of the work environment to update.
        export_extension (str): The new export extension to set for the work environment.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.

    Logs:
        Logs an informational message if the export extension is successfully modified.
    """
    if not db_utils.update_data('project',
                                'work_envs',
                                ('export_extension', export_extension),
                                ('id', work_env_id)):
        return
    logger.info(f'Work env export extension modified')
    return 1


def get_user_locks(user_id, column='*'):
    """
    Retrieve rows from the 'work_envs' table in the 'project' database where the 
    specified user has locks.

    Args:
        user_id (int): The ID of the user whose locks are to be retrieved.
        column (str, optional): The column(s) to retrieve from the table. Defaults to '*'.

    Returns:
        list: A list of rows from the 'work_envs' table that match the specified user lock criteria.
    """
    work_env_rows = db_utils.get_row_by_column_data('project',
                                                    'work_envs',
                                                    ('lock_id', user_id),
                                                    column)
    return work_env_rows


def get_lock(work_env_id):
    """
    Checks if the specified work environment is locked by another user and logs a warning if so.

    Args:
        work_env_id (int): The ID of the work environment to check.

    Returns:
        str or None: The username of the user who has locked the work environment, 
                     or None if the environment is not locked or is locked by the current user.

    Behavior:
        - Retrieves the current user's ID.
        - Checks if the work environment is locked and if the lock belongs to the current user.
        - If the environment is locked by another user, logs a warning with the username of the locking user.
    """
    current_user_id = repository.get_user_row_by_name(
        environment.get_user(), 'id')
    work_env_lock_id = get_work_env_data(work_env_id, 'lock_id')
    if (not work_env_lock_id) or (work_env_lock_id == current_user_id):
        return
    lock_user_name = repository.get_user_data(work_env_lock_id, 'user_name')
    logger.warning(f"Work env locked by {lock_user_name}")
    return lock_user_name


def set_work_env_lock(work_env_id, lock=1, force=0):
    """
    Sets or removes a lock on a work environment.

    Args:
        work_env_id (int): The ID of the work environment to lock or unlock.
        lock (int, optional): Indicates whether to lock (1) or unlock (0) the work environment. Defaults to 1 (lock).
        force (int, optional): If set to 1, forces the lock/unlock operation regardless of the current state. Defaults to 0.

    Returns:
        int or None: Returns 1 if the operation is successful, otherwise returns None.

    Behavior:
        - If `lock` is set to 1, the function attempts to lock the work environment by associating it with the current user's ID.
        - If `lock` is set to 0, the function removes the lock by setting the associated user ID to None.
        - If `force` is not set and the work environment is already locked, the function exits without making changes.
        - Logs an informational message indicating whether the work environment was locked or unlocked.
    """
    if lock:
        user_id = repository.get_user_row_by_name(environment.get_user(), 'id')
    else:
        user_id = None
    if not force:
        if get_lock(work_env_id) and not force:
            return
    if not db_utils.update_data('project',
                                'work_envs',
                                ('lock_id', user_id),
                                ('id', work_env_id)):
        return
    if user_id:
        logger.info(f'Work env locked')
    else:
        logger.info(f'Work env unlocked')
    return 1


def unlock_all():
    """
    Unlocks all work environments locked by the current user.

    This function retrieves the current user's ID, fetches all work environment
    IDs locked by the user, and unlocks each of them by setting their lock status
    to 0.

    Returns:
        int: Always returns 1 to indicate successful execution.
    """
    user_id = repository.get_user_row_by_name(environment.get_user(), 'id')
    work_env_ids = get_user_locks(user_id, 'id')
    for work_env_id in work_env_ids:
        set_work_env_lock(work_env_id, 0)
    return 1


def toggle_lock(work_env_id):
    """
    Toggles the lock state of a work environment.

    If the work environment is not locked, it locks it for the current user.
    If the work environment is locked by the current user, it unlocks it.
    If the work environment is locked by another user, logs a warning with the
    name of the user who has locked it.

    Args:
        work_env_id (int): The ID of the work environment to toggle the lock for.

    Returns:
        None or result of `set_work_env_lock`:
            - If the lock is toggled, returns the result of `set_work_env_lock`.
            - If the work environment is locked by another user, returns None.
    """
    current_user_id = repository.get_user_row_by_name(
        environment.get_user(), 'id')
    lock_id = get_work_env_data(work_env_id, 'lock_id')
    if lock_id == None:
        return set_work_env_lock(work_env_id)
    elif lock_id == current_user_id:
        return set_work_env_lock(work_env_id, 0)
    lock_user_name = repository.get_user_data(lock_id, 'user_name')
    logger.warning(f"Work env locked by {lock_user_name}")
    return


def add_work_time(work_env_id, time_to_add):
    """
    Updates the work time for a specific work environment by adding the specified time.

    Args:
        work_env_id (int): The unique identifier of the work environment.
        time_to_add (int): The amount of time to add to the current work time.

    Returns:
        bool: True if the update was successful, False otherwise.

    Raises:
        KeyError: If the 'work_time' key is not found in the work environment data.
        Exception: If the database update operation fails.

    Notes:
        This function retrieves the current work time for the specified work environment,
        adds the provided time to it, and updates the database with the new value.
    """
    work_env_row = get_work_env_data(work_env_id)
    work_time = work_env_row['work_time']
    new_work_time = work_time + time_to_add
    return db_utils.update_data('project',
                                'work_envs',
                                ('work_time', new_work_time),
                                ('id', work_env_id))


def add_stage_work_time(stage_id, time_to_add):
    """
    Updates the work time of a specific stage by adding the specified time.

    Args:
        stage_id (int): The unique identifier of the stage to update.
        time_to_add (int): The amount of time to add to the stage's current work time.

    Returns:
        bool: True if the update was successful, False otherwise.

    Raises:
        KeyError: If the 'work_time' key is not found in the stage data.
        Exception: If the database update operation fails.

    Notes:
        This function retrieves the current work time of the specified stage,
        adds the provided time to it, and updates the database with the new value.
    """
    stage_row = get_stage_data(stage_id)
    work_time = stage_row['work_time']
    new_work_time = work_time + time_to_add
    return db_utils.update_data('project',
                                'stages',
                                ('work_time', new_work_time),
                                ('id', stage_id))


def update_stage_progress(stage_id):
    """
    Updates the progress of a specific stage in the project.

    This function retrieves the current state of the stage using its ID. If the 
    stage is marked as 'done' or 'omit', the progress is set to 100. Otherwise, 
    the progress is set to 0. If the calculated progress matches the current 
    progress stored in the database, no update is performed. Otherwise, the 
    progress value is updated in the database.

    Args:
        stage_id (int): The unique identifier of the stage to update.

    Returns:
        bool: True if the database update was successful, False otherwise, or 
              None if no update was necessary.
    """
    stage_row = get_stage_data(stage_id)
    if stage_row['state'] == 'done' or stage_row['state'] == 'omit':
        progress = 100
    else:
        progress = 0
    if progress == stage_row['progress']:
        return
    return db_utils.update_data('project',
                                'stages',
                                ('progress', progress),
                                ('id', stage_id))


def add_progress_event(type, name, datas_dic):
    """
    Adds a progress event to the 'progress_events' table in the 'project' database.

    Args:
        type (str): The type of the progress event.
        name (str): The name of the progress event.
        datas_dic (dict): A dictionary containing additional data related to the event.

    Returns:
        int: The ID of the newly created row in the 'progress_events' table.

    Notes:
        - The function uses the current time to generate the creation time and day.
        - The `tools.convert_time` function is used to convert the current time into a day and hour format.
        - The `db_utils.create_row` function is used to insert the event into the database.
    """
    day, hour = tools.convert_time(time.time())
    return db_utils.create_row('project',
                               'progress_events',
                               ('creation_time',
                                'day',
                                'type',
                                'name',
                                'datas_dic'),
                               (time.time(),
                                day,
                                type,
                                name,
                                datas_dic))


def update_progress_event(progress_event_id, data_tuple):
    """
    Updates a progress event in the 'progress_events' table of the 'project' database.

    Args:
        progress_event_id (int): The unique identifier of the progress event to update.
        data_tuple (tuple): A tuple containing the data to update in the progress event.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    return db_utils.update_data('project',
                                'progress_events',
                                data_tuple,
                                ('id', progress_event_id))


def update_progress_events(set_values):
    """
    Updates the 'progress_events' field in the 'project' table with the provided values.

    Args:
        set_values (list): A list of dictionaries containing the data to update. 
                           Each dictionary should specify the fields and their new values.

    Returns:
        None or result of the update operation:
            - Returns None if the input list is empty.
            - Otherwise, returns the result of the database update operation.
    """
    if len(set_values) == 0:
        return
    return db_utils.update_multiple_data('project',
                                         'progress_events',
                                         set_values)


def add_version(name, file_path, work_env_id, comment='', screenshot_path=None, thumbnail_path=None):
    """
    Adds a new version entry to the project database.

    This function creates a new version record in the database for a given 
    work environment. It checks for the existence of a version with the 
    same name and work environment ID before proceeding. If the version 
    already exists, a warning is logged, and the function returns without 
    making any changes.

    Args:
        name (str): The name of the version to be added.
        file_path (str): The file path associated with the version.
        work_env_id (int): The ID of the work environment where the version belongs.
        comment (str, optional): A comment or description for the version. Defaults to an empty string.
        screenshot_path (str, optional): The file path to a screenshot associated with the version. Defaults to None.
        thumbnail_path (str, optional): The file path to a thumbnail image associated with the version. Defaults to None.

    Returns:
        int or None: The ID of the newly created version if successful, or None if the version 
        already exists or if the creation fails.

    Raises:
        None: This function does not raise any exceptions directly.

    Side Effects:
        - Logs a warning if the version already exists.
        - Logs an informational message upon successful creation of the version.
        - Analyzes the comment for tags and associates them with the created version.

    Notes:
        - The function constructs a hierarchical string representation of the version's 
          location in the project structure based on domain, category, asset, stage, 
          variant, and work environment data.
        - The function interacts with multiple database tables and utility functions 
          to retrieve and store data.
    """
    if (db_utils.check_existence_by_multiple_data('project',
                                                  'versions',
                                                  ('name', 'work_env_id'),
                                                  (name, work_env_id))):
        logger.warning(f"Version {name} already exists")
        return
    work_env_row = get_work_env_data(work_env_id)
    variant_row = get_variant_data(work_env_row['variant_id'])
    stage_row = get_stage_data(variant_row['stage_id'])
    asset_row = get_asset_data(stage_row['asset_id'])
    category_row = get_category_data(asset_row['category_id'])
    domain_name = get_domain_data(category_row['domain_id'], 'name')
    string_asset = f"{domain_name}/"
    string_asset += f"{category_row['name']}/"
    string_asset += f"{asset_row['name']}/"
    string_asset += f"{stage_row['name']}/"
    string_asset += f"{variant_row['name']}/"
    string_asset += f"{work_env_row['name']}/"
    string_asset += f"{name}"
    version_id = db_utils.create_row('project',
                                     'versions',
                                     ('name',
                                      'creation_time',
                                      'creation_user',
                                      'comment',
                                      'file_path',
                                      'screenshot_path',
                                      'thumbnail_path',
                                      'string',
                                      'work_env_id'),
                                     (name,
                                      time.time(),
                                      environment.get_user(),
                                      comment,
                                      file_path,
                                      screenshot_path,
                                      thumbnail_path,
                                      string_asset,
                                      work_env_id))
    if not version_id:
        return
    tags.analyse_comment(comment, 'work_version', version_id)
    logger.info(f"Version {name} added to project")
    return version_id


def add_video(name, file_path, variant_id, comment='', thumbnail_path=None):
    """
    Adds a video entry to the project database.

    This function checks if a video with the given name and variant ID already exists.
    If it does, a warning is logged, and the function exits without adding the video.
    Otherwise, it retrieves related data for the variant, stage, asset, category, 
    and domain, and creates a new video entry in the database.

    Args:
        name (str): The name of the video.
        file_path (str): The file path of the video.
        variant_id (int): The ID of the variant associated with the video.
        comment (str, optional): A comment or description for the video. Defaults to an empty string.
        thumbnail_path (str, optional): The file path of the video's thumbnail. Defaults to None.

    Returns:
        int or None: The ID of the newly created video entry if successful, or None if the video 
        could not be added.
    """
    if (db_utils.check_existence_by_multiple_data('project',
                                                  'videos',
                                                  ('name', 'variant_id'),
                                                  (name, variant_id))):
        logger.warning(f"Video {name} already exists")
        return
    variant_row = get_variant_data(variant_id)
    stage_row = get_stage_data(variant_row['stage_id'])
    asset_row = get_asset_data(stage_row['asset_id'])
    category_row = get_category_data(asset_row['category_id'])
    domain_name = get_domain_data(category_row['domain_id'], 'name')
    video_id = db_utils.create_row('project',
                                   'videos',
                                   ('name',
                                    'creation_time',
                                    'creation_user',
                                    'comment',
                                    'file_path',
                                    'thumbnail_path',
                                    'variant_id'),
                                   (name,
                                    time.time(),
                                    environment.get_user(),
                                    comment,
                                    file_path,
                                    thumbnail_path,
                                    variant_id))
    if not video_id:
        return
    logger.info(f"Video {name} added to project")
    return video_id


def get_video_data(video_id, column='*'):
    """
    Retrieve video data from the database based on the given video ID.

    Args:
        video_id (int): The unique identifier of the video to retrieve.
        column (str, optional): The specific column(s) to retrieve from the database.
                                Defaults to '*' to retrieve all columns.

    Returns:
        dict or None: A dictionary containing the video data if found, or None if the video
                      is not found or an error occurs.

    Logs:
        Logs an error message if the video is not found in the database.
    """
    videos_rows = db_utils.get_row_by_column_data('project',
                                                  'videos',
                                                  ('id', video_id),
                                                  column)
    if videos_rows is None or len(videos_rows) < 1:
        logger.error("Video not found")
        return
    return videos_rows[0]


def get_work_version_data_by_string(string, column='*'):
    """
    Retrieve work version data from the 'project' database table based on a given string.

    Args:
        string (str): The string value to search for in the 'versions' table.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' (all columns).

    Returns:
        dict or None: The first row of the matching work version data as a dictionary if found,
                      or None if no matching data is found.

    Logs:
        Logs an error message if no matching work version is found.
    """
    work_version_rows = db_utils.get_row_by_column_data('project',
                                                        'versions',
                                                        ('string', string),
                                                        column)
    if work_version_rows is None or len(work_version_rows) < 1:
        logger.error("Work version not found")
        return
    return work_version_rows[0]


def get_version_data(version_id, column='*'):
    """
    Retrieve version data from the 'versions' table in the 'project' database.

    Args:
        version_id (int): The ID of the version to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary representing the first row of the retrieved version data 
                      if found, or None if no matching version is found.

    Logs:
        Logs an error message if the version is not found.
    """
    work_version_rows = db_utils.get_row_by_column_data('project',
                                                        'versions',
                                                        ('id', version_id),
                                                        column)
    if work_version_rows is None or len(work_version_rows) < 1:
        logger.error("Version not found")
        return
    return work_version_rows[0]


def modify_version_comment(version_id, comment=''):
    """
    Modifies the comment of a specific version in the project database.

    Args:
        version_id (int): The ID of the version whose comment is to be modified.
        comment (str, optional): The new comment to set for the version. Defaults to an empty string.

    Returns:
        int or None: Returns 1 if the comment was successfully modified, 
                     otherwise returns None if the modification is forbidden or fails.

    Logs:
        - Logs a warning if the current user is not the creator of the version or if the update fails.
        - Logs an info message if the comment is successfully modified.
    """
    if environment.get_user() != get_version_data(version_id, 'creation_user'):
        logger.warning("You did not created this file, modification forbidden")
        return
    if not db_utils.update_data('project',
                                'versions',
                                ('comment', comment),
                                ('id', version_id)):
        logger.warning('Version NOT comment modified')
        return
    logger.info('Version comment modified')
    return 1


def modify_version_screen(version_id, screenshot_path, thumbnail_path):
    """
    Updates the screenshot and thumbnail paths for a specific version in the database.

    Args:
        version_id (int): The unique identifier of the version to be updated.
        screenshot_path (str): The new file path for the version's screenshot.
        thumbnail_path (str): The new file path for the version's thumbnail.

    Returns:
        bool: True if both the screenshot and thumbnail paths were successfully updated, 
              False otherwise.

    Logs:
        Logs an informational message if both updates are successful.
    """
    screenshot_path_success = db_utils.update_data('project',
                                                   'versions',
                                                   ('screenshot_path',
                                                    screenshot_path),
                                                   ('id', version_id))
    thumbnail_path_success = db_utils.update_data('project',
                                                  'versions',
                                                  ('thumbnail_path',
                                                   thumbnail_path),
                                                  ('id', version_id))
    if screenshot_path_success*thumbnail_path_success:
        logger.info('Version screen modified')
    return screenshot_path_success*thumbnail_path_success


def remove_version(version_id, force=0):
    """
    Removes a version from the project.

    Args:
        version_id (int): The ID of the version to be removed.
        force (int, optional): If set to a non-zero value, forces the removal 
            regardless of admin privileges. Defaults to 0.

    Returns:
        int: Returns 1 if the version is successfully removed.

    Behavior:
        - If `force` is not set and the user is not an admin, the function 
          exits without performing any action.
        - For each export version associated with the given work version ID:
            - Updates the export version's `work_version_id` and `software` 
              fields to `None`.
        - Attempts to delete the version from the database table `project.versions`.
        - Logs a warning if the version could not be removed.
        - Logs an info message upon successful removal.
    """
    if not force:
        if not repository.is_admin():
            return
    for export_version_id in get_export_versions_by_work_version_id(version_id, 'id'):
        update_export_version_data(
            export_version_id, ('work_version_id', None))
        update_export_version_data(export_version_id, ('software', None))
    if not db_utils.delete_row('project', 'versions', version_id):
        logger.warning(f"Version NOT removed from project")
    logger.info(f"Version removed from project")
    return 1


def search_version(data_to_search, work_env_id=None, column_to_search='name', column='*'):
    """
    Searches for version information in the 'versions' table of the 'project' database.

    Args:
        data_to_search (str): The value to search for in the specified column.
        work_env_id (int, optional): The ID of the work environment to filter the search. 
                                     If None, the search is not filtered by work environment. Defaults to None.
        column_to_search (str, optional): The column name to search within. Defaults to 'name'.
        column (str, optional): The column(s) to retrieve from the database. Defaults to '*'.

    Returns:
        list: A list of rows matching the search criteria. Each row is represented as a dictionary or tuple, 
              depending on the database utility implementation.
    """
    if work_env_id:
        versions_rows = db_utils.get_row_by_column_part_data_and_data('project',
                                                                      'versions',
                                                                      (column_to_search,
                                                                       data_to_search),
                                                                      ('work_env_id',
                                                                          work_env_id),
                                                                      column)
    else:
        versions_rows = db_utils.get_row_by_column_part_data('project',
                                                             'versions',
                                                             (column_to_search,
                                                              data_to_search),
                                                             column)
    return versions_rows


def add_playlist(name, data, thumbnail_path=None):
    """
    Adds a new playlist to the project database.

    This function creates a new playlist entry in the database if the playlist
    name is safe and does not already exist. It logs appropriate warnings or
    information messages based on the operation's success or failure.

    Args:
        name (str): The name of the playlist to be added. Must pass safety checks.
        data (str): The data associated with the playlist.
        thumbnail_path (str, optional): The file path to the playlist's thumbnail. Defaults to None.

    Returns:
        int or None: The ID of the newly created playlist if successful, or None if the operation fails.
    """
    if not tools.is_safe(name):
        return
    if db_utils.check_existence('project',
                                'playlists',
                                'name',
                                name):
        logger.warning(f"Playlist {name} already exists")
        return
    playlist_id = db_utils.create_row('project',
                                      'playlists',
                                      ('name',
                                       'creation_time',
                                       'creation_user',
                                       'data',
                                       'thumbnail_path',
                                       'last_save_user',
                                       'last_Save_time'),
                                      (name,
                                       time.time(),
                                          environment.get_user(),
                                          data,
                                          thumbnail_path,
                                          environment.get_user(),
                                          time.time()))
    if not playlist_id:
        return
    logger.info(f"Playlist {name} added to project")
    return playlist_id


def get_all_playlists(column='*'):
    """
    Retrieve all playlists from the database.

    Args:
        column (str): The specific column(s) to retrieve from the 'playlists' table.
                      Defaults to '*' to retrieve all columns.

    Returns:
        list: A list of rows representing the playlists retrieved from the database.
    """
    playlist_rows = db_utils.get_rows('project',
                                      'playlists',
                                      column)
    return playlist_rows


def remove_playlist(playlist_id):
    """
    Removes a playlist from the project database.

    This function checks if a playlist with the given ID exists in the database.
    If the playlist exists, it attempts to delete it. Logs are generated to indicate
    the success or failure of the operation.

    Args:
        playlist_id (int): The ID of the playlist to be removed.

    Returns:
        int or None: Returns 1 if the playlist was successfully removed.
                     Returns None if the playlist does not exist or if the removal fails.

    Logs:
        - Warning: If the playlist is not found or if the removal fails.
        - Info: If the playlist is successfully removed.
    """
    if not db_utils.check_existence('project',
                                    'playlists',
                                    'id',
                                    playlist_id):
        logger.warning(f"Playlist not found")
        return
    if not db_utils.delete_row('project', 'playlists', playlist_id):
        logger.warning(f"Playlist NOT removed from project")
        return
    logger.info(f"PLaylist removed from project")
    return 1


def get_playlist_data(playlist_id, column='*'):
    """
    Retrieve data for a specific playlist from the database.

    Args:
        playlist_id (int): The unique identifier of the playlist to retrieve.
        column (str, optional): The specific column(s) to retrieve from the database.
                                Defaults to '*' to retrieve all columns.

    Returns:
        dict or None: A dictionary containing the playlist data if found, or None if the playlist
                      does not exist.

    Logs:
        Logs an error message if the playlist is not found.
    """
    playlists_rows = db_utils.get_row_by_column_data('project',
                                                     'playlists',
                                                     ('id', playlist_id),
                                                     column)
    if playlists_rows is None or len(playlists_rows) < 1:
        logger.error("Playlist not found")
        return
    return playlists_rows[0]


def update_playlist_data(playlist_id, data_tuple):
    """
    Updates the data of a playlist in the database.

    This function modifies the playlist record in the 'playlists' table
    of the 'project' database using the provided playlist ID and data tuple.
    If the update operation fails, a warning is logged. If successful, 
    an informational log is created, and the function returns 1.

    Args:
        playlist_id (int): The unique identifier of the playlist to be updated.
        data_tuple (tuple): A tuple containing the data to update in the playlist.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise None.
    """
    if not db_utils.update_data('project',
                                'playlists',
                                data_tuple,
                                ('id', playlist_id)):
        logger.warning('Playlist NOT modified')
        return
    logger.info('Playlist modified')
    return 1


def add_software(name, extension, file_command, no_file_command, batch_file_command='', batch_no_file_command=''):
    """
    Adds a new software entry to the project database.

    This function registers a software with the specified attributes into the 
    'softwares' table of the project database. It performs checks to ensure 
    the software is registered and does not already exist in the project.

    Args:
        name (str): The name of the software to add.
        extension (str): The file extension associated with the software.
        file_command (str): The command to execute when a file is provided.
        no_file_command (str): The command to execute when no file is provided.
        batch_file_command (str, optional): The batch command to execute when a file is provided. Defaults to an empty string.
        batch_no_file_command (str, optional): The batch command to execute when no file is provided. Defaults to an empty string.

    Returns:
        int or None: The ID of the newly created software entry in the database 
        if successful, or None if the operation fails.

    Logs:
        - Logs a warning if the software is not registered or already exists.
        - Logs an info message when the software is successfully added.
    """
    if name not in softwares_vars._softwares_list_:
        logger.warning("Unregistered software")
        return
    if name in get_softwares_names_list():
        logger.warning(f"{name} already exists")
        return
    software_id = db_utils.create_row('project',
                                      'softwares',
                                      ('name',
                                       'extension',
                                       'path',
                                       'batch_path',
                                       'additionnal_scripts',
                                       'additionnal_env',
                                       'file_command',
                                       'no_file_command',
                                       'batch_file_command',
                                       'batch_no_file_command'),
                                      (name,
                                       extension,
                                       '',
                                       '',
                                       '',
                                       '',
                                       file_command,
                                       no_file_command,
                                       batch_file_command,
                                       batch_no_file_command))
    if not software_id:
        return
    logger.info(f"Software {name} added to project")
    return software_id


def get_softwares_names_list():
    """
    Retrieves a list of software names from the 'softwares' table in the 'project' database.

    This function queries the database using the `db_utils.get_rows` method to fetch all rows
    from the 'softwares' table in the 'project' database, specifically retrieving the 'name' column.

    Returns:
        list: A list of software names retrieved from the database.
    """
    softwares_rows = db_utils.get_rows('project', 'softwares', 'name')
    return softwares_rows


def set_software_path(software_id, path):
    """
    Updates the path of a software in the database if the provided path is valid.

    Args:
        software_id (int): The unique identifier of the software to update.
        path (str): The file path to the software executable.

    Returns:
        int or None: Returns 1 if the software path was successfully updated.
                     Returns None if the path is invalid or the update fails.

    Logs:
        - Logs a warning if the provided path is not a valid executable.
        - Logs a warning if the database update fails.
        - Logs an info message if the software path is successfully updated.
    """
    if not path_utils.isfile(path):
        logger.warning(f"{path} is not a valid executable")
        return
    if not db_utils.update_data('project',
                                'softwares',
                                ('path', path),
                                ('id', software_id)):
        logger.warning('Software path NOT modified')
        return
    logger.info('Software path modified')
    return 1


def set_software_batch_path(software_id, path):
    """
    Updates the batch path of a software in the database if the provided path is valid.

    Args:
        software_id (int): The unique identifier of the software whose batch path is to be updated.
        path (str): The file path to the software's batch executable.

    Returns:
        int or None: Returns 1 if the batch path was successfully updated, 
                     None if the path is invalid or the update operation failed.

    Logs:
        - Logs a warning if the provided path is not a valid executable.
        - Logs a warning if the database update operation fails.
        - Logs an info message if the batch path is successfully updated.
    """
    if not path_utils.isfile(path):
        logger.warning(f"{path} is not a valid executable")
        return
    if not db_utils.update_data('project',
                                'softwares',
                                ('batch_path', path),
                                ('id', software_id)):
        logger.warning('Software batch path NOT modified')
        return
    logger.info('Software batch path modified')
    return 1


def set_software_additionnal_scripts(software_id, paths_list):
    """
    Updates the additional scripts associated with a specific software in the database.

    This function modifies the 'additionnal_scripts' field for a given software ID
    in the 'project.softwares' table by storing the provided list of paths as a JSON string.

    Args:
        software_id (int): The unique identifier of the software to update.
        paths_list (list): A list of file paths to be set as additional scripts.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise None.

    Logs:
        - Logs a warning if the update fails.
        - Logs an info message if the update is successful.
    """
    if not db_utils.update_data('project',
                                'softwares',
                                ('additionnal_scripts', json.dumps(paths_list)),
                                ('id', software_id)):
        logger.warning('Additionnal script env NOT modified')
        return
    logger.info('Additionnal script env modified')
    return 1


def set_software_additionnal_env(software_id, env_dic):
    """
    Updates the additional environment variables for a specific software in the database.

    Args:
        software_id (int): The unique identifier of the software to update.
        env_dic (dict): A dictionary containing the additional environment variables to set.

    Returns:
        int or None: Returns 1 if the update was successful, otherwise None.

    Logs:
        - Logs a warning if the update fails.
        - Logs an info message if the update is successful.
    """
    if not db_utils.update_data('project',
                                'softwares',
                                ('additionnal_env', json.dumps(env_dic)),
                                ('id', software_id)):
        logger.warning('Additionnal env NOT modified')
        return
    logger.info('Additionnal env modified')
    return 1


def get_software_data(software_id, column='*'):
    """
    Retrieve software data from the 'softwares' table in the 'project' database.

    Args:
        software_id (int): The ID of the software to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary containing the software data if found, or None 
                      if no matching software is found.

    Logs:
        Logs an error message if the software is not found.
    """
    softwares_rows = db_utils.get_row_by_column_data('project',
                                                     'softwares',
                                                     ('id', software_id),
                                                     column)
    if softwares_rows is None or len(softwares_rows) < 1:
        logger.error("Software not found")
        return
    return softwares_rows[0]


def get_software_data_by_name(software_name, column='*'):
    """
    Retrieve software data from the database by its name.

    This function queries the 'softwares' table in the 'project' database
    to fetch data for a specific software identified by its name. The
    desired columns can be specified, or all columns will be retrieved
    by default.

    Args:
        software_name (str): The name of the software to search for.
        column (str, optional): The column(s) to retrieve from the database.
            Defaults to '*' (all columns).

    Returns:
        dict or None: A dictionary containing the software data if found,
            or None if no matching software is found.

    Logs:
        Logs an error message if the software is not found in the database.
    """
    softwares_rows = db_utils.get_row_by_column_data('project',
                                                     'softwares',
                                                     ('name', software_name),
                                                     column)
    if softwares_rows is None or len(softwares_rows) < 1:
        logger.error("Software not found")
        return
    return softwares_rows[0]


def create_extension_row(stage, software_id, extension):
    """
    Adds a new extension row to the 'extensions' table in the 'project' database.

    This function attempts to create a new row in the 'extensions' table with the
    provided stage, software_id, and extension values. If the row creation fails,
    a warning is logged. If successful, an informational log is created.

    Args:
        stage (str): The stage of the project to associate with the extension.
        software_id (int): The ID of the software to associate with the extension.
        extension (str): The extension to be added.

    Returns:
        int or None: Returns 1 if the extension is successfully added, otherwise None.
    """
    if not db_utils.create_row('project',
                               'extensions',
                               ('stage',
                                'software_id',
                                'extension'),
                               (stage,
                                software_id,
                                extension)):
        logger.warning("Extension not added")
        return
    logger.info("Extension added")
    return 1


def get_default_extension(stage, software_id):
    """
    Retrieves the default file extension for a given stage and software ID 
    from the database.

    Args:
        stage (str): The stage of the project (e.g., "modeling", "texturing").
        software_id (str): The identifier of the software (e.g., "maya", "blender").

    Returns:
        str: The default file extension associated with the given stage and 
             software ID, if found.
        None: If no matching extension is found, logs an error and returns None.

    Logs:
        Logs an error message if the extension is not found in the database.
    """
    export_row = db_utils.get_row_by_multiple_data('project',
                                                   'extensions',
                                                   ('stage', 'software_id'),
                                                   (stage, software_id))
    if export_row is None or len(export_row) < 1:
        logger.error("Extension not found")
        return
    return export_row[0]['extension']


def get_default_extension_row(stage, software_id, ignore_warning=False):
    """
    Retrieve the default extension row for a given stage and software ID.

    This function queries the 'project' database table for an extension row
    that matches the specified stage and software ID. If no matching row is
    found, it logs an error (unless `ignore_warning` is set to True) and 
    returns None.

    Args:
        stage (str): The stage identifier to filter the query.
        software_id (str): The software ID to filter the query.
        ignore_warning (bool, optional): If True, suppresses the error log 
            when no matching row is found. Defaults to False.

    Returns:
        dict or None: The first matching extension row as a dictionary if 
        found, otherwise None.
    """
    export_row = db_utils.get_row_by_multiple_data('project',
                                                   'extensions',
                                                   ('stage', 'software_id'),
                                                   (stage, software_id))
    if export_row is None or len(export_row) < 1:
        if not ignore_warning:
            logger.error("Extension row not found")
        return
    return export_row[0]


def set_default_extension(extension_id, extension):
    """
    Updates the default extension for a project in the database.

    This function modifies the 'extensions' field of a project in the database
    by updating the extension associated with the given extension ID. If the
    update is successful, it logs a success message and returns 1. Otherwise,
    it logs a warning indicating that the extension was not modified.

    Args:
        extension_id (int): The unique identifier of the extension to be updated.
        extension (str): The new extension value to set.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.

    Logs:
        - Logs a warning if the extension is not modified.
        - Logs an info message if the extension is successfully modified.
    """
    if not db_utils.update_data('project',
                                'extensions',
                                ('extension', extension),
                                ('id', extension_id)):
        logger.warning('Extension not modified')
        return
    logger.info('Extension modified')
    return 1


def create_settings_row(frame_rate, image_format, deadline):
    """
    Creates a new settings row in the 'project' database table if it does not already exist.

    Args:
        frame_rate (int): The frame rate to be set in the settings.
        image_format (dict): A dictionary representing the image format settings.
        deadline (str): The deadline to be set in the settings.

    Returns:
        int or None: Returns 1 if the settings row is successfully created. 
                     Returns None if the settings row already exists or if the creation fails.

    Logs:
        - Logs an error if a settings row already exists.
        - Logs a warning if the creation of the settings row fails.
        - Logs an info message if the settings row is successfully created.
    """
    if len(db_utils.get_rows('project', 'settings', 'id')) != 0:
        logger.error("Settings row already exists")
        return
    if not db_utils.create_row('project',
                               'settings',
                               ('frame_rate',
                                'image_format',
                                'deadline',
                                'users_ids'),
                               (frame_rate,
                                json.dumps(image_format),
                                deadline,
                                json.dumps([]))):
        logger.warning("Project settings not initiated")
        return
    logger.info("Project settings initiated")
    return 1


def set_frame_rate(frame_rate):
    """
    Updates the frame rate setting for the project in the database.

    This function modifies the 'frame_rate' field in the 'settings' table
    of the 'project' database. If the update is successful, it logs an
    informational message. If the update fails, it logs a warning message.

    Args:
        frame_rate (int or float): The desired frame rate to set for the project.

    Returns:
        int or None: Returns 1 if the frame rate was successfully updated,
                     otherwise returns None.
    """
    if not db_utils.update_data('project',
                                'settings',
                                ('frame_rate', frame_rate),
                                ('id', 1)):
        logger.warning('Project frame rate not modified')
        return
    logger.info('Project frame rate modified')
    return 1


def get_frame_rate():
    """
    Retrieves the frame rate from the project settings in the database.

    This function queries the 'project' table in the database for the 
    'frame_rate' value associated with the project settings (identified by id=1). 
    If the frame rate is not found or the query fails, an error is logged.

    Returns:
        float or int: The frame rate value parsed from the database, if found.
        None: If the frame rate is not found or an error occurs.
    """
    frame_rate_list = db_utils.get_row_by_column_data('project',
                                                      'settings',
                                                      ('id', 1),
                                                      'frame_rate')
    if frame_rate_list is None or len(frame_rate_list) < 1:
        logger.error("Project settings not found")
        return
    return json.loads(frame_rate_list[0])


def set_OCIO(OCIO_config_file):
    """
    Updates the OpenColorIO (OCIO) configuration file path in the project settings.

    This function modifies the 'OCIO' field in the 'settings' table of the 'project' database.
    If the update is successful, it logs a success message and returns 1. Otherwise, it logs
    a warning message indicating that the OCIO configuration was not modified.

    Args:
        OCIO_config_file (str): The file path to the OCIO configuration file.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.
    """
    if not db_utils.update_data('project',
                                'settings',
                                ('OCIO', OCIO_config_file),
                                ('id', 1)):
        logger.warning('Project OCIO not modified')
        return
    logger.info('Project OCIO modified')
    return 1


def get_OCIO():
    """
    Retrieves the OpenColorIO (OCIO) configuration from the project settings.

    This function queries the database for the OCIO configuration stored in the
    'project' table under the 'settings' column where the 'id' is 1. If no
    configuration is found or the result is empty, an error is logged.

    Returns:
        str: The OCIO configuration if found, otherwise None.
    """
    ocio_list = db_utils.get_row_by_column_data('project',
                                                'settings',
                                                ('id', 1),
                                                'OCIO')
    if ocio_list is None or len(ocio_list) < 1:
        logger.error("Project settings not found")
        return
    return ocio_list[0]


def get_mean_render_time():
    """
    Retrieves the mean render time from the project settings in the database.

    This function queries the 'project' table in the database for the 
    'mean_render_time' value associated with the project settings where 
    the 'id' is 1. If the settings are not found or the result is empty, 
    an error is logged and the function returns None.

    Returns:
        float or None: The mean render time if found, otherwise None.
    """
    mean_render_time_list = db_utils.get_row_by_column_data('project',
                                                            'settings',
                                                            ('id', 1),
                                                            'mean_render_time')
    if mean_render_time_list is None or len(mean_render_time_list) < 1:
        logger.error("Project settings not found")
        return
    return mean_render_time_list[0]


def set_mean_render_time(render_time_in_seconds):
    """
    Updates the mean render time for the project in the database.

    If the provided render time is less than or equal to 0, it defaults to 60 seconds.
    The function attempts to update the 'mean_render_time' field in the 'project' table
    under the 'settings' column for the record with an ID of 1. If the update fails,
    a warning is logged. If the update succeeds, an informational message is logged.

    Args:
        render_time_in_seconds (int): The mean render time in seconds to be set.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.
    """
    if render_time_in_seconds <= 0:
        render_time_in_seconds = 60
    if not db_utils.update_data('project',
                                'settings',
                                ('mean_render_time', render_time_in_seconds),
                                ('id', 1)):
        logger.warning('Project mean render time not modified')
        return
    logger.info('Project mean render time modified')
    return 1


def get_render_nodes_number():
    """
    Retrieves the number of render nodes from the project settings in the database.

    This function queries the 'project' table in the database for the 'render_nodes_number'
    field within the 'settings' column where the 'id' is 1. If the settings are not found
    or the result is empty, an error is logged, and the function returns None.

    Returns:
        int or None: The number of render nodes if found, otherwise None.
    """
    render_nodes_number_list = db_utils.get_row_by_column_data('project',
                                                               'settings',
                                                               ('id', 1),
                                                               'render_nodes_number')
    if render_nodes_number_list is None or len(render_nodes_number_list) < 1:
        logger.error("Project settings not found")
        return
    return render_nodes_number_list[0]


def set_render_nodes_number(render_nodes_number):
    """
    Updates the number of render nodes in the project settings.

    This function ensures that the number of render nodes is at least 1.
    It then updates the 'render_nodes_number' field in the 'project' settings
    table of the database. If the update fails, a warning is logged. If the
    update is successful, an informational message is logged.

    Args:
        render_nodes_number (int): The desired number of render nodes. Must be greater than 0.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.
    """
    if render_nodes_number <= 0:
        render_nodes_number = 1
    if not db_utils.update_data('project',
                                'settings',
                                ('render_nodes_number', render_nodes_number),
                                ('id', 1)):
        logger.warning('Project render nodes number not modified')
        return
    logger.info('Project render nodes number time modified')
    return 1


def set_image_format(image_format):
    """
    Updates the image format setting for the project in the database.

    Args:
        image_format (any): The new image format to be set. It will be serialized to JSON before being stored.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise None.

    Logs:
        - Logs a warning if the update fails.
        - Logs an info message if the update is successful.
    """
    if not db_utils.update_data('project',
                                'settings',
                                ('image_format', json.dumps(image_format)),
                                ('id', 1)):
        logger.warning('Project format not modified')
        return
    logger.info('Project format modified')
    return 1


def get_image_format():
    """
    Retrieves the image format settings from the project database.

    This function queries the 'project' table in the database for the 
    'image_format' field in the 'settings' column where the 'id' is 1. 
    If no settings are found or the result is empty, an error is logged.

    Returns:
        dict: A dictionary containing the image format settings if found.
        None: If the settings are not found or an error occurs.
    """
    image_format_list = db_utils.get_row_by_column_data('project',
                                                        'settings',
                                                        ('id', 1),
                                                        'image_format')
    if image_format_list is None or len(image_format_list) < 1:
        logger.error("Project settings not found")
        return
    return json.loads(image_format_list[0])


def set_deadline(time_float):
    """
    Updates the project deadline in the database.

    This function modifies the 'deadline' field in the 'project' table's 
    'settings' column for the project with ID 1. If the update is successful, 
    it logs a success message and returns 1. Otherwise, it logs a warning 
    message indicating that the deadline was not modified.

    Args:
        time_float (float): The new deadline value to be set, represented as a float.

    Returns:
        int or None: Returns 1 if the deadline was successfully updated, 
        otherwise returns None.
    """
    if not db_utils.update_data('project',
                                'settings',
                                ('deadline', time_float),
                                ('id', 1)):
        logger.warning('Project deadline not modified')
        return
    logger.info('Project deadline modified')
    return 1


def get_deadline():
    """
    Retrieves the project deadline from the database.

    This function queries the 'project' table in the database for the 'deadline'
    field in the 'settings' row where the 'id' is 1. If no data is found or the
    result is empty, an error is logged and the function returns None.

    Returns:
        Any: The deadline value if found, otherwise None.

    Logs:
        Logs an error message if the project settings are not found.
    """
    deadline_list = db_utils.get_row_by_column_data('project',
                                                    'settings',
                                                    ('id', 1),
                                                    'deadline')
    if deadline_list is None or len(deadline_list) < 1:
        logger.error("Project settings not found")
        return
    return deadline_list[0]


def get_users_ids_list():
    """
    Retrieves a list of user IDs from the 'project' table in the database.

    This function queries the 'project' table for the 'users_ids' column 
    where the 'id' is 1. If no data is found, it returns an empty list. 
    Otherwise, it parses the JSON-encoded string from the database into 
    a Python list and returns it.

    Returns:
        list: A list of user IDs. Returns an empty list if no data is found.
    """
    users_ids_list = db_utils.get_row_by_column_data('project',
                                                     'settings',
                                                     ('id', 1),
                                                     'users_ids')
    if users_ids_list is None:
        return []
    return json.loads(users_ids_list[0])


def add_user(user_id):
    """
    Adds a user ID to the list of users if it is not already present.

    This function retrieves the current list of user IDs, checks if the given
    user ID is already in the list, and if not, appends it to the list and
    updates the stored list of user IDs.

    Args:
        user_id (str): The ID of the user to be added.

    Returns:
        bool: True if the user list was updated successfully, or None if the
              user ID was already in the list.
    """
    users_ids_list = get_users_ids_list()
    if user_id in users_ids_list:
        return
    users_ids_list.append(user_id)
    return update_users_list(users_ids_list)


def remove_user(user_id):
    """
    Removes a user from the list of user IDs if they exist.

    Args:
        user_id (int): The ID of the user to be removed.

    Returns:
        bool: True if the user list was successfully updated, 
              None if the user ID was not found or no update was performed.

    Notes:
        - This function retrieves the current list of user IDs using 
          `get_users_ids_list()`.
        - If the specified user ID is not in the list, the function 
          exits without making changes.
        - If the user ID is found, it is removed from the list, and 
          the updated list is saved using `update_users_list()`.
    """
    users_ids_list = get_users_ids_list()
    if user_id not in users_ids_list:
        return
    users_ids_list.remove(user_id)
    return update_users_list(users_ids_list)


def update_users_list(users_ids_list):
    """
    Updates the list of user IDs in the project settings.

    This function updates the 'users_ids' field in the 'project' table's 
    'settings' column with the provided list of user IDs. If the update 
    operation fails, a warning is logged. If successful, an informational 
    message is logged, and the function returns 1.

    Args:
        users_ids_list (list): A list of user IDs to be updated in the project settings.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.
    """
    if not db_utils.update_data('project',
                                'settings',
                                ('users_ids', json.dumps(users_ids_list)),
                                ('id', 1)):
        logger.warning('Project users list not updated')
        return
    logger.info('Project users list updated')
    return 1


def get_shared_files_folder():
    """
    Retrieves the path to the shared files folder for the current project.

    This function constructs the path to the shared files folder by combining
    the project's root path with the folder name defined in the project variables.

    Returns:
        str: The full path to the shared files folder.
    """
    return path_utils.join(environment.get_project_path(), project_vars._shared_files_folder_)


def get_scripts_folder():
    """
    Retrieves the path to the scripts folder within the current project.

    This function constructs the path to the scripts folder by combining the 
    project's root path, obtained from the environment, with the predefined 
    scripts folder name stored in `project_vars._scripts_folder_`.

    Returns:
        str: The full path to the scripts folder.
    """
    return path_utils.join(environment.get_project_path(), project_vars._scripts_folder_)


def get_hooks_folder():
    """
    Retrieves the path to the hooks folder for the current project.

    This function constructs the path to the hooks folder by combining the 
    project's root path with the hooks folder name defined in the project 
    variables.

    Returns:
        str: The full path to the hooks folder.
    """
    return path_utils.join(environment.get_project_path(), project_vars._hooks_folder_)


def get_plugins_folder():
    """
    Retrieves the path to the plugins folder for the current project.

    This function constructs the path to the plugins folder by joining the 
    project's root path with the predefined plugins folder name.

    Returns:
        str: The full path to the plugins folder.
    """
    return path_utils.join(environment.get_project_path(), project_vars._plugins_folder_)


def get_temp_scripts_folder():
    """
    Retrieves the path to the temporary scripts folder within the project directory.
    Ensures that the folder exists by creating it if necessary.

    Returns:
        str: The absolute path to the temporary scripts folder.
    """
    shared_files_folder = path_utils.join(
        environment.get_project_path(), project_vars._scripts_folder_, 'temp')
    path_utils.makedirs(shared_files_folder)
    return shared_files_folder


def add_event(event_type, title, message, data, additional_message=None, image_path=None):
    """
    Adds a new event to the 'events' table in the 'project' database.

    Args:
        event_type (str): The type of the event (e.g., error, info, warning).
        title (str): The title of the event.
        message (str): The main message or description of the event.
        data (dict): Additional data related to the event, stored as JSON.
        additional_message (str, optional): An optional additional message for the event. Defaults to None.
        image_path (str, optional): An optional file path to an image associated with the event. Defaults to None.

    Returns:
        int: The ID of the newly created event if successful, otherwise None.
    """
    event_id = db_utils.create_row('project',
                                   'events',
                                   ('creation_user',
                                    'creation_time',
                                    'type',
                                    'title',
                                    'message',
                                    'data',
                                    'additional_message',
                                    'image_path'),
                                   (environment.get_user(),
                                    time.time(),
                                    event_type,
                                    title,
                                    message,
                                    json.dumps(data),
                                    additional_message,
                                    image_path))
    if not event_id:
        return
    logger.debug("Event added")
    return event_id


def search_event(data_to_search, column_to_search='title', column='*'):
    """
    Searches for events in the 'events' table of the 'project' database based on a specific column and value.

    Args:
        data_to_search (str): The value to search for in the specified column.
        column_to_search (str, optional): The name of the column to search in. Defaults to 'title'.
        column (str, optional): The column(s) to retrieve from the matching rows. Defaults to '*', which retrieves all columns.

    Returns:
        list: A list of rows from the 'events' table that match the search criteria.
    """
    events_rows = db_utils.get_row_by_column_part_data('project',
                                                       'events',
                                                       (column_to_search,
                                                        data_to_search),
                                                       column)
    return events_rows


def modify_event_message(event_id, message):
    """
    Modify the message of a specific event in the database.

    This function updates the message of an event identified by its event_id
    in the 'events' table of the 'project' database. If the update is successful,
    it logs a success message and returns 1. Otherwise, it logs a warning message.

    Args:
        event_id (int): The unique identifier of the event to be modified.
        message (str): The new message to be set for the event.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.
    """
    if not db_utils.update_data('project',
                                'events',
                                ('message', message),
                                ('id', event_id)):
        logger.warning('Event message not modified')
        return
    logger.info('Event message modified')
    return 1


def get_event_data(event_id, column='*'):
    """
    Retrieve event data from the 'events' table in the 'project' database.

    Args:
        event_id (int): The ID of the event to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary representing the first row of the event data if found, 
                      or None if the event is not found.

    Logs:
        Logs an error message if the event is not found.
    """
    events_rows = db_utils.get_row_by_column_data('project',
                                                  'events',
                                                  ('id', event_id),
                                                  column)
    if events_rows is None or len(events_rows) < 1:
        logger.error("Event not found")
        return
    return events_rows[0]


def get_all_events(column='*'):
    """
    Retrieve all events from the 'events' table in the 'project' database.

    Args:
        column (str): The column(s) to retrieve from the 'events' table. 
                      Defaults to '*' to select all columns.

    Returns:
        list: A list of rows representing the events retrieved from the database.
    """
    events_rows = db_utils.get_rows('project',
                                    'events',
                                    column)
    return events_rows


def add_shelf_separator():
    """
    Creates a new shelf separator entry in the 'shelf_scripts' table of the 'project' database.

    This function retrieves all existing shelf scripts, calculates the position for the new separator,
    and inserts a new row into the database with the specified attributes. If the operation is successful,
    it logs the creation of the separator and returns the ID of the newly created row.

    Returns:
        int: The ID of the newly created shelf separator row if successful, or None if the operation fails.
    """
    rows = get_all_shelf_scripts()
    shelf_script_id = db_utils.create_row('project',
                                          'shelf_scripts',
                                          ('creation_user',
                                           'creation_time',
                                           'name',
                                           'py_file',
                                           'help',
                                           'only_subprocess',
                                           'icon',
                                           'type',
                                           'position'),
                                          (environment.get_user(),
                                           time.time(),
                                           'separator',
                                           None,
                                           None,
                                           None,
                                           None,
                                           'separator',
                                           len(rows)))
    if not shelf_script_id:
        return
    logger.info("Shelf separator created")
    return shelf_script_id


def add_shelf_script(name,
                     py_file,
                     help,
                     only_subprocess=0,
                     icon=ressources._default_script_shelf_icon_):
    """
    Adds a new shelf script to the project database.

    Args:
        name (str): The name of the shelf script.
        py_file (str): The path to the Python file associated with the shelf script.
        help (str): A description or help text for the shelf script.
        only_subprocess (int, optional): Indicates whether the script should run only in a subprocess.
            Defaults to 0 (False). Set to 1 (True) to enable subprocess-only execution.
        icon (str, optional): The path to the icon file for the shelf script. Defaults to the
            default script shelf icon.

    Returns:
        int or None: The ID of the created shelf script if successful, or None if the creation failed.

    Notes:
        - If a shelf script with the same name already exists, the function logs a warning and exits.
        - If the provided icon path is invalid, the default icon is used.
        - The icon is resized to 60 pixels and stored in the shared files folder.
        - The function logs the creation of the shelf script upon success.
    """
    if only_subprocess == 0:
        only_subprocess = False
    else:
        only_subprocess = True
    shelf_script_id = None
    if db_utils.check_existence('project', 'shelf_scripts', 'name', name):
        logger.warning(f"{name} already exists")
        return
    if not path_utils.isfile(icon):
        icon = ressources._default_script_shelf_icon_
    shared_icon = tools.get_filename_without_override(path_utils.join(get_shared_files_folder(),
                                                                      os.path.basename(icon)))
    path_utils.copyfile(icon, shared_icon)
    image.resize_image_file(shared_icon, 60)
    rows = get_all_shelf_scripts()
    shelf_script_id = db_utils.create_row('project',
                                          'shelf_scripts',
                                          ('creation_user',
                                           'creation_time',
                                           'name',
                                           'py_file',
                                           'help',
                                           'only_subprocess',
                                           'icon',
                                           'type',
                                           'position'),
                                          (environment.get_user(),
                                           time.time(),
                                           name,
                                           py_file,
                                           help,
                                           only_subprocess,
                                           shared_icon,
                                           'tool',
                                           len(rows)))
    if not shelf_script_id:
        return
    logger.info("Shelf script created")
    return shelf_script_id


def edit_shelf_script(script_id, help, icon, only_subprocess):
    """
    Updates the properties of a shelf script in the database and filesystem.

    Args:
        script_id (int): The unique identifier of the shelf script to be edited.
        help (str): The new help text for the shelf script.
        icon (str): The file path to the new icon for the shelf script.
        only_subprocess (bool): Flag indicating whether the script should only run in a subprocess.

    Returns:
        int: Always returns 1 to indicate the function executed.

    Behavior:
        - Updates the 'help' field in the database if it differs from the current value.
        - Updates the 'icon' field in the database and copies/resizes the icon file if it differs.
        - Updates the 'only_subprocess' field in the database if it differs.
        - Logs warnings if updates fail and logs info messages for successful updates.
    """
    script_row = get_shelf_script_data(script_id)
    if script_row['help'] != help:
        if not db_utils.update_data('project',
                                    'shelf_scripts',
                                    ('help', help),
                                    ('id', script_id)):
            logger.warning('Tool help not modified')
        logger.info('Tool help modified')
    if script_row['icon'] != icon:
        if not path_utils.isfile(icon):
            icon = ressources._default_script_shelf_icon_
        shared_icon = tools.get_filename_without_override(path_utils.join(get_shared_files_folder(),
                                                                          os.path.basename(icon)))
        path_utils.copyfile(icon, shared_icon)
        image.resize_image_file(shared_icon, 60)
        if not db_utils.update_data('project',
                                    'shelf_scripts',
                                    ('icon', shared_icon),
                                    ('id', script_id)):
            logger.warning('Tool icon not modified')
        logger.info('Tool icon modified')
    if script_row['only_subprocess'] != only_subprocess:
        if not db_utils.update_data('project',
                                    'shelf_scripts',
                                    ('only_subprocess', only_subprocess),
                                    ('id', script_id)):
            logger.info('Tool settings not modified')
        logger.info('Tool settings modified')
    return 1


def modify_shelf_script_position(script_id, position):
    """
    Modify the position of a shelf script in the project database.

    This function updates the position of a shelf script identified by its 
    script ID in the 'shelf_scripts' table of the 'project' database. If the 
    update is successful, it logs a success message and returns 1. Otherwise, 
    it logs a warning message indicating the failure.

    Args:
        script_id (int): The unique identifier of the shelf script to modify.
        position (int): The new position value to assign to the shelf script.

    Returns:
        int or None: Returns 1 if the position is successfully modified, 
        otherwise returns None.
    """
    if not db_utils.update_data('project',
                                'shelf_scripts',
                                ('position', position),
                                ('id', script_id)):
        logger.warning('Tool position not modified')
        return
    logger.info('Tool position modified')
    return 1


def delete_shelf_script(script_id):
    """
    Deletes a shelf script from the project database and removes associated files if applicable.

    Args:
        script_id (int): The unique identifier of the shelf script to be deleted.

    Returns:
        int: Returns 1 if the deletion is successful and the script is removed.
        None: Returns None if the user is not an admin or if the deletion fails.

    Behavior:
        - Retrieves the shelf script data using the provided script_id.
        - Checks if the current user has admin privileges; if not, the function exits.
        - Deletes the shelf script row from the database.
        - If the script is of type 'tool', removes the associated Python file and icon file.
        - Logs the removal of the tool or separator from the project.
    """
    script_row = get_shelf_script_data(script_id)
    if not repository.is_admin():
        return
    success = db_utils.delete_row('project', 'shelf_scripts', script_id)
    if not db_utils.delete_row('project', 'shelf_scripts', script_id):
        return
    if script_row['type'] == 'tool':
        tools.remove_file(script_row['py_file'])
        tools.remove_file(script_row['icon'])
        logger.info(f"Tool removed from project")
    else:
        logger.info(f"Separator removed from project")
    return 1


def get_shelf_script_data(script_id, column='*'):
    """
    Retrieve data for a specific shelf script from the database.

    Args:
        script_id (int): The unique identifier of the shelf script to retrieve.
        column (str, optional): The specific column(s) to retrieve from the database. 
                                Defaults to '*' to retrieve all columns.

    Returns:
        dict or None: A dictionary containing the data of the first matching shelf script row 
                      if found, or None if no matching row is found.

    Logs:
        Logs an error message if the shelf script is not found.
    """
    shelf_scripts_rows = db_utils.get_row_by_column_data('project',
                                                         'shelf_scripts',
                                                         ('id', script_id),
                                                         column)
    if shelf_scripts_rows is None or len(shelf_scripts_rows) < 1:
        logger.error("Shelf script not found")
        return
    return shelf_scripts_rows[0]


def get_all_shelf_scripts(column='*'):
    """
    Retrieve all shelf scripts from the database.

    Args:
        column (str): The column(s) to retrieve from the 'shelf_scripts' table. 
                      Defaults to '*' to select all columns.

    Returns:
        list: A list of rows from the 'shelf_scripts' table in the 'project' database.
    """
    shelf_scripts_rows = db_utils.get_rows('project',
                                           'shelf_scripts',
                                           column)
    return shelf_scripts_rows


def create_group(name, color):
    """
    Creates a new group in the 'project' database if it does not already exist.

    Args:
        name (str): The name of the group to be created.
        color (str): The color associated with the group.

    Returns:
        int or None: The ID of the newly created group if successful, or None if the group
        already exists or the creation fails.

    Logs:
        - A warning if the group already exists.
        - An info message if the group is successfully created.
    """
    if (db_utils.check_existence('project',
                                 'groups',
                                 'name', name)):
        logger.warning(f"{name} already exists")
        return
    group_id = db_utils.create_row('project',
                                   'groups',
                                   ('name',
                                    'creation_time',
                                    'creation_user',
                                    'color'),
                                   (name,
                                    time.time(),
                                    environment.get_user(),
                                    color))
    if not group_id:
        return
    logger.info('Group created')
    return group_id


def get_groups(column='*'):
    """
    Retrieve rows from the 'groups' table in the 'project' database.

    Args:
        column (str): The specific column(s) to retrieve. Defaults to '*' 
                      to select all columns.

    Returns:
        list: A list of rows retrieved from the 'groups' table.
    """
    groups_rows = db_utils.get_rows('project', 'groups', column=column)
    return groups_rows


def get_group_data(group_id, column='*'):
    """
    Retrieve data for a specific group from the database.

    Args:
        group_id (int): The unique identifier of the group to retrieve.
        column (str, optional): The specific column(s) to retrieve from the database. 
                                Defaults to '*' to retrieve all columns.

    Returns:
        dict or None: A dictionary containing the data of the first matching group row 
                      if found, or None if no matching group is found.

    Logs:
        Logs an error message if the group is not found.
    """
    groups_rows = db_utils.get_row_by_column_data('project',
                                                  'groups',
                                                  ('id', group_id),
                                                  column)
    if groups_rows is None or len(groups_rows) < 1:
        logger.error("Group not found")
        return
    return groups_rows[0]


def get_group_by_name(name, column='*'):
    """
    Retrieve a group from the database by its name.

    Args:
        name (str): The name of the group to retrieve.
        column (str, optional): The specific column(s) to retrieve from the database.
            Defaults to '*' to retrieve all columns.

    Returns:
        dict or None: The first row of the group data as a dictionary if found,
            or None if the group is not found.

    Logs:
        Logs an error message if the group is not found.
    """
    groups_rows = db_utils.get_row_by_column_data('project',
                                                  'groups',
                                                  ('name', name),
                                                  column)
    if groups_rows is None or len(groups_rows) < 1:
        logger.error("Group not found")
        return
    return groups_rows[0]


def modify_group_color(group_id, color):
    """
    Modify the color of a group in the database.

    This function updates the color of a group identified by `group_id` in the 
    database if the provided `color` is a valid hexadecimal color code.

    Args:
        group_id (int): The unique identifier of the group whose color is to be modified.
        color (str): The new color to assign to the group, specified as a hexadecimal color code 
                     (e.g., "#FFFFFF" or "#FFF").

    Returns:
        int or None: Returns 1 if the color was successfully modified. Returns None if the color 
                     is invalid or if the database update operation fails.

    Logs:
        - Logs a warning if the provided color is not a valid hexadecimal color code.
        - Logs a warning if the database update operation fails.
        - Logs an info message if the color is successfully modified.
    """
    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
    if not match:
        logger.warning(f"{color} is not a valid hex color code")
        return
    if not db_utils.update_data('project',
                                'groups',
                                ('color', color),
                                ('id', group_id)):
        logger.warning('Group color not modified')
        return
    logger.info('Group color modified')
    return 1


def remove_group(group_id):
    """
    Removes a group and its associated references from the project.

    This function performs the following steps:
    1. Removes all grouped references associated with the given group ID.
    2. Removes all referenced groups associated with the given group ID.
    3. Deletes the group from the 'groups' table in the 'project' database.

    If the group cannot be deleted from the database, a warning is logged.
    Otherwise, a success message is logged, and the function returns 1.

    Args:
        group_id (int): The unique identifier of the group to be removed.

    Returns:
        int or None: Returns 1 if the group is successfully removed, 
        otherwise returns None.
    """
    for grouped_reference_id in get_grouped_references(group_id, 'id'):
        remove_grouped_reference(grouped_reference_id)
    for referenced_group_id in get_referenced_groups_by_group_id(group_id, 'id'):
        remove_referenced_group(referenced_group_id)
    if not db_utils.delete_row('project', 'groups', group_id):
        logger.warning(f"Group NOT removed from project")
        return
    logger.info(f"Group removed from project")
    return 1


def create_referenced_group(work_env_id, group_id, namespace, count=None, activated=1):
    """
    Creates a referenced group in the database if it does not already exist.

    This function checks if a referenced group with the given namespace and 
    work environment ID already exists in the database. If it does not exist, 
    it creates a new entry in the 'referenced_groups_data' table with the 
    provided details.

    Args:
        work_env_id (int): The ID of the work environment where the group is being referenced.
        group_id (int): The ID of the group to be referenced.
        namespace (str): A unique namespace for the referenced group.
        count (int, optional): An optional count value associated with the group. Defaults to None.
        activated (int, optional): A flag indicating whether the group is activated. Defaults to 1.

    Returns:
        int or None: The ID of the newly created referenced group if successful, 
                     or None if the group already exists or creation fails.

    Logs:
        - Logs a warning if the namespace already exists.
        - Logs an info message when a referenced group is successfully created.
    """
    group_name = get_group_data(group_id, 'name')
    if (db_utils.check_existence_by_multiple_data('project',
                                                  'referenced_groups_data',
                                                  ('namespace', 'work_env_id'),
                                                  (namespace, work_env_id))):
        logger.warning(f"{namespace} already exists")
        return
    referenced_group_id = db_utils.create_row('project',
                                              'referenced_groups_data',
                                              ('creation_time',
                                               'creation_user',
                                               'namespace',
                                               'count',
                                               'group_id',
                                               'group_name',
                                               'work_env_id',
                                               'activated'),
                                              (time.time(),
                                               environment.get_user(),
                                               namespace,
                                               count,
                                               group_id,
                                               group_name,
                                               work_env_id,
                                               activated))
    if not referenced_group_id:
        return
    logger.info(f"Referenced group created")
    return referenced_group_id


def remove_referenced_group(referenced_group_id):
    """
    Removes a referenced group from the project database.

    This function attempts to delete a row from the 'referenced_groups_data' table
    in the 'project' database using the provided referenced group ID. If the deletion
    is successful, it logs a success message and returns 1. If the deletion fails,
    it logs a warning message and exits without returning a value.

    Args:
        referenced_group_id (int): The ID of the referenced group to be removed.

    Returns:
        int: Returns 1 if the referenced group is successfully removed.
             Returns None if the deletion fails.

    Logs:
        - Logs a warning if the referenced group could not be removed.
        - Logs an info message if the referenced group is successfully removed.
    """
    if not db_utils.delete_row('project', 'referenced_groups_data', referenced_group_id):
        logger.warning(f"Referenced group NOT removed from project")
        return
    logger.info(f"Referenced group removed from project")
    return 1


def remove_video(video_id):
    """
    Removes a video from the project by its ID.

    This function attempts to delete a video entry from the 'videos' table
    in the 'project' database. If the deletion is successful, it logs a 
    success message and returns 1. Otherwise, it logs a failure message.

    Args:
        video_id (int): The unique identifier of the video to be removed.

    Returns:
        int or None: Returns 1 if the video is successfully removed, 
        otherwise returns None.
    """
    if not db_utils.delete_row('project', 'videos', video_id):
        logger.info(f"Video NOT removed from project")
        return
    logger.info(f"Video removed from project")
    return 1


def get_referenced_groups(work_env_id, column='*'):
    """
    Retrieve referenced group data from the 'project' table in the database.

    Args:
        work_env_id (int): The ID of the work environment to filter the data.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        list: A list of rows containing the referenced group data for the specified 
              work environment ID.
    """
    referenced_groups_rows = db_utils.get_row_by_column_data('project',
                                                             'referenced_groups_data',
                                                             ('work_env_id',
                                                              work_env_id),
                                                             column)
    return referenced_groups_rows


def get_videos(variant_id, column='*'):
    """
    Retrieve video records from the 'videos' table in the 'project' database.

    Args:
        variant_id (int): The ID of the variant to filter videos by.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        list: A list of rows representing the video records that match the given variant ID.
    """
    videos_rows = db_utils.get_row_by_column_data('project',
                                                  'videos',
                                                  ('variant_id', variant_id),
                                                  column)
    return videos_rows


def get_all_videos(column='*', order='creation_time'):
    """
    Retrieve all video records from the 'videos' table in the 'project' database.

    Args:
        column (str): The column(s) to retrieve from the table. Defaults to '*', which selects all columns.
        order (str): The column by which to order the results. Defaults to 'creation_time'.

    Returns:
        list: A list of rows representing the video records, ordered in descending order by the specified column.
    """
    videos_rows = db_utils.get_rows('project',
                                    'videos',
                                    column,
                                    order,
                                    'DESC')
    return videos_rows


def get_referenced_groups_by_group_id(group_id, column='*'):
    """
    Retrieve rows of referenced groups from the 'project' database table 
    based on a given group ID.

    Args:
        group_id (int or str): The ID of the group to filter the referenced groups.
        column (str, optional): The specific column(s) to retrieve from the 
            database. Defaults to '*' (all columns).

    Returns:
        list or None: A list of rows containing the referenced groups data 
        matching the given group ID, or None if no data is found.
    """
    referenced_groups_rows = db_utils.get_row_by_column_data('project',
                                                             'referenced_groups_data',
                                                             ('group_id',
                                                              group_id),
                                                             column)
    return referenced_groups_rows


def get_referenced_group_data(referenced_group_id, column='*'):
    """
    Retrieve data for a referenced group from the 'referenced_groups_data' table in the 'project' database.

    Args:
        referenced_group_id (int): The ID of the referenced group to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', which retrieves all columns.

    Returns:
        dict or None: A dictionary containing the data for the referenced group if found, or None if the group is not found.

    Logs:
        Logs an error message if the referenced group is not found.
    """
    referenced_groups_rows = db_utils.get_row_by_column_data('project',
                                                             'referenced_groups_data',
                                                             ('id', referenced_group_id),
                                                             column)
    if referenced_groups_rows is None or len(referenced_groups_rows) < 1:
        logger.error("Referenced group not found")
        return
    return referenced_groups_rows[0]


def get_referenced_group_by_namespace(work_env_id, namespace, column='*'):
    """
    Retrieve a referenced group from the database based on the given work environment ID 
    and namespace.

    Args:
        work_env_id (int): The ID of the work environment to search within.
        namespace (str): The namespace of the referenced group to retrieve.
        column (str, optional): The specific column(s) to retrieve from the database. 
                                Defaults to '*' (all columns).

    Returns:
        dict or None: A dictionary representing the first row of the referenced group 
                      data if found, or None if no matching data is found.

    Logs:
        Logs an error message if no referenced group is found for the given criteria.
    """
    referenced_groups_rows = db_utils.get_row_by_multiple_data('project',
                                                               'referenced_groups_data',
                                                               ('work_env_id',
                                                                'namespace'),
                                                               (work_env_id,
                                                                namespace),
                                                               column)
    if referenced_groups_rows is None or len(referenced_groups_rows) < 1:
        logger.error("Referenced group not found")
        return
    return referenced_groups_rows[0]


def create_grouped_reference(group_id, export_version_id, namespace, count=None, auto_update=0, activated=1):
    """
    Creates a grouped reference entry in the database for a given group and export version.

    Args:
        group_id (int): The ID of the group to associate with the reference.
        export_version_id (int): The ID of the export version to associate with the reference.
        namespace (str): The namespace for the grouped reference.
        count (int, optional): The count value for the grouped reference. Defaults to None.
        auto_update (int, optional): Flag indicating whether the reference should auto-update. Defaults to 0.
        activated (int, optional): Flag indicating whether the reference is activated. Defaults to 1.

    Returns:
        int: The ID of the newly created grouped reference, or None if creation failed or the namespace already exists.

    Logs:
        - Logs a warning if the namespace already exists.
        - Logs an info message when a grouped reference is successfully created.
    """
    export_id = get_export_version_data(export_version_id, 'export_id')
    stage_name = get_stage_data(get_export_data(export_id, 'stage_id'),
                                'name')
    if (db_utils.check_existence_by_multiple_data('project',
                                                  'grouped_references_data',
                                                  ('namespace', 'group_id'),
                                                  (namespace, group_id))):
        logger.warning(f"{namespace} already exists")
        return
    reference_id = db_utils.create_row('project',
                                       'grouped_references_data',
                                       ('creation_time',
                                        'creation_user',
                                        'namespace',
                                        'count',
                                        'stage',
                                        'group_id',
                                        'export_id',
                                        'export_version_id',
                                        'auto_update',
                                        'activated'),
                                       (time.time(),
                                        environment.get_user(),
                                        namespace,
                                        count,
                                        stage_name,
                                        group_id,
                                        export_id,
                                        export_version_id,
                                        auto_update,
                                        activated))
    if not reference_id:
        return
    logger.info(f"Grouped reference created")
    return reference_id


def remove_grouped_reference(grouped_reference_id):
    """
    Removes a grouped reference from the database.

    This function attempts to delete a grouped reference identified by 
    `grouped_reference_id` from the 'grouped_references_data' table in the 
    'project' database. If the deletion is unsuccessful, a warning is logged. 
    If successful, an informational log is created, and the function returns 1.

    Args:
        grouped_reference_id (int): The unique identifier of the grouped 
        reference to be removed.

    Returns:
        int or None: Returns 1 if the grouped reference is successfully 
        deleted, otherwise returns None.
    """
    if not db_utils.delete_row('project', 'grouped_references_data', grouped_reference_id):
        logger.warning("Grouped reference NOT deleted")
        return
    logger.info("Grouped reference deleted")
    return 1


def get_grouped_references(group_id, column='*'):
    """
    Retrieve grouped references from the 'project' table based on the specified group ID.

    Args:
        group_id (int): The ID of the group to filter the references.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' (all columns).

    Returns:
        list: A list of rows containing the grouped references data for the specified group ID.
    """
    grouped_references_rows = db_utils.get_row_by_column_data('project',
                                                              'grouped_references_data',
                                                              ('group_id',
                                                               group_id),
                                                              column)
    return grouped_references_rows


def get_grouped_reference_data(grouped_reference_id, column='*'):
    """
    Retrieve grouped reference data from the database based on the provided ID.

    Args:
        grouped_reference_id (int): The ID of the grouped reference to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: The first row of the grouped reference data as a dictionary if found, 
                      or None if no data is found.

    Logs:
        Logs an error message if the grouped reference data is not found.
    """
    grouped_references_rows = db_utils.get_row_by_column_data('project',
                                                              'grouped_references_data',
                                                              ('id', grouped_reference_id),
                                                              column)
    if grouped_references_rows is None or len(grouped_references_rows) < 1:
        logger.error("Grouped reference not found")
        return
    return grouped_references_rows[0]


def get_grouped_reference_by_namespace(group_id, namespace, column='*'):
    """
    Retrieve a grouped reference from the database by group ID and namespace.

    This function queries the 'grouped_references_data' table in the 'project' database
    to fetch a row that matches the specified group ID and namespace. Optionally, a specific
    column or set of columns can be retrieved.

    Args:
        group_id (int): The ID of the group to filter by.
        namespace (str): The namespace to filter by.
        column (str, optional): The column(s) to retrieve. Defaults to '*', which retrieves all columns.

    Returns:
        dict or None: The first row of the grouped reference data as a dictionary if found,
                      or None if no matching data is found.

    Logs:
        Logs an error message if no grouped reference is found.

    Raises:
        None
    """
    grouped_references_rows = db_utils.get_row_by_multiple_data('project',
                                                                'grouped_references_data',
                                                                ('group_id',
                                                                 'namespace'),
                                                                (group_id,
                                                                 namespace),
                                                                column)
    if grouped_references_rows is None or len(grouped_references_rows) < 1:
        logger.error("Grouped reference not found")
        return
    return grouped_references_rows[0]


def update_grouped_reference_data(grouped_reference_id, data_tuple):
    """
    Updates the grouped reference data in the database for a given grouped reference ID.

    Args:
        grouped_reference_id (int): The ID of the grouped reference to update.
        data_tuple (tuple): A tuple containing the data to update in the grouped reference.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.

    Logs:
        Logs a warning if the update fails.
        Logs an info message if the update is successful.
    """
    if not db_utils.update_data('project',
                                'grouped_references_data',
                                data_tuple,
                                ('id', grouped_reference_id)):
        logger.warning('Grouped reference modified')
        return
    logger.info('Grouped reference modified')
    return 1


def update_grouped_reference(grouped_reference_id, export_version_id):
    """
    Updates the export version ID of a grouped reference in the database.

    This function modifies the 'grouped_references_data' table in the 'project' database
    by updating the 'export_version_id' field for the specified grouped reference ID.
    If the update is successful, a log message is recorded, and the function returns 1.
    If the update fails, a different log message is recorded, and the function returns None.

    Args:
        grouped_reference_id (int): The ID of the grouped reference to update.
        export_version_id (int): The new export version ID to set for the grouped reference.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise None.

    Logs:
        - Logs 'Grouped reference modified' if the update is successful.
        - Logs 'Grouped reference not modified' if the update fails.
    """
    if not db_utils.update_data('project',
                                'grouped_references_data',
                                ('export_version_id', export_version_id),
                                ('id', grouped_reference_id)):
        logger.info('Grouped reference not modified')
        return
    logger.info('Grouped reference modified')
    return 1


def modify_grouped_reference_export(grouped_reference_id, export_id):
    """
    Modifies the grouped reference export by updating its associated export ID 
    and export version ID.

    This function retrieves the default export version ID for the given export ID. 
    If no export version ID is found, the function returns without making any changes. 
    Otherwise, it updates the grouped reference data with the provided export ID 
    and the retrieved export version ID.

    Args:
        grouped_reference_id (int): The ID of the grouped reference to be modified.
        export_id (int): The ID of the export to associate with the grouped reference.

    Returns:
        int: Returns 1 if the grouped reference data is successfully updated, 
             otherwise returns None.
    """
    export_version_id = get_default_export_version(export_id, 'id')
    if not export_version_id:
        return
    update_grouped_reference_data(
        grouped_reference_id, ('export_id', export_id))
    update_grouped_reference_data(
        grouped_reference_id, ('export_version_id', export_version_id))
    return 1


def modify_grouped_reference_auto_update(grouped_reference_id, auto_update):
    """
    Modifies the auto-update setting of a grouped reference and updates its 
    export version ID if applicable.

    Args:
        grouped_reference_id (int): The unique identifier of the grouped reference.
        auto_update (bool): A flag indicating whether auto-update should be enabled (True) 
                            or disabled (False).

    Returns:
        int or None: Returns 1 if the auto-update is enabled and the export version ID 
                     is successfully updated. Returns None otherwise.

    Behavior:
        - If `auto_update` is True, it sets the auto-update flag to 1 and attempts to 
          update the export version ID of the grouped reference.
        - If `auto_update` is False, it disables the auto-update flag and exits without 
          modifying the export version ID.
        - If no default export version ID is found, the function exits without making 
          further changes.
    """
    if auto_update:
        auto_update = 1
    update_grouped_reference_data(
        grouped_reference_id, ('auto_update', auto_update))
    if not auto_update:
        return
    export_id = get_grouped_reference_data(grouped_reference_id, 'export_id')
    export_version_id = get_default_export_version(export_id, 'id')
    if not export_version_id:
        return
    update_grouped_reference_data(
        grouped_reference_id, ('export_version_id', export_version_id))
    return 1


def modify_grouped_reference_activation(grouped_reference_id, activated):
    """
    Modify the activation status of a grouped reference.

    This function updates the activation status of a grouped reference
    in the database. If the `activated` parameter is truthy, it is converted
    to the integer value `1` before being passed to the update function.

    Args:
        grouped_reference_id (int): The unique identifier of the grouped reference.
        activated (bool or int): The desired activation status. If truthy, it will
                                 be converted to `1`.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    if activated:
        activated = 1
    return update_grouped_reference_data(grouped_reference_id, ('activated', activated))


def modify_referenced_group_activation(referenced_group_id, activated):
    """
    Modify the activation status of a referenced group.

    This function updates the activation status of a referenced group
    in the database. If the `activated` parameter is True, it converts
    it to 1 before updating the data.

    Args:
        referenced_group_id (int): The unique identifier of the referenced group.
        activated (bool): The desired activation status. True for active, False for inactive.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    if activated:
        activated = 1
    return update_referenced_group_data(referenced_group_id, ('activated', activated))


def search_group(name, column='*'):
    """
    Searches for a group in the 'groups' table of the 'project' database 
    based on the provided name and retrieves the specified column(s).

    Args:
        name (str): The name of the group to search for.
        column (str, optional): The column(s) to retrieve from the table. 
            Defaults to '*' to retrieve all columns.

    Returns:
        list: A list of rows matching the search criteria from the 'groups' table.
    """
    groups_rows = db_utils.get_row_by_column_part_data('project',
                                                       'groups',
                                                       ('name', name),
                                                       column)
    return groups_rows


def get_all_tag_groups(column='*'):
    """
    Retrieve all tag groups from the 'tag_groups' table in the 'project' database.

    Args:
        column (str): The specific column(s) to retrieve from the table. 
                      Defaults to '*' to select all columns.

    Returns:
        list: A list of rows representing the tag groups retrieved from the database.
    """
    tag_groups_rows = db_utils.get_rows('project',
                                        'tag_groups',
                                        column)
    return tag_groups_rows


def get_tag_group_by_name(name, column='*'):
    """
    Retrieve a tag group from the database by its name.

    This function queries the 'tag_groups' table in the 'project' database
    for a row that matches the specified name. Optionally, a specific column
    or columns can be retrieved instead of all columns.

    Args:
        name (str): The name of the tag group to retrieve.
        column (str, optional): The column(s) to retrieve from the database.
            Defaults to '*' (all columns).

    Returns:
        dict or None: The first row of the matching tag group as a dictionary
            if found, or None if no matching tag group is found.

    Logs:
        Logs an error message if no tag group is found.
    """
    tag_groups_rows = db_utils.get_row_by_column_part_data('project',
                                                           'tag_groups',
                                                           ('name', name),
                                                           column)
    if tag_groups_rows is None or len(tag_groups_rows) < 1:
        logger.error("Tag group not found")
        return
    return tag_groups_rows[0]


def get_tag_group_data(tag_group_id, column='*'):
    """
    Retrieve data for a specific tag group from the database.

    Args:
        tag_group_id (int): The ID of the tag group to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary containing the data for the tag group if found, 
                      or None if the tag group does not exist.

    Logs:
        Logs an error message if the tag group is not found.
    """
    tag_groups_rows = db_utils.get_row_by_column_part_data('project',
                                                           'tag_groups',
                                                           ('id', tag_group_id),
                                                           column)
    if tag_groups_rows is None or len(tag_groups_rows) < 1:
        logger.error("Tag group not found")
        return
    return tag_groups_rows[0]


def create_tag_group(group_name):
    """
    Creates a new tag group in the project database if it does not already exist.

    Args:
        group_name (str): The name of the tag group to be created.

    Returns:
        int or None: The ID of the newly created tag group if successful, 
                     or None if the creation failed or the group already exists.

    Logs:
        - A warning if the group name is not safe or already exists.
        - An info message if the tag group is successfully created.

    Notes:
        - The function checks if the group name is safe using `tools.is_safe`.
        - It ensures the group name does not already exist by querying `get_all_tag_groups('name')`.
        - The tag group is created in the 'tag_groups' table of the 'project' database.
        - The `user_ids` field is initialized as an empty JSON array.
    """
    if not tools.is_safe(group_name):
        return
    if group_name in get_all_tag_groups('name'):
        logger.warning(f"{group_name} already exists")
        return
    tag_group_id = db_utils.create_row('project',
                                       'tag_groups',
                                       ('creation_time',
                                        'creation_user',
                                        'name',
                                        'user_ids'),
                                       (time.time(),
                                        environment.get_user(),
                                        group_name,
                                        json.dumps([])))
    if not tag_group_id:
        return
    logger.info(f"Tag groups created")
    return tag_group_id


def delete_tag_group(group_name):
    """
    Deletes a tag group from the project by its name.

    This function retrieves a tag group by its name and attempts to delete it
    from the database. If the tag group does not exist, the function returns
    without performing any action. If the deletion fails, a warning is logged.
    Otherwise, a success message is logged.

    Args:
        group_name (str): The name of the tag group to delete.

    Logs:
        - A warning if the tag group could not be removed from the project.
        - An info message if the tag group was successfully deleted.
    """
    tag_group_row = get_tag_group_by_name(group_name)
    if not tag_group_row:
        return
    if not db_utils.delete_row('project', 'tag_groups', tag_group_row['id']):
        logger.warning(f"Tag group {group_name} NOT removed from project")
        return
    logger.info(f"{group_name} deleted")


def suscribe_to_tag_group(group_name):
    """
    Subscribes the current user to a specified tag group.

    This function retrieves the tag group by its name and checks if the current
    user is already subscribed to it. If not, the user is added to the tag group's
    list of subscribers, and the updated list is saved to the database.

    Args:
        group_name (str): The name of the tag group to subscribe to.

    Returns:
        None: The function does not return a value. It logs messages to indicate
        the subscription status.

    Logs:
        - Logs an info message if the user is already subscribed to the tag group.
        - Logs an info message when the user successfully subscribes to the tag group.
    """
    tag_group_row = get_tag_group_by_name(group_name)
    if not tag_group_row:
        return
    user_ids = json.loads(tag_group_row['user_ids'])
    user_id = repository.get_user_row_by_name(environment.get_user(), 'id')
    if user_id in user_ids:
        logger.info("You already suscribed to this tag group")
        return
    user_ids.append(user_id)
    if db_utils.update_data('project',
                            'tag_groups',
                            ('user_ids', json.dumps(user_ids)),
                            ('id', tag_group_row['id'])):
        logger.info(
            f"{environment.get_user()} suscribed to {group_name} tag group.")


def unsuscribe_from_tag_group(group_name):
    """
    Unsubscribes the current user from a specified tag group.

    This function removes the current user's ID from the list of user IDs
    associated with the given tag group. If the user is not subscribed to
    the tag group, a log message is generated, and no further action is taken.

    Args:
        group_name (str): The name of the tag group to unsubscribe from.

    Returns:
        None

    Logs:
        - Logs a message if the user is not subscribed to the tag group.
        - Logs a message upon successful unsubscription from the tag group.

    Database Operations:
        - Updates the 'user_ids' field in the 'tag_groups' table of the 'project' database.
    """
    tag_group_row = get_tag_group_by_name(group_name)
    if not tag_group_row:
        return
    user_ids = json.loads(tag_group_row['user_ids'])
    user_id = repository.get_user_row_by_name(environment.get_user(), 'id')
    if user_id not in user_ids:
        logger.info("You didn't suscribed to this tag group")
        return
    user_ids.remove(user_id)
    if db_utils.update_data('project',
                            'tag_groups',
                            ('user_ids', json.dumps(user_ids)),
                            ('id', tag_group_row['id'])):
        logger.info(
            f"{environment.get_user()} unsuscribed from {group_name} tag group.")


def create_assets_group(asset_group_name, category_id):
    """
    Creates a new asset group within a specified category.

    This function checks if the provided asset group name is safe and unique 
    within the given category. If the name is valid and does not already exist, 
    it creates a new asset group in the database and assigns it a default color.

    Args:
        asset_group_name (str): The name of the asset group to be created.
        category_id (int): The ID of the category to which the asset group belongs.

    Returns:
        int: The ID of the newly created asset group if successful.
        None: If the asset group name is unsafe, already exists, or creation fails.

    Logs:
        - A warning if the asset group name already exists in the category.
        - An info message when the asset group is successfully created.
    """
    if not tools.is_safe(asset_group_name):
        return
    if asset_group_name in get_category_asset_groups(category_id, 'name'):
        logger.warning(f"{asset_group_name} already exists")
        return
    asset_group_id = db_utils.create_row('project',
                                         'assets_groups',
                                         ('creation_time',
                                          'creation_user',
                                          'name',
                                          'color',
                                          'category_id'),
                                         (time.time(),
                                          environment.get_user(),
                                          asset_group_name,
                                          '#9c9c9c',
                                          category_id))
    if not asset_group_id:
        return
    logger.info(f"Asset group created")
    return asset_group_id


def get_category_asset_groups(category_id, column='*'):
    """
    Retrieve asset group rows from the 'assets_groups' table in the 'project' database
    based on the specified category ID.

    Args:
        category_id (int): The ID of the category to filter asset groups.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*',
            which retrieves all columns.

    Returns:
        list: A list of rows from the 'assets_groups' table that match the given
        category ID. The structure of the rows depends on the specified column(s).
    """
    assets_groups_rows = db_utils.get_row_by_column_data('project',
                                                         'assets_groups',
                                                         ('category_id',
                                                          category_id),
                                                         column)
    return assets_groups_rows


def get_all_assets_groups(column='*'):
    """
    Retrieve all rows from the 'assets_groups' table in the 'project' database.

    Args:
        column (str): The specific column(s) to retrieve from the table. 
                      Defaults to '*' to select all columns.

    Returns:
        list: A list of rows from the 'assets_groups' table based on the specified column(s).
    """
    assets_groups_rows = db_utils.get_rows('project',
                                           'assets_groups',
                                           column)
    return assets_groups_rows


def get_assets_group_data(assets_group_id, column='*'):
    """
    Retrieve data for a specific assets group from the database.

    Args:
        assets_group_id (int): The ID of the assets group to retrieve.
        column (str, optional): The specific column(s) to retrieve from the database. 
                                Defaults to '*' to retrieve all columns.

    Returns:
        dict or None: A dictionary containing the data of the assets group if found, 
                      or None if the assets group is not found.

    Logs:
        Logs an error message if the assets group is not found.
    """
    assets_groups_rows = db_utils.get_row_by_column_data('project',
                                                         'assets_groups',
                                                         ('id', assets_group_id),
                                                         column)
    if assets_groups_rows is None or len(assets_groups_rows) < 1:
        logger.error("Assets group not found")
        return
    return assets_groups_rows[0]


def add_asset_to_assets_group(asset_id, assets_group_id):
    """
    Adds an asset to a specified assets group if they belong to the same category.

    This function retrieves the asset and assets group data, checks if they exist,
    and ensures that both belong to the same category before updating the asset's
    group association in the database.

    Args:
        asset_id (int): The unique identifier of the asset to be added.
        assets_group_id (int): The unique identifier of the target assets group.

    Returns:
        int or None: Returns 1 if the asset was successfully added to the group.
                     Returns None if the operation was not performed due to
                     mismatched categories, missing data, or if the asset is
                     already in the specified group.

    Logs:
        - Logs a warning if the asset and group do not belong to the same category.
        - Logs an info message when the asset is successfully added to the group.
    """
    asset_row = get_asset_data(asset_id)
    assets_group_row = get_assets_group_data(assets_group_id)
    if not asset_row:
        return
    if not assets_group_row:
        return
    if asset_row['category_id'] != assets_group_row['category_id']:
        logger.warning(
            f"Asset and group doesn't have the same category, can't move asset")
        return
    if asset_row['assets_group_id'] == assets_group_id:
        return
    if db_utils.update_data('project',
                            'assets',
                            ('assets_group_id', assets_group_id),
                            ('id', asset_id)):
        logger.info(f"Asset added to {assets_group_row['name']} assets group")
        return 1


def get_assets_group_childs(assets_group_id, column='*'):
    """
    Retrieve child assets belonging to a specific assets group.

    Args:
        assets_group_id (int): The ID of the assets group to retrieve child assets for.
        column (str, optional): The specific column(s) to retrieve from the database. 
                                Defaults to '*' to retrieve all columns.

    Returns:
        list: A list of rows representing the child assets of the specified assets group.
    """
    assets_rows = db_utils.get_row_by_column_data('project',
                                                  'assets',
                                                  ('assets_group_id',
                                                   assets_group_id),
                                                  column)
    return assets_rows


def remove_asset_from_assets_group(asset_id):
    """
    Removes an asset from its associated assets group in the database.

    This function retrieves the asset data using the provided asset ID. If the asset exists
    and is associated with an assets group, it updates the database to remove the association
    by setting the `assets_group_id` to None. Logs the operation if successful.

    Args:
        asset_id (int): The unique identifier of the asset to be removed from its group.

    Returns:
        int: Returns 1 if the asset was successfully removed from the group.
        None: Returns None if the asset does not exist, is not associated with a group, 
              or if the database update fails.
    """
    asset_row = get_asset_data(asset_id)
    if not asset_row:
        return
    if asset_row['assets_group_id'] is None:
        return
    if db_utils.update_data('project',
                            'assets',
                            ('assets_group_id', None),
                            ('id', asset_id)):
        logger.info(f"Asset removed from group")
        return 1


def remove_assets_group(assets_group_id):
    """
    Removes an assets group and its associated child assets from the project.

    This function retrieves all child asset IDs associated with the given 
    assets group ID, removes each child asset from the assets group, and 
    then deletes the assets group from the database. If the deletion fails, 
    a warning is logged. Otherwise, a success message is logged.

    Args:
        assets_group_id (int): The ID of the assets group to be removed.

    Returns:
        int: Returns 1 if the assets group is successfully removed.
        None: Returns None if the assets group could not be removed.
    """
    child_assets_ids = get_assets_group_childs(assets_group_id, 'id')
    for asset_id in child_assets_ids:
        remove_asset_from_assets_group(asset_id)
    if not db_utils.delete_row('project', 'assets_groups', assets_group_id):
        logger.warning(f"Assets group NOT removed from project")
        return
    logger.info(f"Assets group removed from project")
    return 1


def create_project(project_name, project_path, project_password, project_image=None):
    """
    Creates a new project with the specified parameters.
    Args:
        project_name (str): The name of the project. Must not be an empty string.
        project_path (str): The file path where the project will be created. Must not be an empty string.
        project_password (str): The password for the project. Must not be an empty string.
        project_image (Optional[Any]): An optional image associated with the project. Defaults to None.
    Returns:
        int or None: Returns 1 if the project is successfully created, otherwise returns None.
    Logs:
        - Logs a warning if any of the required parameters (project_name, project_path, project_password) are empty.
        - Logs an info message upon successful project creation.
    Notes:
        - If the project creation fails at any step, the function will terminate early and clean up any partially created data.
        - The `repository.create_project` function is used to create the project in the repository.
        - The `init_project` function is used to initialize the project at the specified path.
        - If initialization fails, the created project entry in the repository is removed.
    """
    do_creation = 1

    if project_name == '':
        logger.warning("Please provide a project name")
        do_creation = 0
    if project_path == '':
        logger.warning("Please provide a project path")
        do_creation = 0
    if project_password == '':
        logger.warning("Please provide a password")
        do_creation = 0

    if not do_creation:
        return
    project_id = repository.create_project(
        project_name, project_path, project_password, project_image)
    if not project_id:
        return
    if not init_project(project_path, project_name):
        repository.remove_project_row(project_id)
        return
    logger.info(f"{project_name} created")
    return 1


def init_project(project_path, project_name):
    """
    Initializes a new project by creating the necessary directory structure 
    and database tables.

    Args:
        project_path (str): The file system path where the project directory 
            should be created.
        project_name (str): The name of the project, which is also used as 
            the database name.

    Returns:
        str or None: Returns the project name if initialization is successful, 
            otherwise returns None.

    Behavior:
        - Checks if the specified project directory exists; if not, it creates it.
        - Verifies if a database with the given project name already exists:
            - Logs a warning if the database exists and exits the function.
        - Creates a new database if it does not exist.
        - Sets up various tables in the database required for the project, 
          including settings, assets, stages, versions, and more.
    """
    if not path_utils.isdir(project_path):
        path_utils.mkdir(project_path)
    if db_utils.check_database_existence(project_name):
        logger.warning(f"Database {project_name} already exists")
        return
    if not db_utils.create_database(project_name):
        return
    create_settings_table(project_name)
    create_softwares_table(project_name)
    create_domains_table(project_name)
    create_categories_table(project_name)
    create_assets_groups_table(project_name)
    create_assets_table(project_name)
    create_assets_preview_table(project_name)
    create_stages_table(project_name)
    create_variants_table(project_name)
    create_asset_tracking_events_table(project_name)
    create_work_envs_table(project_name)
    create_versions_table(project_name)
    create_exports_table(project_name)
    create_export_versions_table(project_name)
    create_references_table(project_name)
    create_extensions_table(project_name)
    create_events_table(project_name)
    create_shelf_scripts_table(project_name)
    create_groups_table(project_name)
    create_referenced_groups_table(project_name)
    create_grouped_references_table(project_name)
    create_progress_events_table(project_name)
    create_videos_table(project_name)
    create_tag_groups_table(project_name)
    create_playlists_table(project_name)
    return project_name


def create_domains_table(database):
    """
    Creates a table named 'domains_data' in the specified database if it does not already exist.

    The table includes the following columns:
        - id: A serial primary key.
        - name: A unique text field that cannot be null.
        - creation_time: A double precision field representing the creation time, cannot be null.
        - creation_user: A text field representing the user who created the entry, cannot be null.
        - string: A text field, cannot be null.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS domains_data (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL UNIQUE,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        string text NOT NULL
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Categories table created")
    return 1


def create_categories_table(database):
    """
    Creates the 'categories' table in the specified database if it does not already exist.

    The table includes the following columns:
        - id: Serial primary key.
        - name: Text, not null.
        - creation_time: Double precision, not null.
        - creation_user: Text, not null.
        - string: Text, not null.
        - domain_id: Integer, not null, with a foreign key reference to the 'domains_data' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS categories (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        string text NOT NULL,
                                        domain_id integer NOT NULL,
                                        FOREIGN KEY (domain_id) REFERENCES domains_data (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Categories table created")
    return 1


def create_assets_table(database):
    """
    Creates the 'assets' table in the specified database if it does not already exist.

    The table includes the following columns:
        - id: Serial primary key.
        - name: Text, not null, representing the name of the asset.
        - creation_time: Double precision, not null, representing the creation timestamp.
        - creation_user: Text, not null, representing the user who created the asset.
        - inframe: Integer, not null, representing the in-frame value.
        - outframe: Integer, not null, representing the out-frame value.
        - preroll: Integer, not null, representing the preroll value.
        - postroll: Integer, not null, representing the postroll value.
        - string: Text, not null, representing additional information about the asset.
        - category_id: Integer, not null, foreign key referencing the 'categories' table.
        - assets_group_id: Integer, foreign key referencing the 'assets_groups' table.

    Foreign key constraints:
        - category_id references the 'id' column in the 'categories' table.
        - assets_group_id references the 'id' column in the 'assets_groups' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating the successful creation of the 'assets' table.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS assets (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        inframe integer NOT NULL,
                                        outframe integer NOT NULL,
                                        preroll integer NOT NULL,
                                        postroll integer NOT NULL,
                                        string text NOT NULL,
                                        category_id integer NOT NULL,
                                        assets_group_id integer,
                                        FOREIGN KEY (category_id) REFERENCES categories (id),
                                        FOREIGN KEY (assets_group_id) REFERENCES assets_groups (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Assets table created")
    return 1


def create_assets_preview_table(database):
    """
    Creates the 'assets_preview' table in the specified database if it does not already exist.

    The table includes the following columns:
    - id: A serial primary key.
    - manual_override: A text field for manual override information.
    - preview_path: A text field for storing the preview path.
    - asset_id: An integer foreign key referencing the 'id' column in the 'assets' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS assets_preview (
                                        id serial PRIMARY KEY,
                                        manual_override text,
                                        preview_path text,
                                        asset_id integer NOT NULL,
                                        FOREIGN KEY (asset_id) REFERENCES assets (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Assets preview table created")
    return 1


def create_stages_table(database):
    """
    Creates the 'stages' table in the specified database if it does not already exist.

    The 'stages' table includes the following columns:
        - id: Serial primary key.
        - name: Text, not null, representing the name of the stage.
        - creation_time: Double precision, not null, representing the creation timestamp.
        - creation_user: Text, not null, representing the user who created the stage.
        - state: Text, not null, representing the current state of the stage.
        - assignment: Text, optional, representing the assignment details.
        - work_time: Real, not null, representing the work time in hours.
        - estimated_time: Real, optional, representing the estimated time in hours.
        - start_date: Real, not null, representing the start date as a timestamp.
        - progress: Real, not null, representing the progress percentage.
        - tracking_comment: Text, optional, for tracking comments.
        - default_variant_id: Integer, optional, representing the default variant ID.
        - string: Text, not null, representing a descriptive string.
        - asset_id: Integer, not null, foreign key referencing the 'assets' table.
        - domain_id: Integer, not null, foreign key referencing the 'domains_data' table.
        - priority: Text, not null, representing the priority level.
        - note: Text, optional, for additional notes.

    Foreign key constraints:
        - asset_id references the 'id' column in the 'assets' table.
        - domain_id references the 'id' column in the 'domains_data' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating the successful creation of the 'stages' table.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS stages (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        state text NOT NULL,
                                        assignment text,
                                        work_time real NOT NULL,
                                        estimated_time real,
                                        start_date real NOT NULL,
                                        progress real NOT NULL,
                                        tracking_comment text,
                                        default_variant_id integer,
                                        string text NOT NULL,
                                        asset_id integer NOT NULL,
                                        domain_id integer NOT NULL,
                                        priority text NOT NULL,
                                        note text,
                                        FOREIGN KEY (asset_id) REFERENCES assets (id),
                                        FOREIGN KEY (domain_id) REFERENCES domains_data (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Stages table created")
    return 1


def create_variants_table(database):
    """
    Creates the 'variants' table in the specified database if it does not already exist.

    The 'variants' table includes the following columns:
        - id: Serial primary key.
        - name: Text, not null, representing the name of the variant.
        - creation_time: Double precision, not null, representing the creation timestamp.
        - creation_user: Text, not null, representing the user who created the variant.
        - comment: Text, optional, for additional comments about the variant.
        - default_work_env_id: Integer, optional, representing the default work environment ID.
        - string: Text, not null, representing a descriptive string for the variant.
        - stage_id: Integer, not null, foreign key referencing the 'stages' table.

    Foreign key constraints:
        - stage_id references the 'id' column in the 'stages' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating the successful creation of the 'variants' table.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS variants (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        comment text,
                                        default_work_env_id integer,
                                        string text NOT NULL,
                                        stage_id integer NOT NULL,
                                        FOREIGN KEY (stage_id) REFERENCES stages (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Variants table created")
    return 1


def create_asset_tracking_events_table(database):
    """
    Creates the 'asset_tracking_events' table in the specified database if it does not already exist.

    The 'asset_tracking_events' table includes the following columns:
        - id: Serial primary key.
        - creation_time: Double precision, not null, representing the creation timestamp.
        - creation_user: Text, not null, representing the user who created the event.
        - event_type: Text, not null, representing the type of the event.
        - data: Text, not null, containing additional data related to the event.
        - comment: Text, optional, for additional comments about the event.
        - stage_id: Integer, not null, foreign key referencing the 'stages' table.

    Foreign key constraints:
        - stage_id references the 'id' column in the 'stages' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating the successful creation of the 'asset_tracking_events' table.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS asset_tracking_events (
                                        id serial PRIMARY KEY,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        event_type text NOT NULL,
                                        data text NOT NULL,
                                        comment text,
                                        stage_id integer NOT NULL,
                                        FOREIGN KEY (stage_id) REFERENCES stages (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Asset tracking events table created")
    return 1


def create_work_envs_table(database):
    """
    Creates the 'work_envs' table in the specified database if it does not already exist.

    The 'work_envs' table includes the following columns:
        - id: Serial primary key.
        - name: Text, not null, representing the name of the work environment.
        - creation_time: Double precision, not null, representing the creation timestamp.
        - creation_user: Text, not null, representing the user who created the work environment.
        - variant_id: Integer, not null, foreign key referencing the 'variants' table.
        - lock_id: Integer, optional, representing the ID of the user who locked the work environment.
        - export_extension: Text, optional, representing the file extension for exports.
        - work_time: Real, not null, representing the total work time in hours.
        - string: Text, not null, representing a descriptive string for the work environment.
        - software_id: Integer, not null, foreign key referencing the 'softwares' table.

    Foreign key constraints:
        - variant_id references the 'id' column in the 'variants' table.
        - software_id references the 'id' column in the 'softwares' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating the successful creation of the 'work_envs' table.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS work_envs (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        variant_id integer NOT NULL,
                                        lock_id integer,
                                        export_extension text,
                                        work_time real NOT NULL,
                                        string text NOT NULL,
                                        software_id integer NOT NULL,
                                        FOREIGN KEY (variant_id) REFERENCES variants (id),
                                        FOREIGN KEY (software_id) REFERENCES softwares (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Work envs table created")
    return 1


def create_references_table(database):
    """
    Creates the 'references_data' table in the specified database if it does not already exist.

    The table includes the following columns:
        - id: Primary key, auto-incrementing serial number.
        - creation_time: Timestamp indicating when the record was created.
        - creation_user: Text field indicating the user who created the record.
        - namespace: Text field for the namespace of the reference.
        - count: Text field for the count of references (optional).
        - stage: Text field indicating the stage of the reference.
        - work_env_id: Foreign key referencing the 'work_envs' table.
        - export_id: Foreign key referencing the 'exports' table.
        - export_version_id: Foreign key referencing the 'export_versions' table.
        - auto_update: Integer field indicating whether auto-update is enabled.
        - activated: Integer field indicating whether the reference is activated.

    Foreign key constraints:
        - work_env_id references the 'work_envs' table.
        - export_id references the 'exports' table.
        - export_version_id references the 'export_versions' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS references_data (
                                        id serial PRIMARY KEY,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        namespace text NOT NULL,
                                        count text,
                                        stage text NOT NULL,
                                        work_env_id integer NOT NULL,
                                        export_id integer NOT NULL,
                                        export_version_id integer NOT NULL,
                                        auto_update integer NOT NULL,
                                        activated integer NOT NULL,
                                        FOREIGN KEY (work_env_id) REFERENCES work_envs (id),
                                        FOREIGN KEY (export_id) REFERENCES exports (id),
                                        FOREIGN KEY (export_version_id) REFERENCES export_versions (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("References table created")
    return 1


def create_referenced_groups_table(database):
    """
    Creates the 'referenced_groups_data' table in the specified database if it does not already exist.

    The table includes the following columns:
        - id: Primary key, auto-incrementing serial.
        - creation_time: Timestamp of when the record was created, stored as a double precision value.
        - creation_user: Text field indicating the user who created the record.
        - namespace: Text field for the namespace associated with the record.
        - count: Text field for additional count-related information (optional).
        - group_id: Integer referencing the 'id' column in the 'groups' table.
        - group_name: Text field for the name of the group.
        - work_env_id: Integer referencing the 'id' column in the 'work_envs' table.
        - activated: Integer indicating whether the group is activated (e.g., 1 for active, 0 for inactive).

    Foreign key constraints:
        - group_id references the 'id' column in the 'groups' table.
        - work_env_id references the 'id' column in the 'work_envs' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating the successful creation of the table.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS referenced_groups_data (
                                        id serial PRIMARY KEY,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        namespace text NOT NULL,
                                        count text,
                                        group_id integer NOT NULL,
                                        group_name text NOT NULL,
                                        work_env_id integer NOT NULL,
                                        activated integer NOT NULL,
                                        FOREIGN KEY (group_id) REFERENCES groups (id),
                                        FOREIGN KEY (work_env_id) REFERENCES work_envs (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Referenced groups table created")
    return 1


def create_grouped_references_table(database):
    """
    Creates the 'grouped_references_data' table in the specified database if it does not already exist.

    The table includes the following columns:
        - id: Primary key, serial type.
        - creation_time: Timestamp of creation, double precision, not null.
        - creation_user: User who created the entry, text, not null.
        - namespace: Namespace of the entry, text, not null.
        - count: Count of references, text.
        - stage: Stage of the entry, text, not null.
        - group_id: Foreign key referencing the 'groups' table, integer, not null.
        - export_id: Foreign key referencing the 'exports' table, integer, not null.
        - export_version_id: Foreign key referencing the 'export_versions' table, integer, not null.
        - auto_update: Indicates if auto-update is enabled, integer, not null.
        - activated: Indicates if the entry is activated, integer, not null.

    Foreign key constraints:
        - group_id references the 'groups' table.
        - export_id references the 'exports' table.
        - export_version_id references the 'export_versions' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS grouped_references_data (
                                        id serial PRIMARY KEY,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        namespace text NOT NULL,
                                        count text,
                                        stage text NOT NULL,
                                        group_id integer NOT NULL,
                                        export_id integer NOT NULL,
                                        export_version_id integer NOT NULL,
                                        auto_update integer NOT NULL,
                                        activated integer NOT NULL,
                                        FOREIGN KEY (group_id) REFERENCES groups (id),
                                        FOREIGN KEY (export_id) REFERENCES exports (id),
                                        FOREIGN KEY (export_version_id) REFERENCES export_versions (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Grouped references table created")
    return 1


def create_groups_table(database):
    """
    Creates a 'groups' table in the specified database if it does not already exist.

    The table includes the following columns:
        - id: Serial primary key.
        - name: Text, not null, representing the name of the group.
        - creation_time: Double precision, not null, representing the time of creation.
        - creation_user: Text, not null, representing the user who created the group.
        - color: Text, optional, representing the color associated with the group.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS groups (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        color text
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Groups table created")
    return 1


def create_exports_table(database):
    """
    Creates the 'exports' table in the specified database if it does not already exist.

    The 'exports' table includes the following columns:
        - id: Primary key, auto-incrementing serial number.
        - name: Text field, not null, representing the name of the export.
        - creation_time: Double precision field, not null, representing the time of creation.
        - creation_user: Text field, not null, representing the user who created the export.
        - stage_id: Integer field, not null, foreign key referencing the 'id' column in the 'stages' table.
        - string: Text field, not null, representing additional information about the export.
        - default_export_version: Integer field, optional, representing the default version of the export.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating that the 'exports' table has been created.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS exports (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        stage_id integer NOT NULL,
                                        string text NOT NULL,
                                        default_export_version integer,
                                        FOREIGN KEY (stage_id) REFERENCES stages (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Exports table created")
    return 1


def create_versions_table(database):
    """
    Creates the 'versions' table in the specified database if it does not already exist.

    The 'versions' table includes the following columns:
        - id: Serial primary key.
        - name: Text, not null, representing the name of the version.
        - creation_time: Double precision, not null, representing the creation timestamp.
        - creation_user: Text, not null, representing the user who created the version.
        - comment: Text, optional, for additional comments about the version.
        - file_path: Text, not null, representing the file path of the version.
        - screenshot_path: Text, optional, representing the file path of the screenshot.
        - thumbnail_path: Text, optional, representing the file path of the thumbnail.
        - string: Text, not null, representing a descriptive string for the version.
        - work_env_id: Integer, not null, foreign key referencing the 'work_envs' table.

    Foreign key constraints:
        - work_env_id references the 'id' column in the 'work_envs' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating the successful creation of the 'versions' table.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS versions (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        comment text,
                                        file_path text NOT NULL,
                                        screenshot_path text,
                                        thumbnail_path text,
                                        string text NOT NULL,
                                        work_env_id integer NOT NULL,
                                        FOREIGN KEY (work_env_id) REFERENCES work_envs (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Versions table created")
    return 1


def create_videos_table(database):
    """
    Creates the 'videos' table in the specified database if it does not already exist.

    The 'videos' table includes the following columns:
        - id: Serial primary key.
        - name: Text, not null, representing the name of the video.
        - creation_time: Double precision, not null, representing the creation timestamp.
        - creation_user: Text, not null, representing the user who created the video.
        - comment: Text, optional, for additional comments about the video.
        - file_path: Text, not null, representing the file path of the video.
        - thumbnail_path: Text, optional, representing the file path of the video's thumbnail.
        - variant_id: Integer, not null, foreign key referencing the 'variants' table.

    Foreign key constraints:
        - variant_id references the 'id' column in the 'variants' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating the successful creation of the 'videos' table.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS videos (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        comment text,
                                        file_path text NOT NULL,
                                        thumbnail_path text,
                                        variant_id integer NOT NULL,
                                        FOREIGN KEY (variant_id) REFERENCES variants (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Videos table created")
    return 1


def create_export_versions_table(database):
    """
    Creates the 'export_versions' table in the specified database if it does not already exist.

    The 'export_versions' table includes the following columns:
        - id: Serial primary key.
        - name: Text, not null, representing the name of the export version.
        - creation_time: Double precision, not null, representing the creation timestamp.
        - creation_user: Text, not null, representing the user who created the export version.
        - comment: Text, optional, for additional comments about the export version.
        - files: Text, not null, representing the file paths associated with the export version.
        - stage_id: Integer, not null, foreign key referencing the 'stages' table.
        - work_version_id: Integer, optional, foreign key referencing the 'versions' table.
        - work_version_thumbnail_path: Text, optional, representing the thumbnail path of the work version.
        - software: Text, optional, representing the software used for the export version.
        - string: Text, not null, representing a descriptive string for the export version.
        - export_id: Integer, not null, foreign key referencing the 'exports' table.

    Foreign key constraints:
        - stage_id references the 'id' column in the 'stages' table.
        - export_id references the 'id' column in the 'exports' table.
        - work_version_id references the 'id' column in the 'versions' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating the successful creation of the 'export_versions' table.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS export_versions (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        creation_user text NOT NULL,
                                        comment text,
                                        files text NOT NULL,
                                        stage_id integer NOT NULL,
                                        work_version_id integer,
                                        work_version_thumbnail_path text,
                                        software text,
                                        string text NOT NULL,
                                        export_id integer NOT NULL,
                                        FOREIGN KEY (stage_id) REFERENCES stages (id),
                                        FOREIGN KEY (export_id) REFERENCES exports (id),
                                        FOREIGN KEY (work_version_id) REFERENCES versions (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Export versions table created")
    return 1


def create_softwares_table(database):
    """
    Creates the 'softwares' table in the specified database if it does not already exist.

    The 'softwares' table includes the following columns:
        - id: Serial primary key.
        - name: Text, not null, representing the name of the software.
        - extension: Text, not null, representing the file extension associated with the software.
        - path: Text, optional, representing the file path to the software executable.
        - batch_path: Text, optional, representing the file path to the batch executable.
        - additionnal_scripts: Text, optional, representing additional scripts as a JSON string.
        - additionnal_env: Text, optional, representing additional environment variables as a JSON string.
        - file_command: Text, not null, representing the command to execute when a file is provided.
        - no_file_command: Text, not null, representing the command to execute when no file is provided.
        - batch_file_command: Text, optional, representing the batch command to execute when a file is provided.
        - batch_no_file_command: Text, optional, representing the batch command to execute when no file is provided.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating the successful creation of the 'softwares' table.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS softwares (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        extension text NOT NULL,
                                        path text,
                                        batch_path text,
                                        additionnal_scripts text,
                                        additionnal_env text,
                                        file_command text NOT NULL,
                                        no_file_command text NOT NULL,
                                        batch_file_command text,
                                        batch_no_file_command text
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Softwares table created")
    return 1


def create_settings_table(database):
    """
    Creates a 'settings' table in the specified database if it does not already exist.

    The table includes the following columns:
        - id: Primary key, auto-incrementing serial number.
        - frame_rate: Text field, not null.
        - image_format: Text field, not null.
        - deadline: Real number, not null.
        - users_ids: Text field, not null.
        - mean_render_time: Integer field, default value is 1800.
        - render_nodes_number: Integer field, default value is 1.
        - OCIO: Text field, optional.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS settings (
                                        id serial PRIMARY KEY,
                                        frame_rate text NOT NULL,
                                        image_format text NOT NULL,
                                        deadline real NOT NULL,
                                        users_ids text NOT NULL,
                                        mean_render_time integer NOT NULL DEFAULT 1800,
                                        render_nodes_number integer NOT NULL DEFAULT 1,
                                        OCIO text
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Settings table created")
    return 1


def create_extensions_table(database):
    """
    Creates the 'extensions' table in the specified database if it does not already exist.

    The 'extensions' table includes the following columns:
        - id: Serial primary key.
        - stage: Text, not null, representing the stage of the project.
        - software_id: Integer, not null, foreign key referencing the 'softwares' table.
        - extension: Text, not null, representing the file extension associated with the stage and software.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating the successful creation of the 'extensions' table.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS extensions (
                                        id serial PRIMARY KEY,
                                        stage text NOT NULL,
                                        software_id integer NOT NULL,
                                        extension text NOT NULL
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Extensions table created")
    return 1


def create_events_table(database):
    """
    Creates an 'events' table in the specified database if it does not already exist.

    The table includes the following columns:
        - id: Serial primary key.
        - creation_user: Text, not null, stores the user who created the event.
        - creation_time: Double precision, not null, stores the timestamp of event creation.
        - type: Text, not null, stores the type of the event.
        - title: Text, not null, stores the title of the event.
        - message: Text, not null, stores the main message of the event.
        - data: Text, optional, stores additional data related to the event.
        - additional_message: Text, optional, stores any additional message for the event.
        - image_path: Text, optional, stores the path to an image associated with the event.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: Returns None if the table creation fails.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS events (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        type text NOT NULL,
                                        title text NOT NULL,
                                        message text NOT NULL,
                                        data text,
                                        additional_message text,
                                        image_path text
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Events table created")
    return 1


def create_progress_events_table(database):
    """
    Creates a table named 'progress_events' in the specified database if it does not already exist.

    The table includes the following columns:
        - id: A serial primary key.
        - creation_time: A double precision value representing the creation time.
        - day: A text field representing the day.
        - type: A text field representing the type of the event.
        - name: A text field representing the name of the event.
        - datas_dic: A text field containing additional data in dictionary format.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS progress_events (
                                        id serial PRIMARY KEY,
                                        creation_time double precision NOT NULL,
                                        day text NOT NULL,
                                        type text NOT NULL,
                                        name text NOT NULL,
                                        datas_dic text NOT NULL
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Progress table created")
    return 1


def create_tag_groups_table(database):
    """
    Creates the 'tag_groups' table in the specified database if it does not already exist.

    The table includes the following columns:
        - id: A serial primary key.
        - creation_user: A text field indicating the user who created the tag group.
        - creation_time: A double precision field indicating the creation timestamp.
        - name: A text field for the name of the tag group.
        - user_ids: A text field containing user IDs associated with the tag group.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS tag_groups (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        name text NOT NULL,
                                        user_ids text NOT NULL
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Tag groups table created")
    return 1


def create_playlists_table(database):
    """
    Creates the 'playlists' table in the specified database if it does not already exist.

    The table includes the following columns:
        - id: A serial primary key.
        - creation_user: The username of the user who created the playlist (text, not null).
        - creation_time: The timestamp of when the playlist was created (double precision, not null).
        - name: The name of the playlist (text, not null).
        - data: The playlist data (text, not null).
        - thumbnail_path: The file path to the playlist's thumbnail (text, nullable).
        - last_save_user: The username of the user who last saved the playlist (text, not null).
        - last_save_time: The timestamp of the last save operation (double precision, not null).

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating that the 'playlists' table was created.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS playlists (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        name text NOT NULL,
                                        data text NOT NULL,
                                        thumbnail_path text,
                                        last_save_user text NOT NULL,
                                        last_save_time double precision NOT NULL
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Playlists table created")
    return 1


def create_assets_groups_table(database):
    """
    Creates the 'assets_groups' table in the specified database if it does not already exist.

    The 'assets_groups' table includes the following columns:
        - id: Serial primary key.
        - creation_user: Text, not null, representing the user who created the asset group.
        - creation_time: Double precision, not null, representing the creation timestamp.
        - name: Text, not null, representing the name of the asset group.
        - color: Text, not null, representing the color associated with the asset group.
        - category_id: Integer, not null, foreign key referencing the 'categories' table.

    Foreign key constraints:
        - category_id references the 'id' column in the 'categories' table.

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.

    Logs:
        Logs a message indicating the successful creation of the 'assets_groups' table.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS assets_groups (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        name text NOT NULL,
                                        color text NOT NULL,
                                        category_id integer NOT NULL,
                                        FOREIGN KEY (category_id) REFERENCES categories (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Assets groups table created")
    return 1


def create_shelf_scripts_table(database):
    """
    Creates the 'shelf_scripts' table in the specified database if it does not already exist.

    The table includes the following columns:
        - id: Primary key, auto-incrementing serial number.
        - creation_user: Text field to store the user who created the entry.
        - creation_time: Double precision field to store the creation timestamp.
        - name: Text field to store the name of the script.
        - py_file: Text field to store the path to the Python file (optional).
        - help: Text field to store help or description information (optional).
        - only_subprocess: Boolean field to indicate if the script should only run in a subprocess.
        - icon: Text field to store the path to the icon file (optional).
        - type: Text field to store the type of the script (required).
        - position: Integer field to store the position or order of the script (required).

    Args:
        database: The database connection object where the table will be created.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: If the table creation fails or already exists.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS shelf_scripts (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        creation_time double precision NOT NULL,
                                        name text NOT NULL,
                                        py_file text,
                                        help text,
                                        only_subprocess bool,
                                        icon text,
                                        type text NOT NULL,
                                        position integer NOT NULL
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Shelf scripts table created")
    return 1
