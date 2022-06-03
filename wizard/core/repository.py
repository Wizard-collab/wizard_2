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

# This module is used to manage and access 
# the repository database

# The repository database stores the following informations:
#       - The users list ( name, hashed password, email )
#       - The projects list ( name, path, hashed password )
#       - The ip wraps ( roughly looks like cookies in web )

# Python modules
import os
import time
import socket
import json
import logging

# Wizard modules
from wizard.core import db_utils
from wizard.core import tools
from wizard.core import path_utils
from wizard.core import environment
from wizard.core import image
from wizard.vars import repository_vars
from wizard.vars import ressources

logger = logging.getLogger(__name__)

def create_project(project_name, project_path, project_password, project_image = None):
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

    if project_image is None:
        project_image = image.project_random_image(project_name)   

    project_image_ascii = process_project_image(project_image)
    
    if do_creation:
        if project_name not in get_projects_names_list():
            if project_path not in get_projects_paths_list():
                if get_user_row_by_name(environment.get_user())['administrator']:
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
                                    tools.encrypt_string(project_password),
                                    project_image_ascii,
                                    environment.get_user(),
                                    time.time()))
                    if project_id:
                        logger.info(f'Project {project_name} added to repository')
                        return project_id
                    else:
                        return None
                else:
                    logger.warning("You need to be administrator to create a project")
                    return None
            else:
                logger.warning(f'Path {project_path} already assigned to another project')
                return None
        else:
            logger.warning(f'Project {project_name} already exists')
            return None
    else:
        return None

def remove_project_row(project_id):
    if db_utils.delete_row('repository', 'projects', project_id):
        logger.info('Project row removed')
        return 1
    else:
        return None

def get_administrator_pass():
    user_row = get_user_row_by_name('admin')
    if user_row:
        return user_row['pass']

def get_projects_list():
    projects_rows = db_utils.get_rows('repository', 'projects')
    return projects_rows

def get_projects_names_list():
    projects_rows = db_utils.get_rows('repository', 'projects', 'project_name')
    return projects_rows

def get_projects_paths_list():
    projects_rows = db_utils.get_rows('repository', 'projects', 'project_path')
    return projects_rows

def get_project_row_by_name(name):
    projects_rows = db_utils.get_row_by_column_data('repository',
                                                    'projects',
                                                    ('project_name', name))
    if len(projects_rows) >= 1:
        return projects_rows[0]
    else:
        logger.error("Project not found")
        return None

def get_project_row(project_id, column='*'):
    projects_rows = db_utils.get_row_by_column_data('repository',
                                                    'projects',
                                                    ('id', project_id),
                                                    column)
    return projects_rows[0]

def get_project_path_by_name(name):
    return get_project_row_by_name(name)['project_path']

def modify_project_password(project_name,
                            project_password,
                            new_password,
                            administrator_pass=''):
    if tools.decrypt_string(get_administrator_pass(),
                            administrator_pass):
        if project_name in get_projects_names_list():
            if tools.decrypt_string(
                    get_project_row_by_name(project_name)['project_password'],
                    project_password):
                if db_utils.update_data('repository',
                            'projects',
                            ('project_password', tools.encrypt_string(new_password)),
                            ('project_name', project_name)):
                        logger.info(f'{project_name} password modified')
                        return 1
                else:
                    return None
            else:
                logger.warning(f'Wrong password for {project_name}')
        else:
            logger.warning(f'{project_name} not found')
    else:
        logger.warning('Wrong administrator pass')

def modify_project_image(project_name, project_image):
    if project_image:
        if path_utils.isfile(project_image):
            project_image_ascii = process_project_image(project_image)
            if db_utils.update_data('repository',
                                    'projects',
                                    ('project_image', project_image_ascii),
                                    ('project_name', project_name)):
                logger.info(f'{project_name} image modified')
                return 1
            else:
                return None
        else:
            logger.warning(f'{project_image} not found')
            return None
    else:
        return None

def process_project_image(image_file):
    bytes_data = image.convert_image_to_bytes(image_file)
    pillow_image = image.convert_image_bytes_to_pillow(bytes_data)
    pillow_image, fixed_width, height_size = image.resize_image_with_fixed_width(pillow_image, 500)
    pillow_image = image.crop_image_height(pillow_image, 282)
    bytes_data = image.convert_PILLOW_image_to_bytes(pillow_image)
    return image.convert_bytes_to_str_data(bytes_data)

