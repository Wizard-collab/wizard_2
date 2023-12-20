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
import re
import os
import time
import datetime
import json
import shutil
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
from wizard.vars import env_vars
from wizard.vars import ressources

logger = logging.getLogger(__name__)

def add_domain(name):
    domain_id = db_utils.create_row('project',
                        'domains_data', 
                        ('name', 'creation_time', 'creation_user', 'string'), 
                        (name, time.time(), environment.get_user(), name))
    if not domain_id:
        logger.warning(f"{name} not added to project")
        return
    logger.info(f"Domain {name} added to project")
    return domain_id

def get_domains(column='*'):
    domain_rows = db_utils.get_rows('project', 'domains_data', column=column)
    return domain_rows

def get_domain_data(domain_id, column='*'):
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
    categories_rows = db_utils.get_row_by_column_data('project',
                                                    'categories',
                                                    ('domain_id', domain_id),
                                                    column)
    return categories_rows

def get_domain_child_by_name(domain_id, category_name, column='*'):
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
    categories_rows = db_utils.get_rows('project',
                                            'categories',
                                            column)
    return categories_rows

def add_category(name, domain_id):
    if name == '' or name is None:
        logger.warning(f"Please provide a valid category name")
        return
    if (db_utils.check_existence_by_multiple_data('project', 
                                    'categories',
                                    ('name', 'domain_id'),
                                    (name, domain_id))):
        logger.warning(f"{name} already exists")
        return
    domain_name = get_domain_data(domain_id, 'name')
    string_asset = f"{domain_name}/{name}"
    category_id = db_utils.create_row('project',
                        'categories',
                        ('name', 'creation_time', 'creation_user', 'string', 'domain_id'), 
                        (name, time.time(), environment.get_user(), string_asset, domain_id))
    if not category_id:
        return
    logger.info(f"Category {name} added to project")
    return category_id

def remove_category(category_id, force=0):
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
    assets_rows = db_utils.get_row_by_column_data('project',
                                                    'assets',
                                                    ('category_id', category_id),
                                                    column)
    return assets_rows

def get_category_child_by_name(category_id, asset_name, column='*'):
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
    asset_rows = db_utils.get_row_by_column_data('project',
                                                        'assets',
                                                        ('string', string),
                                                        column)
    if not asset_rows or len(asset_rows) < 1:
        logger.error("Asset not found")
        return
    return asset_rows[0]

def add_asset_preview(asset_id):
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
    assets_preview_rows = db_utils.get_rows('project',
                                            'assets_preview',
                                            column)
    return assets_preview_rows

def modify_asset_preview(asset_id, preview_path):
    if not db_utils.update_data('project',
                            'assets_preview',
                            ('preview_path', preview_path),
                            ('asset_id', asset_id)):
        return
    logger.debug('Asset preview modified')
    return 1

def remove_asset_preview(asset_id):
    if not db_utils.delete_row('project',
                                'assets_preview',
                                asset_id,
                                'asset_id'):
        return
    logger.info(f"Asset preview removed from project")
    return 1

def modify_asset_manual_preview(asset_id, preview_path):
    if not db_utils.update_data('project',
                            'assets_preview',
                            ('manual_override', preview_path),
                            ('asset_id', asset_id)):
        return
    logger.debug('Asset preview modified')
    return 1

def get_all_assets(column='*'):
    assets_rows = db_utils.get_rows('project',
                                            'assets',
                                            column)
    return assets_rows

def get_all_sequence_assets(column='*'):
    domain_id = get_domain_by_name('sequences', 'id')
    categories_ids = get_domain_childs(domain_id, 'id')
    assets_rows = []
    for category_id in categories_ids:
        assets_rows += (get_category_childs(category_id))
    return assets_rows

def remove_asset(asset_id, force=0):
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
    stages_rows = db_utils.get_row_by_column_data('project',
                                                        'stages',
                                                        ('asset_id', asset_id),
                                                        column)
    return stages_rows

def get_asset_child_by_name(asset_id, stage_name, column='*'):
    stages_rows = db_utils.get_row_by_multiple_data('project',
                                                    'stages',
                                                    ('asset_id', 'name'),
                                                    (asset_id, stage_name),
                                                    column)
    if stages_rows is None or len(stages_rows) < 1:
        logger.error("Stage not found")
        return
    return stages_rows[0]

def get_asset_data(asset_id, colmun='*'):
    assets_rows = db_utils.get_row_by_column_data('project',
                                                        'assets',
                                                        ('id', asset_id),
                                                        colmun)
    if assets_rows is None or len(assets_rows) < 1:
        logger.error("Asset not found")
        return
    return assets_rows[0]

def add_stage(name, asset_id):
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
    stage_rows = db_utils.get_row_by_column_data('project',
                                                'stages',
                                                ('string', string),
                                                column)
    if stage_rows is None or len(stage_rows) < 1:
        logger.error("Stage not found")
        return
    return stage_rows[0]

def get_all_stages(column='*'):
    stages_rows = db_utils.get_rows('project',
                                        'stages',
                                        column)
    return stages_rows

def remove_stage(stage_id, force = 0):
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
    if not db_utils.update_data('project',
                        'stages',
                        ('default_variant_id', variant_id),
                        ('id', stage_id)):
        return
    logger.debug('Default variant modified')
    return 1

def get_stage_data(stage_id, column='*'):
    stages_rows = db_utils.get_row_by_column_data('project',
                                                        'stages',
                                                        ('id', stage_id),
                                                        column)
    if stages_rows is None or len(stages_rows) < 1:
        logger.error("Stage not found")
        return
    return stages_rows[0]

def get_stage_childs(stage_id, column='*'):
    variants_rows = db_utils.get_row_by_column_data('project',
                                                        'variants',
                                                        ('stage_id', stage_id),
                                                        column)
    return variants_rows

def get_stage_child_by_name(stage_id, variant_name, column='*'):
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
    variant_rows = db_utils.get_row_by_column_data('project',
                                                    'variants',
                                                    ('string', string),
                                                    column)
    if variant_rows is None or len(variant_rows) < 1:
        logger.error("Variant not found")
        return
    return variant_rows[0]

def get_variant_by_name(stage_id, name, column='*'):
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
    variants_rows = db_utils.get_rows('project',
                                            'variants',
                                            column)
    return variants_rows

