# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

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
    championship_participation = repository.get_user_row_by_name(
        environment.get_user(), 'championship_participation')
    if not championship_participation:
        logger.warning("You don't participate to the championship.")
        return
    if artefact_name not in game_vars.artefacts_dic.keys():
        return
    stock = repository.get_artefact_stock(artefact_name)
    if stock == 0:
        logger.warning(
            f"{artefact_name} stocks are empty until someone use it.")
        return
    user_row = repository.get_user_row_by_name(environment.get_user())
    if 'coins' not in user_row.keys():
        return
    if game_vars.artefacts_dic[artefact_name]['price'] > user_row['coins']:
        logger.warning(
            f'Not enough coins to buy this artefact : {artefact_name}')
        return
    current_artefacts_dic = json.loads(user_row['artefacts'])
    count = list(current_artefacts_dic.values()).count(artefact_name)
    if count + stock == game_vars.artefacts_dic[artefact_name]['stock']\
            and (stock == 1)\
            and (game_vars.artefacts_dic[artefact_name]['stock'] > 1):
        logger.warning(f"You can't buy all the artefacts.")
        return
    current_artefacts_dic[time.time()] = artefact_name
    if not repository.modify_user_artefacts(environment.get_user(), current_artefacts_dic):
        return
    repository.remove_artefact_stock(artefact_name)
    repository.modify_user_coins(environment.get_user(
    ), user_row['coins']-game_vars.artefacts_dic[artefact_name]['price'])
    return 1


def remove_artefact_from_dic(artefact_name, artefacts_dic):
    for key in artefacts_dic.keys():
        if artefacts_dic[key] == artefact_name:
            del artefacts_dic[key]
            return artefacts_dic


def get_artefact_key(artefact_name, artefacts_dic):
    for key in artefacts_dic.keys():
        if artefacts_dic[key] == artefact_name:
            return key


def give_artefact(artefact_name, destination_user):
    user_row = repository.get_user_row_by_name(environment.get_user())
    championship_participation = user_row['championship_participation']
    if not championship_participation:
        logger.warning("You don't participate to the championship.")
        return
    if artefact_name not in game_vars.artefacts_dic.keys():
        return
    artefacts_dic = json.loads(user_row['artefacts'])
    if artefact_name not in artefacts_dic.values():
        logger.warning(f"You don't have this artefact : {artefact_name}")
        return
    artefact_time_id = get_artefact_key(artefact_name, artefacts_dic)
    artefacts_dic = remove_artefact_from_dic(artefact_name, artefacts_dic)
    if not repository.modify_user_artefacts(environment.get_user(), artefacts_dic):
        return
    destination_user_artefacts_dic = json.loads(
        repository.get_user_row_by_name(destination_user, 'artefacts'))
    destination_user_artefacts_dic[artefact_time_id] = artefact_name
    if not repository.modify_user_artefacts(destination_user, destination_user_artefacts_dic):
        return
    logger.info(f"{artefact_name} given to {destination_user}")


def give_coins(amount, destination_user):
    user_row = repository.get_user_row_by_name(environment.get_user())
    championship_participation = user_row['championship_participation']
    if not championship_participation:
        logger.warning("You don't participate to the championship.")
        return
    if user_row['coins'] < amount:
        logger.warning("You don't have enough coins")
        return
    new_coins = user_row['coins'] - amount
    if not repository.modify_user_coins(environment.get_user(), new_coins):
        return
    destination_user_coins = repository.get_user_row_by_name(
        destination_user, 'coins')
    amount_without_tax = amount - (int(amount*game_vars._transaction_tax_))
    new_destination_user_coins = destination_user_coins + amount_without_tax
    if not repository.modify_user_coins(destination_user, new_destination_user_coins):
        return
    logger.info(f"{amount} coins given to {destination_user}")


def use_artefact(artefact_name, destination_user=None):
    championship_participation = repository.get_user_row_by_name(
        environment.get_user(), 'championship_participation')
    if not championship_participation:
        logger.warning("You don't participate to the championship.")
        return
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
    user_row = repository.get_user_row_by_name(environment.get_user())
    artefacts_dic = json.loads(user_row['artefacts'])
    if artefact_name not in artefacts_dic.values():
        logger.warning(f"You don't have this artefact : {artefact_name}")
        return
    artefact_time_id = get_artefact_key(artefact_name, artefacts_dic)
    if game_vars.artefacts_dic[artefact_name]['type'] == 'attack':

        user_participation = repository.get_user_row_by_name(
            destination_user, 'championship_participation')
        if not user_participation:
            logger.warning(
                f"{destination_user} doens't participate to the championship.")
            return
        if check_immunity(destination_user):
            return
        if not send_attack(destination_user, artefact_name):
            return
        if 'steal_attack_1' in artefact_name:
            steal_attack_1(destination_user)
        if 'steal_attack_2' in artefact_name:
            if not steal_attack_2(destination_user):
                return
        repository.add_attack_event(
            environment.get_user(), destination_user, artefact_name)

    if 'heal' in artefact_name:
        heal(game_vars.artefacts_dic[artefact_name]['amount'])
    artefacts_dic = remove_artefact_from_dic(artefact_name, artefacts_dic)
    if not repository.modify_user_artefacts(environment.get_user(), artefacts_dic):
        return
    repository.add_artefact_stock(artefact_name)
    return 1


def check_immunity(destination_user):
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
    destination_user_coins = repository.get_user_row_by_name(
        destination_user, 'coins')
    if destination_user_coins == 0:
        logger.warning(
            f"{destination_user} doesn't have coins, attack failed.")
        return
    range_step = int(destination_user_coins/10)
    l = list(range(0, destination_user_coins, range_step))
    percent_step = 100/len(l)
    weights_list = []
    for a in l:
        index = l.index(a)+1
        weight = 100-(percent_step*index)+percent_step/2
        weights_list.append(weight)
    coins_amount = random.choices(l, weights=weights_list)[0]
    repository.remove_user_coins(destination_user, coins_amount)
    repository.add_user_coins(environment.get_user(), coins_amount)
    return coins_amount


def send_attack(destination_user, attack_name):
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
