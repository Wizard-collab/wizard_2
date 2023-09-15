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
from wizard.core import support
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
    if not do_creation:
        return
    if project_name in get_projects_names_list():
        logger.warning(f'Project {project_name} already exists')
        return
    if project_path in get_projects_paths_list():
        logger.warning(f'Path {project_path} already assigned to another project')
        return
    if not get_user_row_by_name(environment.get_user())['administrator']:
        logger.warning("You need to be administrator to create a project")
        return
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
    if not project_id:
        return
    logger.info(f'Project {project_name} added to repository')
    return project_id

def remove_project_row(project_id):
    if not db_utils.delete_row('repository', 'projects', project_id):
        return
    logger.info('Project row removed')
    return 1

def get_administrator_pass():
    user_row = get_user_row_by_name('admin')
    if not user_row:
        return
    return user_row['pass']

def get_projects_list():
    return db_utils.get_rows('repository', 'projects')

def get_projects_names_list():
    return db_utils.get_rows('repository', 'projects', 'project_name')

def get_projects_paths_list():
    return db_utils.get_rows('repository', 'projects', 'project_path')

def get_project_row_by_name(name):
    projects_rows = db_utils.get_row_by_column_data('repository',
                                                    'projects',
                                                    ('project_name', name))
    if projects_rows is None or len(projects_rows) < 1:
        logger.error("Project not found")
        return
    return projects_rows[0]

def get_project_row(project_id, column='*'):
    projects_rows = db_utils.get_row_by_column_data('repository',
                                                    'projects',
                                                    ('id', project_id),
                                                    column)
    if projects_rows is None or len(projects_rows) < 1:
        logger.error("Project not found")
        return
    return projects_rows[0]

def get_project_path_by_name(name):
    project_row = get_project_row_by_name(name)
    if not project_row:
        return
    return project_row['project_path']

def modify_project_password(project_name,
                            project_password,
                            new_password,
                            administrator_pass=''):
    if not tools.decrypt_string(get_administrator_pass(),
                            administrator_pass):
        logger.warning('Wrong administrator pass')
        return
    if project_name not in get_projects_names_list():
        logger.warning(f'{project_name} not found')
        return
    if not tools.decrypt_string(
            get_project_row_by_name(project_name)['project_password'],
            project_password):
        logger.warning(f'Wrong password for {project_name}')
        return
    if not db_utils.update_data('repository',
                'projects',
                ('project_password', tools.encrypt_string(new_password)),
                ('project_name', project_name)):
        return
    logger.info(f'{project_name} password modified')
    return 1

def modify_project_image(project_name, project_image):
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
    bytes_data = image.convert_image_to_bytes(image_file)
    pillow_image = image.convert_image_bytes_to_pillow(bytes_data)
    pillow_image, fixed_width, height_size = image.resize_image_with_fixed_width(pillow_image, 600)
    pillow_image = image.crop_image_height(pillow_image, 337)
    bytes_data = image.convert_PILLOW_image_to_bytes(pillow_image)
    return image.convert_bytes_to_str_data(bytes_data)

def create_user(user_name,
                    password,
                    email,
                    administrator_pass='',
                    profile_picture=None,
                    championship_participation=1):
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
    if not do_creation:
        return
    if user_name in get_user_names_list():
        logger.warning(f'User {user_name} already exists')
        return
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
                    json.dumps([]),
                    json.dumps({}))):
        return
    info = f"User {user_name} created"
    if administrator:
        info += ' ( privilege : administrator )'
    else:
        info += ' ( privilege : user )'
    logger.info(info)
    return 1

def modify_user_profile_picture(user_name, profile_picture):
    if not profile_picture:
        return
    if not path_utils.isfile(profile_picture):
        logger.warning(f'{profile_picture} not found')
        return
    profile_picture_ascii = image.convert_image_to_str_data(profile_picture, 100)
    if not db_utils.update_data('repository',
                            'users',
                            ('profile_picture', profile_picture_ascii),
                            ('user_name', user_name)):
        return
    logger.info(f'{user_name} profile picture modified')
    return 1