def search_variant_by_column_data(data_tuple, column='*'):
    variants_rows = db_utils.get_row_by_column_part_data('project',
                                                        'variants',
                                                        (data_tuple[0], data_tuple[1]),
                                                        column)
    return variants_rows

def get_variant_work_env_child_by_name(variant_id, work_env_name, column='*'):
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
    return db_utils.check_existence('project', 'work_envs', 'id', work_env_id)

def remove_variant(variant_id, force = 0):
    if not force:
        if not repository.is_admin():
            return
    for work_env_id in get_variant_work_envs_childs(variant_id, 'id'):
        remove_work_env(work_env_id, force)
    for video_id in get_videos(variant_id, 'id'):
        remove_video(video_id)
    for stage_id in db_utils.get_row_by_column_data('project', 
                                                    'stages', 
                                                    ('default_variant_id', variant_id), 
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
    variants_rows = db_utils.get_row_by_column_data('project', 
                                                        'variants', 
                                                        ('id', variant_id), 
                                                        column)
    if variants_rows is None or len(variants_rows) < 1:
        logger.error("Variant not found")
        return
    return variants_rows[0]

def set_variant_data(variant_id, column, data):
    if not db_utils.update_data('project',
                            'variants',
                            (column, data),
                            ('id', variant_id)):
        return
    logger.debug('Variant modified')
    return 1

def set_stage_data(stage_id, column, data):
    if not db_utils.update_data('project',
                            'stages',
                            (column, data),
                            ('id', stage_id)):
        return
    logger.debug('Stage modified')
    return 1

def add_asset_tracking_event(stage_id, event_type, data, comment=''):
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
    if not repository.is_admin():
        return
    if not db_utils.delete_row('project', 'asset_tracking_events', asset_tracking_event_id):
        logger.warning(f"Asset tracking event NOT removed from project")
        return
    logger.info(f"Asset tracking event removed from project")
    return 1

def remove_progress_event(progress_event_id):
    if not repository.is_admin():
        return
    if not db_utils.delete_row('project', 'progress_events', progress_event_id):
        logger.warning(f"Stage progress event NOT removed from project")
    logger.info(f"Stage progress event removed from project")
    return 1

def get_asset_tracking_event_data(asset_tracking_event_id, column='*'):
    asset_tracking_events_rows = db_utils.get_row_by_column_data('project',
                                                        'asset_tracking_events',
                                                        ('id', asset_tracking_event_id),
                                                        column)
    if asset_tracking_events_rows is None or len(asset_tracking_events_rows) < 1:
        logger.error("Asset tracking event not found")
        return
    return asset_tracking_events_rows[0]

def get_asset_tracking_events(stage_id, column='*'):
    asset_tracking_events_rows = db_utils.get_row_by_column_data('project', 
                                                        'asset_tracking_events', 
                                                        ('stage_id', stage_id), 
                                                        column)
    return asset_tracking_events_rows

def get_all_progress_events(column='*'):
    progress_events_rows = db_utils.get_rows('project',
                                        'progress_events',
                                        column, order='id')
    return progress_events_rows

def get_variant_work_envs_childs(variant_id, column='*'):
    work_envs_rows = db_utils.get_row_by_column_data('project', 
                                                        'work_envs', 
                                                        ('variant_id', variant_id), 
                                                        column)
    return work_envs_rows

def get_work_env_variant_child_by_name(variant_id, work_env_name, column='*'):
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
    exports_rows = db_utils.get_row_by_column_data('project', 
                                                        'exports', 
                                                        ('stage_id', stage_id), 
                                                        column)
    return exports_rows

def get_export_by_name(name, stage_id):
    export_row = db_utils.get_row_by_multiple_data('project', 
                                                        'exports', 
                                                        ('name', 'stage_id'), 
                                                        (name, stage_id))
    if export_row is None and len(export_row) < 1:
        logger.error("Export not found")
        return
    return export_row[0]

def get_export_data(export_id, column='*'):
    export_rows = db_utils.get_row_by_column_data('project', 
                                                        'exports', 
                                                        ('id', export_id), 
                                                        column)
    if export_rows is None or len(export_rows) < 1:
        logger.error("Export not found")
        return
    return export_rows[0]

def get_export_childs(export_id, column='*'):
    exports_versions_rows = db_utils.get_row_by_column_data('project', 
                                                        'export_versions', 
                                                        ('export_id', export_id), 
                                                        column)
    return exports_versions_rows

def is_export(name, stage_id):
    return db_utils.check_existence_by_multiple_data('project', 
                                    'exports',
                                    ('name', 'stage_id'),
                                    (name, stage_id))

def add_export(name, stage_id):
    if (db_utils.check_existence_by_multiple_data('project', 
                                    'exports',
                                    ('name', 'stage_id'),
                                    (name, stage_id))):
        logger.warning(f"{name} already exists")
        return
    #variant_row = get_variant_data(variant_id)
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
    export_rows = db_utils.get_row_by_column_data('project',
                                                        'exports',
                                                        ('string', string),
                                                        column)
    if export_rows is None and len(export_rows) < 1:
        logger.error("Export not found")
        return
    return export_rows[0]

def remove_export(export_id, force = 0):
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
    export_versions_rows = db_utils.get_row_by_column_data('project',
                                                        'export_versions',
                                                        ('export_id', export_id),
                                                        column)
    return export_versions_rows

def get_export_versions_by_work_version_id(work_version_id, column='*'):
    export_versions_rows = db_utils.get_row_by_column_data('project',
                                                        'export_versions',
                                                        ('work_version_id', work_version_id),
                                                        column)
    return export_versions_rows

def get_export_versions_by_user_name(creation_user, column='*'):
    export_versions_rows = db_utils.get_row_by_column_data('project',
                                                        'export_versions',
                                                        ('creation_user', creation_user),
                                                        column)
    return export_versions_rows

def get_all_export_versions(column='*'):
    export_versions_rows = db_utils.get_rows('project',
                                                'export_versions',
                                                column)
    return export_versions_rows

def get_default_export_version(export_id, column='*'):
    default_export_version = get_export_data(export_id, 'default_export_version')
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
    datas = db_utils.get_last_row_by_column_data('project',
                                                        'export_versions',
                                                        ('export_id', export_id),
                                                        column)
    if datas is None or datas == []:
        return
    return datas[0]

def set_default_export_version(export_id, export_version_id):
    if not db_utils.update_data('project',
                                'exports',
                                ('default_export_version', export_version_id),
                                ('id', export_id)):
        return
    propagate_auto_update(export_id, export_version_id)
    logger.info(f'Default export version modified')
    return 1

def add_export_version(name, files, export_id, work_version_id=None, comment=''):
    if (db_utils.check_existence_by_multiple_data('project', 
                                    'export_versions',
                                    ('name', 'export_id'),
                                    (name, export_id))):
        logger.warning(f"{name} already exists")
        return
    stage_id = get_export_data(export_id, 'stage_id')
    if work_version_id is not None:
        version_row = get_version_data(work_version_id)
        work_version_thumbnail = version_row['thumbnail_path']
        work_env_id = version_row['work_env_id']
        software_id = get_work_env_data(work_env_id, 'software_id')
        software = get_software_data(software_id, 'name')
    else:
        software = None
        work_version_thumbnail = None
    export_row = get_export_data(export_id)
    #variant_row = get_variant_data(export_row['variant_id'])
    stage_row = get_stage_data(export_row['stage_id'])
    asset_row = get_asset_data(stage_row['asset_id'])
    category_row = get_category_data(asset_row['category_id'])
    domain_name = get_domain_data(category_row['domain_id'], 'name')
    string_asset = f"{domain_name}/"
    string_asset += f"{category_row['name']}/"
    string_asset += f"{asset_row['name']}/"
    string_asset += f"{stage_row['name']}/"
    #string_asset += f"{variant_row['name']}/"
    string_asset += f"{export_row['name']}/"
    string_asset += f"{name}"
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
    if not export_version_id:
        return
    logger.info(f"Export version {name} added to project")
    tags.analyse_comment(comment, 'export_version', export_version_id)
    propagate_auto_update(export_id, export_version_id)
    return export_version_id

def get_export_version_data_by_string(string, column='*'):
    export_version_rows = db_utils.get_row_by_column_data('project',
                                                        'exports_versions',
                                                        ('string', string),
                                                        column)
    if export_version_rows is None or len(export_version_rows) < 1:
        logger.error("Export version not found")
        return
    return export_version_rows[0]

def propagate_auto_update(export_id, export_version_id):
    default_export_version_id = get_default_export_version(export_id, 'id')
    if (export_version_id == default_export_version_id) or (export_version_id is None):
        references_rows = db_utils.get_row_by_multiple_data('project', 
                                                            'references_data', 
                                                            ('export_id', 'auto_update'), 
                                                            (export_id, 1))
        grouped_references_rows = db_utils.get_row_by_multiple_data('project', 
                                                            'grouped_references_data', 
                                                            ('export_id', 'auto_update'), 
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
    references_rows = db_utils.get_row_by_column_data('project',
                                                        'references_data',
                                                        ('export_version_id', export_version_id),
                                                        column)
    return references_rows

def get_grouped_export_version_destination(export_version_id, column='*'):
    grouped_references_rows = db_utils.get_row_by_column_data('project',
                                                        'grouped_references_data',
                                                        ('export_version_id', export_version_id),
                                                        column)
    return grouped_references_rows

def get_export_versions_by_stage(stage_id, column='*'):
    export_versions_rows = db_utils.get_row_by_column_data('project',
                                                        'export_versions',
                                                        ('stage_id', stage_id),
                                                        column)
    return export_versions_rows

def remove_export_version(export_version_id, force = 0):
    if not force:
        if not repository.is_admin():
            return
    export_row = get_export_data(get_export_version_data(export_version_id, 'export_id'))
    if export_row['default_export_version'] == export_version_id:
        set_default_export_version(export_row['id'], None)
    for reference_id in get_export_version_destinations(export_version_id, 'id'):
        remove_reference(reference_id)
    for grouped_reference_id in get_grouped_export_version_destination(export_version_id, 'id'):
        remove_grouped_reference(grouped_reference_id)
    if not db_utils.delete_row('project', 'export_versions', export_version_id):
        logger.warning("Export version NOT removed from project")
    logger.info("Export version removed from project")
    return 1

def search_export_version(data_to_search, variant_id=None, column_to_search='name', column='*'):
    if variant_id:
        export_versions_rows = db_utils.get_row_by_column_part_data_and_data('project',
                                                        'export_versions',
                                                        (column_to_search, data_to_search),
                                                        ('variant_id', variant_id),
                                                        column)
    else:
        export_versions_rows = db_utils.get_row_by_column_part_data('project',
                                                            'export_versions',
                                                            (column_to_search, data_to_search),
                                                            column)
    return export_versions_rows

def get_export_version_data(export_version_id, column='*'):
    export_versions_rows = db_utils.get_row_by_column_data('project', 
                                                        'export_versions', 
                                                        ('id', export_version_id), 
                                                        column)
    if export_versions_rows is None or len(export_versions_rows) < 1:
        logger.error("Export version not found")
        return
    return export_versions_rows[0]

def update_export_version_data(export_version_id, data_tuple):
    return db_utils.update_data('project',
                                    'export_versions',
                                    data_tuple,
                                    ('id', export_version_id))

def modify_export_version_comment(export_version_id, comment):
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
    work_env_rows = db_utils.get_row_by_column_data('project',
                                                        'work_envs',
                                                        ('string', string),
                                                        column)
    if work_env_rows is None or len(work_env_rows) < 1:
        logger.error("Work env not found")
        return
    return work_env_rows[0]

def create_reference(work_env_id, export_version_id, namespace, count=None, auto_update=0):
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
                                'auto_update'),
                            (time.time(),
                                environment.get_user(),
                                namespace,
                                count,
                                stage_name,
                                work_env_id,
                                export_id,
                                export_version_id,
                                auto_update))
    if not reference_id:
        return
    logger.info(f"Reference created")
    return reference_id

