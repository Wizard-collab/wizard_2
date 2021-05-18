# coding: utf-8

# Python modules
import os

# Wizard modules
from wizard.core import environment
from wizard.core import project

def create_domain(name):
	domain_id = project.project().add_domain(name)
	if domain_id:
		dir_name = os.path.join(environment.get_project_path(), name)
		if not os.path.isdir(dir_name):
			os.mkdir(dir_name)

def get_domain_path_by_id(domain_id):
	domain_name = project.project().get_domain_name_by_id(domain_id)
	domain_dir_name = os.path.join(environment.get_project_path(), domain_name)
	return domain_dir_name

def create_category(name, domain_id):
	category_id = project.project().add_category(name, domain_id)
	if category_id:
		dir_name = os.path.join(get_domain_path_by_id(domain_id), name)
		if not os.path.isdir(dir_name):
			os.mkdir(dir_name)