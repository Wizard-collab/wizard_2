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

# This module manages the wizard "game" part
# it uses the "repository" module to access 
# and write user data
# Uses this module to add xps, levels,
# remove levels and remove life

# Python modules
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from wizard.core import repository
from wizard.core import environment

def add_xps(amount):
	# Add the amount of xps to the user
	# if the xp amount gets to 100,
	# the user win 1 level and the xps
	# get back to 0
	user_row = repository.get_user_row_by_name(environment.get_user())
	new_total_xp = user_row['total_xp'] + amount
	new_xp = user_row['xp'] + amount
	if new_xp >= 100:
		new_xp -= 100
		add_levels(1)
	repository.modify_user_xp(user_row['user_name'], new_xp)
	repository.modify_user_total_xp(user_row['user_name'], new_total_xp)
	return 1

def add_levels(amount):
	user_row = repository.get_user_row_by_name(environment.get_user())
	new_level = user_row['level'] + amount
	return repository.modify_user_level(user_row['user_name'], new_level)

def remove_levels(amount):
	user_row = repository.get_user_row_by_name(environment.get_user())
	new_level = user_row['level'] - amount
	if new_level <= 0:
		new_level = 0
	repository.modify_user_level(user_row['user_name'], new_level)
	repository.add_death(user_row['user_name'])
	return 1

def remove_levels_to_user(amount, user):
	user_row = repository.get_user_row_by_name(user)
	new_level = user_row['level'] - amount
	if new_level <= 0:
		new_level = 0
	repository.modify_user_level(user_row['user_name'], new_level)
	repository.add_death(user_row['user_name'])
	return 1

def remove_life(amount):
	# Remove the given amount of life of
	# the current user
	# If the life is 0% or less,
	# the user loose 2 levels and
	# the life get back to 100%
	user_row = repository.get_user_row_by_name(environment.get_user())
	new_life = user_row['life'] - amount
	if new_life <= 0:
		new_life = 100
		remove_levels(1)
	return repository.modify_user_life(user_row['user_name'], new_life)

def analyse_comment(comment, life_amount):
	# Analyse if a comment length is 10 characters 
	# minimum, if not, removes life_amount from the user
	if len(comment) < 5:
		remove_life(life_amount)
		logger.info(f"Warning, bad commenting just made you loose {life_amount}% of life")
		logger.info(f"Comment with more than 5 characters to avoid loosing life.")
	else:
		repository.increase_user_comments_count(environment.get_user())
	return 1
	
def add_coins(amount):
	return repository.add_user_coins(environment.get_user(), amount)
