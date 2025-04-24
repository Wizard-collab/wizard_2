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
This module provides a comprehensive set of functions for managing a repository system.
It includes functionalities for handling projects, users, quotes, IP addresses, artefacts,
and attack events. The module interacts with a database to perform CRUD operations and
ensures data integrity through validations and logging.

Key Features:
- Project Management: Create, remove, and modify projects.
- User Management: Create, modify, and manage user privileges, passwords, and profiles.
- Quotes System: Add, score, and manage quotes.
- Artefacts Management: Initialize, retrieve, and update artefact stocks.
- IP Management: Track and manage IP addresses associated with users and projects.
- Attack Events: Log and retrieve attack events.
- Database Initialization: Create and initialize database tables for the repository.

Dependencies:
- Python modules: time, socket, json, logging
- Wizard modules: db_utils, support, tools, path_utils, environment, image
- Variables: repository_vars, game_vars

Logging:
- Logs warnings, errors, and informational messages to track operations and issues.

Usage:
- Import this module and call the desired functions to interact with the repository system.
- Ensure the database and required tables are initialized before using the module.

Author: Leo BRUNEL
License: MIT License
"""

# Python modules
import time
import socket
import json
import logging

# Wizard modules
from wizard.core import db_utils
from wizard.core import support
from wizard.core import tools
from wizard.core import path_utils
from wizard.core import environment
from wizard.core import image
from wizard.vars import repository_vars
from wizard.vars import game_vars

logger = logging.getLogger(__name__)


def create_project(project_name, project_path, project_password, project_image=None):
    """
    Creates a new project in the repository.

    Args:
        project_name (str): The name of the project. Must not be empty.
        project_path (str): The file path where the project will be stored. Must not be empty.
        project_password (str): The password for the project. Must not be empty.
        project_image (Optional[Any]): An optional image for the project. If not provided, a random image will be generated.

    Returns:
        int: The ID of the newly created project if successful.
        None: If the project creation fails due to validation errors or other issues.

    Raises:
        None

    Notes:
        - Logs warnings if required fields are missing or if the project already exists.
        - Ensures the user has administrator privileges before creating the project.
        - Encrypts the project password before storing it in the database.
        - Generates a random project image if none is provided.
        - Validates that the project name and path are unique within the repository.
    """
    # Initialize a flag to check if all required fields are provided
    do_creation = 1

    # Validate the project name
    if project_name == '':
        logger.warning("Please provide a project name")
        do_creation = 0

    # Validate the project path
    if project_path == '':
        logger.warning("Please provide a project path")
        do_creation = 0

    # Validate the project password
    if project_password == '':
        logger.warning("Please provide a password")
        do_creation = 0

    # Generate a random project image if none is provided
    if project_image is None:
        project_image = image.project_random_image(project_name)

    # Process the project image into ASCII format
    project_image_ascii = process_project_image(project_image)

    # If any required field is missing, abort the creation process
    if not do_creation:
        return

    # Check if the project name already exists in the repository
    if project_name in get_projects_names_list():
        logger.warning(f'Project {project_name} already exists')
        return

    # Check if the project path is already assigned to another project
    if project_path in get_projects_paths_list():
        logger.warning(
            f'Path {project_path} already assigned to another project')
        return

    # Ensure the user has administrator privileges
    if not get_user_row_by_name(environment.get_user())['administrator']:
        logger.warning("You need to be administrator to create a project")
        return

    # Create a new project row in the database
    project_id = db_utils.create_row('repository',
                                     'projects',
                                     ('project_name',
                                      'project_path',
                                      'project_password',
                                      'project_image',
                                      'creation_user',
                                      'creation_time'),
                                     (project_name,
                                         project_path,
                                         tools.encrypt_string(
                                             project_password),
                                         project_image_ascii,
                                         environment.get_user(),
                                         time.time()))

    # If the project creation fails, return None
    if not project_id:
        return

    # Log the successful creation of the project
    logger.info(f'Project {project_name} added to repository')

    # Return the ID of the newly created project
    return project_id


def remove_project_row(project_id):
    """
    Removes a project row from the 'projects' table in the 'repository' database.

    This function attempts to delete a row corresponding to the given project ID
    from the specified database table. If the deletion is successful, it logs
    the action and returns 1. If the deletion fails, the function exits without
    performing further actions.

    Args:
        project_id (int): The unique identifier of the project to be removed.

    Returns:
        int or None: Returns 1 if the project row is successfully removed, 
        otherwise returns None.
    """
    if not db_utils.delete_row('repository', 'projects', project_id):
        return
    logger.info('Project row removed')
    return 1


def get_administrator_pass():
    """
    Retrieves the password for the administrator user.

    This function fetches the user row corresponding to the username 'admin'
    by calling `get_user_row_by_name`. If the user row exists, it returns the
    password associated with the administrator. If the user row does not exist,
    the function returns None.

    Returns:
        str or None: The password of the administrator if the user exists,
        otherwise None.
    """
    user_row = get_user_row_by_name('admin')
    if not user_row:
        return
    return user_row['pass']


def get_projects_list():
    """
    Retrieve the list of projects from the 'repository' database table.

    Returns:
        list: A list of rows representing the projects retrieved from the database.
    """
    return db_utils.get_rows('repository', 'projects')


def get_projects_names_list():
    """
    Retrieves a list of all project names from the 'projects' table in the 'repository' database.

    Returns:
        list: A list of project names.
    """
    return db_utils.get_rows('repository', 'projects', 'project_name')


def get_projects_paths_list():
    """
    Retrieves a list of project paths from the 'repository' database table.

    This function queries the 'repository' database table for rows in the 
    'projects' column and extracts the 'project_path' field for each row.

    Returns:
        list: A list of project paths retrieved from the database.
    """
    return db_utils.get_rows('repository', 'projects', 'project_path')


def get_project_row_by_name(name):
    """
    Retrieve the first project row from the 'projects' table in the 'repository' database
    that matches the specified project name.

    Args:
        name (str): The name of the project to search for.

    Returns:
        dict or None: The first matching project row as a dictionary if found, 
                      or None if no matching project is found.

    Logs:
        Logs an error message if no project is found with the specified name.
    """
    projects_rows = db_utils.get_row_by_column_data('repository',
                                                    'projects',
                                                    ('project_name', name))
    if projects_rows is None or len(projects_rows) < 1:
        logger.error("Project not found")
        return
    return projects_rows[0]


def get_project_row(project_id, column='*'):
    """
    Retrieve a specific row from the 'projects' table in the 'repository' database.

    Args:
        project_id (int): The ID of the project to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', which retrieves all columns.

    Returns:
        dict or None: A dictionary representing the first matching project row if found, 
                      or None if no matching row is found.

    Logs:
        Logs an error message if the project is not found.
    """
    projects_rows = db_utils.get_row_by_column_data('repository',
                                                    'projects',
                                                    ('id', project_id),
                                                    column)
    if projects_rows is None or len(projects_rows) < 1:
        logger.error("Project not found")
        return
    return projects_rows[0]


def get_project_path_by_name(name):
    """
    Retrieve the file path of a project by its name.

    Args:
        name (str): The name of the project.

    Returns:
        str or None: The file path of the project if found, otherwise None.
    """
    project_row = get_project_row_by_name(name)
    if not project_row:
        return
    return project_row['project_path']


def modify_project_password(project_name,
                            project_password,
                            new_password,
                            administrator_pass=''):
    """
    Modify the password of a specified project.

    This function updates the password of a project in the repository
    after verifying the administrator password and the current project password.

    Args:
        project_name (str): The name of the project whose password is to be modified.
        project_password (str): The current password of the project.
        new_password (str): The new password to set for the project.
        administrator_pass (str, optional): The administrator password for authentication. Defaults to an empty string.

    Returns:
        int or None: Returns 1 if the password is successfully modified, 
                        None if the operation fails due to invalid credentials or other issues.

    Logs:
        - Logs a warning if the administrator password is incorrect.
        - Logs a warning if the project name is not found.
        - Logs a warning if the current project password is incorrect.
        - Logs an info message if the password is successfully modified.
    """
    # Verify the administrator password
    if not tools.decrypt_string(get_administrator_pass(),
                                administrator_pass):
        logger.warning('Wrong administrator pass')
        return

    # Check if the project name exists in the repository
    if project_name not in get_projects_names_list():
        logger.warning(f'{project_name} not found')
        return

    # Verify the current project password
    if not tools.decrypt_string(
            get_project_row_by_name(project_name)['project_password'],
            project_password):
        logger.warning(f'Wrong password for {project_name}')
        return

    # Update the project password in the database
    if not db_utils.update_data('repository',
                                'projects',
                                ('project_password',
                                 tools.encrypt_string(new_password)),
                                ('project_name', project_name)):
        return

    # Log the successful password modification
    logger.info(f'{project_name} password modified')
    return 1


def modify_project_image(project_name, project_image):
    """
    Modify the image associated with a project by updating it in the repository.

    Args:
        project_name (str): The name of the project whose image is to be modified.
        project_image (str): The file path to the new project image.

    Returns:
        int or None: Returns 1 if the project image was successfully modified, 
                     otherwise returns None.

    Logs:
        - Logs a warning if the provided project_image does not exist.
        - Logs an info message if the project image is successfully modified.

    Notes:
        - If the project_image is None or empty, the function exits early.
        - The image is processed into an ASCII format before being updated in the database.
        - The database update is performed on the 'repository' table under the 'projects' section.
    """
    if not project_image:
        return
    if not path_utils.isfile(project_image):
        logger.warning(f'{project_image} not found')
        return
    project_image_ascii = process_project_image(project_image)
    if not db_utils.update_data('repository',
                                'projects',
                                ('project_image', project_image_ascii),
                                ('project_name', project_name)):
        return
    logger.info(f'{project_name} image modified')
    return 1


def process_project_image(image_file):
    """
    Processes an image file by performing a series of transformations and 
    returns the processed image data as a string.

    Steps performed:
    1. Converts the input image file to bytes.
    2. Converts the byte data to a PIL (Pillow) image object.
    3. Resizes the image to a fixed width of 600 pixels while maintaining aspect ratio.
    4. Crops the height of the image to 337 pixels.
    5. Converts the modified PIL image back to bytes.
    6. Converts the byte data to a string representation.

    Args:
        image_file: The input image file to be processed.

    Returns:
        str: The processed image data as a string.
    """
    bytes_data = image.convert_image_to_bytes(image_file)
    pillow_image = image.convert_image_bytes_to_pillow(bytes_data)
    pillow_image, fixed_width, height_size = image.resize_image_with_fixed_width(
        pillow_image, 600)
    pillow_image = image.crop_image_height(pillow_image, 337)
    bytes_data = image.convert_PILLOW_image_to_bytes(pillow_image)
    return image.convert_bytes_to_str_data(bytes_data)


def create_user(user_name,
                password,
                email,
                administrator_pass='',
                profile_picture=None,
                championship_participation=1):
    """
    Creates a new user in the repository.

    Args:
        user_name (str): The name of the user. Must not be empty.
        password (str): The password for the user. Must not be empty.
        email (str): The email address of the user. Must not be empty.
        administrator_pass (str, optional): The administrator password for granting admin privileges. Defaults to ''.
        profile_picture (str, optional): The file path to the user's profile picture. Defaults to None.
        championship_participation (int, optional): Indicates if the user participates in championships. Defaults to 1.

    Returns:
        int: Returns 1 if the user is successfully created, otherwise None.

    Logs:
        - Logs warnings if required fields are missing or if the user already exists.
        - Logs an info message upon successful user creation, including their privilege level.
    """
    # Flag to determine if the user creation process should proceed
    do_creation = 1

    # Validate the user name
    if user_name == '':
        logger.warning('Please provide a user name')
        do_creation = None

    # Validate the password
    if password == '':
        logger.warning('Please provide a password')
        do_creation = None

    # Validate the email
    if email == '':
        logger.warning('Please provide an email')
        do_creation = None

    # Abort the creation process if any required field is missing
    if not do_creation:
        return

    # Check if the user name already exists in the repository
    if user_name in get_user_names_list():
        logger.warning(f'User {user_name} already exists')
        return

    # Determine if the user should have administrator privileges
    administrator = 0
    if tools.decrypt_string(get_administrator_pass(),
                            administrator_pass):
        administrator = 1

    # Handle the profile picture
    if profile_picture:
        # If a profile picture is provided, ensure the file exists
        if not path_utils.isfile(profile_picture):
            profile_picture = image.user_random_image(user_name)
    else:
        # Generate a random profile picture if none is provided
        profile_picture = image.user_random_image(user_name)

    # Convert the profile picture to ASCII format
    profile_picture_ascii = image.convert_image_to_str_data(
        profile_picture, 100)

    # Create the user in the database
    if not db_utils.create_row('repository',
                               'users',
                               ('user_name',
                                'pass',
                                'email',
                                'profile_picture',
                                'xp',
                                'total_xp',
                                'work_time',
                                'comments_count',
                                'deaths',
                                'level',
                                'life',
                                'administrator',
                                'coins',
                                'championship_participation',
                                'championship_ban_time',
                                'artefacts',
                                'keeped_artefacts'),
                               (user_name,
                                tools.encrypt_string(password),
                                email,
                                profile_picture_ascii,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                100,
                                administrator,
                                0,
                                int(championship_participation),
                                None,
                                json.dumps({}),
                                json.dumps({}))):
        return

    # Log the successful creation of the user
    info = f"User {user_name} created"
    if administrator:
        info += ' ( privilege : administrator )'
    else:
        info += ' ( privilege : user )'
    logger.info(info)

    # Return success
    return 1


def modify_user_profile_picture(user_name, profile_picture):
    """
    Modifies the profile picture of a user in the repository.

    Args:
        user_name (str): The username of the user whose profile picture is to be modified.
        profile_picture (str): The file path to the new profile picture.

    Returns:
        int or None: Returns 1 if the profile picture was successfully modified, 
                     otherwise returns None.

    Logs:
        - Logs a warning if the provided profile picture file does not exist.
        - Logs an info message if the profile picture is successfully modified.

    Notes:
        - The profile picture is converted to ASCII string data before being stored.
        - The function does nothing if the `profile_picture` argument is empty or invalid.
    """
    if not profile_picture:
        return
    if not path_utils.isfile(profile_picture):
        logger.warning(f'{profile_picture} not found')
        return
    profile_picture_ascii = image.convert_image_to_str_data(
        profile_picture, 100)
    if not db_utils.update_data('repository',
                                'users',
                                ('profile_picture', profile_picture_ascii),
                                ('user_name', user_name)):
        return
    logger.info(f'{user_name} profile picture modified')
    return 1


def upgrade_user_privilege(user_name, administrator_pass):
    """
    Upgrade a user's privilege to administrator if certain conditions are met.

    Args:
        user_name (str): The username of the user whose privilege is to be upgraded.
        administrator_pass (str): The administrator password for authentication.

    Returns:
        int or None: Returns 1 if the privilege is successfully upgraded, 
                     None if the operation fails or conditions are not met.

    Logs:
        - Logs an error if the user is not found.
        - Logs an info message if the user is already an administrator.
        - Logs a warning if the provided administrator password is incorrect.
        - Logs an info message upon successful privilege upgrade.

    Conditions:
        - The user must exist in the system.
        - The user must not already be an administrator.
        - The provided administrator password must match the stored password.
        - The database update operation must succeed.
    """
    if user_name not in get_user_names_list():
        logger.error(f'{user_name} not found')
        return
    user_row = get_user_row_by_name(user_name)
    if user_row['administrator']:
        logger.info(f'User {user_name} is already administrator')
        return
    if not tools.decrypt_string(get_administrator_pass(),
                                administrator_pass):
        logger.warning('Wrong administrator pass')
        return
    if not db_utils.update_data('repository',
                                'users',
                                ('administrator', 1),
                                ('user_name', user_name)):
        return
    logger.info(f'Administrator privilege set for {user_name}')
    return 1


def downgrade_user_privilege(user_name, administrator_pass):
    """
    Downgrades the privilege of a user from administrator to a regular user.

    Args:
        user_name (str): The username of the user whose privileges are to be downgraded.
        administrator_pass (str): The administrator password for authentication.

    Returns:
        int or None: Returns 1 if the privilege downgrade is successful, 
                     None if the operation fails or is not applicable.

    Logs:
        - Logs an error if the user is not found.
        - Logs an info message if the user is already not an administrator.
        - Logs a warning if the provided administrator password is incorrect.
        - Logs an info message upon successful privilege downgrade.

    Notes:
        - The function checks if the user exists and is an administrator.
        - Validates the administrator password before performing the downgrade.
        - Updates the database to reflect the privilege change.
    """
    if user_name not in get_user_names_list():
        logger.error(f'{user_name} not found')
        return
    user_row = get_user_row_by_name(user_name)
    if not user_row['administrator']:
        logger.info(f'User {user_name} is not administrator')
        return
    if not tools.decrypt_string(get_administrator_pass(),
                                administrator_pass):
        logger.warning('Wrong administrator pass')
        return
    if not db_utils.update_data('repository',
                                'users',
                                ('administrator', 0),
                                ('user_name', user_name)):
        return
    logger.info(f'Privilege downgraded to user for {user_name}')
    return 1


def modify_user_password(user_name, password, new_password):
    """
    Modify the password of a user in the repository.

    Args:
        user_name (str): The username of the user whose password is to be modified.
        password (str): The current password of the user.
        new_password (str): The new password to set for the user.

    Returns:
        int or None: Returns 1 if the password was successfully modified, 
                     or None if the operation failed (e.g., user not found, 
                     incorrect current password, or database update failure).

    Logs:
        - Logs a warning if the provided current password is incorrect.
        - Logs an info message if the password is successfully modified.
    """
    user_row = get_user_row_by_name(user_name)
    if not user_row:
        return
    if not tools.decrypt_string(user_row['pass'], password):
        logger.warning(f'Wrong password for {user_name}')
        return
    if not db_utils.update_data('repository',
                                'users',
                                ('pass',
                                 tools.encrypt_string(new_password)),
                                ('user_name', user_name)):
        return
    logger.info(f'{user_name} password modified')
    return 1


def reset_user_password(user_name, administrator_pass, new_password):
    """
    Resets the password for a specified user.

    Args:
        user_name (str): The username of the account whose password is to be reset.
        administrator_pass (str): The administrator's password for authentication.
        new_password (str): The new password to set for the user.

    Returns:
        int or None: Returns 1 if the password was successfully reset, 
                     None if the operation failed due to invalid user, 
                     incorrect administrator password, or database update failure.

    Logs:
        - Logs a warning if the administrator password is incorrect.
        - Logs an info message if the user's password is successfully modified.
    """
    user_row = get_user_row_by_name(user_name)
    if not user_row:
        return
    if not tools.decrypt_string(get_administrator_pass(),
                                administrator_pass):
        logger.warning("Wrong administrator_pass")
        return
    if not db_utils.update_data('repository',
                                'users',
                                ('pass',
                                 tools.encrypt_string(new_password)),
                                ('user_name', user_name)):
        return
    logger.info(f'{user_name} password modified')
    return 1


def get_users_list():
    """
    Retrieve a list of users from the 'users' table in the 'repository' database.

    The users are ordered by their 'level' in descending order, and for users
    with the same level, by their 'total_xp' in descending order.

    Returns:
        list: A list of rows representing users, sorted by the specified criteria.
    """
    return db_utils.get_rows('repository', 'users', order='level DESC, total_xp DESC;')

    def get_users_list_by_xp_order():
        """
        Retrieves a list of users from the 'users' table in the 'repository' database,
        ordered by their total experience points (total_xp) in descending order.

        Returns:
            list: A list of rows representing users, sorted by total_xp in descending order.
        """
        return db_utils.get_rows('repository', 'users', order='total_xp DESC;')


def get_users_list_by_deaths_order():
    """
    Retrieves a list of users from the 'users' table in the 'repository' database,
    ordered by the number of deaths in descending order.

    Returns:
        list: A list of rows representing users, sorted by their death count in descending order.
    """
    return db_utils.get_rows('repository', 'users', order='deaths DESC;')


def get_users_list_by_work_time_order():
    """
    Retrieves a list of users from the 'users' table in the 'repository' database,
    ordered by their work time in descending order.

    Returns:
        list: A list of rows representing users, sorted by their work time in descending order.
    """
    return db_utils.get_rows('repository', 'users', order='work_time DESC;')


def get_users_list_by_comments_count_order():
    """
    Retrieves a list of users from the 'users' table in the 'repository' database,
    ordered by the number of comments they have made in descending order.

    Returns:
        list: A list of rows representing users, sorted by their comments count in descending order.
    """
    return db_utils.get_rows('repository', 'users', order='comments_count DESC;')


def get_user_names_list():
    """
    Retrieves a list of all user names from the 'users' table in the 'repository' database.

    Returns:
        list: A list of user names.
    """
    return db_utils.get_rows('repository', 'users', 'user_name')


def get_user_row_by_name(name, column='*'):
    """
    Retrieve a user row from the 'users' table in the 'repository' database 
    by matching the specified user name.

    Args:
        name (str): The name of the user to search for.
        column (str, optional): The column(s) to retrieve from the database. 
                                Defaults to '*' (all columns).

    Returns:
        dict or None: The first matching user row as a dictionary if found, 
                      or None if no matching user is found.

    Logs:
        Logs an error message if no user is found.
    """
    users_rows = db_utils.get_row_by_column_data('repository',
                                                 'users',
                                                 ('user_name', name),
                                                 column)
    if users_rows is None or len(users_rows) < 1:
        logger.error("User not found")
        return
    return users_rows[0]


def get_user_data(user_id, column='*'):
    """
    Retrieve user data from the 'users' table in the 'repository' database.

    Args:
        user_id (int): The ID of the user to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*', 
                                which retrieves all columns.

    Returns:
        dict or None: A dictionary containing the user's data if found, or None if 
                      the user is not found.

    Logs:
        Logs an error message if the user is not found.
    """
    users_rows = db_utils.get_row_by_column_data('repository',
                                                 'users',
                                                 ('id', user_id),
                                                 column)
    if users_rows is None or len(users_rows) < 1:
        logger.error("User not found")
        return
    return users_rows[0]


def modify_user_xp(user_name, xp):
    """
    Modify the experience points (XP) of a user in the repository.

    Args:
        user_name (str): The name of the user whose XP is to be modified.
        xp (int): The new XP value to set for the user.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    return db_utils.update_data('repository',
                                'users',
                                ('xp', xp),
                                ('user_name', user_name))


