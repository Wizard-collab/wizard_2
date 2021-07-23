# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module is used to manage and access 
# the site database

# The site database stores the following informations:
#       - The users list ( name, hashed password, email )
#       - The projects list ( name, path, hashed password )
#       - The ip wraps ( roughly looks like cookies in web )

# Python modules
import os
import time
import socket
import json

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

from wizard.core import db_utils
from wizard.core import tools
from wizard.core import environment
from wizard.core import image
from wizard.vars import site_vars
from wizard.vars import ressources

def create_project(project_name, project_path, project_password):
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

    if do_creation:
        if project_name not in get_projects_names_list():
            if project_path not in get_projects_paths_list():
                if get_user_row_by_name(environment.get_user())['pass']:
                    if db_utils.create_row('site',
                                    'projects', 
                                    ('project_name', 'project_path', 'project_password'), 
                                    (project_name,
                                    project_path,
                                    tools.encrypt_string(project_password))):
                        logger.info(f'Project {project_name} added to site')
                        return 1
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

def get_administrator_pass():
    return get_user_row_by_name('admin')['pass']

def get_projects_list():
    projects_rows = db_utils.get_rows('site', 'projects')
    return projects_rows

def get_projects_names_list():
    projects_rows = db_utils.get_rows('site', 'projects', 'project_name')
    return projects_rows

def get_projects_paths_list():
    projects_rows = db_utils.get_rows('site', 'projects', 'project_path')
    return projects_rows

def get_project_row_by_name(name):
    projects_rows = db_utils.get_row_by_column_data('site',
                                                    'projects',
                                                    ('project_name', name))
    return projects_rows[0]

