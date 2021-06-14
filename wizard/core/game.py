# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module manages the wizard "game" part
# it uses the "site" module to access 
# and write user data
# Uses this module to add xps, levels,
# remove levels and remove life

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

from wizard.core import site
from wizard.core import environment

def add_xps(amount):
	user_row = site.site().get_user_row_by_name(environment.get_user())
	new_xp = user_row['xp'] + amount
	if new_xp >= 100:
		new_xp -= 100
		add_levels(1)
	site.site().modify_user_xp(user_row['user_name'], new_xp)

def add_levels(amount):
	user_row = site.site().get_user_row_by_name(environment.get_user())
	new_level = user_row['level'] + amount
	site.site().modify_user_level(user_row['user_name'], new_level)

def remove_levels(amount):
	user_row = site.site().get_user_row_by_name(environment.get_user())
	new_level = user_row['level'] - amount
	if new_level <= 0:
		new_level = 0
	site.site().modify_user_level(user_row['user_name'], new_level)

def remove_life(amount):
	user_row = site.site().get_user_row_by_name(environment.get_user())
	new_life = user_row['life'] - amount
	if new_life <= 0:
		new_life = 100
		remove_levels(2)
	site.site().modify_user_life(user_row['user_name'], new_life)

def analyse_comment(comment, life_amount):
	if len(comment) < 10:
		remove_life(life_amount)
		logging.info(f"Warning, bad commenting just made you loose {life_amount}% of life")