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

"""
This module provides functionality for managing user progression, including experience points (XP),
levels, life, and coins. It also includes mechanisms for analyzing user comments and applying
consequences or rewards based on their content.

The module interacts with a repository to retrieve and update user data, and it uses the environment
module to identify the current user.

Functions:
    - add_xps(amount): Adds XP to the current user and handles level progression.
    - add_levels(amount): Increases the user's level by a specified amount.
    - remove_levels(amount): Decreases the user's level and records a death if necessary.
    - remove_levels_to_user(amount, user): Reduces the level of a specified user and records a death.
    - remove_life(amount): Deducts life from the user and removes a level if life reaches zero.
    - analyse_comment(comment, life_amount): Analyzes a comment and applies consequences or rewards.
    - add_coins(amount): Adds coins to the user's account.
"""

# Python modules
import random
import logging

# Wizard modules
from wizard.core import environment
from wizard.core import repository

logger = logging.getLogger(__name__)


def add_xps(amount):
    """
    Adds experience points (XP) to the current user's account and handles level progression.

    Args:
        amount (int): The amount of XP to add.

    Returns:
        int: Always returns 1 to indicate successful execution.

    Functionality:
        - Retrieves the current user's data from the repository.
        - Adds the specified amount of XP to the user's total XP and current XP.
        - If the current XP exceeds or equals 100, it deducts 100 from the current XP
          and increments the user's level by 1.
        - Updates the user's XP and total XP in the repository.
    """
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
    """
    Increases the level of the current user by a specified amount.

    Args:
        amount (int): The number of levels to add to the user's current level.

    Returns:
        bool: True if the user's level was successfully updated, False otherwise.

    Dependencies:
        - repository.get_user_row_by_name: Retrieves the user's data by their name.
        - environment.get_user: Gets the current user's name.
        - repository.modify_user_level: Updates the user's level in the repository.

    Raises:
        KeyError: If the 'level' or 'user_name' keys are missing in the user_row dictionary.
    """
    user_row = repository.get_user_row_by_name(environment.get_user())
    new_level = user_row['level'] + amount
    return repository.modify_user_level(user_row['user_name'], new_level)


def remove_levels(amount):
    """
    Decreases the user's level by the specified amount and updates the repository accordingly.
    If the resulting level is less than or equal to zero, it is set to zero.
    Additionally, records a death for the user in the repository.

    Args:
        amount (int): The number of levels to remove from the user's current level.

    Returns:
        int: Always returns 1 to indicate the operation was completed.
    """
    user_row = repository.get_user_row_by_name(environment.get_user())
    new_level = user_row['level'] - amount
    if new_level <= 0:
        new_level = 0
    repository.modify_user_level(user_row['user_name'], new_level)
    repository.add_death(user_row['user_name'])
    return 1


def remove_levels_to_user(amount, user):
    """
    Reduces the level of a specified user by a given amount. If the resulting level 
    is less than or equal to zero, it sets the user's level to zero. Additionally, 
    records a "death" for the user.

    Args:
        amount (int): The number of levels to remove from the user.
        user (str): The username of the user whose level is to be reduced.

    Returns:
        int: Always returns 1 as a success indicator.

    Side Effects:
        - Updates the user's level in the repository.
        - Adds a death record for the user in the repository.
    """
    user_row = repository.get_user_row_by_name(user)
    new_level = user_row['level'] - amount
    if new_level <= 0:
        new_level = 0
    repository.modify_user_level(user_row['user_name'], new_level)
    repository.add_death(user_row['user_name'])
    return 1


def remove_life(amount):
    """
    Reduces the life of the current user by the specified amount. If the user's life 
    reaches zero or below, it resets the life to 100 and removes one level from the user.

    Args:
        amount (int): The amount of life to be deducted.

    Returns:
        bool: True if the user's life was successfully updated in the repository, 
              False otherwise.
    """
    user_row = repository.get_user_row_by_name(environment.get_user())
    new_life = user_row['life'] - amount
    if new_life <= 0:
        new_life = 100
        remove_levels(1)
    return repository.modify_user_life(user_row['user_name'], new_life)


def analyse_comment(comment, life_amount):
    """
    Analyzes a user's comment and applies consequences based on its length.

    If the comment is shorter than 5 characters, the user loses a percentage of life
    and is warned about the importance of providing meaningful comments. Otherwise,
    the user's comment count is increased, and they are rewarded with coins based on
    the comment's length.

    Args:
        comment (str): The user's comment to be analyzed.
        life_amount (int): The percentage of life to be deducted if the comment is too short.

    Returns:
        int: Always returns 1 as a success indicator.

    Side Effects:
        - Deducts life from the user if the comment is too short.
        - Logs warnings for insufficient comment length.
        - Increases the user's comment count in the repository.
        - Adds coins to the user's account based on the comment's length.
    """
    if len(comment) < 5:
        remove_life(life_amount)
        logger.info(
            f"Warning, bad commenting just made you loose {life_amount}% of life")
        logger.info(
            f"Comment with more than 5 characters to avoid loosing life.")
    else:
        repository.increase_user_comments_count(environment.get_user())
        add_coins(len(comment)/random.randint(2, 5))
    return 1


def add_coins(amount):
    """
    Adds a specified amount of coins to the current user's account.

    Args:
        amount (int): The number of coins to add.

    Returns:
        bool: True if the coins were successfully added, False otherwise.
    """
    return repository.add_user_coins(environment.get_user(), amount)
