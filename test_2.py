import time
import random

from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

percent_step = 100.0/1000.0
percent = 0.0

print("wizard_task_name:Exporting asset")

for a in range(0,1001):
	print(a)
	print("wizard_task_percent:"+str(percent))
	percent+=percent_step
	time.sleep(0.01)
	logger.warning(random.randint(0,10000))
'''
import time

import PyWizard
import speed_test
print('wizard_task_status:done')
'''
