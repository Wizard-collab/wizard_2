import wapi
import logging

# Get a list of the current domains
domains_ids = wapi.assets.list_domains(column='id')
for domain_id in domains_ids:
  # For each domain, list the child categories, using the domain name as parent
  categories_ids = wapi.assets.list_categories(domain_id, column='id')
  for category_id in categories_ids:
    # Then list the child assets using this category id
    assets_ids = wapi.assets.list_assets(category_id, column='id')
    for asset_id in assets_ids:
      # Then list the child stages using this asset id
      stages = wapi.assets.list_stages(asset_id)
      for stage_row in stages:
        # Log each stage string and id
        logging.info(stage_row['string'])
        logging.info(stage_row['id'])
        logging.info(stage_row)