def remove_reference(reference_id):
    if not db_utils.delete_row('project', 'references_data', reference_id):
        logger.warning("Reference NOT deleted")
        return
    logger.info("Reference deleted")
    return 1

def get_references(work_env_id, column='*'):
    references_rows = db_utils.get_row_by_column_data('project',
                                                        'references_data',
                                                        ('work_env_id', work_env_id),
                                                        column)
    return references_rows

def get_references_by_export_version(export_version_id, column='*'):
    references_rows = db_utils.get_row_by_column_data('project',
                                                        'references_data',
                                                        ('export_version_id', export_version_id),
                                                        column)
    return references_rows

def get_grouped_references_by_export_version(export_version_id, column='*'):
    references_rows = db_utils.get_row_by_column_data('project',
                                                        'grouped_references_data',
                                                        ('export_version_id', export_version_id),
                                                        column)
    return references_rows

def get_references_by_export(export_id, column='*'):
    references_rows = db_utils.get_row_by_column_data('project',
                                                        'references_data',
                                                        ('export_id', export_id),
                                                        column)
    return references_rows

def get_reference_data(reference_id, column='*'):
    reference_rows = db_utils.get_row_by_column_data('project',
                                                        'references_data',
                                                        ('id', reference_id),
                                                        column)
    if reference_rows is None or len(reference_rows) < 1:
        logger.error("Reference not found")
        return
    return reference_rows[0]

