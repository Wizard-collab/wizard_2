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
        return domain_rows[0][1]

    def get_domain_path(self, domain_id):
        domain_rows = db_utils.get_row_by_column_data(self.database_file, 'domains', ('id', domain_id))
        return domain_rows[0][4]

    def get_domain_childs_names(self, domain_id):
        child_names = []
        categories_rows = db_utils.get_row_by_column_data(self.database_file, 'categories', ('domain_id', domain_id))
        for row in categories_rows:
            child_names.append(row[1])
        return child_names

    def get_domain_childs(self, domain_id):
        child_names = []
        categories_rows = db_utils.get_row_by_column_data(self.database_file, 'categories', ('domain_id', domain_id))
        return categories_rows

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

    def get_category_childs_names(self, category_id):
        child_names = []
        assets_rows = db_utils.get_row_by_column_data(self.database_file, 'assets', ('category_id', category_id))
        for row in assets_rows:
            child_names.append(row[1])
        return child_names

    def get_category_childs(self, category_id):
        child_names = []
        assets_rows = db_utils.get_row_by_column_data(self.database_file, 'assets', ('category_id', category_id))
        return assets_rows

    def get_category_parent_id(self, category_id):
        category_rows = db_utils.get_row_by_column_data(self.database_file, 'categories', ('id', category_id))
        return category_rows[0][4]

    def get_category_name(self, category_id):
        category_rows = db_utils.get_row_by_column_data(self.database_file, 'categories', ('id', category_id))
        return category_rows[0][1]

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

    def get_asset_childs_names(self, asset_id):
        child_names = []
        stages_rows = db_utils.get_row_by_column_data(self.database_file, 'stages', ('asset_id', asset_id))
        for row in stages_rows:
            child_names.append(row[1])
        return child_names

    def get_asset_childs(self, asset_id):
        child_names = []
        stages_rows = db_utils.get_row_by_column_data(self.database_file, 'stages', ('asset_id', asset_id))
        return stages_rows

    def get_asset_parent_id(self, asset_id):
        assets_rows = db_utils.get_row_by_column_data(self.database_file, 'assets', ('id', asset_id))
        return assets_rows[0][4]

    def get_asset_name(self, asset_id):
        category_rows = db_utils.get_row_by_column_data(self.database_file, 'assets', ('id', asset_id))
        return category_rows[0][1]

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

    def get_stage_parent_id(self, stage_id):
        stages_rows = db_utils.get_row_by_column_data(self.database_file, 'stages', ('id', stage_id))
        return stages_rows[0][5]

    def set_stage_default_variant(self, stage_id, variant_id):
        if db_utils.update_data(self.database_file,
                            'stages',
                            ('default_variant_id', variant_id),
                            ('id', stage_id)):
            logging.info('Default variant modified')

    def get_stage_name(self, stage_id):
        stages_rows = db_utils.get_row_by_column_data(self.database_file, 'stages', ('id', stage_id))
        return stages_rows[0][1]

    def get_stage_childs_names(self, stage_id):
        child_names = []
        variants_rows = db_utils.get_row_by_column_data(self.database_file, 'variants', ('stage_id', stage_id))
        for row in variants_rows:
            child_names.append(row[1])
        return child_names

    def get_stage_childs(self, stage_id):
        child_names = []
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
            create_softwares_table(database_file)
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

def create_softwares_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS softwares (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        variant_id integer NOT NULL,
                                        FOREIGN KEY (variant_id) REFERENCES variants (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Softwares table created")

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
                                        software_id integer NOT NULL,
                                        FOREIGN KEY (software_id) REFERENCES softwares (id)
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