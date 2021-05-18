from wizard.core import site
from wizard.core import user
from wizard.core import environment

from wizard.core import logging
logging = logging.get_logger(__name__)

if not environment.build_site_env(site_path=user.user().get_site_path()):
	logging.info('Please set a site path')
else:
	if not environment.build_user_env(user_name=user.user().get_user()):
		logging.info('Please connect a user')
	else:
		project_name = user.user().get_project()
		if not environment.build_project_env(project_name=project_name,
											project_path=site.site().get_project_path_by_name(project_name)):
			logging.info('Please connect to a project')