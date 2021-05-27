# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module is used to manage and access 
# the project database

# The project database stores the following informations:
#       - The instances ( domains,
#                         categories,
#                         assets,
#                         stages,
#                         variants, 
#                         work_envs and versions )
#       - The project settings ( frame rate,
#                                image format and users ids )
#       - The softwares datas (software name,
#                              executable path,
#                              extension,
#                              the additional environments,
#                              the additionnal scripts paths)

# Python modules
import os
import time
import json

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

from wizard.database.create_database import create_database
from wizard.database import utility as db_utils
from wizard.core import tools
from wizard.vars import project_vars
from wizard.vars import softwares_vars
from wizard.core import site
from wizard.core import environment

class project:
    def __init__(self):
        self.database_file = get_database_file(environment.get_project_path())

    def add_domain(self, name):
        domain_id = db_utils.create_row(self.database_file,
                            'domains', 
                            ('name', 'creation_time', 'creation_user'), 
                            (name, time.time(), environment.get_user()))
        if domain_id:
            logging.info(f"Domain {name} added to project")
        return domain_id

    def get_domains(self):
        domain_rows = db_utils.get_rows(self.database_file, 'domains')
        return domain_rows

    def get_domain_data(self, domain_id, column='*'):
        domain_rows = db_utils.get_row_by_column_data(self.database_file,
                                                        'domains',
                                                        ('id', domain_id),
                                                        column)
        if len(domain_rows) >= 1:
            return domain_rows[0]
        else:
            logging.error("Domain not found")
            return None

    def get_domain_childs(self, domain_id, column='*'):
        categories_rows = db_utils.get_row_by_column_data(self.database_file,
                                                        'categories',
                                                        ('domain_id', domain_id),
                                                        column)
        return categories_rows

    def remove_domain(self, domain_id):
        success = None
        if site.site().is_admin():
            for category_id in self.get_domain_childs(domain_id, 'id'):
                self.remove_category(category_id)
            success = db_utils.delete_row(self.database_file, 'domains', domain_id)
            if success:
                logging.info(f"Domain removed from project")
        return success

    def add_category(self, name, domain_id):
        if not (db_utils.check_existence(self.database_file, 
                                        'categories',
                                        ('name', 'domain_id'),
                                        (name, domain_id))):
            category_id = db_utils.create_row(self.database_file,
                                'categories',
                                ('name', 'creation_time', 'creation_user', 'domain_id'), 
                                (name, time.time(), environment.get_user(), domain_id))
            if category_id:
                logging.info(f"Category {name} added to project")
            return category_id
        else:
            logging.warning(f"{name} already exists")

    def remove_category(self, category_id):
        success = None
        if site.site().is_admin():
            for asset_id in self.get_category_childs(category_id, 'id'):
                self.remove_asset(asset_id)
            success = db_utils.delete_row(self.database_file, 'categories', category_id)
            if success:
                logging.info(f"Category removed from project")
        return success

    def get_category_childs(self, category_id, column="*"):
        assets_rows = db_utils.get_row_by_column_data(self.database_file,
                                                        'assets',
                                                        ('category_id', category_id),
                                                        column)
        return assets_rows

    def get_category_data(self, category_id, column='*'):
        category_rows = db_utils.get_row_by_column_data(self.database_file,
                                                        'categories',
                                                        ('id', category_id),
                                                        column)
        if category_rows and len(category_rows) >= 1:
            return category_rows[0]
        else:
            logging.error("Category not found")
            return None

    def add_asset(self, name, category_id):
        if not (db_utils.check_existence(self.database_file, 
                                        'assets',
                                        ('name', 'category_id'),
                                        (name, category_id))):
            asset_id = db_utils.create_row(self.database_file,
                                'assets', 
                                ('name', 'creation_time', 'creation_user', 'category_id'), 
                                (name, time.time(), environment.get_user(), category_id))
            if asset_id:
                logging.info(f"Asset {name} added to project")
            return asset_id
        else:
            logging.warning(f"{name} already exists")

    def remove_asset(self, asset_id):
        success = None
        if site.site().is_admin():
            for stage_id in self.get_asset_childs(asset_id, 'id'):
                self.remove_stage(stage_id)
            success = db_utils.delete_row(self.database_file, 'assets', asset_id)
            if success:
                logging.info(f"Asset removed from project")
        return success

    def get_asset_childs(self, asset_id, column='*'):
        stages_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'stages',
                                                            ('asset_id', asset_id),
                                                            column)
        return stages_rows

    def get_asset_data(self, asset_id, colmun='*'):
        assets_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'assets',
                                                            ('id', asset_id),
                                                            colmun)
        if assets_rows and len(assets_rows) >= 1:
            return assets_rows[0]
        else:
            logging.error("Asset not found")
            return None

    def add_stage(self, name, asset_id):
        if not (db_utils.check_existence(self.database_file, 
                                        'stages',
                                        ('name', 'asset_id'),
                                        (name, asset_id))):
            stage_id = db_utils.create_row(self.database_file,
                                'stages', 
                                ('name',
                                    'creation_time',
                                    'creation_user',
                                    'asset_id'), 
                                (name,
                                    time.time(),
                                    environment.get_user(),
                                    asset_id))
            if stage_id:
                logging.info(f"Stage {name} added to project")
            return stage_id
        else:
            logging.warning(f"{name} already exists")

    def remove_stage(self, stage_id):
        success = None
        if site.site().is_admin():
            for variant_id in self.get_stage_childs(stage_id, 'id'):
                self.remove_variant(variant_id)
            success = db_utils.delete_row(self.database_file, 'stages', stage_id)
            if success:
                logging.info(f"Stage removed from project")
        return success

    def set_stage_default_variant(self, stage_id, variant_id):
        if db_utils.update_data(self.database_file,
                            'stages',
                            ('default_variant_id', variant_id),
                            ('id', stage_id)):
            logging.info('Default variant modified')

    def get_stage_data(self, stage_id, column='*'):
        stages_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'stages',
                                                            ('id', stage_id),
                                                            column)
        if stages_rows and len(stages_rows) >= 1:
            return stages_rows[0]
        else:
            logging.error("Stage not found")
            return None

    def get_stage_childs(self, stage_id, column='*'):
        variants_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'variants',
                                                            ('stage_id', stage_id),
                                                            column)
        return variants_rows

    def add_variant(self, name, stage_id, comment):
        if not (db_utils.check_existence(self.database_file, 
                                        'variants',
                                        ('name', 'stage_id'),
                                        (name, stage_id))):
            variant_id = db_utils.create_row(self.database_file,
                                'variants', 
                                ('name',
                                    'creation_time',
                                    'creation_user',
                                    'comment',
                                    'stage_id'), 
                                (name,
                                    time.time(),
                                    environment.get_user(),
                                    comment, stage_id))
            if variant_id:
                logging.info(f"Variant {name} added to project")
            return variant_id
        else:
            logging.warning(f"{name} already exists")

    def remove_variant(self, variant_id):
        success = None
        if site.site().is_admin():
            for work_env_id in self.get_variant_work_envs_childs(variant_id, 'id'):
                self.remove_work_env(work_env_id)
            success = db_utils.delete_row(self.database_file, 'variants', variant_id)
            if success:
                logging.info(f"Variant removed from project")
        return success

    def get_variant_data(self, variant_id, column='*'):
        variants_rows = db_utils.get_row_by_column_data(self.database_file, 
                                                            'variants', 
                                                            ('id', variant_id), 
                                                            column)
        if variants_rows and len(variants_rows) >= 1:
            return variants_rows[0]
        else:
            logging.error("Variant not found")
            return None

    def get_variant_work_envs_childs(self, variant_id, column='*'):
        work_envs_rows = db_utils.get_row_by_column_data(self.database_file, 
                                                            'work_envs', 
                                                            ('variant_id', variant_id), 
                                                            column)
        return work_envs_rows

    def add_work_env(self, name, software_id, variant_id):
        if not (db_utils.check_existence(self.database_file, 
                                        'work_envs',
                                        ('name', 'variant_id'),
                                        (name, variant_id))):
            work_env_id = db_utils.create_row(self.database_file,
                                'work_envs', 
                                ('name',
                                    'creation_time',
                                    'creation_user',
                                    'variant_id',
                                    'lock_id',
                                    'software_id'), 
                                (name,
                                    time.time(),
                                    environment.get_user(),
                                    variant_id,
                                    None,
                                    software_id))
            if work_env_id:
                logging.info(f"Work env {name} added to project")
            return work_env_id
        else:
            logging.warning(f"{name} already exists")
            return None

    def remove_work_env(self, work_env_id):
        success = None
        if site.site().is_admin():
            for version_id in self.get_work_versions(work_env_id, 'id'):
                self.remove_version(version_id)
            success = db_utils.delete_row(self.database_file, 'work_envs', work_env_id)
            if success:
                logging.info("Work env removed from project")
        return success

    def get_work_versions(self, work_env_id, column='*'):
        versions_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'versions',
                                                            ('work_env_id', work_env_id),
                                                            column)
        return versions_rows

    def get_last_work_version(self, work_env_id, column='*'):
        versions_rows = db_utils.get_last_row_by_column_data(self.database_file,
                                                            'versions',
                                                            ('work_env_id', work_env_id),
                                                            column)
        return versions_rows

    def get_work_env_data(self, work_env_id, column='*'):
        work_env_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'work_envs',
                                                            ('id', work_env_id),
                                                            column)
        if work_env_rows and len(work_env_rows) >= 1:
            return work_env_rows[0]
        else:
            logging.error("Work env not found")
            return None

    def get_lock(self, work_env_id):
        current_user_id = site.site().get_user_row_by_name(environment.get_user(), 'id')
        work_env_lock_id = self.get_work_env_data(work_env_id, 'lock_id')
        if (not work_env_lock_id) or (work_env_lock_id == current_user_id):
            return None
        else:
            lock_user_name = site.site().get_user_row(work_env_lock_id, 'user_name')
            logging.warning(f"Work env locked by {lock_user_name}")
            return lock_user_name

    def set_work_env_lock(self, work_env_id, lock=1):
        if lock:
            user_id = site.site().get_user_row_by_name(environment.get_user(), 'id')
        else:
            user_id = None
        if not self.get_lock(work_env_id):
            if db_utils.update_data(self.database_file,
                                    'work_envs',
                                    ('lock_id', user_id),
                                    ('id', work_env_id)):
                if user_id:
                    logging.info(f'Work env locked')
                else:
                    logging.info(f'Work env unlocked')
                return 1
            else:
                return None

    def add_version(self, name, file_path, work_env_id, comment='', screenshot=None):
        version_id = db_utils.create_row(self.database_file,
                            'versions', 
                            ('name',
                                'creation_time',
                                'creation_user',
                                'comment',
                                'file_path',
                                'screenshot',
                                'work_env_id'), 
                            (name,
                                time.time(),
                                environment.get_user(),
                                comment,
                                file_path,
                                screenshot,
                                work_env_id))
        if version_id:
            logging.info(f"Version {name} added to project")
        return version_id

    def get_version_data(self, version_id, column='*'):
        work_envs_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'versions',
                                                            ('id', version_id),
                                                            column)
        if work_envs_rows and len(work_envs_rows) >= 1:
            return work_envs_rows[0]
        else:
            logging.error("Version not found")
            return None

    def remove_version(self, version_id):
        success = None
        if site.site().is_admin():
            success = db_utils.delete_row(self.database_file, 'versions', version_id)
            if success :
                logging.info(f"Version removed from project")
        return success

    def add_software(self, name, extension, file_command, no_file_command):
        if name in softwares_vars._softwares_list_:
            if name not in self.get_softwares_names_list():
                software_id = db_utils.create_row(self.database_file,
                                'softwares', 
                                ('name', 
                                    'extension',
                                    'path',
                                    'additionnal_scripts',
                                    'additionnal_env',
                                    'file_command',
                                    'no_file_command'), 
                                (name,
                                    extension,
                                    '',
                                    '',
                                    '',
                                    file_command,
                                    no_file_command))
                if software_id:
                    logging.info(f"Software {name} added to project")
                return software_id
            else:
                logging.warning(f"{name} already exists")
                return None
        else:
            logging.warning("Unregistered software")
            return None

    def get_softwares_names_list(self):
        softwares_rows = db_utils.get_rows(self.database_file, 'softwares', 'name')
        return softwares_rows

    def set_software_path(self, software_id, path):
        if os.path.isfile(path):
            if db_utils.update_data(self.database_file,
                                'softwares',
                                ('path', path),
                                ('id', software_id)):
                logging.info('Software path modified')
                return 1
            else:
                return None
        else:
            logging.warning(f"{path} is not a valid executable")
            return None

    def get_software_data(self, software_id, column='*'):
        softwares_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'softwares',
                                                            ('id', software_id),
                                                            column)
        if softwares_rows and len(softwares_rows) >= 1:
            return softwares_rows[0]
        else:
            logging.error("Software not found")
            return None

    def create_settings_row(self, frame_rate, image_format):
        if len(db_utils.get_rows(self.database_file, 'settings', 'id'))==0:
            if db_utils.create_row(self.database_file,
                                                'settings',
                                                ('frame_rate',
                                                    'image_format',
                                                    'users_ids'),
                                                (frame_rate,
                                                    json.dumps(image_format),
                                                    json.dumps(list()))):
                logging.info("Project settings initiated")
                return 1
            else:
                return None
        else:
            logging.error("Settings row already exists")
            return None

    def set_frame_rate(self, frame_rate):
        if db_utils.update_data(self.database_file,
                                'settings',
                                ('frame_rate', frame_rate),
                                ('id', 1)):
            logging.info('Project frame rate modified')
            return 1
        else:
            return None

    def get_frame_rate(self):
        frame_rate_list = db_utils.get_row_by_column_data(self.database_file,
                                                            'settings',
                                                            ('id', 1),
                                                            'frame_rate')
        if frame_rate_list and len(frame_rate_list) >= 1:
            return json.loads(frame_rate_list[0])
        else:
            logging.error("Project settings not found")
            return None

    def set_image_format(self, image_format):
        if db_utils.update_data(self.database_file,
                                'settings',
                                ('image_format', json.dumps(image_format)),
                                ('id', 1)):
            logging.info('Project format modified')
            return 1
        else:
            return None

    def get_image_format(self):
        image_format_list = db_utils.get_row_by_column_data(self.database_file,
                                                            'settings',
                                                            ('id', 1),
                                                            'image_format')
        if image_format_list and len(image_format_list) >= 1:
            return json.loads(image_format_list[0])
        else:
            logging.error("Project settings not found")
            return None

    def get_users_ids_list(self):
        users_ids_list = db_utils.get_row_by_column_data(self.database_file,
                                                            'settings',
                                                            ('id', 1),
                                                            'users_ids')
        if users_ids_list and len(users_ids_list) >= 1:
            return json.loads(users_ids_list[0])
        else:
            logging.error("Project settings not found")
            return None

    def add_user(self, user_id):
        users_ids_list = self.get_users_ids_list()
        if user_id not in users_ids_list:
            users_ids_list.append(user_id)
            self.update_users_list(users_ids_list)

    def remove_user(self, user_id):
        users_ids_list = self.get_users_ids_list()
        if user_id in users_ids_list:
            users_ids_list.remove(user_id)
            self.update_users_list(users_ids_list)

    def update_users_list(self, users_ids_list):
        if db_utils.update_data(self.database_file,
                                'settings',
                                ('users_ids', json.dumps(users_ids_list)),
                                ('id', 1)):
            logging.info('Project users list updated')
            return 1
        else:
            return None


