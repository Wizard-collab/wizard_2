from wizard.core import project
import statistics





total = []

category_rows = project.get_all_categories()
asset_rows = project.get_all_assets()
stage_rows = project.get_all_stages()
variant_rows = project.get_all_variants()

categories_ids_percents = dict()
assets_ids_percents = dict()
stage_ids_percents = dict()

stages_percent = dict()
stages_percent['modeling'] = []
stages_percent['rigging'] = []
stages_percent['grooming'] = []
stages_percent['texturing'] = []
stages_percent['shading'] = []
stages_percent['layout'] = []
stages_percent['animation'] = []
stages_percent['cfx'] = []
stages_percent['fx'] = []
stages_percent['camera'] = []
stages_percent['lighting'] = []
stages_percent['compositing'] = []

for category_row in category_rows:
    categories_ids_percents[category_row['id']] = dict()
    categories_ids_percents[category_row['id']]['percents_list'] = []
    categories_ids_percents[category_row['id']]['stages_percent'] = dict()
    categories_ids_percents[category_row['id']]['row'] = category_row

for asset_row in asset_rows:
    assets_ids_percents[asset_row['id']] = dict()
    assets_ids_percents[asset_row['id']]['percents_list'] = []
    assets_ids_percents[asset_row['id']]['row'] = asset_row

for stage_row in stage_rows:
    stage_ids_percents[stage_row['id']] = dict()
    stage_ids_percents[stage_row['id']]['percents_list'] = []
    stage_ids_percents[stage_row['id']]['row'] = stage_row


for variant_row in variant_rows:
    if variant_row['estimated_time'] is not None:
        percent = (float(variant_row['work_time'])/float(variant_row['estimated_time']))*100
        if percent > 100:
            percent = 100
    else:
        percent = 0
    if variant_row['state'] == 'done':
        percent = 100
    
    stage_id = variant_row['stage_id']
    stage_ids_percents[stage_id]['percents_list'].append(percent)

    stage_name = stage_ids_percents[stage_id]['row']['name']
    stages_percent[stage_name].append(percent)

    asset_id = stage_ids_percents[stage_id]['row']['asset_id']
    #assets_ids_percents[asset_id]['percents_list'].append(percent)

    category_id = assets_ids_percents[asset_id]['row']['category_id']
    categories_ids_percents[category_id]['percents_list'].append(percent)
    if stage_name not in categories_ids_percents[category_id]['stages_percent'].keys():
        categories_ids_percents[category_id]['stages_percent'][stage_name] = []
    categories_ids_percents[category_id]['stages_percent'][stage_name].append(percent)

    total.append(percent)

print('\n')

if total != []:
    print(f"TOTAL : {str(statistics.mean(total))}")

print('\n')


for stage in stages_percent.keys():
    if stages_percent[stage] == []:
        percent = 0
    else:
        percent = str(statistics.mean(stages_percent[stage]))
    print(f"{stage} : {percent}%")

print('\n')

for category in categories_ids_percents.keys():
    if categories_ids_percents[category]['percents_list'] != []:
        percent = str(statistics.mean(categories_ids_percents[category]['percents_list']))
        print(f"{categories_ids_percents[category]['row']['name']} : {percent}%")

    for stage in categories_ids_percents[category]['stages_percent'].keys():
        if categories_ids_percents[category]['stages_percent'][stage] != []:
            percent = str(statistics.mean(categories_ids_percents[category]['stages_percent'][stage]))
            print(f"    {stage} : {percent}%")
    
    if categories_ids_percents[category]['percents_list'] != []:
        print('\n') 