def get_reference_by_namespace(work_env_id, namespace, column='*'):
    reference_rows = db_utils.get_row_by_multiple_data('project',
                                                        'references_data',
                                                        ('work_env_id', 'namespace'),
                                                        (work_env_id, namespace),
                                                        column)
    if reference_rows is None or len(reference_rows) < 1:
        logger.error("Reference not found")
        return
    return reference_rows[0]

'''
def modify_reference_variant(reference_id, variant_id):
    exports_list = get_variant_export_childs(variant_id, 'id')
    if exports_list is None or exports_list == []:
        logger.warning("No export found")
        return
    export_id = exports_list[0]
    export_version_id = get_default_export_version(export_id, 'id')
    if export_version_id:
        update_reference_data(reference_id, ('export_id', export_id))
        update_reference_data(reference_id, ('export_version_id', export_version_id))
    return 1
'''

def modify_reference_export(reference_id, export_id):
    export_version_id = get_default_export_version(export_id, 'id')
    if export_version_id:
        update_reference_data(reference_id, ('export_id', export_id))
        update_reference_data(reference_id, ('export_version_id', export_version_id))
    return 1

def modify_reference_auto_update(reference_id, auto_update):
    if auto_update:
        auto_update = 1
    update_reference_data(reference_id, ('auto_update', auto_update))
    if auto_update:
        export_id = get_reference_data(reference_id, 'export_id')
        export_version_id = get_default_export_version(export_id, 'id')
        if not export_version_id:
            return 1
        update_reference_data(reference_id, ('export_version_id', export_version_id))
    return 1

def update_reference_data(reference_id, data_tuple):
    if not db_utils.update_data('project',
                        'references_data',
                        data_tuple,
                        ('id', reference_id)):
        return
    logger.info('Reference modified')
    return 1

def update_reference(reference_id, export_version_id):
    if not db_utils.update_data('project',
                        'references_data',
                        ('export_version_id', export_version_id),
                        ('id', reference_id)):
        return
    logger.info('Reference modified')
    return 1

def remove_work_env(work_env_id, force = 0):
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
    versions_rows = db_utils.get_row_by_column_data('project',
                                                        'versions',
                                                        ('work_env_id', work_env_id),
                                                        column)
    return versions_rows

def get_work_version_by_name(work_env_id, name, column='*'):
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
    versions_rows = db_utils.get_row_by_column_data('project', 
                                                        'versions', 
                                                        ('creation_user', creation_user), 
                                                        column)
    return versions_rows

def get_all_work_versions(column='*'):
    work_versions_rows = db_utils.get_rows('project',
                                                'versions',
                                                column)
    return work_versions_rows

def get_last_work_version(work_env_id, column='*'):
    versions_rows = db_utils.get_last_row_by_column_data('project',
                                                        'versions',
                                                        ('work_env_id', work_env_id),
                                                        column)
    return versions_rows

def get_last_video_version(variant_id, column='*'):
    videos_rows = db_utils.get_last_row_by_column_data('project',
                                                        'videos',
                                                        ('variant_id', variant_id),
                                                        column)
    return videos_rows

def get_work_env_data(work_env_id, column='*'):
    work_env_rows = db_utils.get_row_by_column_data('project',
                                                        'work_envs',
                                                        ('id', work_env_id),
                                                        column)
    if work_env_rows is None or len(work_env_rows) < 1:
        logger.error("Work env not found")
        return
    return work_env_rows[0]

def get_all_work_envs(column='*'):
    work_env_rows = db_utils.get_rows('project',
                                                'work_envs',
                                                column)
    return work_env_rows

def get_work_env_by_name(variant_id, name, column='*'):
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
    if not db_utils.update_data('project',
                                'work_envs',
                                ('export_extension', export_extension),
                                ('id', work_env_id)):
        return
    logger.info(f'Work env export extension modified')
    return 1

def get_user_locks(user_id, column='*'):
    work_env_rows = db_utils.get_row_by_column_data('project',
                                                        'work_envs',
                                                        ('lock_id', user_id),
                                                        column)
    return work_env_rows

def get_lock(work_env_id):
    current_user_id = repository.get_user_row_by_name(environment.get_user(), 'id')
    work_env_lock_id = get_work_env_data(work_env_id, 'lock_id')
    if (not work_env_lock_id) or (work_env_lock_id == current_user_id):
        return
    lock_user_name = repository.get_user_data(work_env_lock_id, 'user_name')
    logger.warning(f"Work env locked by {lock_user_name}")
    return lock_user_name

def set_work_env_lock(work_env_id, lock=1, force=0):
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
    user_id = repository.get_user_row_by_name(environment.get_user(), 'id')
    work_env_ids = get_user_locks(user_id, 'id')
    for work_env_id in work_env_ids:
        set_work_env_lock(work_env_id, 0)
    return 1

def toggle_lock(work_env_id):
    current_user_id = repository.get_user_row_by_name(environment.get_user(), 'id')
    lock_id = get_work_env_data(work_env_id, 'lock_id')
    if lock_id == None:
        return set_work_env_lock(work_env_id)
    elif lock_id == current_user_id:
        return set_work_env_lock(work_env_id, 0)
    lock_user_name = repository.get_user_data(lock_id, 'user_name')
    logger.warning(f"Work env locked by {lock_user_name}")
    return

