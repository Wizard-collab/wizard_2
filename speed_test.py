from wizard.core import assets
for a in range(0,20):
	print(str(a).zfill(4))
	asset_id = assets.create_asset(str(a).zfill(4), 5)
	stage_id = assets.create_stage('layout', asset_id)
	stage_id = assets.create_stage('animation', asset_id)
	stage_id = assets.create_stage('cfx', asset_id)
	stage_id = assets.create_stage('fx', asset_id)
	stage_id = assets.create_stage('camera', asset_id)
	stage_id = assets.create_stage('lighting', asset_id)
	stage_id = assets.create_stage('compositing', asset_id)