def create_user(user_name,
                    password,
                    email,
                    administrator_pass='',
                    profile_picture=None):
    do_creation = 1
    if user_name == '':
        logger.warning('Please provide a user name')
        do_creation = None
    if password == '':
        logger.warning('Please provide a password')
        do_creation = None
    if email == '':
        logger.warning('Please provide an email')
        do_creation = None
        
    if do_creation:
        if user_name not in get_user_names_list():
            administrator = 0
            if tools.decrypt_string(get_administrator_pass(),
                                    administrator_pass):
                administrator = 1
            if profile_picture:
                if not path_utils.isfile(profile_picture):
                    profile_picture = image.user_random_image(user_name)
            else:
                profile_picture = image.user_random_image(user_name)
            profile_picture_ascii = image.convert_image_to_str_data(profile_picture, 100)
            if db_utils.create_row('repository',
                        'users', 
                        ('user_name',
                            'pass',
                            'email',
                            'profile_picture',
                            'xp',
                            'total_xp',
                            'level',
                            'life',
                            'administrator'), 
                        (user_name,
                            tools.encrypt_string(password),
                            email,
                            profile_picture_ascii,
                            0,
                            0,
                            0,
                            100,
                            administrator)):

                info = f"User {user_name} created"
                if administrator:
                    info += ' ( privilege : administrator )'
                else:
                    info += ' ( privilege : user )'
                logger.info(info)
                return 1
            else:
                return None
        else:
            logger.warning(f'User {user_name} already exists')
            return None

def modify_user_profile_picture(user_name, profile_picture):
    if profile_picture:
        if path_utils.isfile(profile_picture):
            profile_picture_ascii = image.convert_image_to_str_data(profile_picture, 100)
            if db_utils.update_data('repository',
                                    'users',
                                    ('profile_picture', profile_picture_ascii),
                                    ('user_name', user_name)):
                logger.info(f'{user_name} profile picture modified')
                return 1
            else:
                return None
        else:
            logger.warning(f'{profile_picture} not found')
            return None
    else:
        return None

def upgrade_user_privilege(user_name, administrator_pass):
    if user_name in get_user_names_list():
        user_row = get_user_row_by_name(user_name)
        if not user_row['administrator']:
            if tools.decrypt_string(get_administrator_pass(),
                                        administrator_pass):
                if db_utils.update_data('repository',
                                        'users',
                                        ('administrator',1),
                                        ('user_name', user_name)):
                    logger.info(f'Administrator privilege set for {user_name}')
            else:
                logger.warning('Wrong administrator pass')
        else:
            logger.info(f'User {user_name} is already administrator')
    else:
        logger.error(f'{user_name} not found')

def downgrade_user_privilege(user_name, administrator_pass):
    if user_name in get_user_names_list():
        user_row = get_user_row_by_name(user_name)
        if user_row['administrator']:
            if tools.decrypt_string(get_administrator_pass(),
                                        administrator_pass):
                if db_utils.update_data('repository',
                                        'users',
                                        ('administrator',0),
                                        ('user_name', user_name)):
                    logger.info(f'Privilege downgraded to user for {user_name}')
                    return 1
            else:
                logger.warning('Wrong administrator pass')
                return None
        else:
            logger.info(f'User {user_name} is not administrator')
            return None
    else:
        logger.error(f'{user_name} not found')
        return None

def modify_user_password(user_name, password, new_password):
    user_row = get_user_row_by_name(user_name)
    if user_row:
        if tools.decrypt_string(user_row['pass'], password):
            if db_utils.update_data('repository',
                                    'users',
                                    ('pass',
                                        tools.encrypt_string(new_password)),
                                    ('user_name', user_name)):
                    logger.info(f'{user_name} password modified')
                    return 1
            else:
                return None
        else:
            logger.warning(f'Wrong password for {user_name}')
            return None

def get_users_list():
    users_rows = db_utils.get_rows('repository', 'users', order='level DESC, xp DESC;')
    return users_rows

def get_user_names_list():
    users_rows = db_utils.get_rows('repository', 'users', 'user_name')
    return users_rows