def add_work_time(work_env_id, time_to_add):
    work_env_row = get_work_env_data(work_env_id)
    work_time = work_env_row['work_time']
    new_work_time = work_time + time_to_add
    return db_utils.update_data('project',
                            'work_envs',
                            ('work_time', new_work_time),
                            ('id', work_env_id))

def add_stage_work_time(stage_id, time_to_add):
    stage_row = get_stage_data(stage_id)
    work_time = stage_row['work_time']
    new_work_time = work_time + time_to_add
    return db_utils.update_data('project',
                            'stages',
                            ('work_time', new_work_time),
                            ('id', stage_id))

def update_stage_progress(stage_id):
    stage_row = get_stage_data(stage_id)
    if stage_row['state'] == 'done' or stage_row['state'] == 'omit' :
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
    day, hour = tools.convert_time(time.time())
    '''
    if db_utils.check_existence_by_multiple_data('project', 
                                    'progress_events',
                                    ('name', 'day'),
                                    (name, day)):
        row_id = db_utils.get_row_by_multiple_data('project',
                                                'progress_events',
                                                ('name', 'day'),
                                                (name, day), 'id')
        db_utils.update_data('project',
                                'progress_events',
                                ('datas_dic', datas_dic),
                                ('id', row_id[0]))
        db_utils.update_data('project',
                                'progress_events',
                                ('creation_time', time.time()),
                                ('id', row_id[0]))
    else:
    '''
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
    return db_utils.update_data('project',
                        'progress_events',
                        data_tuple,
                        ('id', progress_event_id))

def add_version(name, file_path, work_env_id, comment='', screenshot_path=None, thumbnail_path=None):
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
    videos_rows = db_utils.get_row_by_column_data('project',
                                                        'videos',
                                                        ('id', video_id),
                                                        column)
    if videos_rows is None or len(videos_rows) < 1:
        logger.error("Video not found")
        return
    return videos_rows[0]

def get_work_version_data_by_string(string, column='*'):
    work_version_rows = db_utils.get_row_by_column_data('project',
                                                        'versions',
                                                        ('string', string),
                                                        column)
    if work_version_rows is None or len(work_version_rows) < 1:
        logger.error("Work version not found")
        return
    return work_version_rows[0]

def get_version_data(version_id, column='*'):
    work_version_rows = db_utils.get_row_by_column_data('project',
                                                        'versions',
                                                        ('id', version_id),
                                                        column)
    if work_version_rows is None or len(work_version_rows) < 1:
        logger.error("Version not found")
        return
    return work_version_rows[0]

def modify_version_comment(version_id, comment=''):
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
    screenshot_path_success = db_utils.update_data('project',
                        'versions',
                        ('screenshot_path', screenshot_path),
                        ('id', version_id))
    thumbnail_path_success = db_utils.update_data('project',
                        'versions',
                        ('thumbnail_path', thumbnail_path),
                        ('id', version_id))
    if screenshot_path_success*thumbnail_path_success:
        logger.info('Version screen modified')
    return screenshot_path_success*thumbnail_path_success

def remove_version(version_id, force = 0):
    if not force:
        if not repository.is_admin():
            return
    for export_version_id in get_export_versions_by_work_version_id(version_id, 'id'):
        update_export_version_data(export_version_id, ('work_version_id', None))
        update_export_version_data(export_version_id, ('software', None))
    if not db_utils.delete_row('project', 'versions', version_id) :
        logger.warning(f"Version NOT removed from project")
    logger.info(f"Version removed from project")
    return 1

def search_version(data_to_search, work_env_id=None, column_to_search='name', column='*'):
    if work_env_id:
        versions_rows = db_utils.get_row_by_column_part_data_and_data('project',
                                                        'versions',
                                                        (column_to_search, data_to_search),
                                                        ('work_env_id', work_env_id),
                                                        column)
    else:
        versions_rows = db_utils.get_row_by_column_part_data('project',
                                                            'versions',
                                                            (column_to_search, data_to_search),
                                                            column)
    return versions_rows

def add_software(name, extension, file_command, no_file_command, batch_file_command='', batch_no_file_command=''):
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
    softwares_rows = db_utils.get_rows('project', 'softwares', 'name')
    return softwares_rows

def set_software_path(software_id, path):
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
    if not db_utils.update_data('project',
                            'softwares',
                            ('additionnal_scripts', json.dumps(paths_list)),
                            ('id', software_id)):
        logger.warning('Additionnal script env NOT modified')
        return
    logger.info('Additionnal script env modified')
    return 1

def set_software_additionnal_env(software_id, env_dic):
    if not db_utils.update_data('project',
                            'softwares',
                            ('additionnal_env', json.dumps(env_dic)),
                            ('id', software_id)):
        logger.warning('Additionnal env NOT modified')
        return
    logger.info('Additionnal env modified')
    return 1

def get_software_data(software_id, column='*'):
    softwares_rows = db_utils.get_row_by_column_data('project',
                                                        'softwares',
                                                        ('id', software_id),
                                                        column)
    if softwares_rows is None or len(softwares_rows) < 1:
        logger.error("Software not found")
        return
    return softwares_rows[0]

def get_software_data_by_name(software_name, column='*'):
    softwares_rows = db_utils.get_row_by_column_data('project',
                                                        'softwares',
                                                        ('name', software_name),
                                                        column)
    if softwares_rows is None or len(softwares_rows) < 1:
        logger.error("Software not found")
        return
    return softwares_rows[0]

def create_extension_row(stage, software_id, extension):
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
    export_row = db_utils.get_row_by_multiple_data('project', 
                                                        'extensions', 
                                                        ('stage', 'software_id'), 
                                                        (stage, software_id))
    if export_row is None or len(export_row) < 1:
        logger.error("Extension not found")
        return
    return export_row[0]['extension']

def get_default_extension_row(stage, software_id):
    export_row = db_utils.get_row_by_multiple_data('project', 
                                                        'extensions', 
                                                        ('stage', 'software_id'), 
                                                        (stage, software_id))
    if export_row is None or len(export_row) < 1:
        logger.error("Extension row not found")
        return
    return export_row[0]

