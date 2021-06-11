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
from wizard.core import logging
logging = logging.get_logger(__name__)

while not user.user().get_site_path():
	site_path = input('Please set a site path : ')
	if not os.path.isfile(site.get_database_file(site_path)):
		init_site = input("Site database doesn't exists, init database (y/n) ? : ")
		if init_site == 'y':
			admin_password = input('Administator password : ')
			admin_email = input('Administator email : ')
			if site.init_site(site_path, admin_password, admin_email):
				user.user().set_site_path(site_path)
	else:
		user.user().set_site_path(site_path)


while not user.get_user():
	do_create_user = input('Create user (y/n) ? : ')
	if do_create_user == 'y':
		user_name = input('User name : ')
		password = input('Password : ')
		email = input('Email : ')
		profile_picture = input('Profile picture ( without any "\\" ) ( Optional ) : ')
		administrator_pass = input('Administrator pass ( Optional ) : ')
		site.site().create_user(user_name,
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
		create_project.create_project(project_name, project_path, project_password)
	else:
		project_name = input('Project name : ')
		project_password = input('Project password : ')
		user.log_project(project_name, project_password)

def stdout_tree():
	project_obj = project.project()
	domains_rows = project_obj.get_domains()
	for domain_row in domains_rows:
		print(f"{domain_row['id']}-{domain_row['name']}")
		for category_row in project_obj.get_domain_childs(domain_row['id']):
			print(f"  {category_row['id']}-{category_row['name']}")
			for asset_row in project_obj.get_category_childs(category_row['id']):
				print(f"    {asset_row['id']}-{asset_row['name']}")
				for stage_row in project_obj.get_asset_childs(asset_row['id']):
					print(f"      {stage_row['id']}-{stage_row['name']}")
					for variant_row in project_obj.get_stage_childs(stage_row['id']):
						print(f"        {variant_row['id']}-{variant_row['name']}")
						for work_env_row in project_obj.get_variant_work_envs_childs(variant_row['id']):
							print(f"          {work_env_row['id']}-{work_env_row['name']}")
							for version_row in project_obj.get_work_versions(work_env_row['id']):
								print(f"            {version_row['id']}-{version_row['name']}")



def main():
	try:
		file = sys.argv[1]
		exec(open(file).read())
	except IndexError:
		server = communicate.communicate_server()
		server.start()
		import code
		console = code.InteractiveConsole()
		console.interact(banner=None, exitmsg=None)
	except:
		logging.error(str(traceback.format_exc()))

if __name__ == '__main__':
	main()