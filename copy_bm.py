import time
from wizard.core import threaded_copy
import os
import shutil

destination_1 = "Y:/E5/dev/copy_BM"
files_list = []
for file in os.listdir("D:/SCRIPT/LOCAL/benchmark"):
	files_list.append(os.path.join("D:/SCRIPT/LOCAL/benchmark", file))

# Threaded
start_time = time.time()
threaded_copy.threaded_copy(files_list, destination_1).copy()
print(f"Threaded copy time : {time.time()-start_time}")

# Straight
start_time = time.time()
for file in files_list:
	dest_file = os.path.join(destination_1, os.path.basename(file))
	shutil.copyfile(file, dest_file)
print(f"Normal copy time : {time.time()-start_time}")