def set_default_extension(extension_id, extension):
    if not db_utils.update_data('project',
                            'extensions',
                            ('extension', extension),
                            ('id', extension_id)):
        logger.warning('Extension not modified')
        return
    logger.info('Extension modified')
    return 1

def create_settings_row(frame_rate, image_format, deadline):
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
    if not db_utils.update_data('project',
                            'settings',
                            ('frame_rate', frame_rate),
                            ('id', 1)):
        logger.warning('Project frame rate not modified')
        return
    logger.info('Project frame rate modified')
    return 1

def get_frame_rate():
    frame_rate_list = db_utils.get_row_by_column_data('project',
                                                        'settings',
                                                        ('id', 1),
                                                        'frame_rate')
    if frame_rate_list is None or len(frame_rate_list) < 1:
        logger.error("Project settings not found")
        return
    return json.loads(frame_rate_list[0])

def set_image_format(image_format):
    if not db_utils.update_data('project',
                            'settings',
                            ('image_format', json.dumps(image_format)),
                            ('id', 1)):
        logger.warning('Project format not modified')
        return
    logger.info('Project format modified')
    return 1

def get_image_format():
    image_format_list = db_utils.get_row_by_column_data('project',
                                                        'settings',
                                                        ('id', 1),
                                                        'image_format')
    if image_format_list is None or len(image_format_list) < 1:
        logger.error("Project settings not found")
        return
    return json.loads(image_format_list[0])

def set_deadline(time_float):
    if not db_utils.update_data('project',
                            'settings',
                            ('deadline', time_float),
                            ('id', 1)):
        logger.warning('Project deadline not modified')
        return
    logger.info('Project deadline modified')
    return 1

def get_deadline():
    deadline_list = db_utils.get_row_by_column_data('project',
                                                        'settings',
                                                        ('id', 1),
                                                        'deadline')
    if deadline_list is None or len(deadline_list) < 1:
        logger.error("Project settings not found")
        return
    return deadline_list[0]

def get_users_ids_list():
    users_ids_list = db_utils.get_row_by_column_data('project',
                                                        'settings',
                                                        ('id', 1),
                                                        'users_ids')
    if users_ids_list is None :
        return []
    return json.loads(users_ids_list[0])

def add_user(user_id):
    users_ids_list = get_users_ids_list()
    if user_id in users_ids_list:
        return
    users_ids_list.append(user_id)
    return update_users_list(users_ids_list)

def remove_user(user_id):
    users_ids_list = get_users_ids_list()
    if user_id not in users_ids_list:
        return
    users_ids_list.remove(user_id)
    return update_users_list(users_ids_list)

def update_users_list(users_ids_list):
    if not db_utils.update_data('project',
                            'settings',
                            ('users_ids', json.dumps(users_ids_list)),
                            ('id', 1)):
        logger.warning('Project users list not updated')
        return
    logger.info('Project users list updated')
    return 1

def get_shared_files_folder():
    return path_utils.join(environment.get_project_path(), project_vars._shared_files_folder_)

def get_scripts_folder():
    return path_utils.join(environment.get_project_path(), project_vars._scripts_folder_)

def get_hooks_folder():
    return path_utils.join(environment.get_project_path(), project_vars._hooks_folder_)

def get_plugins_folder():
    return path_utils.join(environment.get_project_path(), project_vars._plugins_folder_)

def get_temp_scripts_folder():
    shared_files_folder = path_utils.join(environment.get_project_path(), project_vars._scripts_folder_, 'temp')
    path_utils.makedirs(shared_files_folder)
    return shared_files_folder

def add_event(event_type, title, message, data, additional_message=None, image_path=None):
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
    events_rows = db_utils.get_row_by_column_part_data('project',
                                                    'events',
                                                    (column_to_search, data_to_search),
                                                    column)
    return events_rows

def modify_event_message(event_id, message):
    if not db_utils.update_data('project',
                                'events',
                                ('message', message),
                                ('id', event_id)):
        logger.warning('Event message not modified')
        return
    logger.info('Event message modified')
    return 1

def get_event_data(event_id, column='*'):
    events_rows = db_utils.get_row_by_column_data('project',
                                                        'events',
                                                        ('id', event_id),
                                                        column)
    if events_rows is None or len(events_rows) < 1:
        logger.error("Event not found")
        return
    return events_rows[0]

def get_all_events(column='*'):
    events_rows = db_utils.get_rows('project',
                                        'events',
                                        column)
    return events_rows

def add_shelf_separator():
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
    if not db_utils.update_data('project',
                            'shelf_scripts',
                            ('position', position),
                            ('id', script_id)):
        logger.warning('Tool position not modified')
        return
    logger.info('Tool position modified')
    return 1

def delete_shelf_script(script_id):
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
    shelf_scripts_rows = db_utils.get_row_by_column_data('project',
                                                        'shelf_scripts',
                                                        ('id', script_id),
                                                        column)
    if shelf_scripts_rows is None or len(shelf_scripts_rows) < 1:
        logger.error("Shelf script not found")
        return
    return shelf_scripts_rows[0]

def get_all_shelf_scripts(column='*'):
    shelf_scripts_rows = db_utils.get_rows('project',
                                            'shelf_scripts',
                                            column)
    return shelf_scripts_rows

def create_group(name, color):
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
    groups_rows = db_utils.get_rows('project', 'groups', column=column)
    return groups_rows

def get_group_data(group_id, column='*'):
    groups_rows = db_utils.get_row_by_column_data('project', 
                                                    'groups', 
                                                    ('id', group_id), 
                                                    column)
    if groups_rows is None or len(groups_rows) < 1:
        logger.error("Group not found")
        return
    return groups_rows[0]

def get_group_by_name(name, column='*'):
    groups_rows = db_utils.get_row_by_column_data('project', 
                                                    'groups', 
                                                    ('name', name), 
                                                    column)
    if groups_rows is None or len(groups_rows) < 1:
        logger.error("Group not found")
        return
    return groups_rows[0]

def modify_group_color(group_id, color):
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
    for grouped_reference_id in get_grouped_references(group_id, 'id'):
        remove_grouped_reference(grouped_reference_id)
    for referenced_group_id in get_referenced_groups_by_group_id(group_id, 'id'):
        remove_referenced_group(referenced_group_id)
    if not db_utils.delete_row('project', 'groups', group_id):
        logger.warning(f"Group NOT removed from project")
        return
    logger.info(f"Group removed from project")
    return 1

