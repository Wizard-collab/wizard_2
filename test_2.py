from wizard.core import project
import random

for variant_id in project.get_all_variants('id'):
	estimated_time = 200
	work_time = random.randint(1,200)
	project.set_variant_data(variant_id, 'work_time', work_time)
	project.set_variant_data(variant_id, 'estimated_time', estimated_time)