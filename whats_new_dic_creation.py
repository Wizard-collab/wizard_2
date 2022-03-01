whats_new_dic = dict()
whats_new_dic['Substance painter custom export'] = dict()
whats_new_dic['Substance painter custom export']['type'] = 'debug'
whats_new_dic['Substance painter custom export']['comment'] = 'You can now export maps from substance painter with custom export preset'
whats_new_dic['All wizard white are now 85% white'] = dict()
whats_new_dic['All wizard white are now 85% white']['type'] = 'modification'
whats_new_dic['All wizard white are now 85% white']['comment'] = None
whats_new_dic['Stage creation item hidden when all stage are existing'] = dict()
whats_new_dic['Stage creation item hidden when all stage are existing']['type'] = 'debug'
whats_new_dic['Stage creation item hidden when all stage are existing']['comment'] = None
whats_new_dic['All blue and red buttons are now default'] = dict()
whats_new_dic['All blue and red buttons are now default']['type'] = 'debug'
whats_new_dic['All blue and red buttons are now default']['comment'] = 'You can now press enter on dialogs, it will automatically press the blue or red button'
whats_new_dic['This whatsnew widget'] = dict()
whats_new_dic['This whatsnew widget']['type'] = 'new'
whats_new_dic['This whatsnew widget']['comment'] = 'See the wizard version modification here'

import yaml
with open('ressources/whatsnew.yaml', 'w') as f:
	yaml.dump(whats_new_dic, f)