# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Wizard core modules
from wizard.vars import ressources

artefacts_dic = dict()
artefacts_dic['mouse_attack_10'] = dict()
artefacts_dic['mouse_attack_10']['price'] = 50
artefacts_dic['mouse_attack_10']['name'] = 'Jiggly mouse 10s '
artefacts_dic['mouse_attack_10']['description'] = 'Randomly move the cursor of your target for 10s'
artefacts_dic['mouse_attack_10']['duration'] = 10
artefacts_dic['mouse_attack_10']['icon'] = ressources._potion_red_icon_
artefacts_dic['mouse_attack_30'] = dict()
artefacts_dic['mouse_attack_30']['price'] = 300
artefacts_dic['mouse_attack_30']['name'] = 'Jiggly mouse 30s '
artefacts_dic['mouse_attack_30']['description'] = 'Randomly move the cursor of your target for 30s'
artefacts_dic['mouse_attack_30']['duration'] = 30
artefacts_dic['mouse_attack_30']['icon'] = ressources._potion_red_icon_
artefacts_dic['mouse_attack_120'] = dict()
artefacts_dic['mouse_attack_120']['price'] = 3000
artefacts_dic['mouse_attack_120']['name'] = 'Jiggly mouse 2mins'
artefacts_dic['mouse_attack_120']['description'] = 'Randomly move the cursor of your target for 120s'
artefacts_dic['mouse_attack_120']['duration'] = 120
artefacts_dic['mouse_attack_120']['icon'] = ressources._potion_red_icon_
artefacts_dic['life_attack_10'] = dict()
artefacts_dic['life_attack_10']['price'] = 50
artefacts_dic['life_attack_10']['name'] = 'Life attack 10'
artefacts_dic['life_attack_10']['description'] = 'Remove 10% of life for your target'
artefacts_dic['life_attack_10']['force'] = 10
artefacts_dic['life_attack_10']['icon'] = ressources._sword_icon_
artefacts_dic['life_attack_33'] = dict()
artefacts_dic['life_attack_33']['price'] = 300
artefacts_dic['life_attack_33']['name'] = 'Life attack 33'
artefacts_dic['life_attack_33']['description'] = 'Remove 33% of life for your target'
artefacts_dic['life_attack_33']['force'] = 33
artefacts_dic['life_attack_33']['icon'] = ressources._sword_icon_
artefacts_dic['life_attack_100'] = dict()
artefacts_dic['life_attack_100']['price'] = 1000
artefacts_dic['life_attack_100']['name'] = 'Kill'
artefacts_dic['life_attack_100']['description'] = 'Remove all life, your target will loose one level'
artefacts_dic['life_attack_100']['force'] = 100
artefacts_dic['life_attack_100']['icon'] = ressources._sword_icon_
artefacts_dic['negative_5'] = dict()
artefacts_dic['negative_5']['price'] = 200
artefacts_dic['negative_5']['name'] = 'Negative 5min'
artefacts_dic['negative_5']['description'] = 'Switch your target wizard into negative colors for 5mins'
artefacts_dic['negative_5']['duration'] = 5
artefacts_dic['negative_5']['icon'] = ressources._book_purple_icon_
artefacts_dic['negative_30'] = dict()
artefacts_dic['negative_30']['price'] = 600
artefacts_dic['negative_30']['name'] = 'Negative 30min'
artefacts_dic['negative_30']['description'] = 'Switch your target wizard into negative colors for 30mins'
artefacts_dic['negative_30']['duration'] = 30
artefacts_dic['negative_30']['icon'] = ressources._book_purple_icon_
artefacts_dic['negative_120'] = dict()
artefacts_dic['negative_120']['price'] = 1200
artefacts_dic['negative_120']['name'] = 'Negative 2hours'
artefacts_dic['negative_120']['description'] = 'Switch your target wizard into negative colors for 2 hours'
artefacts_dic['negative_120']['duration'] = 30
artefacts_dic['negative_120']['icon'] = ressources._book_purple_icon_
artefacts_dic['heal'] = dict()
artefacts_dic['heal']['price'] = 150
artefacts_dic['heal']['name'] = 'Recover potion'
artefacts_dic['heal']['description'] = 'Get all your life back'
artefacts_dic['heal']['icon'] = ressources._potion_green_icon_

_creation_xp_ = 2
_save_xp_ = 1
_video_xp_ = 3
_export_xp_ = 3
_save_penalty_ = 2
_video_penalty_ = 4
_export_penalty_ = 10
