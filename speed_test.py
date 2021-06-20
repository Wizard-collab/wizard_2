from wizard.core import assets
from wizard.core import project
from wizard.core import logging
from wizard.vars import assets_vars
logging = logging.get_logger(__name__)

import time
start_time = time.time()
for a in range(0,100):
	begin_time = time.time()
	asset_id = assets.create_asset(str(time.time()), 2)
	for stage in assets_vars._assets_stages_list_:
		stage_id = assets.create_stage(stage, asset_id)
		variant_id = project.project().get_stage_data(stage_id, 'default_variant_id')
		assets.create_work_env(1, variant_id)
	print(time.time()-begin_time)
print(time.time()-start_time)
