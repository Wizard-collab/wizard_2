# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# PyWizard is the wizard application without GUI
# Use PyWizard to execute batch commands like
# large amount of instances creation or archiving

# Python modules
import sys
import os
import traceback

# Wizard modules
from wizard.core import user
from wizard.core import project
from wizard.core import site
from wizard.core import create_project
from wizard.core import communicate
from wizard.core import environment
from wizard.core import db_core
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

while not user.user().get_psql_dns():
	psql_host = input("PostgreSQL host : ")
	psql_port = input("PostgreSQL port : ")
	psql_user = input("PostgreSQL user : ")
	psql_password = input("PostgreSQL password : ")
	user.user().set_psql_dns(
							psql_host,
							psql_port,
							psql_user,
							psql_password
							)

db_server = db_core.db_server()
db_server.start()

if not site.is_site_database():
	while not site.is_site_database():
		init_site = input("Site database doesn't exists, init database (y/n) ? : ")
		if init_site == 'y':
			admin_password = input('Administator password : ')
			admin_email = input('Administator email : ')
			site.create_site_database()
			db_server.site='site'
			site.init_site(admin_password, admin_email)

db_server.site='site'
site.add_ip_user()

while not user.get_user():
	do_create_user = input('Create user (y/n) ? : ')
	if do_create_user == 'y':
		user_name = input('User name : ')
		password = input('Password : ')
		email = input('Email : ')
		profile_picture = input('Profile picture ( without any "\\" ) ( Optional ) : ')
		administrator_pass = input('Administrator pass ( Optional ) : ')
		site.create_user(user_name,
								password,
								email,
								administrator_pass,
								profile_picture)
	else:
		user_name = input('User name : ')
		password = input('Password : ')
		user.log_user(user_name, password)

while not user.get_project():
	do_create_project = input('Create project (y/n) ? : ')
	if do_create_project == 'y':
		project_name = input('Project name : ')
		project_path = input('Project path : ')
		project_password = input('Project password : ')
		if project.create_project(project_name, project_path, project_password):
			db_server.project_name = project_name
			create_project.create_project(project_name, project_path, project_password)

	else:
		project_name = input('Project name : ')
		project_password = input('Project password : ')
		user.log_project(project_name, project_password)

db_server.project_name = environment.get_project_name()
softwares_server = communicate.communicate_server()
softwares_server.start()