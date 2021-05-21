from wizard.core import site
from wizard.core import user
from wizard.core import environment
from wizard.core import project
from wizard.core import assets
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
				
				start_time = time.time()
				for domain_tuple in project.project().get_domains():
					print(f'{domain_tuple[0]} - {domain_tuple[1]}')
					for category_tuple in project.project().get_domain_childs(domain_tuple[0]):
						print(f'  {category_tuple[0]} - {category_tuple[1]}')
						for asset_tuple in project.project().get_category_childs(category_tuple[0]):
							print(f'    {asset_tuple[0]} - {asset_tuple[1]}')
							for stage_tuple in project.project().get_asset_childs(asset_tuple[0]):
								print(f'      {stage_tuple[0]} - {stage_tuple[1]}')
								for variant_tuple in project.project().get_stage_childs(stage_tuple[0]):
									print(f'        {variant_tuple[0]} - {variant_tuple[1]}')
									for work_env_tuple in project.project().get_variant_work_envs_childs(variant_tuple[0]):
										print(f'          {work_env_tuple[0]} - {work_env_tuple[1]}')
										for version_tuple in project.project().get_work_versions(work_env_tuple[0]):
											print(f'            {version_tuple[0]} - {version_tuple[1]}')

				print(str(time.time()-start_time))

				'''
				for a in range(0,100):
					asset_id = assets.create_asset(str(time.time()), 1)
					stage_id = assets.create_stage('modeling', asset_id)
					variant_id = project.project().get_stage_childs(stage_id)[0][0]
					assets.create_work_env('maya', variant_id)
					assets.create_work_env('guerilla', variant_id)
					assets.create_work_env('substance', variant_id)
					assets.create_work_env('mari', variant_id)
					stage_id = assets.create_stage('rigging', asset_id)
					variant_id = project.project().get_stage_childs(stage_id)[0][0]
					assets.create_work_env('maya', variant_id)
					assets.create_work_env('guerilla', variant_id)
					assets.create_work_env('substance', variant_id)
					assets.create_work_env('mari', variant_id)
					stage_id = assets.create_stage('texturing', asset_id)
					variant_id = project.project().get_stage_childs(stage_id)[0][0]
					assets.create_work_env('maya', variant_id)
					assets.create_work_env('guerilla', variant_id)
					assets.create_work_env('substance', variant_id)
					assets.create_work_env('mari', variant_id)
				'''


				

		else:
			logging.info('Please connect to a project')
			
