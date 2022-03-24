whats_new_dic = dict()
whats_new_dic['Project preferences'] = dict()
whats_new_dic['Project preferences']['type'] = 'new'
whats_new_dic['Project preferences']['comment'] = 'You can now modify your project settings'
whats_new_dic['Batch exports'] = dict()
whats_new_dic['Batch exports']['type'] = 'new'
whats_new_dic['Batch exports']['comment'] = 'You can now export data from the work versions tab'
whats_new_dic['References groups'] = dict()
whats_new_dic['References groups']['type'] = 'new'
whats_new_dic['References groups']['comment'] = 'Create references in custom groups and reference groups in scenes'
whats_new_dic['Hooks'] = dict()
whats_new_dic['Hooks']['type'] = 'new'
whats_new_dic['Hooks']['comment'] = 'Use script hooks to add features to your exports and imports'

import yaml
with open('ressources/whatsnew.yaml', 'w') as f:
	yaml.dump(whats_new_dic, f)