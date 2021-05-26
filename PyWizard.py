# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# PyWizard is the wizard application without GUI
# Use PyWizard to execute batch commands like
# large amount of instances creation or archiving

# Python modules
import sys
import traceback

# Wizard modules
from wizard.core import user
from wizard.core import site
from wizard.core import create_project
from wizard.core import communicate
from wizard.core import logging
logging = logging.get_logger(__name__)

while not user.user().get_site_path():
	site_path = input('Please set a site path : ')
	user.user().set_site_path(site_path)

while not user.get_user():
	do_create_user = input('Create user (y/n) ? : ')
	if do_create_user == 'y':
		user_name = input('User name : ')
		password = input('Password : ')
		email = input('Email : ')
		administrator_pass = input('Administrator pass ( Optional ) : ')
		site.site().create_user(user_name,
								password,
								email,
								administrator_pass)
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