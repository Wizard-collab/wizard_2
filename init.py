from wizard.core import site
from wizard.core import user
from wizard.core import environment

from wizard.core import logging
logging = logging.get_logger(__name__)

if not environment.build_site_env(site_path=user.user().get_site_path()):
	logging.info('Please set a site path')
else:
	if environment.build_user_env(user_name=user.user().get_user()):
		logging.info('Please connect a user')
