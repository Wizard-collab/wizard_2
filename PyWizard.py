# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# PyWizard is the wizard application without GUI
# Use PyWizard to execute batch commands like
# large amount of instances creation or archiving

# Python modules
import sys

# Wizard modules
from wizard.core import user
from wizard.core import logging
logging = logging.get_logger(__name__)

while not user.user().get_site_path():
	site_path = input('Please set a site path : ')
	user.user().set_site_path(site_path)

while not user.get_user():
	user_name = input('User name : ')
	password = input('Password : ')
	user.log_user(user_name, password)

while not user.get_project():
	project_name = input('Project name : ')
	project_password = input('Project password : ')
	user.log_project(project_name, project_password)

def main():
	try:
		file = sys.argv[1]
		exec(open(file).read())
	except IndexError:
		import code
		console = code.InteractiveConsole()
		console.interact(banner=None, exitmsg=None)

if __name__ == '__main__':
	main()