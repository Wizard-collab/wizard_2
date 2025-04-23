# coding: utf-8
# Wizard hook

import logging
logger = logging.getLogger(__name__)


def after_export(export_version_string,
                 export_dir,
                 stage_name,
                 gui):
    ''' This function is triggered
            after an export.

            The "export_version_string" argument is the exported asset as
            string

            The "export_dir" argument is the directory where the 
            asset was exported

            The "stage_name" argument is the name of the
            exported stage

            The "gui" argument is true if wizard is openned 
            with the user interface, if it is PyWizard or wizard_CMD,
            gui will be false.'''
    pass


def after_category_creation(string_category,
                            category_name,
                            gui):
    ''' This function is triggered
            after a stage creation.

            The "string_category" argument is the created category as
            string

            The "category_name" argument is the name of the
            created category

            The "gui" argument is true if wizard is openned 
            with the user interface, if it is PyWizard or wizard_CMD,
            gui will be false.'''
    pass


def after_asset_creation(string_asset,
                         asset_name,
                         gui):
    ''' This function is triggered
            after a stage creation.

            The "string_asset" argument is the created asset as
            string

            The "asset_name" argument is the name of the
            created asset

            The "gui" argument is true if wizard is openned 
            with the user interface, if it is PyWizard or wizard_CMD,
            gui will be false.'''
    pass


def after_stage_creation(string_stage,
                         stage_name,
                         gui):
    ''' This function is triggered
            after a stage creation.

            The "stage_string" argument is the created stage as
            string

            The "stage_name" argument is the name of the
            created stage

            The "gui" argument is true if wizard is openned 
            with the user interface, if it is PyWizard or wizard_CMD,
            gui will be false.'''
    pass


def after_variant_creation(string_variant,
                           variant_name,
                           gui):
    ''' This function is triggered
            after a stage creation.

            The "string_variant" argument is the created variant as
            string

            The "variant_name" argument is the name of the
            created variant

            The "gui" argument is true if wizard is openned 
            with the user interface, if it is PyWizard or wizard_CMD,
            gui will be false.'''
    pass


def after_work_environment_creation(string_work_env,
                                    software_name,
                                    gui):
    ''' This function is triggered
            after a stage creation.

            The "string_work_env" argument is the created work environment as
            string

            The "software_name" argument is the name of the
            created work environment

            The "gui" argument is true if wizard is openned 
            with the user interface, if it is PyWizard or wizard_CMD,
            gui will be false.'''
    pass


def after_work_version_creation(string_work_version,
                                version_name,
                                file_name,
                                gui):
    ''' This function is triggered
            after a stage creation.

            The "string_work_version" argument is the created work version as
            string

            The "version_name" argument is the name of the
            created version

            The "file_name" argument is the file associated to the work version

            The "gui" argument is true if wizard is openned 
            with the user interface, if it is PyWizard or wizard_CMD,
            gui will be false.'''
    pass


def after_reference_creation(string_work_environment,
                             string_referenced_export_version,
                             stage_name,
                             referenced_stage_name,
                             gui):
    ''' This function is triggered
            after a stage creation.

            The "string_work_environment" argument is the destination work environment
            as string

            The "string_referenced_export_version" argument is the referenced export version
            as string

            The "stage_name" argument is the name of the destination stage

            The "referenced_stage_name" argument is the name of the referenced stage

            The "gui" argument is true if wizard is openned 
            with the user interface, if it is PyWizard or wizard_CMD,
            gui will be false.'''
    pass
