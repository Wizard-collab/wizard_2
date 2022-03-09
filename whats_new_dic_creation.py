whats_new_dic = dict()
whats_new_dic['Project preferences'] = dict()
whats_new_dic['Project preferences']['type'] = 'new'
whats_new_dic['Project preferences']['comment'] = 'You can now modify your project settings'
whats_new_dic['Batch exports'] = dict()
whats_new_dic['Batch exports']['type'] = 'new'
whats_new_dic['Batch exports']['comment'] = 'You can now export data from the work versions tab'

import yaml
with open('ressources/whatsnew.yaml', 'w') as f:
	yaml.dump(whats_new_dic, f)