def get_database_file(project_path):
    if project_path:
        database_file = os.path.join(project_path, project_vars._project_database_file_)
    else:
        database_file = None
    return database_file

def create_project(project_name, project_path, project_password):
    if site.site().create_project(project_name, project_path, project_password):
        if init_project(project_path):
            logging.info(f"{project_name} created")
            environment.build_project_env(project_name, project_path)
            return 1
        else:
            return None
    else:
        return None

def init_project(project_path):
    if not os.path.isdir(project_path):
        os.mkdir(project_path)
    database_file = get_database_file(project_path)
    if not os.path.isfile(database_file):
        if create_database(database_file):
            create_domains_table(database_file)
            create_categories_table(database_file)
            create_assets_table(database_file)
            create_stages_table(database_file)
            create_variants_table(database_file)
            create_work_envs_table(database_file)
            create_exports_table(database_file)
            create_versions_table(database_file)
            create_export_versions_table(database_file)
            create_softwares_table(database_file)
            create_settings_table(database_file)
            return database_file
    else:
        logging.warning("Database file already exists")
        return None

def create_domains_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS domains (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL UNIQUE,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Categories table created")

def create_categories_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS categories (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        domain_id integer NOT NULL,
                                        FOREIGN KEY (domain_id) REFERENCES domains (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Categories table created")

def create_assets_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS assets (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        category_id integer NOT NULL,
                                        FOREIGN KEY (category_id) REFERENCES categories (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Assets table created")

def create_stages_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS stages (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        default_variant_id integer,
                                        asset_id integer NOT NULL,
                                        FOREIGN KEY (asset_id) REFERENCES assets (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Stages table created")

def create_variants_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS variants (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        comment text,
                                        stage_id integer NOT NULL,
                                        FOREIGN KEY (stage_id) REFERENCES stages (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Variants table created")

def create_work_envs_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS work_envs (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        variant_id integer NOT NULL,
                                        lock_id integer,
                                        software_id integer NOT NULL,
                                        FOREIGN KEY (variant_id) REFERENCES variants (id)
                                        FOREIGN KEY (software_id) REFERENCES softwares (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Work envs table created")

def create_exports_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS exports (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        variant_id integer NOT NULL,
                                        FOREIGN KEY (variant_id) REFERENCES variants (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Exports table created")

def create_versions_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS versions (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        comment text,
                                        file_path text NOT NULL,
                                        screenshot blob,
                                        work_env_id integer NOT NULL,
                                        FOREIGN KEY (work_env_id) REFERENCES work_envs (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Versions table created")

def create_export_versions_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS export_versions (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        comment text,
                                        file_list text NOT NULL,
                                        export_id integer NOT NULL,
                                        FOREIGN KEY (export_id) REFERENCES exports (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Export versions table created")

def create_softwares_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS softwares (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        extension text NOT NULL,
                                        path text,
                                        additionnal_scripts text,
                                        additionnal_env text,
                                        file_command text NOT NULL,
                                        no_file_command text NOT NULL
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Softwares table created")

def create_settings_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS settings (
                                        id integer PRIMARY KEY,
                                        frame_rate text NOT NULL,
                                        image_format text NOT NULL,
                                        users_ids text
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Settings table created")