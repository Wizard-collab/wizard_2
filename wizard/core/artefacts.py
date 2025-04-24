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
This module provides functionalities for managing artefacts in the Wizard game.
Artefacts are special items that players can buy, use, transfer, or manage within
the game. The module includes functions for purchasing artefacts, transferring
artefacts or coins between users, using artefacts for various purposes (e.g., attack,
heal, or keep), and handling artefact expiration.

Key Features:
- Artefact purchase with stock and coin validation.
- Artefact transfer between users.
- Artefact usage for attacks, healing, or keeping.
- Coin transfer with transaction tax.
- Artefact and coin stealing attacks.
- Artefact expiration management.

Dependencies:
- Python modules: json, time, random, logging.
- Wizard core modules: game_vars, game, repository, environment, team_client.

Logging:
- Logs warnings for invalid operations (e.g., insufficient coins, invalid artefact names).
- Logs informational messages for successful operations (e.g., artefact transfer, attack sent).

Notes:
- The module interacts with external modules for data persistence and game logic.
- Artefact data is stored and manipulated as JSON-encoded dictionaries.
- The module assumes that repository methods handle data persistence correctly.
"""

# Python modules
import json
import time
import random
import logging

# Wizard core modules
from wizard.vars import game_vars
from wizard.core import game
from wizard.core import repository
from wizard.core import environment
from wizard.core import team_client

logger = logging.getLogger(__name__)


def buy_artefact(artefact_name):
    """
    Attempts to purchase an artefact for the current user.

    Args:
        artefact_name (str): The name of the artefact to be purchased.

    Returns:
        int or None: Returns 1 if the artefact is successfully purchased, 
                     otherwise returns None.

    Behavior:
        - Checks if the user is participating in the championship. If not, logs a warning and exits.
        - Validates if the artefact exists in the game's artefact dictionary. If not, exits.
        - Checks the stock of the artefact. If the stock is 0, logs a warning and exits.
        - Retrieves the user's data and ensures they have a 'coins' field. If not, exits.
        - Verifies if the user has enough coins to purchase the artefact. If not, logs a warning and exits.
        - Ensures the user cannot purchase all artefacts if the stock is limited and certain conditions are met.
        - Updates the user's artefacts with the purchased artefact.
        - Deducts the artefact's price from the user's coins.
        - Decreases the artefact's stock in the repository.

    Warnings:
        - Logs warnings for various conditions such as insufficient coins, empty stock, or invalid artefact names.
    """
    # Check if the user is participating in the championship
    championship_participation = repository.get_user_row_by_name(
        environment.get_user(), 'championship_participation')
    if not championship_participation:
        logger.warning("You don't participate to the championship.")
        return

    # Validate if the artefact exists in the game's artefact dictionary
    if artefact_name not in game_vars.artefacts_dic.keys():
        return

    # Check the stock of the artefact
    stock = repository.get_artefact_stock(artefact_name)
    if stock == 0:
        logger.warning(
            f"{artefact_name} stocks are empty until someone use it.")
        return

    # Retrieve the user's data and ensure they have a 'coins' field
    user_row = repository.get_user_row_by_name(environment.get_user())
    if 'coins' not in user_row.keys():
        return

    # Verify if the user has enough coins to purchase the artefact
    if game_vars.artefacts_dic[artefact_name]['price'] > user_row['coins']:
        logger.warning(
            f'Not enough coins to buy this artefact : {artefact_name}')
        return

    # Ensure the user cannot purchase all artefacts if the stock is limited
    current_artefacts_dic = json.loads(user_row['artefacts'])
    count = list(current_artefacts_dic.values()).count(artefact_name)
    if count + stock == game_vars.artefacts_dic[artefact_name]['stock']\
            and (stock == 1)\
            and (game_vars.artefacts_dic[artefact_name]['stock'] > 1):
        logger.warning(f"You can't buy all the artefacts.")
        return

    # Update the user's artefacts with the purchased artefact
    current_artefacts_dic[time.time()] = artefact_name
    if not repository.modify_user_artefacts(environment.get_user(), current_artefacts_dic):
        return

    # Deduct the artefact's price from the user's coins
    repository.remove_artefact_stock(artefact_name)
    repository.modify_user_coins(environment.get_user(
    ), user_row['coins']-game_vars.artefacts_dic[artefact_name]['price'])

    # Return success
    return 1


def remove_artefact_from_dic(artefact_name, artefacts_dic):
    """
    Removes an artefact from the artefacts dictionary.

    Args:
        artefact_name (str): The name of the artefact to be removed.
        artefacts_dic (dict): The dictionary containing artefacts with their time IDs as keys.

    Returns:
        dict: The updated artefacts dictionary with the specified artefact removed.
    """
    for key in artefacts_dic.keys():
        if artefacts_dic[key] == artefact_name:
            del artefacts_dic[key]
            return artefacts_dic


def get_artefact_key(artefact_name, artefacts_dic):
    """
    Retrieves the time ID key of a specific artefact from the artefacts dictionary.

    Args:
        artefact_name (str): The name of the artefact to find.
        artefacts_dic (dict): The dictionary containing artefacts with their time IDs as keys.

    Returns:
        str: The time ID key of the specified artefact, or None if not found.
    """
    for key in artefacts_dic.keys():
        if artefacts_dic[key] == artefact_name:
            return key


def give_artefact(artefact_name, destination_user):
    """
    Transfers an artefact from the current user to a specified destination user.

    Args:
        artefact_name (str): The name of the artefact to be transferred.
        destination_user (str): The username of the recipient.

    Returns:
        None

    Behavior:
        - Checks if the current user is participating in the championship. If not, logs a warning and exits.
        - Validates if the specified artefact exists in the game's artefact dictionary. If not, exits.
        - Checks if the current user possesses the specified artefact. If not, logs a warning and exits.
        - Removes the artefact from the current user's artefact dictionary and updates the repository.
        - Adds the artefact to the destination user's artefact dictionary and updates the repository.
        - Logs a success message upon successful transfer.

    Notes:
        - The function interacts with external modules such as `repository`, `environment`, and `game_vars`.
        - Artefact data is stored and manipulated as JSON-encoded dictionaries.
        - The function assumes that `repository.modify_user_artefacts` handles persistence of artefact changes.
    """
    # Retrieve the current user's data
    user_row = repository.get_user_row_by_name(environment.get_user())

    # Check if the user is participating in the championship
    championship_participation = user_row['championship_participation']
    if not championship_participation:
        logger.warning("You don't participate to the championship.")
        return

    # Validate if the artefact exists in the game's artefact dictionary
    if artefact_name not in game_vars.artefacts_dic.keys():
        return

    # Retrieve the user's artefacts and check if they own the specified artefact
    artefacts_dic = json.loads(user_row['artefacts'])
    if artefact_name not in artefacts_dic.values():
        logger.warning(f"You don't have this artefact : {artefact_name}")
        return

    # Get the time ID key of the artefact and remove it from the user's artefacts
    artefact_time_id = get_artefact_key(artefact_name, artefacts_dic)
    artefacts_dic = remove_artefact_from_dic(artefact_name, artefacts_dic)
    if not repository.modify_user_artefacts(environment.get_user(), artefacts_dic):
        return

    # Retrieve the destination user's artefacts and add the transferred artefact
    destination_user_artefacts_dic = json.loads(
        repository.get_user_row_by_name(destination_user, 'artefacts'))
    destination_user_artefacts_dic[artefact_time_id] = artefact_name
    if not repository.modify_user_artefacts(destination_user, destination_user_artefacts_dic):
        return

    # Log a success message indicating the artefact transfer
    logger.info(f"{artefact_name} given to {destination_user}")


def give_coins(amount, destination_user):
    """
    Transfers a specified amount of coins from the current user to a destination user,
    applying a transaction tax. The function ensures that the current user participates
    in the championship and has sufficient coins before proceeding with the transaction.

    Args:
        amount (int): The number of coins to transfer.
        destination_user (str): The username of the recipient.

    Returns:
        None: The function logs warnings or information messages and does not return any value.

    Logs:
        - A warning if the current user does not participate in the championship.
        - A warning if the current user does not have enough coins.
        - An informational message upon successful transfer of coins.

    Notes:
        - The transaction tax is applied to the transferred amount, reducing the coins
          received by the destination user.
        - The function interacts with a repository to fetch and modify user data.
    """
    # Retrieve the current user's data
    user_row = repository.get_user_row_by_name(environment.get_user())

    # Check if the user is participating in the championship
    championship_participation = user_row['championship_participation']
    if not championship_participation:
        logger.warning("You don't participate to the championship.")
        return

    # Verify if the user has enough coins to transfer
    if user_row['coins'] < amount:
        logger.warning("You don't have enough coins")
        return

    # Deduct the specified amount of coins from the current user
    new_coins = user_row['coins'] - amount
    if not repository.modify_user_coins(environment.get_user(), new_coins):
        return

    # Retrieve the destination user's current coin balance
    destination_user_coins = repository.get_user_row_by_name(
        destination_user, 'coins')

    # Calculate the amount to transfer after applying the transaction tax
    amount_without_tax = amount - (int(amount * game_vars._transaction_tax_))
    new_destination_user_coins = destination_user_coins + amount_without_tax

    # Update the destination user's coin balance
    if not repository.modify_user_coins(destination_user, new_destination_user_coins):
        return

    # Log a success message indicating the transfer
    logger.info(f"{amount} coins given to {destination_user}")


def use_artefact(artefact_name, destination_user=None):
    """
    Uses an artefact for the current user or against a destination user.
    This function handles the logic for using artefacts in the game. It checks
    the user's championship participation, artefact ownership, and artefact type
    to determine the appropriate action. Artefacts can be used for attacks, healing,
    or kept for future use.
    Args:
        artefact_name (str): The name of the artefact to be used.
        destination_user (str, optional): The username of the target user for the artefact.
            Defaults to None, which means the artefact is used by the current user.
    Returns:
        int or None: Returns 1 if the artefact is successfully used, or None if the
        operation fails due to various conditions (e.g., artefact not owned, target
        user not participating in the championship, etc.).
    Raises:
        None: This function does not raise any exceptions directly but logs warnings
        for invalid operations.
    Notes:
        - Artefacts of type 'attack' can be used against other users participating
          in the championship.
        - Artefacts of type 'heal' restore health to the current user.
        - Artefacts with 'keep' usage cannot be accumulated.
        - The function updates the artefact inventory and logs attack events when
          applicable.
    """
    # Check if the user is participating in the championship
    championship_participation = repository.get_user_row_by_name(
        environment.get_user(), 'championship_participation')
    if not championship_participation:
        logger.warning("You don't participate to the championship.")
        return

    # Handle artefacts with 'keep' usage for the current user
    if (destination_user == environment.get_user()) and game_vars.artefacts_dic[artefact_name]['usage'] == 'keep':
        keeped_artefacts_dic = json.loads(repository.get_user_row_by_name(
            environment.get_user(), 'keeped_artefacts'))
        if artefact_name in keeped_artefacts_dic.values():
            logger.warning(
                f"You can't cummulate {game_vars.artefacts_dic[artefact_name]['name']} !")
            return
        keeped_artefacts_dic[str(time.time())] = artefact_name
        repository.modify_keeped_artefacts(
            environment.get_user(), keeped_artefacts_dic)

    # Check if the user owns the specified artefact
    user_row = repository.get_user_row_by_name(environment.get_user())
    artefacts_dic = json.loads(user_row['artefacts'])
    if artefact_name not in artefacts_dic.values():
        logger.warning(f"You don't have this artefact : {artefact_name}")
        return

    # Handle artefacts of type 'attack'
    if game_vars.artefacts_dic[artefact_name]['type'] == 'attack':

        # Check if the destination user is participating in the championship
        user_participation = repository.get_user_row_by_name(
            destination_user, 'championship_participation')
        if not user_participation:
            logger.warning(
                f"{destination_user} doens't participate to the championship.")
            return

        # Check if the destination user has immunity
        if check_immunity(destination_user):
            return

        # Send the attack to the destination user
        if not send_attack(destination_user, artefact_name):
            return

        # Handle specific attack types
        if 'steal_attack_1' in artefact_name:
            steal_attack_1(destination_user)
        if 'steal_attack_2' in artefact_name:
            if not steal_attack_2(destination_user):
                return

        # Log the attack event in the repository
        repository.add_attack_event(
            environment.get_user(), destination_user, artefact_name)

    # Handle artefacts of type 'heal'
    if 'heal' in artefact_name:
        heal(game_vars.artefacts_dic[artefact_name]['amount'])

    # Remove the used artefact from the user's inventory
    artefacts_dic = remove_artefact_from_dic(artefact_name, artefacts_dic)
    if not repository.modify_user_artefacts(environment.get_user(), artefacts_dic):
        return

    # Add the used artefact back to the stock
    repository.add_artefact_stock(artefact_name)

    # Return success
    return 1


def check_immunity(destination_user):
    """
    Checks if the destination user has an active immunity artefact.

    Args:
        destination_user (str): The username of the target user.

    Returns:
        int or None: Returns 1 if the destination user has an active immunity artefact,
                     otherwise returns None.

    Behavior:
        - Retrieves the destination user's keeped artefacts.
        - Iterates through the artefacts to check for an active immunity artefact.
        - Logs a warning if the attack fails due to immunity.

    Notes:
        - Immunity artefacts have a duration, and expired artefacts are ignored.
        - The function assumes that the repository and game_vars modules provide
          the necessary data for artefact validation.
    """
    destination_user_row = repository.get_user_row_by_name(destination_user)
    destination_user_keeped_artefacts = json.loads(
        destination_user_row['keeped_artefacts'])
    for time_id, keeped_artefact in destination_user_keeped_artefacts.items():
        if 'immunity' not in keeped_artefact:
            continue
        if time.time() > float(time_id) + game_vars.artefacts_dic[keeped_artefact]['duration']:
            continue
        logger.warning(
            f"Your attack just failed, {destination_user} has an immunity artefact !")
        return 1


def check_keeped_artefacts_expiration():
    """
    Checks and removes expired keeped artefacts for the current user.

    Returns:
        int or None: Returns 1 if any artefacts were removed, otherwise returns None.

    Behavior:
        - Retrieves the current user's keeped artefacts.
        - Iterates through the artefacts to check for expiration based on their duration.
        - Removes expired artefacts and updates the repository.
        - Logs information about expired artefacts.

    Notes:
        - Artefacts are considered expired if their duration has passed since their time ID.
        - The function assumes that the repository and game_vars modules provide
          the necessary data for artefact validation and updates.
    """
    user_row = repository.get_user_row_by_name(environment.get_user())
    user_keeped_artefacts = json.loads(user_row['keeped_artefacts'])
    time_ids = list(user_keeped_artefacts.keys())
    update = 0
    for time_id in time_ids:
        keeped_artefact = user_keeped_artefacts[time_id]
        if time.time() > float(time_id) + game_vars.artefacts_dic[keeped_artefact]['duration']:
            logger.info(
                f"{game_vars.artefacts_dic[keeped_artefact]['name']} is expired")
            del user_keeped_artefacts[time_id]
            update = 1
    if not update:
        return
    repository.modify_keeped_artefacts(
        environment.get_user(), user_keeped_artefacts)
    return 1


def check_artefacts_expiration():
    """
    Checks and removes expired artefacts from the user's inventory.

    Returns:
        int or None: Returns 1 if any artefacts were removed, otherwise returns None.

    Behavior:
        - Retrieves the current user's artefacts.
        - Iterates through the artefacts to check for expiration based on a global expiration time.
        - Removes expired artefacts, updates the repository, and adds them back to the stock.
        - Logs information about expired artefacts.

    Notes:
        - Artefacts are considered expired if their expiration time has passed since their time ID.
        - The function assumes that the repository and game_vars modules provide
          the necessary data for artefact validation and updates.
    """
    user_row = repository.get_user_row_by_name(environment.get_user())
    user_artefacts = json.loads(user_row['artefacts'])
    time_ids = list(user_artefacts.keys())
    update = 0
    for time_id in time_ids:
        artefact = user_artefacts[time_id]
        if time.time() > float(time_id) + game_vars._artefact_expiration_:
            logger.info(
                f"{game_vars.artefacts_dic[artefact]['name']} is expired")
            del user_artefacts[time_id]
            repository.add_artefact_stock(artefact)
            update = 1
    if not update:
        return
    repository.modify_user_artefacts(environment.get_user(), user_artefacts)
    return 1


def heal(amount):
    """
    Restores the user's life by a specified amount, up to a maximum of 100%.

    Args:
        amount (int): The amount of life to restore. If 100, the user's life is set to 100%.

    Returns:
        None: The function logs the updated life percentage and does not return any value.

    Behavior:
        - If the amount is 100, sets the user's life to 100%.
        - Otherwise, adds the specified amount to the user's current life.
        - Ensures the user's life does not exceed 100%.
        - Updates the user's life in the repository and logs the new life percentage.

    Notes:
        - The function assumes that the repository module provides the necessary
          methods to fetch and update the user's life.
    """
    if amount == 100:
        life = 100
    else:
        life = repository.get_user_row_by_name(
            environment.get_user(), 'life') + amount
        if life > 100:
            life = 100
    repository.modify_user_life(environment.get_user(), life)
    logger.info(f"You just drank a heal potion, your life is now at {life}% !")


def steal_attack_1(destination_user):
    """
    Executes a level-stealing attack on the destination user.

    Args:
        destination_user (str): The username of the target user.

    Returns:
        int or None: Returns 1 if the attack is successful, otherwise returns None.

    Behavior:
        - Retrieves the destination user's level.
        - If the destination user has no levels, logs a warning and exits.
        - Removes one level from the destination user and adds it to the current user.

    Notes:
        - The function interacts with the `repository` and `game` modules to modify user levels.
        - Logs warnings for invalid operations, such as attacking a user with no levels.
    """
    destination_user_level = repository.get_user_row_by_name(
        destination_user, 'level')
    if destination_user_level == 0:
        logger.warning(
            f"{destination_user} doesn't have levels for you, attack failed.")
        return
    game.remove_levels_to_user(1, destination_user)
    game.add_levels(1)
    return 1


def steal_attack_2(destination_user):
    """
    Executes a coin-stealing attack on the destination user.

    Args:
        destination_user (str): The username of the target user.

    Returns:
        int or None: Returns the amount of coins stolen if the attack is successful, otherwise returns None.

    Behavior:
        - Retrieves the destination user's coin balance.
        - If the destination user has no coins, logs a warning and exits.
        - Calculates a random amount of coins to steal using a weighted probability distribution.
        - Removes the stolen coins from the destination user and adds them to the current user's balance.

    Notes:
        - The function uses a weighted random selection to determine the amount of coins stolen.
        - Logs warnings for invalid operations, such as attacking a user with no coins.
        - Interacts with the `repository` module to modify user coin balances.
    """
    # Retrieve the destination user's coin balance
    destination_user_coins = repository.get_user_row_by_name(
        destination_user, 'coins')

    # Check if the destination user has any coins
    if destination_user_coins == 0:
        logger.warning(
            f"{destination_user} doesn't have coins, attack failed.")
        return

    # Calculate the range step for dividing the coin balance into intervals
    range_step = int(destination_user_coins / 10)

    # Create a list of intervals based on the range step
    l = list(range(0, destination_user_coins, range_step))

    # Calculate the percentage step for weighting the intervals
    percent_step = 100 / len(l)

    # Generate a list of weights for each interval
    weights_list = []
    for a in l:
        index = l.index(a) + 1
        weight = 100 - (percent_step * index) + percent_step / 2
        weights_list.append(weight)

    # Randomly select an amount of coins to steal based on the weights
    coins_amount = random.choices(l, weights=weights_list)[0]

    # Deduct the stolen coins from the destination user
    repository.remove_user_coins(destination_user, coins_amount)

    # Add the stolen coins to the current user's balance
    repository.add_user_coins(environment.get_user(), coins_amount)

    # Return the amount of coins stolen
    return coins_amount


def send_attack(destination_user, attack_name):
    """
    Sends an attack signal to a specified user within the team environment.

    This function constructs a signal dictionary containing the attack type,
    the sender's user information, and the destination user. It then attempts
    to send the signal to the team server using the `team_client.send_prank` method.

    Args:
        destination_user (str): The username of the target user to send the attack to.
        attack_name (str): The name of the attack to be sent.

    Returns:
        int: Returns 1 if the attack signal is successfully sent.
        None: Returns None if the team server is not connected or the signal fails to send.

    Logs:
        - A warning if the team server is not connected.
        - A warning if the destination user cannot be reached.
        - An info message if the attack is successfully sent.
    """
    signal_dic = dict()
    signal_dic['attack_type'] = attack_name
    signal_dic['from_user'] = environment.get_user()
    signal_dic['destination_user'] = destination_user
    DNS = environment.get_team_dns()
    if not DNS:
        logger.warning(
            "You're not connected to the team server, can't reach other users.")
        return
    if not team_client.send_prank(environment.get_team_dns(), signal_dic):
        logger.warning(f"Can't reach {destination_user}, not using artefact.")
        return
    logger.info(f"Attack sent to {destination_user}")
    return 1