def modify_user_total_xp(user_name, total_xp):
    """
    Updates the total experience points (XP) of a user in the database.

    Args:
        user_name (str): The name of the user whose XP is to be updated.
        total_xp (int): The new total XP value to be set for the user.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    return db_utils.update_data('repository',
                                'users',
                                ('total_xp', total_xp),
                                ('user_name', user_name))


def modify_user_championship_participation(user_name, championship_participation, ban_time=game_vars._default_ban_time_):
    """
    Modifies the championship participation status of a user and applies a temporary ban 
    to prevent further modifications within a specified time period.

    Args:
        user_name (str): The name of the user whose participation is being modified.
        championship_participation (bool): The new participation status for the user.
        ban_time (float, optional): The duration of the ban in seconds. Defaults to 
            `game_vars._default_ban_time_`.

    Returns:
        None

    Logs:
        - A warning if the user is still under a ban, including the remaining ban time.
        - An info message when the participation is successfully modified, including the ban duration.

    Notes:
        - If the user is currently banned from modifying their participation, the function 
          will not proceed with the update.
        - Updates are made to the 'users' table in the 'repository' database.
    """
    user_row = get_user_row_by_name(user_name)
    championship_ban_time = user_row['championship_ban_time']
    if championship_ban_time:
        if time.time() < championship_ban_time:
            time_left = tools.convert_seconds_to_string_time_with_days(
                championship_ban_time - time.time())
            logger.warning(
                f"You can't modify your participation for now. You will be able to switch again in {time_left}")
            return
    db_utils.update_data('repository',
                         'users',
                         ('championship_ban_time', time.time()+ban_time),
                         ('user_name', user_name))
    db_utils.update_data('repository',
                         'users',
                         ('championship_participation',
                             championship_participation),
                         ('user_name', user_name))
    logger.info(
        f"{user_name} participation modified, ban time : {tools.convert_seconds_to_string_time_with_days(ban_time)}")


def increase_user_comments_count(user_name):
    """
    Increases the comment count for a specific user in the database.

    This function retrieves the current comment count for the given user
    from the 'users' table in the 'repository' database. If the user has
    an existing comment count, it increments the count by 1. If the user
    does not have a comment count, it initializes the count to 1. The
    updated comment count is then saved back to the database.

    Args:
        user_name (str): The username of the user whose comment count
                         needs to be updated.

    Returns:
        bool: True if the update operation was successful, False otherwise.
    """
    old_comments_count = db_utils.get_row_by_column_data('repository',
                                                         'users',
                                                         ('user_name', user_name),
                                                         'comments_count')
    if old_comments_count and old_comments_count != []:
        comments_count = old_comments_count[0] + 1
    else:
        comments_count = 1
    return db_utils.update_data('repository',
                                'users',
                                ('comments_count', comments_count),
                                ('user_name', user_name))


def add_user_work_time(user_name, work_time_to_add):
    """
    Updates the work time of a user by adding the specified amount of work time.

    This function retrieves the current work time of the user from the database.
    If the user already has recorded work time, the new work time is calculated
    by adding the provided `work_time_to_add` to the existing work time.
    If no work time is found for the user, the provided `work_time_to_add` is used
    as the initial work time. The updated work time is then saved back to the database.

    Args:
        user_name (str): The name of the user whose work time is to be updated.
        work_time_to_add (int or float): The amount of work time to add to the user's record.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    old_work_time = db_utils.get_row_by_column_data('repository',
                                                    'users',
                                                    ('user_name', user_name),
                                                    'work_time')
    if old_work_time and old_work_time != []:
        work_time = old_work_time[0] + work_time_to_add
    else:
        work_time = work_time_to_add
    return db_utils.update_data('repository',
                                'users',
                                ('work_time', work_time),
                                ('user_name', user_name))


