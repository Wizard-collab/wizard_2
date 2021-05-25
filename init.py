from wizard.core import site
from wizard.core import user
from wizard.core import environment
from wizard.core import project
from wizard.core import assets
from wizard.core import communicate
import time

from wizard.core import logging
logging = logging.get_logger(__name__)

if not environment.build_site_env(site_path=user.user().get_site_path()):
	logging.info('Please set a site path')
else:
	if not environment.build_user_env(user_name=user.user().get_user()):
		logging.info('Please connect a user')
	else:
		project_name = user.user().get_project()
		if project_name:
			if not environment.build_project_env(project_name=project_name,
												project_path=site.site().get_project_path_by_name(project_name)):
				logging.info('Please connect to a project')
			else:

				pass

				#show tree
				
				for domain_tuple in project.project().get_domains():
					print(f"{domain_tuple['id']} - {domain_tuple['name']}")
					for category_tuple in project.project().get_domain_childs(domain_tuple['id']):
						print(f"  {category_tuple['id']} - {category_tuple['name']}")
						for asset_tuple in project.project().get_category_childs(category_tuple['id']):
							print(f"    {asset_tuple['id']} - {asset_tuple['name']}")
							for stage_tuple in project.project().get_asset_childs(asset_tuple['id']):
								print(f"      {stage_tuple['id']} - {stage_tuple['name']}")
								for variant_tuple in project.project().get_stage_childs(stage_tuple['id']):
									print(f"        {variant_tuple['id']} - {variant_tuple['name']}")
									for work_env_tuple in project.project().get_variant_work_envs_childs(variant_tuple['id']):
										print(f"          {work_env_tuple['id']} - {work_env_tuple['name']}")
										for version_tuple in project.project().get_work_versions(work_env_tuple['id']):
											print(f"            {version_tuple['id']} - {version_tuple['name']}")

				server = communicate.communicate_server()
				server.start()
				
		else:
			logging.info('Please connect to a project')
			