def get_user_row_by_name(name, column='*'):
    users_rows = db_utils.get_row_by_column_data('repository',
                                                    'users',
                                                    ('user_name', name),
                                                    column)
    if users_rows and len(users_rows) >= 1:
        return users_rows[0]
    else:
        logger.error("User not found")
        return None

def get_user_data(user_id, column='*'):
    users_rows = db_utils.get_row_by_column_data('repository',
                                                    'users',
                                                    ('id', user_id),
                                                    column)
    if users_rows and len(users_rows) >= 1:
        return users_rows[0]
    else:
        logger.error("User not found")
        return None

def modify_user_xp(user_name, xp):
    if db_utils.update_data('repository',
                                'users',
                                ('xp', xp),
                                ('user_name', user_name)):
        logger.debug(f'{user_name} won some xps')
        return 1
    else:
        return None

def modify_user_total_xp(user_name, total_xp):
    if db_utils.update_data('repository',
                                'users',
                                ('total_xp', total_xp),
                                ('user_name', user_name)):
        return 1
    else:
        return None

def modify_user_level(user_name, new_level):
    if db_utils.update_data('repository',
                            'users',
                            ('level', new_level),
                            ('user_name', user_name)):
        logger.info(f'{user_name} is now level {new_level}')
        return 1
    else:
        return None

def modify_user_life(user_name, life):
    if db_utils.update_data('repository',
                                    'users',
                                    ('life', life),
                                    ('user_name', user_name)):
        logger.debug(f'{user_name} life is {life}%')
        return 1
    else:
        return None

def modify_user_email(user_name, email):
    if email != '':
        if db_utils.update_data('repository',
                                        'users',
                                        ('email', email),
                                        ('user_name', user_name)):
            return 1
        else:
            return None
    else:
        logger.warning('Please enter a valid email')
        return None

def is_admin():
    is_admin = get_user_row_by_name(environment.get_user(), 'administrator')
    if not is_admin:
        logger.info("You are not administrator")
    return is_admin

def add_quote(content):
    quote_id = None
    if content and content != '':
        if len(content)<=100:
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
            if quote_id:
                logger.info("Quote added")
        else:
            logger.warning("Your quote needs to be under 100 characters")
    else:
        logger.warning("Please enter quote content")
    return quote_id

def add_quote_score(quote_id, score):
    sanity = 1
    if not 0 <= score <= 5:
        logger.warning(f"Please note between 0 and 5")
        sanity = 0
    if type(score) != int:
        logger.warning(f"{score} is not an integer")
        sanity = 0
    if sanity:
        current_quote_row = db_utils.get_row_by_column_data('repository',
                                                        'quotes',
                                                        ('id', quote_id))

        if current_quote_row is not None:
            if current_quote_row[0]['creation_user'] != environment.get_user():
                voters_list = json.loads(current_quote_row[0]['voters'])
                if environment.get_user() not in voters_list:
                    current_scores_list = json.loads(current_quote_row[0]['score'])
                    current_scores_list.append(score)
                    voters_list.append(environment.get_user())
                    if db_utils.update_data('repository',
                                                    'quotes',
                                                    ('score',
                                                        json.dumps(current_scores_list)),
                                                    ('id',
                                                        quote_id)):
                        logger.info("Quote score updated")
                    if db_utils.update_data('repository',
                                                    'quotes',
                                                    ('voters',
                                                        json.dumps(voters_list)),
                                                    ('id',
                                                        quote_id)):
                        logger.info("Quote voters updated")
                else:
                    logger.warning("You already voted for this quote")
            else:
                logger.warning("You can't vote for your own quote")

def get_quote_data(quote_id, column='*'):
    quotes_rows = db_utils.get_row_by_column_data('repository',
                                                    'quotes',
                                                    ('id', quote_id),
                                                    column)
    if quotes_rows and len(quotes_rows) >= 1:
        return quotes_rows[0]
    else:
        logger.error("Quote not found")
        return None

def get_all_quotes(column='*'):
    quotes_rows = db_utils.get_rows('repository', 'quotes', column)
    return quotes_rows

def get_ips(column='*'):
    ip_rows = db_utils.get_rows('repository', 'ips_wrap', column)
    return ip_rows