def upgrade_user_privilege(user_name, administrator_pass):
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
                            ('administrator',1),
                            ('user_name', user_name)):
        return
    logger.info(f'Administrator privilege set for {user_name}')
    return 1

def downgrade_user_privilege(user_name, administrator_pass):
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
                            ('administrator',0),
                            ('user_name', user_name)):
        return
    logger.info(f'Privilege downgraded to user for {user_name}')
    return 1

def modify_user_password(user_name, password, new_password):
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
    return db_utils.get_rows('repository', 'users', order='level DESC, total_xp DESC;')

def get_users_list_by_xp_order():
    return db_utils.get_rows('repository', 'users', order='total_xp DESC;')   

def get_users_list_by_deaths_order():
    return db_utils.get_rows('repository', 'users', order='deaths DESC;')

def get_users_list_by_work_time_order():
    return db_utils.get_rows('repository', 'users', order='work_time DESC;')

def get_users_list_by_comments_count_order():
    return db_utils.get_rows('repository', 'users', order='comments_count DESC;')

def get_user_names_list():
    return db_utils.get_rows('repository', 'users', 'user_name')

def get_user_row_by_name(name, column='*'):
    users_rows = db_utils.get_row_by_column_data('repository',
                                                    'users',
                                                    ('user_name', name),
                                                    column)
    if users_rows is None or len(users_rows) < 1:
        logger.error("User not found")
        return
    return users_rows[0]

def get_user_data(user_id, column='*'):
    users_rows = db_utils.get_row_by_column_data('repository',
                                                    'users',
                                                    ('id', user_id),
                                                    column)
    if users_rows is None or len(users_rows) < 1:
        logger.error("User not found")
        return
    return users_rows[0]

def modify_user_xp(user_name, xp):
    return db_utils.update_data('repository',
                                'users',
                                ('xp', xp),
                                ('user_name', user_name))

def modify_user_total_xp(user_name, total_xp):
    return db_utils.update_data('repository',
                                'users',
                                ('total_xp', total_xp),
                                ('user_name', user_name))

def increase_user_comments_count(user_name):
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
    if not db_utils.update_data('repository',
                            'users',
                            ('level', new_level),
                            ('user_name', user_name)):
        return
    logger.info(f'{user_name} is now level {new_level}')
    return 1

def modify_user_life(user_name, life):
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
    if not db_utils.update_data('repository',
                                    'users',
                                    ('coins', coins),
                                    ('user_name', user_name)):
        return
    logger.info(f'{user_name} have now {coins} coins')
    return 1

def add_user_coins(user_name, coins):
    user_coins = get_user_row_by_name(user_name, 'coins')
    if not db_utils.update_data('repository',
                                    'users',
                                    ('coins', user_coins+coins),
                                    ('user_name', user_name)):
        return
    logger.debug(f'{user_name} just won {coins} coins !')
    return 1

def remove_user_coins(user_name, coins):
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
    if not db_utils.update_data('repository',
                                    'users',
                                    ('artefacts', json.dumps(artefacts_list)),
                                    ('user_name', user_name)):
        return
    logger.debug(f'Artefacts list modified')
    return 1

def modify_keeped_artefacts(user_name, artefacts_dic):
    if not db_utils.update_data('repository',
                                    'users',
                                    ('keeped_artefacts', json.dumps(artefacts_dic)),
                                    ('user_name', user_name)):
        return
    logger.debug(f'Keeped artefacts dic modified')
    return 1

def modify_user_email(user_name, email):
    if email == '':
        logger.warning('Please enter a valid email')
        return
    return db_utils.update_data('repository',
                                    'users',
                                    ('email', email),
                                    ('user_name', user_name))

def is_admin():
    is_admin = get_user_row_by_name(environment.get_user(), 'administrator')
    if not is_admin:
        logger.warning("You are not administrator")
    return is_admin

