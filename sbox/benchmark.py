import wapi
for a in range(1,150):
	asset_path=wapi.assets.create_asset("sequences/INTRO", f"benchmark_{str(a)}")
	for stage in ['layout', 'animation', 'cfx', 'fx', 'camera', 'lighting', 'compositing']:
		wapi.assets.create_stage(asset_path, stage)

wapi.team.refresh_ui()

# 500 assets & 2500 stages
# 16h47 > 17h03 ( 16min ) 