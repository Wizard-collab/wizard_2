from wizard.core import assets
from wizard.core import project
from wizard.vars import assets_vars

from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

import time
start_time = time.time()

percent_step = 100.0/10.0
percent= 0.0

for a in range(0,11):
	begin_time = time.time()
	asset_name = str(time.time())
	print('wizard_task_name:creating '+asset_name+'...')
	asset_id = assets.create_asset(asset_name, 2)
	for stage in assets_vars._assets_stages_list_:
		stage_id = assets.create_stage(stage, asset_id)
		variant_id = project.get_stage_data(stage_id, 'default_variant_id')
		assets.create_work_env(1, variant_id)
	print(time.time()-begin_time)
	print('wizard_task_percent:'+str(percent))
	percent+=percent_step
print(time.time()-start_time)
