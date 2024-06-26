import wapi
import time
import statistics
times = []
start_time = time.perf_counter()
for a in range(0,500):
	asset_start_time = time.perf_counter()
	asset_path=wapi.assets.create_asset("sequences/INTRO", f"benchmark_{str(a)}")
	for stage in ['layout', 'animation', 'cfx', 'fx', 'camera', 'lighting', 'compositing']:
		wapi.assets.create_stage(asset_path, stage)
	times.append(time.perf_counter()-asset_start_time)
print(time.perf_counter()-start_time)
print(statistics.mean(times))

wapi.team.refresh_ui()

# 500 assets & 2500 stages
# 16h47 > 17h03 ( 16min ) 

# 1432s ( 2.8 / asset + stages )
# > 23min


# 21/12/2022
#	500 assets ( 3500 stage ) > 30.96s avec singleton


# 21/12/2022 500 assets / 3500 stages
# 1788.74s
# 30.96s
# Acceleration de 6000 %