def get_project_row(project_id, column='*'):
    projects_rows = db_utils.get_row_by_column_data('site',
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
                if db_utils.update_data('site',
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

def create_user(user_name,
                    password,
                    email,
                    administrator_pass='',
                    profile_picture=ressources._default_profile_):
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
                if not os.path.isfile(profile_picture):
                    profile_picture = ressources._default_profile_
            else:
                profile_picture = ressources._default_profile_
            profile_picture_ascii = image.convert_image_to_str_data(profile_picture)
            if db_utils.create_row('site',
                        'users', 
                        ('user_name',
                            'pass',
                            'email',
                            'profile_picture',
                            'xp',
                            'level',
                            'life',
                            'administrator'), 
                        (user_name,
                            tools.encrypt_string(password),
                            email,
                            profile_picture_ascii,
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

def upgrade_user_privilege(user_name, administrator_pass):
    if user_name in get_user_names_list():
        user_row = get_user_row_by_name(user_name)
        if not user_row['administrator']:
            if tools.decrypt_string(get_administrator_pass(),
                                        administrator_pass):
                if db_utils.update_data('site',
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
                if db_utils.update_data('site',
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
            if db_utils.update_data('site',
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
    users_rows = db_utils.get_rows('site', 'users')
    return users_rows

def get_user_names_list():
    users_rows = db_utils.get_rows('site', 'users', 'user_name')
    return users_rows

def get_user_row_by_name(name, column='*'):
    users_rows = db_utils.get_row_by_column_data('site',
                                                    'users',
                                                    ('user_name', name),
                                                    column)
    if users_rows and len(users_rows) >= 1:
        return users_rows[0]
    else:
        logger.error("User not found")
        return None

def get_user_data(user_id, column='*'):
    users_rows = db_utils.get_row_by_column_data('site',
                                                    'users',
                                                    ('id', user_id),
                                                    column)
    if users_rows and len(users_rows) >= 1:
        return users_rows[0]
    else:
        logger.error("User not found")
        return None

def modify_user_xp(user_name, xp):
    if db_utils.update_data('site',
                                'users',
                                ('xp', xp),
                                ('user_name', user_name)):
        logger.debug(f'{user_name} won some xps')
        return 1
    else:
        return None

def modify_user_level(user_name, new_level):
    if db_utils.update_data('site',
                            'users',
                            ('level', new_level),
                            ('user_name', user_name)):
        logger.info(f'{user_name} is now level {new_level}')
        return 1
    else:
        return None

def modify_user_life(user_name, life):
    if db_utils.update_data('site',
                                    'users',
                                    ('life', life),
                                    ('user_name', user_name)):
        logger.debug(f'{user_name} life is {life}%')
        return 1
    else:
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
            quote_id = db_utils.create_row('site',
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
        current_quote_row = db_utils.get_row_by_column_data('site',
                                                        'quotes',
                                                        ('id', quote_id))

        if current_quote_row is not None:
            if current_quote_row[0]['creation_user'] != environment.get_user():
                voters_list = json.loads(current_quote_row[0]['voters'])
                if environment.get_user() not in voters_list:
                    current_scores_list = json.loads(current_quote_row[0]['score'])
                    current_scores_list.append(score)
                    voters_list.append(environment.get_user())
                    if db_utils.update_data('site',
                                                    'quotes',
                                                    ('score',
                                                        json.dumps(current_scores_list)),
                                                    ('id',
                                                        quote_id)):
                        logger.info("Quote score updated")
                    if db_utils.update_data('site',
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
    quotes_rows = db_utils.get_row_by_column_data('site',
                                                    'quotes',
                                                    ('id', quote_id),
                                                    column)
    if quotes_rows and len(quotes_rows) >= 1:
        return quotes_rows[0]
    else:
        logger.error("Quote not found")
        return None

def get_all_quotes(column='*'):
    quotes_rows = db_utils.get_rows('site', 'quotes', column)
    return quotes_rows

def get_ips(column='*'):
    ip_rows = db_utils.get_rows('site', 'ips_wrap', column)
    return ip_rows

def add_ip_user():
    ip = socket.gethostbyname(socket.gethostname())
    ip_rows = get_ips('ip')
    if not ip_rows:
        ip_rows=[]
    if ip not in ip_rows:
        if db_utils.create_row('site',
                            'ips_wrap', 
                            ('ip', 'user_id', 'project_id'), 
                            (ip, None, None)):
            logger.debug("Machine ip added to ips wrap table")

def update_current_ip_data(column, data):
    ip = socket.gethostbyname(socket.gethostname())
    if db_utils.update_data('site',
                                    'ips_wrap',
                                    (column, data),
                                    ('ip', ip)):
        logger.debug("Ip wrap data updated")

def get_current_ip_data(column='*'):
    ip = socket.gethostbyname(socket.gethostname())
    ip_rows = db_utils.get_row_by_column_data('site',
                                                    'ips_wrap',
                                                    ('ip', ip),
                                                    column)
    return ip_rows[0]

def init_site(admin_password, admin_email):
    create_admin_user(admin_password, admin_email)
    for quote in site_vars._default_quotes_list_:
        db_utils.create_row('site',
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

def create_site_database():
    if db_utils.create_database('site'):
        create_users_table()
        create_projects_table()
        create_ip_wrap_table()
        create_quotes_table()
        return 1
    else:
        return None

def is_site_database():
    return db_utils.check_database_existence('site')

def create_admin_user(admin_password, admin_email):
    profile_picture = image.convert_image_to_str_data(ressources._default_profile_)
    if db_utils.create_row('site',
                            'users', 
                            ('user_name', 
                                'pass', 
                                'email', 
                                'profile_picture',
                                'xp',
                                'level',
                                'life', 
                                'administrator'), 
                            ('admin',
                                tools.encrypt_string(admin_password),
                                admin_email,
                                profile_picture,
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
                                        level integer NOT NULL,
                                        life integer NOT NULL,
                                        administrator integer NOT NULL
                                    );"""
    if db_utils.create_table('site', sql_cmd):
        logger.info("Users table created")

def create_projects_table():
    sql_cmd = """ CREATE TABLE IF NOT EXISTS projects (
                                        id serial PRIMARY KEY,
                                        project_name text NOT NULL,
                                        project_path text NOT NULL,
                                        project_password text NOT NULL
                                    );"""
    if db_utils.create_table('site', sql_cmd):
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
    if db_utils.create_table('site', sql_cmd):
        logger.info("Ips wrap table created")

def create_quotes_table():
    sql_cmd = """ CREATE TABLE IF NOT EXISTS quotes (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        content text NOT NULL,
                                        score text NOT NULL,
                                        voters text NOT NULL
                                    );"""
    if db_utils.create_table('site', sql_cmd):
        logger.info("Quotes table created")