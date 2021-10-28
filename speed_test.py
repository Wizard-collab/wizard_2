from wizard.core import assets
for a in range(0,100):
	print(str(a).zfill(4))
	asset_id = assets.create_asset(str(a).zfill(4), 1)
	stage_id = assets.create_stage('modeling', asset_id)
	stage_id = assets.create_stage('rigging', asset_id)
	stage_id = assets.create_stage('grooming', asset_id)
	stage_id = assets.create_stage('texturing', asset_id)
	stage_id = assets.create_stage('shading', asset_id)