def create_referenced_group(work_env_id, group_id, namespace, count=None):
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
                                'work_env_id'),
                            (time.time(),
                                environment.get_user(),
                                namespace,
                                count,
                                group_id,
                                group_name,
                                work_env_id))
    if not referenced_group_id:
        return
    logger.info(f"Referenced group created")
    return referenced_group_id

def remove_referenced_group(referenced_group_id):
    if not db_utils.delete_row('project', 'referenced_groups_data', referenced_group_id):
        logger.warning(f"Referenced group NOT removed from project")
        return
    logger.info(f"Referenced group removed from project")
    return 1

def remove_video(video_id):
    if not db_utils.delete_row('project', 'videos', video_id):
        logger.info(f"Video NOT removed from project")
        return
    logger.info(f"Video removed from project")
    return 1

def get_referenced_groups(work_env_id, column='*'):
    referenced_groups_rows = db_utils.get_row_by_column_data('project',
                                                        'referenced_groups_data',
                                                        ('work_env_id', work_env_id),
                                                        column)
    return referenced_groups_rows

def get_videos(variant_id, column='*'):
    videos_rows = db_utils.get_row_by_column_data('project',
                                                        'videos',
                                                        ('variant_id', variant_id),
                                                        column)
    return videos_rows

def get_referenced_groups_by_group_id(group_id, column='*'):
    referenced_groups_rows = db_utils.get_row_by_column_data('project',
                                                        'referenced_groups_data',
                                                        ('group_id', group_id),
                                                        column)
    return referenced_groups_rows

def get_referenced_group_data(referenced_group_id, column='*'):
    referenced_groups_rows = db_utils.get_row_by_column_data('project', 
                                                    'referenced_groups_data', 
                                                    ('id', referenced_group_id), 
                                                    column)
    if referenced_groups_rows is None or len(referenced_groups_rows) < 1:
        logger.error("Referenced group not found")
        return
    return referenced_groups_rows[0]

def get_referenced_group_by_namespace(work_env_id, namespace, column='*'):
    referenced_groups_rows = db_utils.get_row_by_multiple_data('project', 
                                                    'referenced_groups_data', 
                                                    ('work_env_id', 'namespace'), 
                                                    (work_env_id, namespace), 
                                                    column)
    if referenced_groups_rows is None or len(referenced_groups_rows) < 1:
        logger.error("Referenced group not found")
        return
    return referenced_groups_rows[0]

def create_grouped_reference(group_id, export_version_id, namespace, count=None):
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
                                'auto_update'),
                            (time.time(),
                                environment.get_user(),
                                namespace,
                                count,
                                stage_name,
                                group_id,
                                export_id,
                                export_version_id,
                                0))
    if not reference_id:
        return
    logger.info(f"Grouped reference created")
    return reference_id

def remove_grouped_reference(grouped_reference_id):
    if not db_utils.delete_row('project', 'grouped_references_data', grouped_reference_id):
        logger.warning("Grouped reference NOT deleted")
        return
    logger.info("Grouped reference deleted")
    return 1

def get_grouped_references(group_id, column='*'):
    grouped_references_rows = db_utils.get_row_by_column_data('project',
                                                        'grouped_references_data',
                                                        ('group_id', group_id),
                                                        column)
    return grouped_references_rows

def get_grouped_reference_data(grouped_reference_id, column='*'):
    grouped_references_rows = db_utils.get_row_by_column_data('project', 
                                                    'grouped_references_data', 
                                                    ('id', grouped_reference_id), 
                                                    column)
    if grouped_references_rows is None or len(grouped_references_rows) < 1:
        logger.error("Grouped reference not found")
        return
    return grouped_references_rows[0]

def get_grouped_reference_by_namespace(group_id, namespace, column='*'):
    grouped_references_rows = db_utils.get_row_by_multiple_data('project', 
                                                    'grouped_references_data', 
                                                    ('group_id', 'namespace'), 
                                                    (group_id, namespace), 
                                                    column)
    if grouped_references_rows is None or len(grouped_references_rows) < 1:
        logger.error("Grouped reference not found")
        return
    return grouped_references_rows[0]

def update_grouped_reference_data(grouped_reference_id, data_tuple):
    if not db_utils.update_data('project',
                        'grouped_references_data',
                        data_tuple,
                        ('id', grouped_reference_id)):
        logger.warning('Grouped reference modified')
        return
    logger.info('Grouped reference modified')
    return 1

def update_grouped_reference(grouped_reference_id, export_version_id):
    if not db_utils.update_data('project',
                        'grouped_references_data',
                        ('export_version_id', export_version_id),
                        ('id', grouped_reference_id)):
        logger.info('Grouped reference not modified')
        return
    logger.info('Grouped reference modified')
    return 1

def modify_grouped_reference_export(grouped_reference_id, export_id):
    export_version_id = get_default_export_version(export_id, 'id')
    if not export_version_id:
        return
    update_grouped_reference_data(grouped_reference_id, ('export_id', export_id))
    update_grouped_reference_data(grouped_reference_id, ('export_version_id', export_version_id))
    return 1  

def modify_grouped_reference_auto_update(grouped_reference_id, auto_update):
    if auto_update:
        auto_update = 1
    update_grouped_reference_data(grouped_reference_id, ('auto_update', auto_update))
    if not auto_update:
        return
    export_id = get_grouped_reference_data(grouped_reference_id, 'export_id')
    export_version_id = get_default_export_version(export_id, 'id')
    if not export_version_id:
        return
    update_grouped_reference_data(grouped_reference_id, ('export_version_id', export_version_id))
    return 1

def search_group(name, column='*'):
    groups_rows = db_utils.get_row_by_column_part_data('project',
                                                        'groups',
                                                        ('name', name),
                                                        column)
    return groups_rows

def get_all_tag_groups(column='*'):
    tag_groups_rows = db_utils.get_rows('project',
                                            'tag_groups',
                                            column)
    return tag_groups_rows

def get_tag_group_by_name(name, column='*'):
    tag_groups_rows = db_utils.get_row_by_column_part_data('project',
                                                        'tag_groups',
                                                        ('name', name),
                                                        column)
    if tag_groups_rows is None or len(tag_groups_rows) < 1:
        logger.error("Tag group not found")
        return
    return tag_groups_rows[0]