def add_ip_user():
    ip = socket.gethostbyname(socket.gethostname())
    ip_rows = get_ips('ip')
    if not ip_rows:
        ip_rows=[]
    if ip not in ip_rows:
        if db_utils.create_row('repository',
                            'ips_wrap', 
                            ('ip', 'user_id', 'project_id'), 
                            (ip, None, None)):
            logger.debug("Machine ip added to ips wrap table")

def update_current_ip_data(column, data):
    ip = socket.gethostbyname(socket.gethostname())
    
    if db_utils.update_data('repository',
                                'ips_wrap',
                                (column, data),
                                ('ip', ip)):
        if column == 'user_id':
            db_utils.update_data('repository',
                                    'ips_wrap',
                                    ('project_id', None),
                                    ('ip', ip))
        logger.debug("Ip wrap data updated")

def unlog_project():
    ip = socket.gethostbyname(socket.gethostname())
    db_utils.update_data('repository',
                            'ips_wrap',
                            ('project_id', None),
                            ('ip', ip))

def get_current_ip_data(column='*'):
    ip = socket.gethostbyname(socket.gethostname())
    ip_rows = db_utils.get_row_by_column_data('repository',
                                                    'ips_wrap',
                                                    ('ip', ip),
                                                    column)
    return ip_rows[0]

def init_repository(admin_password, admin_email):
    create_admin_user(admin_password, admin_email)
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
    return 1

def create_repository_database():
    if db_utils.create_database(environment.get_repository()):
        create_users_table()
        create_projects_table()
        create_ip_wrap_table()
        create_quotes_table()
        return 1
    else:
        return None

def is_repository_database(repository_name = None):
    if not repository_name:
        repository_name = environment.get_repository()
    else:
        repository_name = f"repository_{repository_name}"
    return db_utils.check_database_existence(repository_name)

def create_admin_user(admin_password, admin_email):
    profile_picture = image.convert_image_to_str_data(image.user_random_image('admin'), 100)
    if db_utils.create_row('repository',
                            'users', 
                            ('user_name', 
                                'pass', 
                                'email', 
                                'profile_picture',
                                'xp',
                                'total_xp',
                                'level',
                                'life', 
                                'administrator'), 
                            ('admin',
                                tools.encrypt_string(admin_password),
                                admin_email,
                                profile_picture,
                                0,
                                0,
                                0,
                                100,
                                1)):
        logger.info('Admin user created')

def create_users_table():
    sql_cmd = """ CREATE TABLE IF NOT EXISTS users (
                                        id serial PRIMARY KEY,
                                        user_name text NOT NULL,
                                        pass text NOT NULL,
                                        email text NOT NULL,
                                        profile_picture text NOT NULL,
                                        xp integer NOT NULL,
                                        total_xp integer NOT NULL,
                                        level integer NOT NULL,
                                        life integer NOT NULL,
                                        administrator integer NOT NULL
                                    );"""
    if db_utils.create_table(environment.get_repository(), sql_cmd):
        logger.info("Users table created")

def create_projects_table():
    sql_cmd = """ CREATE TABLE IF NOT EXISTS projects (
                                        id serial PRIMARY KEY,
                                        project_name text NOT NULL,
                                        project_path text NOT NULL,
                                        project_password text NOT NULL,
                                        project_image text,
                                        creation_user text NOT NULL,
                                        creation_time real NOT NULL
                                    );"""
    if db_utils.create_table(environment.get_repository(), sql_cmd):
        logger.info("Projects table created")

def create_ip_wrap_table():
    sql_cmd = """ CREATE TABLE IF NOT EXISTS ips_wrap (
                                        id serial PRIMARY KEY,
                                        ip text NOT NULL UNIQUE,
                                        user_id integer,
                                        project_id integer,
                                        FOREIGN KEY (user_id) REFERENCES users (id),
                                        FOREIGN KEY (project_id) REFERENCES projects (id)
                                    );"""
    if db_utils.create_table(environment.get_repository(), sql_cmd):
        logger.info("Ips wrap table created")

def create_quotes_table():
    sql_cmd = """ CREATE TABLE IF NOT EXISTS quotes (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        content text NOT NULL,
                                        score text NOT NULL,
                                        voters text NOT NULL
                                    );"""
    if db_utils.create_table(environment.get_repository(), sql_cmd):
        logger.info("Quotes table created")