def add_death(user_name):
    """
    Increment the death count for a user in the 'users' table of the 'repository' database.

    This function retrieves the current death count for the specified user from the database.
    If the user already has a death count, it increments the count by 1. If the user does not
    have a death count, it initializes the count to 1. The updated death count is then saved
    back to the database.

    Args:
        user_name (str): The username of the user whose death count is to be updated.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    old_deaths = db_utils.get_row_by_column_data('repository',
                                                 'users',
                                                 ('user_name', user_name),
                                                 'deaths')
    if old_deaths and old_deaths != []:
        deaths = old_deaths[0] + 1
    else:
        deaths = 1
    return db_utils.update_data('repository',
                                'users',
                                ('deaths', deaths),
                                ('user_name', user_name))


def modify_user_level(user_name, new_level):
    """
    Modify the level of a user in the repository.

    This function updates the level of a specified user in the database.
    If the update is successful, it logs the change and returns 1.
    If the update fails, it returns None.

    Args:
        user_name (str): The name of the user whose level is to be modified.
        new_level (int): The new level to assign to the user.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise None.
    """
    if not db_utils.update_data('repository',
                                'users',
                                ('level', new_level),
                                ('user_name', user_name)):
        return
    logger.info(f'{user_name} is now level {new_level}')
    return 1


def modify_user_life(user_name, life):
    """
    Modifies the life attribute of a user in the repository.

    If the provided life value exceeds 100, it is capped at 100. 
    Updates the user's life value in the database and logs the change.

    Args:
        user_name (str): The name of the user whose life is being modified.
        life (int): The new life value to set for the user.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise None.
    """
    if life > 100:
        life = 100
    if not db_utils.update_data('repository',
                                'users',
                                ('life', life),
                                ('user_name', user_name)):
        return
    logger.debug(f'{user_name} life is {life}%')
    return 1


def modify_user_coins(user_name, coins):
    """
    Modify the number of coins for a specific user in the database.

    This function updates the 'coins' value for a user identified by their
    username in the 'users' table of the 'repository' database. If the update
    is successful, it logs the new coin count for the user.

    Args:
        user_name (str): The username of the user whose coin count is to be modified.
        coins (int): The new coin value to be set for the user.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.
    """
    if not db_utils.update_data('repository',
                                'users',
                                ('coins', coins),
                                ('user_name', user_name)):
        return
    logger.info(f'{user_name} have now {coins} coins')
    return 1


def add_user_coins(user_name, coins):
    """
    Adds a specified number of coins to a user's account.

    This function retrieves the current coin balance for the specified user,
    updates the balance by adding the given number of coins, and logs the
    transaction. If the update fails, the function returns without making
    any changes.

    Args:
        user_name (str): The name of the user whose coin balance is to be updated.
        coins (int): The number of coins to add to the user's balance.

    Returns:
        int: Returns 1 if the update is successful, otherwise returns None.
    """
    user_coins = get_user_row_by_name(user_name, 'coins')
    if not db_utils.update_data('repository',
                                'users',
                                ('coins', user_coins+coins),
                                ('user_name', user_name)):
        return
    logger.debug(f'{user_name} just won {coins} coins !')
    return 1


def remove_user_coins(user_name, coins):
    """
    Deducts a specified number of coins from a user's account. If the resulting
    coin balance is less than zero, it is set to zero. Updates the user's coin
    balance in the database and logs the transaction.

    Args:
        user_name (str): The name of the user whose coins are to be deducted.
        coins (int): The number of coins to deduct.

    Returns:
        int: Returns 1 if the operation is successful, otherwise None.
    """
    user_coins = get_user_row_by_name(user_name, 'coins')
    new_coins = user_coins-coins
    if new_coins < 0:
        new_coins = 0
    if not db_utils.update_data('repository',
                                'users',
                                ('coins', new_coins),
                                ('user_name', user_name)):
        return
    logger.debug(f'{user_name} just lost {coins} coins !')
    return 1


def modify_user_artefacts(user_name, artefacts_list):
    """
    Modify the artefacts associated with a specific user in the repository.

    This function updates the 'artefacts' field for a given user in the 'repository' database.
    The artefacts list is serialized to JSON format before being stored.

    Args:
        user_name (str): The name of the user whose artefacts are to be modified.
        artefacts_list (list): A list of artefacts to associate with the user.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise returns None.

    Logs:
        Logs a debug message indicating that the artefacts list has been modified.
    """
    if not db_utils.update_data('repository',
                                'users',
                                ('artefacts', json.dumps(artefacts_list)),
                                ('user_name', user_name)):
        return
    logger.debug(f'Artefacts list modified')
    return 1


def modify_keeped_artefacts(user_name, artefacts_dic):
    """
    Modify the 'keeped_artefacts' field for a specific user in the repository.

    This function updates the 'keeped_artefacts' field in the database for the
    given user with the provided artefacts dictionary. If the update is successful,
    it logs a debug message and returns 1. If the update fails, it returns None.

    Args:
        user_name (str): The username of the user whose 'keeped_artefacts' field
                         needs to be updated.
        artefacts_dic (dict): A dictionary containing the artefacts to be stored
                              in the 'keeped_artefacts' field.

    Returns:
        int or None: Returns 1 if the update is successful, otherwise None.
    """
    if not db_utils.update_data('repository',
                                'users',
                                ('keeped_artefacts', json.dumps(artefacts_dic)),
                                ('user_name', user_name)):
        return
    logger.debug(f'Keeped artefacts dic modified')
    return 1


def modify_user_email(user_name, email):
    """
    Updates the email address of a user in the repository.

    Args:
        user_name (str): The username of the user whose email is to be updated.
        email (str): The new email address to be set for the user. 
                     Must not be an empty string.

    Returns:
        bool: True if the email was successfully updated, False otherwise.

    Logs:
        Logs a warning if the provided email is an empty string.
    """
    if email == '':
        logger.warning('Please enter a valid email')
        return
    return db_utils.update_data('repository',
                                'users',
                                ('email', email),
                                ('user_name', user_name))


def is_admin():
    """
    Checks if the current user is an administrator.

    This function retrieves the current user's information and determines 
    if they have administrator privileges. If the user is not an 
    administrator, a warning is logged.

    Returns:
        bool: True if the user is an administrator, False otherwise.
    """
    is_admin = get_user_row_by_name(environment.get_user(), 'administrator')
    if not is_admin:
        logger.warning("You are not administrator")
    return is_admin


def add_quote(content):
    """
    Adds a new quote to the repository if it meets the required conditions.

    Args:
        content (str): The content of the quote to be added. Must be a non-empty
                       string with a maximum length of 100 characters.

    Returns:
        int or None: The ID of the newly created quote if successful, or None
                     if the operation fails or the input is invalid.

    Logs:
        - Logs a warning if the content is empty or exceeds 100 characters.
        - Logs an info message when a quote is successfully added.

    Side Effects:
        - Creates a new row in the 'quotes' table of the 'repository' database.
        - Sends the quote content to the support system.
    """
    if content is None or content == '':
        logger.warning("Please enter quote content")
        return
    if len(content) > 100:
        logger.warning("Your quote needs to be under 100 characters")
        return
    quote_id = db_utils.create_row('repository',
                                   'quotes',
                                   ('creation_user',
                                    'content',
                                    'score',
                                    'voters'),
                                   (environment.get_user(),
                                    content,
                                    json.dumps([]),
                                    json.dumps([])))
    if not quote_id:
        return
    logger.info("Quote added")
    support.send_quote(content)
    return quote_id


def add_quote_score(quote_id, score):
    """
    Adds a score to a quote in the repository if all conditions are met.
    This function performs several checks before adding a score to a quote:
    - Ensures the score is an integer between 0 and 5.
    - Ensures the quote exists in the repository.
    - Prevents users from voting for their own quotes.
    - Prevents users from voting for the same quote multiple times.
    If all conditions are satisfied, the score is added to the quote's score list,
    and the user is added to the list of voters.
    Args:
        quote_id (int): The unique identifier of the quote to be scored.
        score (int): The score to be added to the quote (must be between 0 and 5).
    Returns:
        None: The function does not return a value. It logs warnings or success messages
        based on the outcome of the operation.
    """
    # Initialize a sanity flag to validate the input score
    sanity = 1

    # Check if the score is within the valid range (0 to 5)
    if not 0 <= score <= 5:
        logger.warning(f"Please note between 0 and 5")
        sanity = 0

    # Check if the score is an integer
    if type(score) != int:
        logger.warning(f"{score} is not an integer")
        sanity = 0

    # If the sanity checks fail, abort the operation
    if not sanity:
        return

    # Retrieve the quote row from the database using the quote ID
    current_quote_row = db_utils.get_row_by_column_data('repository',
                                                        'quotes',
                                                        ('id', quote_id))

    # Check if the quote exists in the database
    if current_quote_row is None or current_quote_row == []:
        logger.warning("Quote not found")
        return

    # Prevent users from voting for their own quotes
    if current_quote_row[0]['creation_user'] == environment.get_user():
        logger.warning("You can't vote for your own quote")
        return

    # Retrieve the list of voters for the quote
    voters_list = json.loads(current_quote_row[0]['voters'])

    # Check if the user has already voted for the quote
    if environment.get_user() in voters_list:
        logger.warning("You already voted for this quote")
        return

    # Retrieve the current scores list for the quote
    current_scores_list = json.loads(current_quote_row[0]['score'])

    # Append the new score to the scores list
    current_scores_list.append(score)

    # Add the current user to the voters list
    voters_list.append(environment.get_user())

    # Update the scores list in the database
    if not db_utils.update_data('repository',
                                'quotes',
                                ('score',
                                 json.dumps(current_scores_list)),
                                ('id',
                                 quote_id)):
        return
    logger.info("Quote score updated")

    # Update the voters list in the database
    if not db_utils.update_data('repository',
                                'quotes',
                                ('voters',
                                 json.dumps(voters_list)),
                                ('id',
                                 quote_id)):
        return
    logger.info("Quote voters updated")


def get_quote_data(quote_id, column='*'):
    """
    Retrieve data for a specific quote from the 'quotes' table in the 'repository' database.

    Args:
        quote_id (int): The ID of the quote to retrieve.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' (all columns).

    Returns:
        dict or None: A dictionary containing the data for the specified quote if found,
                      or None if the quote does not exist.

    Logs:
        Logs an error message if the quote is not found.
    """
    quotes_rows = db_utils.get_row_by_column_data('repository',
                                                  'quotes',
                                                  ('id', quote_id),
                                                  column)
    if quotes_rows is None or len(quotes_rows) < 1:
        logger.error("Quote not found")
        return
    return quotes_rows[0]


def remove_quote(quote_id):
    """
    Removes a quote from the repository if the current user is the creator of the quote.

    Args:
        quote_id (int): The unique identifier of the quote to be removed.

    Returns:
        int or None: Returns 1 if the quote is successfully removed, None otherwise.

    Behavior:
        - Retrieves the quote data using the provided quote_id.
        - If the quote does not exist, the function exits without performing any action.
        - Checks if the current user is the creator of the quote. If not, logs a warning and exits.
        - Attempts to delete the quote from the database. If unsuccessful, exits without further action.
        - Logs an informational message upon successful removal of the quote.
    """
    quote_row = get_quote_data(quote_id)
    if not quote_row:
        return
    if environment.get_user() != quote_row['creation_user']:
        logger.warning("You did not created this quote")
        return
    if not db_utils.delete_row('repository', 'quotes', quote_id):
        return
    logger.info("Quote removed from repository")
    return 1


def get_all_quotes(column='*'):
    """
    Retrieve all quotes from the 'quotes' table in the 'repository' database.

    Args:
        column (str): The column(s) to retrieve from the table. Defaults to '*', 
                      which selects all columns.

    Returns:
        list: A list of rows retrieved from the 'quotes' table.
    """
    return db_utils.get_rows('repository', 'quotes', column)


def get_user_quotes(column='*'):
    """
    Retrieves user-specific quotes from the 'quotes' table in the 'repository' database.

    Args:
        column (str): The column(s) to retrieve from the database. Defaults to '*' (all columns).

    Returns:
        list: A list of rows matching the user's data from the specified column(s).
    """
    return db_utils.get_row_by_column_data('repository', 'quotes', ('creation_user', environment.get_user()))


def get_ips(column='*'):
    """
    Retrieve rows from the 'ips_wrap' table in the 'repository' database.

    Args:
        column (str): The column(s) to retrieve. Defaults to '*' to select all columns.

    Returns:
        list: A list of rows retrieved from the specified table and column(s).
    """
    return db_utils.get_rows('repository', 'ips_wrap', column)


def add_ip_user():
    """
    Adds the current machine's IP address to the 'ips_wrap' table in the 'repository' database
    if it is not already present.

    The function retrieves the current machine's IP address and checks if it exists in the list
    of IPs retrieved from the database. If the IP is not found, it attempts to create a new row
    in the 'ips_wrap' table with the IP address and default values for 'user_id' and 'project_id'.
    Logs a debug message if the IP is successfully added.

    Returns:
        int or None: Returns 1 if the IP is successfully added, otherwise returns None.
    """
    ip = socket.gethostbyname(socket.gethostname())
    ip_rows = get_ips('ip')
    if not ip_rows:
        ip_rows = []
    if ip in ip_rows:
        return
    if not db_utils.create_row('repository',
                               'ips_wrap',
                               ('ip', 'user_id', 'project_id'),
                               (ip, None, None)):
        return
    logger.debug("Machine ip added to ips wrap table")
    return 1


def flush_ips():
    """
    Removes all IP addresses from the 'ips_wrap' table in the repository.

    This function performs the following steps:
    - Checks if the current user has administrator privileges.
    - Deletes all rows from the 'ips_wrap' table in the 'repository' database.
    - Logs an informational message upon successful deletion.

    Returns:
        int or None: Returns 1 if the operation is successful, otherwise None.

    Notes:
        - If the user is not an administrator, the function exits without performing any action.
        - If the deletion operation fails, the function exits without further action.
    """
    if not is_admin():
        return
    if not db_utils.delete_rows('repository', 'ips_wrap'):
        return
    logger.info("All users ip removed")
    return 1


def flush_user_ip():
    """
    Removes the current machine's IP address from the 'ips_wrap' table in the 'repository' database
    if it exists.

    This function retrieves the current machine's IP address and checks if it is present in the
    list of IPs fetched from the database. If the IP address is found, it attempts to delete the
    corresponding row from the 'ips_wrap' table. Logs a debug message upon successful deletion.

    Returns:
        int: Returns 1 if the IP address was successfully removed, otherwise None.
    """
    ip = socket.gethostbyname(socket.gethostname())
    ip_rows = get_ips('ip')
    if not ip_rows:
        ip_rows = []
    if ip not in ip_rows:
        return
    if not db_utils.delete_row('repository',
                               'ips_wrap',
                               ip, 'ip'):
        return
    logger.debug("Machine ip removed from ips wrap table")
    return 1


def update_current_ip_data(column, data):
    """
    Updates the current IP data in the 'repository' database table.

    This function retrieves the current machine's IP address and updates the 
    specified column with the provided data in the 'ips_wrap' table of the 
    'repository' database. If the column being updated is 'user_id', it also 
    triggers the `unlog_project` function.

    Args:
        column (str): The name of the column to update.
        data (Any): The data to be set in the specified column.

    Returns:
        int or None: Returns 1 if the column is not 'user_id' and the update 
        is successful. Returns the result of `unlog_project` if the column is 
        'user_id'. Returns None if the update fails.

    Logs:
        Logs a debug message if the IP wrap data is successfully updated.

    Note:
        - The function relies on `socket.gethostbyname` and `socket.gethostname` 
          to determine the current machine's IP address.
        - The `db_utils.update_data` function is used to perform the database update.
    """
    ip = socket.gethostbyname(socket.gethostname())
    if not db_utils.update_data('repository',
                                'ips_wrap',
                                (column, data),
                                ('ip', ip)):
        return
    logger.debug("Ip wrap data updated")
    if column != 'user_id':
        return 1
    return unlog_project()


def unlog_project():
    """
    Unlogs the current project by clearing the associated project ID for the 
    current machine's IP address in the 'repository' database table.

    This function retrieves the current machine's IP address and updates the 
    'repository' table to set the 'project_id' to None for the corresponding 
    IP address. If the update is successful, it logs a debug message indicating 
    that the project has been unlogged and returns 1. If the update fails, the 
    function simply returns without performing any further actions.

    Returns:
        int or None: Returns 1 if the project was successfully unlogged, 
        otherwise returns None.
    """
    ip = socket.gethostbyname(socket.gethostname())
    if not db_utils.update_data('repository',
                                'ips_wrap',
                                ('project_id', None),
                                ('ip', ip)):
        return
    logger.debug("Project unlogged")
    return 1


def add_attack_event(user, destination_user, artefact):
    """
    Adds an attack event to the repository.

    This function creates a new row in the 'attack_events' table of the 
    'repository' database. The row contains information about the user 
    initiating the attack, the target user, the artefact involved, and 
    the timestamp of the attack.

    Args:
        user (str): The username of the user initiating the attack.
        destination_user (str): The username of the target user.
        artefact (str): The artefact associated with the attack.

    Returns:
        None: If the row creation fails, the function returns None.
    """
    if not db_utils.create_row('repository',
                               'attack_events',
                               ('creation_user', 'destination_user',
                                'artefact', 'attack_date'),
                               (user, destination_user, artefact, time.time())):
        return


def get_all_attack_events(column='*'):
    """
    Retrieve all attack events from the 'attack_events' table in the 'repository' database.

    Args:
        column (str): The specific column(s) to retrieve. Defaults to '*' to select all columns.

    Returns:
        list: A list of rows representing the attack events from the database.
    """
    return db_utils.get_rows('repository', 'attack_events', column)


def get_all_artefacts_stocks(column='*'):
    """
    Retrieves all artefact stock data from the 'artefacts' table in the 'repository' database.

    Args:
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' to select all columns.

    Returns:
        list: A list of rows representing the artefact stock data from the database.
    """
    return db_utils.get_rows('repository', 'artefacts', column)


def init_artefacts_stock():
    """
    Initializes the artefacts stock in the repository.

    This function retrieves all existing artefact stocks from the repository.
    If no artefacts are found, it initializes an empty list. It then iterates
    through the artefacts defined in the `game_vars.artefacts_dic` dictionary.
    For each artefact not already present in the repository, it creates a new
    row in the 'repository' table with the artefact name and its stock value.

    Dependencies:
        - `get_all_artefacts_stocks`: Function to fetch all artefact stocks.
        - `game_vars.artefacts_dic`: Dictionary containing artefact details.
        - `db_utils.create_row`: Utility to insert a new row into the database.

    Raises:
        - Any exceptions raised by `get_all_artefacts_stocks` or `db_utils.create_row`.

    Note:
        Ensure that `game_vars.artefacts_dic` and the database utilities are
        properly initialized before calling this function.
    """
    repository_artefacts = get_all_artefacts_stocks('artefact')
    if repository_artefacts is None:
        repository_artefacts = []
    for artefact in game_vars.artefacts_dic.keys():
        if artefact not in repository_artefacts:
            db_utils.create_row('repository',
                                'artefacts',
                                ('artefact',
                                    'stock'),
                                (artefact,
                                    game_vars.artefacts_dic[artefact]['stock']))


def get_artefact_stock(artefact):
    """
    Retrieves the stock information for a given artefact from the repository.

    Args:
        artefact (str): The name or identifier of the artefact to look up.

    Returns:
        Any: The stock information of the artefact if found, otherwise None.

    Logs:
        Logs an error message if the artefact is not found in the repository.
    """
    artefact_rows = db_utils.get_row_by_column_data('repository',
                                                    'artefacts',
                                                    ('artefact', artefact),
                                                    'stock')
    if artefact_rows is None or len(artefact_rows) < 1:
        logger.error(f"Artefact {artefact} not found")
        return
    return artefact_rows[0]


def remove_artefact_stock(artefact):
    """
    Decreases the stock count of a specified artefact by 1 if the stock is greater than 0.
    Logs a warning if the stock is already empty.
    Updates the stock value in the database.

    Args:
        artefact (str): The name or identifier of the artefact whose stock is to be reduced.

    Returns:
        bool: True if the database update was successful, False otherwise.
              Returns None if the stock is already empty.
    """
    stock = get_artefact_stock(artefact)
    if stock > 0:
        new_stock = stock - 1
    else:
        logger.warning(f"{artefact} stock already empty")
        return
    return db_utils.update_data('repository',
                                'artefacts',
                                ('stock', new_stock),
                                ('artefact', artefact))


def add_artefact_stock(artefact):
    """
    Increment the stock count of a specified artefact in the repository.

    Args:
        artefact (str): The identifier of the artefact whose stock is to be incremented.

    Returns:
        bool: True if the stock update was successful, False otherwise.
    """
    stock = get_artefact_stock(artefact)
    return db_utils.update_data('repository',
                                'artefacts',
                                ('stock', stock+1),
                                ('artefact', artefact))


def get_current_ip_data(column='*'):
    """
    Retrieve data for the current machine's IP address from the 'repository' database.

    Args:
        column (str): The column(s) to retrieve from the database. Defaults to '*', 
                      which retrieves all columns.

    Returns:
        dict or None: A dictionary containing the data for the current IP address if found, 
                      otherwise None.

    Logs:
        Logs an error message if the IP address is not found in the database.
    """
    ip = socket.gethostbyname(socket.gethostname())
    ip_rows = db_utils.get_row_by_column_data('repository',
                                              'ips_wrap',
                                              ('ip', ip),
                                              column)
    if ip_rows is None or len(ip_rows) < 1:
        logger.error("Ip not found")
        return
    return ip_rows[0]


def init_repository(admin_password, admin_email):
    """
    Initializes the repository by performing the following actions:
    1. Creates an admin user with the provided password and email.
    2. Initializes the quotes system.
    3. Sets up the artefacts stock.

    Args:
        admin_password (str): The password for the admin user.
        admin_email (str): The email address for the admin user.

    Returns:
        int: Returns 1 upon successful initialization.
    """
    create_admin_user(admin_password, admin_email)
    init_quotes()
    init_artefacts_stock()
    return 1


def init_quotes():
    """
    Initializes the quotes in the repository by iterating through a predefined list of default quotes.
    For each quote, a new row is created in the 'quotes' table of the 'repository' database with the
    following fields:
        - creation_user: Set to 'admin'.
        - content: The quote text.
        - score: An empty JSON array (default value).
        - voters: An empty JSON array (default value).

    This function relies on:
        - `repository_vars._default_quotes_list_`: A predefined list of default quotes.
        - `db_utils.create_row`: A utility function to insert rows into the database.

    Raises:
        Any exceptions that occur during database operations.
    """
    for quote in repository_vars._default_quotes_list_:
        db_utils.create_row('repository',
                            'quotes',
                            ('creation_user',
                                'content',
                                'score',
                                'voters'),
                            ('admin',
                                quote,
                                json.dumps([]),
                                json.dumps([])))


def create_repository_database():
    """
    Creates the repository database and initializes its tables.

    This function checks if the repository database exists and creates it if it does not.
    It then initializes the database by creating the following tables:
    - Users table
    - Projects table
    - IP wrap table
    - Quotes table
    - Attack events table
    - Artefacts table

    Returns:
        int: Returns 1 if the database and tables are successfully created, otherwise None.
    """
    if not db_utils.create_database(environment.get_repository()):
        return
    create_users_table()
    create_projects_table()
    create_ip_wrap_table()
    create_quotes_table()
    create_attack_events_table()
    create_artefacts_table()
    return 1


def is_repository_database(repository_name=None):
    """
    Check if a repository database exists.

    This function verifies the existence of a database associated with a given
    repository name. If no repository name is provided, it retrieves the default
    repository name from the environment.

    Args:
        repository_name (str, optional): The name of the repository. If not provided,
            the default repository name is fetched from the environment.

    Returns:
        bool: True if the repository database exists, False otherwise.
    """
    if not repository_name:
        repository_name = environment.get_repository()
    else:
        repository_name = f"repository_{repository_name}"
    return db_utils.check_database_existence(repository_name)


def create_admin_user(admin_password, admin_email):
    """
    Creates an administrator user in the repository database.

    Args:
        admin_password (str): The password for the admin user. It will be encrypted before storage.
        admin_email (str): The email address for the admin user.

    Returns:
        int: Returns 1 if the admin user is successfully created.
        None: Returns None if the user creation fails.

    Notes:
        - The function generates a random profile picture for the admin user.
        - The admin user is initialized with default values for various attributes such as XP, level, coins, etc.
        - Logs a message indicating successful creation of the admin user.
    """
    profile_picture = image.convert_image_to_str_data(
        image.user_random_image('admin'), 100)
    if not db_utils.create_row('repository',
                               'users',
                               ('user_name',
                                'pass',
                                'email',
                                'profile_picture',
                                'xp',
                                'total_xp',
                                'work_time',
                                'comments_count',
                                'deaths',
                                'level',
                                'life',
                                'administrator',
                                'coins',
                                'championship_participation',
                                'championship_ban_time',
                                'artefacts',
                                'keeped_artefacts'),
                               ('admin',
                                tools.encrypt_string(admin_password),
                                admin_email,
                                profile_picture,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                100,
                                1,
                                0,
                                1,
                                None,
                                json.dumps({}),
                                json.dumps({}))):
        return
    logger.info('Admin user created')
    return 1


def create_users_table():
    """
    Creates the 'users' table in the repository database if it does not already exist.

    The table includes the following columns:
        - id: A unique identifier for each user (primary key).
        - user_name: The username of the user (text, not null).
        - pass: The encrypted password of the user (text, not null).
        - email: The email address of the user (text, not null).
        - profile_picture: The profile picture of the user in text format (not null).
        - xp: The current experience points of the user (integer, not null).
        - total_xp: The total experience points accumulated by the user (integer, not null).
        - work_time: The total work time of the user (real, not null).
        - comments_count: The number of comments made by the user (integer, not null).
        - deaths: The number of deaths recorded for the user (integer, not null).
        - level: The current level of the user (integer, not null).
        - life: The life percentage of the user (integer, not null).
        - administrator: Indicates if the user is an administrator (integer, not null).
        - coins: The number of coins the user has (integer, not null).
        - championship_participation: Indicates if the user participates in championships (integer, not null).
        - championship_ban_time: The time until the user is banned from championships (real, nullable).
        - artefacts: A JSON string representing the user's artefacts (text, not null).
        - keeped_artefacts: A JSON string representing the user's kept artefacts (text, not null).

    Returns:
        int: Returns 1 if the table is successfully created, otherwise None.

    Logs:
        Logs an informational message if the table is successfully created.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS users (
                                        id serial PRIMARY KEY,
                                        user_name text NOT NULL,
                                        pass text NOT NULL,
                                        email text NOT NULL,
                                        profile_picture text NOT NULL,
                                        xp integer NOT NULL,
                                        total_xp integer NOT NULL,
                                        work_time real NOT NULL,
                                        comments_count integer NOT NULL,
                                        deaths integer NOT NULL,
                                        level integer NOT NULL,
                                        life integer NOT NULL,
                                        administrator integer NOT NULL,
                                        coins integer NOT NULL,
                                        championship_participation integer NOT NULL,
                                        championship_ban_time real,
                                        artefacts text NOT NULL,
                                        keeped_artefacts text NOT NULL
                                    );"""
    if not db_utils.create_table(environment.get_repository(), sql_cmd):
        return
    logger.info("Users table created")
    return 1


def create_projects_table():
    """
    Creates the 'projects' table in the database if it does not already exist.

    The table includes the following columns:
        - id: Serial primary key.
        - project_name: Text, not null, the name of the project.
        - project_path: Text, not null, the path to the project.
        - project_password: Text, not null, the password for the project.
        - project_image: Text, optional, the image associated with the project.
        - creation_user: Text, not null, the user who created the project.
        - creation_time: Double precision, not null, the timestamp of project creation.

    Utilizes the `db_utils.create_table` function to execute the SQL command.
    Logs a message if the table is successfully created.

    Returns:
        int: 1 if the table is created successfully.
        None: If the table creation fails or already exists.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS projects (
                                        id serial PRIMARY KEY,
                                        project_name text NOT NULL,
                                        project_path text NOT NULL,
                                        project_password text NOT NULL,
                                        project_image text,
                                        creation_user text NOT NULL,
                                        creation_time double precision NOT NULL
                                    );"""
    if not db_utils.create_table(environment.get_repository(), sql_cmd):
        return
    logger.info("Projects table created")
    return 1


def create_ip_wrap_table():
    """
    Creates the 'ips_wrap' table in the database if it does not already exist.

    The table includes the following columns:
        - id: A serial primary key.
        - ip: A unique text field for storing IP addresses.
        - user_id: An integer referencing the 'id' column in the 'users' table.
        - project_id: An integer referencing the 'id' column in the 'projects' table.

    Foreign key constraints:
        - user_id references the 'id' column in the 'users' table.
        - project_id references the 'id' column in the 'projects' table.

    Logs a message indicating successful creation of the table.

    Returns:
        int: Returns 1 if the table is successfully created, otherwise returns None.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS ips_wrap (
                                        id serial PRIMARY KEY,
                                        ip text NOT NULL UNIQUE,
                                        user_id integer,
                                        project_id integer,
                                        FOREIGN KEY (user_id) REFERENCES users (id),
                                        FOREIGN KEY (project_id) REFERENCES projects (id)
                                    );"""
    if not db_utils.create_table(environment.get_repository(), sql_cmd):
        return
    logger.info("Ips wrap table created")
    return 1


def create_quotes_table():
    """
    Creates the 'quotes' table in the database if it does not already exist.

    The table includes the following columns:
        - id: A serial primary key.
        - creation_user: A text field representing the user who created the quote (not null).
        - content: A text field containing the quote content (not null).
        - score: A text field representing the score of the quote (not null).
        - voters: A text field containing information about voters (not null).

    Uses the `db_utils.create_table` function to execute the SQL command for table creation.
    Logs a message if the table is successfully created.

    Returns:
        int: Returns 1 if the table is created successfully.
        None: If the table creation fails or already exists.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS quotes (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        content text NOT NULL,
                                        score text NOT NULL,
                                        voters text NOT NULL
                                    );"""
    if not db_utils.create_table(environment.get_repository(), sql_cmd):
        return
    logger.info("Quotes table created")
    return 1


def create_attack_events_table():
    """
    Creates the 'attack_events' table in the database if it does not already exist.

    The table includes the following columns:
        - id: A serial primary key.
        - creation_user: A text field representing the user who created the attack event.
        - destination_user: A text field representing the target user of the attack event.
        - artefact: A text field representing the artefact involved in the attack event.
        - attack_date: A real number representing the date of the attack event.

    Utilizes the `db_utils.create_table` function to execute the SQL command for table creation.
    Logs a message if the table is successfully created.

    Returns:
        int: Returns 1 if the table is created successfully.
        None: If the table creation fails or already exists.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS attack_events (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        destination_user text NOT NULL,
                                        artefact text NOT NULL,
                                        attack_date real NOT NULL
                                    );"""
    if not db_utils.create_table(environment.get_repository(), sql_cmd):
        return
    logger.info("Attack events table created")
    return 1


def create_artefacts_table():
    """
    Creates the 'artefacts' table in the database if it does not already exist.

    The table includes the following columns:
        - id: A serial primary key.
        - artefact: A text field that cannot be null.
        - stock: A real number field that cannot be null.

    Uses the `db_utils.create_table` function to execute the SQL command for table creation.
    Logs a message indicating successful creation of the table.

    Returns:
        int: Returns 1 if the table is successfully created.
        None: Returns None if the table creation fails.
    """
    sql_cmd = """ CREATE TABLE IF NOT EXISTS artefacts (
                                        id serial PRIMARY KEY,
                                        artefact text NOT NULL,
                                        stock real NOT NULL
                                    );"""
    if not db_utils.create_table(environment.get_repository(), sql_cmd):
        return
    logger.info("Artefacts table created")
    return 1
