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
artefacts_dic['mouse_attack_1'] = dict()
artefacts_dic['mouse_attack_1']['type'] = 'attack'
artefacts_dic['mouse_attack_1']['usage'] = 'unique'
artefacts_dic['mouse_attack_1']['price'] = 50
artefacts_dic['mouse_attack_1']['name'] = 'Jiggly mouse 10s '
artefacts_dic['mouse_attack_1']['description'] = 'Randomly move the cursor of your target for 10s'
artefacts_dic['mouse_attack_1']['duration'] = 10
artefacts_dic['mouse_attack_1']['icon'] = ressources._potion_green_icon_
artefacts_dic['mouse_attack_2'] = dict()
artefacts_dic['mouse_attack_2']['type'] = 'attack'
artefacts_dic['mouse_attack_2']['usage'] = 'unique'
artefacts_dic['mouse_attack_2']['price'] = 300
artefacts_dic['mouse_attack_2']['name'] = 'Jiggly mouse 30s '
artefacts_dic['mouse_attack_2']['description'] = 'Randomly move the cursor of your target for 30s'
artefacts_dic['mouse_attack_2']['duration'] = 30
artefacts_dic['mouse_attack_2']['icon'] = ressources._potion_red_icon_
artefacts_dic['mouse_attack_3'] = dict()
artefacts_dic['mouse_attack_3']['type'] = 'attack'
artefacts_dic['mouse_attack_3']['usage'] = 'unique'
artefacts_dic['mouse_attack_3']['price'] = 3000
artefacts_dic['mouse_attack_3']['name'] = 'Jiggly mouse 2mins'
artefacts_dic['mouse_attack_3']['description'] = 'Randomly move the cursor of your target for 120s'
artefacts_dic['mouse_attack_3']['duration'] = 120
artefacts_dic['mouse_attack_3']['icon'] = ressources._potion_blue_icon_
artefacts_dic['life_attack_1'] = dict()
artefacts_dic['life_attack_1']['type'] = 'attack'
artefacts_dic['life_attack_1']['usage'] = 'unique'
artefacts_dic['life_attack_1']['price'] = 50
artefacts_dic['life_attack_1']['name'] = 'Life attack 10'
artefacts_dic['life_attack_1']['description'] = 'Remove 10% of life for your target'
artefacts_dic['life_attack_1']['force'] = 10
artefacts_dic['life_attack_1']['icon'] = ressources._sword_icon_
artefacts_dic['life_attack_2'] = dict()
artefacts_dic['life_attack_2']['type'] = 'attack'
artefacts_dic['life_attack_2']['usage'] = 'unique'
artefacts_dic['life_attack_2']['price'] = 300
artefacts_dic['life_attack_2']['name'] = 'Life attack 33'
artefacts_dic['life_attack_2']['description'] = 'Remove 33% of life for your target'
artefacts_dic['life_attack_2']['force'] = 33
artefacts_dic['life_attack_2']['icon'] = ressources._sword_icon_
artefacts_dic['life_attack_3'] = dict()
artefacts_dic['life_attack_3']['type'] = 'attack'
artefacts_dic['life_attack_3']['usage'] = 'unique'
artefacts_dic['life_attack_3']['price'] = 1000
artefacts_dic['life_attack_3']['name'] = 'Kill'
artefacts_dic['life_attack_3']['description'] = 'Remove all life, your target will loose one level'
artefacts_dic['life_attack_3']['force'] = 100
artefacts_dic['life_attack_3']['icon'] = ressources._sword_icon_
artefacts_dic['resolution_attack'] = dict()
artefacts_dic['resolution_attack']['type'] = 'attack'
artefacts_dic['resolution_attack']['usage'] = 'unique'
artefacts_dic['resolution_attack']['price'] = 200
artefacts_dic['resolution_attack']['name'] = 'Resolution 800x600'
artefacts_dic['resolution_attack']['description'] = 'Switch your target screen resolution to 800x600 !'
artefacts_dic['resolution_attack']['icon'] = ressources._book_purple_icon_
artefacts_dic['rickroll_attack'] = dict()
artefacts_dic['rickroll_attack']['type'] = 'attack'
artefacts_dic['rickroll_attack']['usage'] = 'unique'
artefacts_dic['rickroll_attack']['price'] = 200
artefacts_dic['rickroll_attack']['name'] = 'Rickroll'
artefacts_dic['rickroll_attack']['description'] = 'Rickroll your target !'
artefacts_dic['rickroll_attack']['icon'] = ressources._book_red_icon_
artefacts_dic['lock_attack'] = dict()
artefacts_dic['lock_attack']['type'] = 'attack'
artefacts_dic['lock_attack']['usage'] = 'unique'
artefacts_dic['lock_attack']['price'] = 200
artefacts_dic['lock_attack']['name'] = 'Lock'
artefacts_dic['lock_attack']['description'] = 'Lock your target session !'
artefacts_dic['lock_attack']['icon'] = ressources._key_icon_
artefacts_dic['flip_attack_1'] = dict()
artefacts_dic['flip_attack_1']['type'] = 'attack'
artefacts_dic['flip_attack_1']['usage'] = 'unique'
artefacts_dic['flip_attack_1']['price'] = 200
artefacts_dic['flip_attack_1']['name'] = 'Flip screen'
artefacts_dic['flip_attack_1']['description'] = 'Flip your target screen !'
artefacts_dic['flip_attack_1']['icon'] = ressources._mushroom_blue_icon_
artefacts_dic['flip_attack_2'] = dict()
artefacts_dic['flip_attack_2']['type'] = 'attack'
artefacts_dic['flip_attack_2']['usage'] = 'unique'
artefacts_dic['flip_attack_2']['price'] = 200
artefacts_dic['flip_attack_2']['name'] = 'Flip screen 1min'
artefacts_dic['flip_attack_2']['description'] = 'Flip your target screen for 1 minute !'
artefacts_dic['flip_attack_2']['icon'] = ressources._mushroom_orange_icon_
artefacts_dic['heal'] = dict()
artefacts_dic['heal']['type'] = 'protection'
artefacts_dic['heal']['usage'] = 'unique'
artefacts_dic['heal']['price'] = 150
artefacts_dic['heal']['name'] = 'Steak'
artefacts_dic['heal']['description'] = 'Get all your life back'
artefacts_dic['heal']['icon'] = ressources._steak_icon_
artefacts_dic['immunity_1'] = dict()
artefacts_dic['immunity_1']['type'] = 'protection'
artefacts_dic['immunity_1']['usage'] = 'keep'
artefacts_dic['immunity_1']['price'] = 150
artefacts_dic['immunity_1']['name'] = 'Immunity 12h'
artefacts_dic['immunity_1']['duration'] = 12
artefacts_dic['immunity_1']['description'] = 'Protect you from all attacks for 12 hours.'
artefacts_dic['immunity_1']['icon'] = ressources._shield_icon_
artefacts_dic['immunity_2'] = dict()
artefacts_dic['immunity_2']['type'] = 'protection'
artefacts_dic['immunity_2']['usage'] = 'keep'
artefacts_dic['immunity_2']['price'] = 150
artefacts_dic['immunity_2']['name'] = 'Immunity 72h'
artefacts_dic['immunity_2']['duration'] = 72
artefacts_dic['immunity_2']['description'] = 'Protect you from all attacks for 72 hours.'
artefacts_dic['immunity_2']['icon'] = ressources._shield_icon_
artefacts_dic['xp_booster_1'] = dict()
artefacts_dic['xp_booster_1']['type'] = 'booster'
artefacts_dic['xp_booster_1']['usage'] = 'keep'
artefacts_dic['xp_booster_1']['price'] = 150
artefacts_dic['xp_booster_1']['name'] = 'Double xp for 12h'
artefacts_dic['xp_booster_1']['duration'] = 12
artefacts_dic['xp_booster_1']['description'] = 'Double each xp earned for the next 12h.'
artefacts_dic['xp_booster_1']['icon'] = ressources._potion_2_blue_icon_
artefacts_dic['xp_booster_2'] = dict()
artefacts_dic['xp_booster_2']['type'] = 'booster'
artefacts_dic['xp_booster_2']['usage'] = 'keep'
artefacts_dic['xp_booster_2']['price'] = 150
artefacts_dic['xp_booster_2']['name'] = 'Double xp for 72h'
artefacts_dic['xp_booster_2']['duration'] = 72
artefacts_dic['xp_booster_2']['description'] = 'Double each xp earned for the next 72h.'
artefacts_dic['xp_booster_2']['icon'] = ressources._potion_2_pink_icon_
artefacts_dic['coins_booster_1'] = dict()
artefacts_dic['coins_booster_1']['type'] = 'booster'
artefacts_dic['coins_booster_1']['usage'] = 'keep'
artefacts_dic['coins_booster_1']['price'] = 150
artefacts_dic['coins_booster_1']['name'] = 'Double coins for 12h'
artefacts_dic['coins_booster_1']['duration'] = 12
artefacts_dic['coins_booster_1']['description'] = 'Double each coin earned for the next 12h.'
artefacts_dic['coins_booster_1']['icon'] = ressources._coins_1_icon_
artefacts_dic['coins_booster_2'] = dict()
artefacts_dic['coins_booster_2']['type'] = 'booster'
artefacts_dic['coins_booster_2']['usage'] = 'keep'
artefacts_dic['coins_booster_2']['price'] = 150
artefacts_dic['coins_booster_2']['name'] = 'Double coins for 72h'
artefacts_dic['coins_booster_2']['duration'] = 72
artefacts_dic['coins_booster_2']['description'] = 'Double each coin earned for the next 72h.'
artefacts_dic['coins_booster_2']['icon'] = ressources._coins_2_icon_



_creation_xp_ = 2
_save_xp_ = 1
_video_xp_ = 3
_export_xp_ = 3
_save_penalty_ = 2
_video_penalty_ = 4
_export_penalty_ = 10