def add_quote(content):
    if content is None or content == '':
        logger.warning("Please enter quote content")
        return
    if len(content)>100:
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
    sanity = 1
    if not 0 <= score <= 5:
        logger.warning(f"Please note between 0 and 5")
        sanity = 0
    if type(score) != int:
        logger.warning(f"{score} is not an integer")
        sanity = 0
    if not sanity:
        return
    current_quote_row = db_utils.get_row_by_column_data('repository',
                                                    'quotes',
                                                    ('id', quote_id))

    if current_quote_row is None or current_quote_row == []:
        logger.warning("Quote not found")
        return
    if current_quote_row[0]['creation_user'] == environment.get_user():
        logger.warning("You can't vote for your own quote")
        return
    voters_list = json.loads(current_quote_row[0]['voters'])
    if environment.get_user() in voters_list:
        logger.warning("You already voted for this quote")
        return
    current_scores_list = json.loads(current_quote_row[0]['score'])
    current_scores_list.append(score)
    voters_list.append(environment.get_user())
    if not db_utils.update_data('repository',
                                    'quotes',
                                    ('score',
                                        json.dumps(current_scores_list)),
                                    ('id',
                                        quote_id)):
        return
    logger.info("Quote score updated")
    if not db_utils.update_data('repository',
                                    'quotes',
                                    ('voters',
                                        json.dumps(voters_list)),
                                    ('id',
                                        quote_id)):
        return
    logger.info("Quote voters updated")

def get_quote_data(quote_id, column='*'):
    quotes_rows = db_utils.get_row_by_column_data('repository',
                                                    'quotes',
                                                    ('id', quote_id),
                                                    column)
    if quotes_rows is None or len(quotes_rows) < 1:
        logger.error("Quote not found")
        return
    return quotes_rows[0]

def remove_quote(quote_id):
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
    return db_utils.get_rows('repository', 'quotes', column)

def get_user_quotes(column='*'):
    return db_utils.get_row_by_column_data('repository', 'quotes', ('creation_user', environment.get_user()))

def get_ips(column='*'):
    return db_utils.get_rows('repository', 'ips_wrap', column)

def add_ip_user():
    ip = socket.gethostbyname(socket.gethostname())
    ip_rows = get_ips('ip')
    if not ip_rows:
        ip_rows=[]
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
    if not is_admin():
        return
    if not db_utils.delete_rows('repository', 'ips_wrap'):
        return
    logger.info("All users ip removed")
    return 1

def flush_user_ip():
    ip = socket.gethostbyname(socket.gethostname())
    ip_rows = get_ips('ip')
    if not ip_rows:
        ip_rows=[]
    if ip not in ip_rows:
        return
    if not db_utils.delete_row('repository',
                        'ips_wrap', 
                        ip, 'ip'):
        return
    logger.debug("Machine ip removed from ips wrap table")
    return 1

def update_current_ip_data(column, data):
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
    ip = socket.gethostbyname(socket.gethostname())
    if not db_utils.update_data('repository',
                            'ips_wrap',
                            ('project_id', None),
                            ('ip', ip)):
        return
    logger.debug("Project unlogged")
    return 1

def get_current_ip_data(column='*'):
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
    print('zizi')
    create_admin_user(admin_password, admin_email)
    print('lol')
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
    if not db_utils.create_database(environment.get_repository()):
        return
    create_users_table()
    create_projects_table()
    create_ip_wrap_table()
    create_quotes_table()
    return 1

def is_repository_database(repository_name = None):
    if not repository_name:
        repository_name = environment.get_repository()
    else:
        repository_name = f"repository_{repository_name}"
    return db_utils.check_database_existence(repository_name)

def create_admin_user(admin_password, admin_email):
    profile_picture = image.convert_image_to_str_data(image.user_random_image('admin'), 100)
    print('caca')
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
                                json.dumps([]),
                                json.dumps({}))):
        return
    logger.info('Admin user created')
    return 1

def create_users_table():
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
                                        artefacts text NOT NULL,
                                        keeped_artefacts text NOT NULL
                                    );"""
    if not db_utils.create_table(environment.get_repository(), sql_cmd):
        return
    logger.info("Users table created")
    return 1

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
    if not db_utils.create_table(environment.get_repository(), sql_cmd):
        return
    logger.info("Projects table created")
    return 1

def create_ip_wrap_table():
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
    