def get_tag_group_data(tag_group_id, column='*'):
    tag_groups_rows = db_utils.get_row_by_column_part_data('project',
                                                        'tag_groups',
                                                        ('id', tag_group_id),
                                                        column)
    if tag_groups_rows is None or len(tag_groups_rows) < 1:
        logger.error("Tag group not found")
        return
    return tag_groups_rows[0]

def create_tag_group(group_name):
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
    tag_group_row = get_tag_group_by_name(group_name)
    if not tag_group_row:
        return
    if not db_utils.delete_row('project', 'tag_groups', tag_group_row['id']):
        logger.warning(f"Tag group {group_name} NOT removed from project")
        return
    logger.info(f"{group_name} deleted")

def suscribe_to_tag_group(group_name):
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
        logger.info(f"{environment.get_user()} suscribed to {group_name} tag group.")

def unsuscribe_from_tag_group(group_name):
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
        logger.info(f"{environment.get_user()} unsuscribed from {group_name} tag group.")

def create_assets_group(asset_group_name, category_id):
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
    assets_groups_rows = db_utils.get_row_by_column_data('project',
                                                        'assets_groups',
                                                        ('category_id', category_id),
                                                        column)
    return assets_groups_rows

def get_all_assets_groups(column='*'):
    assets_groups_rows = db_utils.get_rows('project',
                                            'assets_groups',
                                            column)
    return assets_groups_rows

def get_assets_group_data(assets_group_id, column='*'):
    assets_groups_rows = db_utils.get_row_by_column_data('project',
                                                        'assets_groups',
                                                        ('id', assets_group_id),
                                                        column)
    if assets_groups_rows is None or len(assets_groups_rows) < 1:
        logger.error("Assets group not found")
        return
    return assets_groups_rows[0] 

def add_asset_to_assets_group(asset_id, assets_group_id):
    asset_row = get_asset_data(asset_id)
    assets_group_row = get_assets_group_data(assets_group_id)
    if not asset_row:
        return
    if not assets_group_row:
        return
    if asset_row['category_id'] != assets_group_row['category_id']:
        logger.warning(f"Asset and group doesn't have the same category, can't move asset")
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
    assets_rows = db_utils.get_row_by_column_data('project',
                                                    'assets',
                                                    ('assets_group_id', assets_group_id),
                                                    column)
    return assets_rows

def remove_asset_from_assets_group(asset_id):
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
    child_assets_ids = get_assets_group_childs(assets_group_id, 'id')
    for asset_id in child_assets_ids:
        remove_asset_from_assets_group(asset_id)
    if not db_utils.delete_row('project', 'assets_groups', assets_group_id):
        logger.warning(f"Assets group NOT removed from project")
        return
    logger.info(f"Assets group removed from project")
    return 1

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

    if not do_creation:
        return
    project_id = repository.create_project(project_name, project_path, project_password, project_image)
    if not project_id:
        return
    if not init_project(project_path, project_name):
        repository.remove_project_row(project_id)
        return
    logger.info(f"{project_name} created")
    return 1

def init_project(project_path, project_name):
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
    return project_name

def create_domains_table(database):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS domains_data (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL UNIQUE,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        string text NOT NULL
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Categories table created")
    return 1

def create_categories_table(database):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS categories (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS assets (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS stages (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS variants (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS asset_tracking_events (
                                        id serial PRIMARY KEY,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS work_envs (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS references_data (
                                        id serial PRIMARY KEY,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        namespace text NOT NULL,
                                        count text,
                                        stage text NOT NULL,
                                        work_env_id integer NOT NULL,
                                        export_id integer NOT NULL,
                                        export_version_id integer NOT NULL,
                                        auto_update integer NOT NULL,
                                        FOREIGN KEY (work_env_id) REFERENCES work_envs (id),
                                        FOREIGN KEY (export_id) REFERENCES exports (id),
                                        FOREIGN KEY (export_version_id) REFERENCES export_versions (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("References table created")
    return 1

def create_referenced_groups_table(database):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS referenced_groups_data (
                                        id serial PRIMARY KEY,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        namespace text NOT NULL,
                                        count text,
                                        group_id integer NOT NULL,
                                        group_name text NOT NULL,
                                        work_env_id integer NOT NULL,
                                        FOREIGN KEY (group_id) REFERENCES groups (id),
                                        FOREIGN KEY (work_env_id) REFERENCES work_envs (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Referenced groups table created")
    return 1

def create_grouped_references_table(database):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS grouped_references_data (
                                        id serial PRIMARY KEY,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        namespace text NOT NULL,
                                        count text,
                                        stage text NOT NULL,
                                        group_id integer NOT NULL,
                                        export_id integer NOT NULL,
                                        export_version_id integer NOT NULL,
                                        auto_update integer NOT NULL,
                                        FOREIGN KEY (group_id) REFERENCES groups (id),
                                        FOREIGN KEY (export_id) REFERENCES exports (id),
                                        FOREIGN KEY (export_version_id) REFERENCES export_versions (id)
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Grouped references table created")
    return 1

def create_groups_table(database):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS groups (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
                                        creation_user text NOT NULL,
                                        color text
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Groups table created")
    return 1

def create_exports_table(database):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS exports (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS versions (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS videos (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS export_versions (
                                        id serial PRIMARY KEY,
                                        name text NOT NULL,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS settings (
                                        id serial PRIMARY KEY,
                                        frame_rate text NOT NULL,
                                        image_format text NOT NULL,
                                        deadline real NOT NULL,
                                        users_ids text NOT NULL
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Settings table created")
    return 1

def create_extensions_table(database):
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS events (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS progress_events (
                                        id serial PRIMARY KEY,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS tag_groups (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        creation_time real NOT NULL,
                                        name text NOT NULL,
                                        user_ids text NOT NULL
                                    );"""
    if not db_utils.create_table(database, sql_cmd):
        return
    logger.info("Tag groups table created")
    return 1

def create_assets_groups_table(database):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS assets_groups (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        creation_time real NOT NULL,
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
    sql_cmd = """ CREATE TABLE IF NOT EXISTS shelf_scripts (
                                        id serial PRIMARY KEY,
                                        creation_user text NOT NULL,
                                        creation_time real NOT NULL,
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
    