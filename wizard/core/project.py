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

from wizard.core import db_utils
from wizard.core import tools
from wizard.core import site
from wizard.core import environment
from wizard.core import image
from wizard.vars import softwares_vars
from wizard.vars import project_vars
from wizard.vars import ressources

class project:
    def __init__(self):
        self.database_file = get_database_file(environment.get_project_path())
        self.project_path = environment.get_project_path()

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

    def get_all_categories(self, column='*'):
        categories_rows = db_utils.get_rows(self.database_file,
                                                'categories',
                                                column)
        return categories_rows

    def add_category(self, name, domain_id):
        if not (db_utils.check_existence_by_multiple_data(self.database_file, 
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

    def get_category_data_by_name(self, name, column='*'):
        category_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'categories',
                                                            ('name', name),
                                                            column)
        if category_rows and len(category_rows) >= 1:
            return category_rows[0]
        else:
            logging.error("Category not found")
            return None

    def add_asset(self, name, category_id):
        if not (db_utils.check_existence_by_multiple_data(self.database_file, 
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

    def get_all_assets(self, column='*'):
        assets_rows = db_utils.get_rows(self.database_file,
                                                'assets',
                                                column)
        return assets_rows

    def search_asset(self, name, category_id=None, column='*'):
        if category_id:
            asset_rows = db_utils.get_row_by_column_part_data_and_data(self.database_file,
                                                            'assets',
                                                            ('name', name),
                                                            ('category_id', category_id),
                                                            column)
        else:
            asset_rows = db_utils.get_row_by_column_part_data(self.database_file,
                                                                'assets',
                                                                ('name', name),
                                                                column)
        return asset_rows

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
        if not (db_utils.check_existence_by_multiple_data(self.database_file, 
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

    def get_all_stages(self, column='*'):
        stages_rows = db_utils.get_rows(self.database_file,
                                                'stages',
                                                column)
        return stages_rows

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
        if not (db_utils.check_existence_by_multiple_data(self.database_file, 
                                        'variants',
                                        ('name', 'stage_id'),
                                        (name, stage_id))):
            variant_id = db_utils.create_row(self.database_file,
                                'variants', 
                                ('name',
                                    'creation_time',
                                    'creation_user',
                                    'comment',
                                    'state',
                                    'stage_id'), 
                                (name,
                                    time.time(),
                                    environment.get_user(),
                                    comment,
                                    'todo',
                                    stage_id))
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
            for export_id in self.get_variant_export_childs(variant_id, 'id'):
                self.remove_export(export_id)
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

    def set_variant_data(self, variant_id, column, data):
        if db_utils.update_data(self.database_file,
                                'variants',
                                (column, data),
                                ('id', variant_id)):
            logging.info('Variant modified')
            return 1
        else:
            return None

    def get_variant_work_envs_childs(self, variant_id, column='*'):
        work_envs_rows = db_utils.get_row_by_column_data(self.database_file, 
                                                            'work_envs', 
                                                            ('variant_id', variant_id), 
                                                            column)
        return work_envs_rows

    def get_variant_export_childs(self, variant_id, column='*'):
        exports_rows = db_utils.get_row_by_column_data(self.database_file, 
                                                            'exports', 
                                                            ('variant_id', variant_id), 
                                                            column)
        return exports_rows

    def get_export_by_name(self, name, variant_id):
        export_row = db_utils.get_row_by_multiple_data(self.database_file, 
                                                            'exports', 
                                                            ('name', 'variant_id'), 
                                                            (name, variant_id))
        if export_row and len(export_row) >= 1:
            return export_row[0]
        else:
            logging.error("Export not found")
            return None

    def get_export_data(self, export_id, column='*'):
        export_rows = db_utils.get_row_by_column_data(self.database_file, 
                                                            'exports', 
                                                            ('id', export_id), 
                                                            column)
        if export_rows and len(export_rows) >= 1:
            return export_rows[0]
        else:
            logging.error("Export not found")
            return None

    def get_export_childs(self, export_id, column='*'):
        exports_versions_rows = db_utils.get_row_by_column_data(self.database_file, 
                                                            'export_versions', 
                                                            ('export_id', export_id), 
                                                            column)
        return exports_versions_rows

    def is_export(self, name, variant_id):
        return db_utils.check_existence_by_multiple_data(self.database_file, 
                                        'exports',
                                        ('name', 'variant_id'),
                                        (name, variant_id))

    def add_export(self, name, variant_id):
        if not (db_utils.check_existence_by_multiple_data(self.database_file, 
                                        'exports',
                                        ('name', 'variant_id'),
                                        (name, variant_id))):
            export_id = db_utils.create_row(self.database_file,
                                'exports', 
                                ('name',
                                    'creation_time',
                                    'creation_user',
                                    'variant_id'), 
                                (name,
                                    time.time(),
                                    environment.get_user(),
                                    variant_id))
            if export_id:
                logging.info(f"Export root {name} added to project")
            return export_id
        else:
            logging.warning(f"{name} already exists")

    def remove_export(self, export_id):
        success = None
        if site.site().is_admin():
            for export_version_id in self.get_export_childs(export_id, 'id'):
                self.remove_export_version(export_version_id)
            success = db_utils.delete_row(self.database_file, 'exports', export_id)
            if success:
                logging.info("Export removed from project")
        return success

    def get_export_versions(self, export_id, column='*'):
        export_versions_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'export_versions',
                                                            ('export_id', export_id),
                                                            column)
        return export_versions_rows

    def get_last_export_version(self, export_id, column='*'):
        versions_rows = db_utils.get_last_row_by_column_data(self.database_file,
                                                            'export_versions',
                                                            ('export_id', export_id),
                                                            column)
        return versions_rows

    def add_export_version(self, name, files, export_id, work_version_id=None, comment=''):
        if not (db_utils.check_existence_by_multiple_data(self.database_file, 
                                        'export_versions',
                                        ('name', 'export_id'),
                                        (name, export_id))):
            export_version_id = db_utils.create_row(self.database_file,
                                'export_versions', 
                                ('name',
                                    'creation_time',
                                    'creation_user',
                                    'comment',
                                    'files',
                                    'work_version_id',
                                    'export_id'), 
                                (name,
                                    time.time(),
                                    environment.get_user(),
                                    comment,
                                    json.dumps(files),
                                    work_version_id,
                                    export_id))
            if export_version_id:
                logging.info(f"Export version {name} added to project")
            return export_version_id
        else:
            logging.warning(f"{name} already exists")

    def get_export_version_destinations(self, export_version_id, column='*'):
        references_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'references_data',
                                                            ('export_version_id', export_version_id),
                                                            column)
        return references_rows

    def remove_export_version(self, export_version_id):
        success = None
        if site.site().is_admin():
            for ticket_id in self.get_export_version_tickets(export_version_id, 'id'):
                self.remove_ticket(ticket_id)
            for reference_id in self.get_export_version_destinations(export_version_id, 'id'):
                self.remove_reference(reference_id)
            success = db_utils.delete_row(self.database_file, 'export_versions', export_version_id)
            if success:
                logging.info("Export version removed from project")
        return success

    def get_export_version_tickets(self, export_version_id, column='*'):
        tickets_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'tickets',
                                                            ('export_version_id', export_version_id),
                                                            column)
        return tickets_rows

    def get_export_version_data(self, export_version_id, column='*'):
        export_versions_rows = db_utils.get_row_by_column_data(self.database_file, 
                                                            'export_versions', 
                                                            ('id', export_version_id), 
                                                            column)
        if export_versions_rows and len(export_versions_rows) >= 1:
            return export_versions_rows[0]
        else:
            logging.error("Export version not found")
            return None

    def add_work_env(self, name, software_id, variant_id):
        if not (db_utils.check_existence_by_multiple_data(self.database_file, 
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

    def create_reference(self, work_env_id, export_version_id, namespace):
        reference_id = None
        if not (db_utils.check_existence_by_multiple_data(self.database_file, 
                                        'references_data',
                                        ('namespace', 'work_env_id'),
                                        (namespace, work_env_id))):
            reference_id = db_utils.create_row(self.database_file,
                                    'references_data', 
                                    ('creation_time',
                                        'creation_user',
                                        'namespace',
                                        'work_env_id',
                                        'export_version_id'),
                                    (time.time(),
                                        environment.get_user(),
                                        namespace,
                                        work_env_id,
                                        export_version_id))
            if work_env_id:
                logging.info(f"Reference created")
        else:
            logging.warning(f"{namespace} already exists")
        return reference_id

    def remove_reference(self, reference_id):
        success = db_utils.delete_row(self.database_file, 'references_data', reference_id)
        if success:
            logging.info("Reference deleted")
        return success

    def get_references(self, work_env_id, column='*'):
        references_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'references_data',
                                                            ('work_env_id', work_env_id),
                                                            column)
        return references_rows

    def remove_work_env(self, work_env_id):
        success = None
        if site.site().is_admin():
            for version_id in self.get_work_versions(work_env_id, 'id'):
                self.remove_version(version_id)
            for reference_id in self.get_references(work_env_id, 'id'):
                self.remove_reference(reference_id)
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
            lock_user_name = site.site().get_user_data(work_env_lock_id, 'user_name')
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

    def add_version(self, name, file_path, work_env_id, comment='', screenshot_path=None):
        version_id = db_utils.create_row(self.database_file,
                            'versions', 
                            ('name',
                                'creation_time',
                                'creation_user',
                                'comment',
                                'file_path',
                                'screenshot_path',
                                'work_env_id'), 
                            (name,
                                time.time(),
                                environment.get_user(),
                                comment,
                                file_path,
                                screenshot_path,
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

    def set_software_additionnal_scripts(self, software_id, paths_list):
        if db_utils.update_data(self.database_file,
                                'softwares',
                                ('additionnal_scripts', json.dumps(paths_list)),
                                ('id', software_id)):
            logging.info('Additionnal script env modified')
            return 1
        else:
            return None

    def set_software_additionnal_env(self, software_id, env_dic):
        if db_utils.update_data(self.database_file,
                                'softwares',
                                ('additionnal_env', json.dumps(env_dic)),
                                ('id', software_id)):
            logging.info('Additionnal env modified')
            return 1
        else:
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

    def create_extension_row(self, stage, software_id, extension):
        if db_utils.create_row(self.database_file,
                                    'extensions',
                                    ('stage',
                                        'software_id',
                                        'extension'),
                                    (stage,
                                        software_id,
                                        extension)):
            logging.info("Extension added")
            return 1
        else:
            return None

    def get_extension(self, stage, software_id):
        export_row = db_utils.get_row_by_multiple_data(self.database_file, 
                                                            'extensions', 
                                                            ('stage', 'software_id'), 
                                                            (stage, software_id))
        if export_row and len(export_row) >= 1:
            return export_row[0]['extension']
        else:
            logging.error("Extension not found")
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

    def create_ticket(self, title, message, export_version_id, destination_user=None, files=[]):
        ticket_id = None
        export_id = self.get_export_version_data(export_version_id, 'export_id')

        is_user = None
        if not destination_user:
            is_user=1
        elif destination_user:
            if site.site().get_user_row_by_name(destination_user):
                is_user=1

        copied_files = tools.copy_files(files, self.get_shared_files_folder())

        if is_user:
            if copied_files is not None:
                if export_id:
                    variant_id = self.get_export_data(export_id, 'variant_id')
                    if variant_id:
                        ticket_id = db_utils.create_row(self.database_file,
                                                            'tickets',
                                                            ('creation_user',
                                                                'creation_time',
                                                                'title',
                                                                'message',
                                                                'state',
                                                                'variant_id',
                                                                'export_version_id',
                                                                'destination_user', 
                                                                'files'),
                                                            (environment.get_user(),
                                                                time.time(),
                                                                title,
                                                                message,
                                                                1,
                                                                variant_id,
                                                                export_version_id,
                                                                destination_user,
                                                                json.dumps(copied_files)))
                        if ticket_id:
                            logging.info("Ticket created")
        return ticket_id

    def get_ticket_data(self, ticket_id, column='*'):
        tickets_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'tickets',
                                                            ('id', ticket_id),
                                                            column)
        if tickets_rows and len(tickets_rows) >= 1:
            return tickets_rows[0]
        else:
            logging.error("Ticket not found")
            return None

    def change_ticket_state(self, ticket_id, state):
        if db_utils.update_data(self.database_file,
                                        'tickets',
                                        ('state', state),
                                        ('id', ticket_id)):
            if not state:
                logging.info('Ticket closed')
            else:
                logging.info('Ticket openned')
            return 1
        else:
            return None

    def remove_ticket(self, ticket_id):
        success = None
        if site.site().is_admin():
            success = db_utils.delete_row(self.database_file, 'tickets', ticket_id)
            if success :
                logging.info(f"Ticket removed from project")
        return success

    def get_shared_files_folder(self):
        shared_files_folder = os.path.join(self.project_path, project_vars._shared_files_folder_)
        return shared_files_folder

    def get_scripts_folder(self):
        shared_files_folder = os.path.join(self.project_path, project_vars._scripts_folder_)
        return shared_files_folder

    def add_event(self, event_type, message, data):
        event_id = db_utils.create_row(self.database_file,
                                                'events',
                                                ('creation_user',
                                                    'creation_time',
                                                    'type',
                                                    'message',
                                                    'data'),
                                                (environment.get_user(),
                                                    time.time(),
                                                    event_type,
                                                    message,
                                                    json.dumps(data)))
        if event_id:
            logging.info("Event added")
        return event_id

    def get_event_data(self, event_id, column='*'):
        events_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'events',
                                                            ('id', event_id),
                                                            column)
        if events_rows and len(events_rows) >= 1:
            return events_rows[0]
        else:
            logging.error("Event not found")
            return None

    def add_shelf_script(self,
                            name,
                            py_file,
                            only_subprocess=0,
                            icon=ressources._default_script_shelf_icon_):
        shelf_script_id = None
        if not db_utils.check_existence(self.database_file, 'shelf_scripts', 'name', name):
            if os.path.isfile(icon):
                icon_bytes = image.convert_image_to_bytes(icon, 45)
            else:
                logging.warning(f"{icon} doesn't exists, assigning default icon")
                icon_bytes = image.convert_image_to_bytes(ressources._default_script_shelf_icon_, 45)

            shelf_script_id = db_utils.create_row(self.database_file,
                                                    'shelf_scripts',
                                                    ('creation_user',
                                                        'creation_time',
                                                        'name',
                                                        'py_file',
                                                        'only_subprocess',
                                                        'icon'),
                                                    (environment.get_user(),
                                                        time.time(),
                                                        name,
                                                        py_file,
                                                        only_subprocess,
                                                        icon_bytes))
            if shelf_script_id:
                logging.info("Shelf script created")
        else:
            logging.warning(f"{name} already exists")
        return shelf_script_id

    def get_shelf_script_data(self, name, column='*'):
        shelf_scripts_rows = db_utils.get_row_by_column_data(self.database_file,
                                                            'shelf_scripts',
                                                            ('name', name),
                                                            column)
        if shelf_scripts_rows and len(shelf_scripts_rows) >= 1:
            return shelf_scripts_rows[0]
        else:
            logging.error("Shelf script not found")
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
        if db_utils.create_database(database_file):
            create_domains_table(database_file)
            create_categories_table(database_file)
            create_assets_table(database_file)
            create_stages_table(database_file)
            create_variants_table(database_file)
            create_work_envs_table(database_file)
            create_references_table(database_file)
            create_exports_table(database_file)
            create_versions_table(database_file)
            create_export_versions_table(database_file)
            create_softwares_table(database_file)
            create_settings_table(database_file)
            create_extensions_table(database_file)
            create_tickets_table(database_file)
            create_events_table(database_file)
            create_shelf_scripts_table(database_file)
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
                                        state text NOT NULL,
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

def create_references_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS references_data (
                                        id integer PRIMARY KEY,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        namespace text NOT NULL,
                                        work_env_id integer NOT NULL,
                                        export_version_id integer NOT NULL,
                                        FOREIGN KEY (work_env_id) REFERENCES work_envs (id)
                                        FOREIGN KEY (export_version_id) REFERENCES export_versions (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("References table created")

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
                                        screenshot_path text,
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
                                        files text NOT NULL,
                                        work_version_id integer,
                                        export_id integer NOT NULL,
                                        FOREIGN KEY (export_id) REFERENCES exports (id)
                                        FOREIGN KEY (work_version_id) REFERENCES versions (id)
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

def create_extensions_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS extensions (
                                        id integer PRIMARY KEY,
                                        stage text NOT NULL,
                                        software_id integer NOT NULL,
                                        extension text NOT NULL
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Extensions table created")

def create_tickets_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS tickets (
                                        id integer PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        creation_time real NOT NULL,
                                        title text NOT NULL,
                                        message text NOT NULL,
                                        state bool,
                                        variant_id integer NOT NULL,
                                        export_version_id integer NOT NULL,
                                        destination_user text,
                                        files text,
                                        FOREIGN KEY (variant_id) REFERENCES variants (id)
                                        FOREIGN KEY (export_version_id) REFERENCES export_versions (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Tickets table created")

def create_events_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS events (
                                        id integer PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        creation_time real NOT NULL,
                                        type text NOT NULL,
                                        message text NOT NULL,
                                        data text
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Events table created")

def create_shelf_scripts_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS shelf_scripts (
                                        id integer PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        creation_time real NOT NULL,
                                        name text NOT NULL UNIQUE,
                                        py_file text NOT NULL,
                                        only_subprocess bool NOT NULL,
                                        icon blob NOT NULL
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Shelf scripts table created")