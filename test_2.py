import time
import random

percent_step = 100.0/100.0
percent = 0.0

print("wizard_task_name:Exporting asset")

for a in range(0,101):
	print(a)
	print("wizard_task_percent:"+str(percent))
	percent+=percent_step
	time.sleep(0.05)
	#print(random.randint(0,10000))
