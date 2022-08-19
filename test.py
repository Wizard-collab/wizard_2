import wapi

'''
print(wapi.repository.projects())
print(wapi.repository.users())
print(wapi.repository.downgrade_user_privilege("l.brunel", 'aaa'))
print(wapi.repository.upgrade_user_privilege("l.brunel", 'aaa'))

print(wapi.user.set("l.brunel", 'aaa'))
print(wapi.user.get())
print(wapi.user.change_password('aaa', 'aaa'))
print(wapi.user.is_admin())

print(wapi.project.set('dev20', 'aaa'))
print(wapi.project.name())
print(wapi.project.path())

wapi.assets.create_sequence('SEQ_0001')
wapi.assets.create_asset("sequences/SEQ_0001", "sh_0001")
wapi.assets.create_stage("sequences/SEQ_0001/sh_0001", "animation")
wapi.assets.create_variant("sequences/SEQ_0001/sh_0001/animation", "test_variant")

wapi.assets.create_work_env("sequences/SEQ_0001/sh_0001/animation/main", 'maya')
wapi.assets.create_export("sequences/SEQ_0001/sh_0001/animation/main", "main", [])
wapi.assets.batch_export("sequences/SEQ_0001/sh_0001/animation/main/maya")
wapi.assets.batch_export_camera("sequences/SEQ_0001/sh_0001/animation/main/maya")

wapi.assets.create_group("my_group")
wapi.assets.modify_group_color("my_group", "#000000")
wapi.assets.delete_group("my_group")

'''

import logging

# Get a list of the current domains
domains = wapi.assets.list_domains('id')
for domain in domains:
  # For each domain, list the child categories, using the domain name as parent
  categories = wapi.assets.list_categories(domain, 'id')
  for category in categories:
    # For each category, build the category path, using a formatted string
    # Then list the child assets using this category path
    assets = wapi.assets.list_assets(category, 'id')
    for asset in assets:
      # For each asset, build the asset path using a formatted string
      # Then list the child stages using this asset path
      stages = wapi.assets.list_stages(asset, 'id')
      for stage in stages:
        # For each stage, build the stage path using a formatted string
        variants = wapi.assets.list_variants(stage)
        for variant in variants:
        	print(variant)