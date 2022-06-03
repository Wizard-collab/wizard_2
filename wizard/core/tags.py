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

# Python modules
import logging
logger = logging.getLogger(__name__)

from wizard.core import repository
from wizard.core import project
from wizard.core import events

def analyse_comment(comment, instance_type, instance_id):
	comment_words = comment.replace('\n', ' ').replace('\r', ' ').split(' ')
	for word in comment_words:
		if word.startswith('@'):
			user = word.replace('@', '')
			user = user.replace('\r', '')
			user = user.replace('\n', '')
			if user in repository.get_user_names_list():
				user_id = repository.get_user_row_by_name(user, 'id')
				if user_id in project.get_users_ids_list():
					events.add_tag_event(instance_type, instance_id, comment, user)
			elif user == 'all':
				events.add_tag_event(instance_type, instance_id, comment, user)
