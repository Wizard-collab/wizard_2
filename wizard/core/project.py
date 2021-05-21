# coding: utf-8

# Python modules
import os
import time

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

from wizard.database.create_database import create_database
from wizard.database import utility as db_utils
from wizard.core import tools
from wizard.vars import project_vars
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
        else:
            return None

    def get_domains(self):
        domain_rows = db_utils.get_rows(self.database_file, 'domains')
        return domain_rows

    def get_domain_name(self, domain_id):
        domain_rows = db_utils.get_row_by_column_data(self.database_file, 'domains', ('id', domain_id))
        if len(domain_rows) >= 1:
            return domain_rows[0][1]
        else:
            logging.error("Domain not found")
            return None

    def get_domain_path(self, domain_id):
        domain_rows = db_utils.get_row_by_column_data(self.database_file, 'domains', ('id', domain_id))
        if len(domain_rows) >= 1:
            return domain_rows[0][4]
        else:
            logging.error("Domain not found")
            return None

    def get_domain_childs_names(self, domain_id):
        child_names = []
        categories_rows = db_utils.get_row_by_column_data(self.database_file, 'categories', ('domain_id', domain_id))
        for row in categories_rows:
            child_names.append(row[1])
        return child_names

    def get_domain_childs(self, domain_id):
        categories_rows = db_utils.get_row_by_column_data(self.database_file, 'categories', ('domain_id', domain_id))
        return categories_rows

    def remove_domain(self, domain_id):
        db_utils.delete_row(self.database_file, 'domains', domain_id)
        logging.info(f"Domain removed from project")

    def add_category(self, name, domain_id):
        if name not in self.get_domain_childs_names(domain_id):
            category_id = db_utils.create_row(self.database_file,
                                'categories', 
                                ('name', 'creation_time', 'creation_user', 'domain_id'), 
                                (name, time.time(), environment.get_user(), domain_id))
            if category_id:
                logging.info(f"Category {name} added to project")
                return category_id
            else:
                return None
        else:
            logging.warning(f"{name} already exists")

    def remove_category(self, category_id):
        db_utils.delete_row(self.database_file, 'categories', category_id)
        logging.info(f"Category removed from project")

    def get_category_childs_names(self, category_id):
        child_names = []
        assets_rows = db_utils.get_row_by_column_data(self.database_file, 'assets', ('category_id', category_id))
        for row in assets_rows:
            child_names.append(row[1])
        return child_names

    def get_category_childs(self, category_id):
        assets_rows = db_utils.get_row_by_column_data(self.database_file, 'assets', ('category_id', category_id))
        return assets_rows

    def get_category_parent_id(self, category_id):
        category_rows = db_utils.get_row_by_column_data(self.database_file, 'categories', ('id', category_id))
        if category_rows and len(category_rows) >= 1:
            return category_rows[0][4]
        else:
            logging.error("Category not found")
            return None

    def get_category_name(self, category_id):
        category_rows = db_utils.get_row_by_column_data(self.database_file, 'categories', ('id', category_id))
        if category_rows and len(category_rows) >= 1:
            return category_rows[0][1]
        else:
            logging.error("Category not found")
            return None

    def add_asset(self, name, category_id):
        if name not in self.get_category_childs_names(category_id):
            asset_id = db_utils.create_row(self.database_file,
                                'assets', 
                                ('name', 'creation_time', 'creation_user', 'category_id'), 
                                (name, time.time(), environment.get_user(), category_id))
            if asset_id:
                logging.info(f"Asset {name} added to project")
                return asset_id
            else:
                return None
        else:
            logging.warning(f"{name} already exists")

    def remove_asset(self, asset_id):
        db_utils.delete_row(self.database_file, 'assets', asset_id)
        logging.info(f"Asset removed from project")

    def get_asset_childs_names(self, asset_id):
        child_names = []
        stages_rows = db_utils.get_row_by_column_data(self.database_file, 'stages', ('asset_id', asset_id))
        for row in stages_rows:
            child_names.append(row[1])
        return child_names

    def get_asset_childs(self, asset_id):
        stages_rows = db_utils.get_row_by_column_data(self.database_file, 'stages', ('asset_id', asset_id))
        return stages_rows

    def get_asset_parent_id(self, asset_id):
        assets_rows = db_utils.get_row_by_column_data(self.database_file, 'assets', ('id', asset_id))
        if assets_rows and len(assets_rows) >= 1:
            return assets_rows[0][4]
        else:
            logging.error("Asset not found")
            return None

    def get_asset_name(self, asset_id):
        assets_rows = db_utils.get_row_by_column_data(self.database_file, 'assets', ('id', asset_id))
        if assets_rows and len(assets_rows) >= 1:
            return assets_rows[0][1]
        else:
            logging.error("Asset not found")
            return None

    def add_stage(self, name, asset_id):
        if name not in self.get_asset_childs_names(asset_id):
            stage_id = db_utils.create_row(self.database_file,
                                'stages', 
                                ('name', 'creation_time', 'creation_user', 'asset_id'), 
                                (name, time.time(), environment.get_user(), asset_id))
            if stage_id:
                logging.info(f"Stage {name} added to project")
                return stage_id
            else:
                return None
        else:
            logging.warning(f"{name} already exists")

    def remove_stage(self, stage_id):
        db_utils.delete_row(self.database_file, 'stages', stage_id)
        logging.info(f"Stage removed from project")

    def get_stage_parent_id(self, stage_id):
        stages_rows = db_utils.get_row_by_column_data(self.database_file, 'stages', ('id', stage_id))
        if stages_rows and len(stages_rows) >= 1:
            return stages_rows[0][5]
        else:
            logging.error("Stage not found")
            return None

    def set_stage_default_variant(self, stage_id, variant_id):
        if db_utils.update_data(self.database_file,
                            'stages',
                            ('default_variant_id', variant_id),
                            ('id', stage_id)):
            logging.info('Default variant modified')

    def get_stage_name(self, stage_id):
        stages_rows = db_utils.get_row_by_column_data(self.database_file, 'stages', ('id', stage_id))
        if stages_rows and len(stages_rows) >= 1:
            return stages_rows[0][1]
        else:
            logging.error("Stage not found")
            return None

    def get_stage_childs_names(self, stage_id):
        child_names = []
        variants_rows = db_utils.get_row_by_column_data(self.database_file, 'variants', ('stage_id', stage_id))
        for row in variants_rows:
            child_names.append(row[1])
        return child_names

    def get_stage_childs(self, stage_id):
        variants_rows = db_utils.get_row_by_column_data(self.database_file, 'variants', ('stage_id', stage_id))
        return variants_rows

    def add_variant(self, name, stage_id, comment):
        if name not in self.get_stage_childs_names(stage_id):
            variant_id = db_utils.create_row(self.database_file,
                                'variants', 
                                ('name', 'creation_time', 'creation_user', 'comment', 'stage_id'), 
                                (name, time.time(), environment.get_user(), comment, stage_id))
            if variant_id:
                logging.info(f"Variant {name} added to project")
                return variant_id
            else:
                return None
        else:
            logging.warning(f"{name} already exists")

    def remove_variant(self, variant_id):
        db_utils.delete_row(self.database_file, 'variants', variant_id)
        logging.info(f"Variant removed from project")

    def get_variant_parent_id(self, variant_id):
        variants_rows = db_utils.get_row_by_column_data(self.database_file, 'variants', ('id', variant_id))
        if variants_rows and len(variants_rows) >= 1:
            return variants_rows[0][5]
        else:
            logging.error("Variant not found")
            return None

    def get_variant_name(self, variant_id):
        variants_rows = db_utils.get_row_by_column_data(self.database_file, 'variants', ('id', variant_id))
        if variants_rows and len(variants_rows) >= 1:
            return variants_rows[0][1]
        else:
            logging.error("Variant not found")
            return None

    def get_variant_work_envs_childs_names(self, variant_id):
        child_names = []
        work_envs_rows = db_utils.get_row_by_column_data(self.database_file, 'work_envs', ('variant_id', variant_id))
        for row in work_envs_rows:
            child_names.append(row[1])
        return child_names

    def get_variant_work_envs_childs(self, variant_id):
        work_envs_rows = db_utils.get_row_by_column_data(self.database_file, 'work_envs', ('variant_id', variant_id))
        return work_envs_rows

    def add_work_env(self, name, variant_id):
        if name not in self.get_variant_work_envs_childs_names(variant_id):
            work_env_id = db_utils.create_row(self.database_file,
                                'work_envs', 
                                ('name', 'creation_time', 'creation_user', 'variant_id'), 
                                (name, time.time(), environment.get_user(), variant_id))
            if work_env_id:
                logging.info(f"Work env {name} added to project")
                return work_env_id
            else:
                return None
        else:
            logging.warning(f"{name} already exists")
            return None

    def remove_work_env(self, work_env_id):
        db_utils.delete_row(self.database_file, 'work_envs', work_env_id)
        logging.info(f"Work env removed from project")

    def get_work_versions_names(self, work_env_id):
        child_names = []
        versions_rows = db_utils.get_row_by_column_data(self.database_file, 'versions', ('work_env_id', work_env_id))
        for row in versions_rows:
            child_names.append(row[1])
        return child_names

    def get_work_versions(self, work_env_id):
        versions_rows = db_utils.get_row_by_column_data(self.database_file, 'versions', ('work_env_id', work_env_id))
        return versions_rows

    def get_work_env_parent_id(self, work_env_id):
        work_envs_rows = db_utils.get_row_by_column_data(self.database_file, 'work_envs', ('id', work_env_id))
        if work_envs_rows and len(work_envs_rows) >= 1:
            return work_envs_rows[0][4]
        else:
            logging.error("Work env not found")
            return None

    def get_work_env_name(self, work_env_id):
        work_envs_rows = db_utils.get_row_by_column_data(self.database_file, 'work_envs', ('id', work_env_id))
        if work_envs_rows and len(work_envs_rows ) >= 1:
            return work_envs_rows[0][1]
        else:
            logging.error("Work env not found")
            return None

    def add_version(self, name, dir_name, work_env_id, comment=''):
        if name not in self.get_work_versions_names(work_env_id):
            version_id = db_utils.create_row(self.database_file,
                                'versions', 
                                ('name', 'creation_time', 'creation_user', 'comment', 'dir_name', 'work_env_id'), 
                                (name, time.time(), environment.get_user(), comment, dir_name, work_env_id))
            if version_id:
                logging.info(f"Version {name} added to project")
                return version_id
            else:
                return None
        else:
            logging.warning(f"{name} already exists")
            return None

    def remove_version(self, version_id):
        db_utils.delete_row(self.database_file, 'versions', version_id)
        logging.info(f"Version removed from project")

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
                                        FOREIGN KEY (variant_id) REFERENCES variants (id)
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
                                        dir_name text NOT NULL,
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
                                        dir_name text NOT NULL,
                                        export_id integer NOT NULL,
                                        FOREIGN KEY (export_id) REFERENCES exports (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Export versions table created")