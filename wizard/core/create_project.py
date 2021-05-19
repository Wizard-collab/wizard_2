# coding: utf-8

# Wizard modules
from wizard.core import project
from wizard.core import assets
from wizard.core import environment
from wizard.vars import assets_vars

# Python modules
import os

def create_project(project_name, project_path, project_password):
	if project.create_project(project_name, project_path, project_password):
		for domain in assets_vars._domains_list_:
			assets.create_domain(domain)
		assets_domain_id = 1
		for category in assets_vars._assets_categories_list_:
			assets.create_category(category, assets_domain_id)