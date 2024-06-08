"""Minikit's Warframe Utilities Module

Module for Discord Bot, that uses
Warframe market's API, Warframestatus's API and Warframe's drops table page
to get useful data and parse it into
a convenient way to read and understand
"""

import discord
import requests
import asyncio
import json
import lxml.html


async def get_market_orders(request):
    """Gets array of market orders for specific item

    Function gets all (sell and buy) orders from warframe.market\n
    Array include orders only from people that are online\n
    Orders are accepted from players of any reputation and any region

    Parameters
    ----------
    request : string
        String name of the item to get orders from warframe.market
        (e.g. "secura_dual_cestra")

    Returns
    -------
    embed: discord_embed
        Orders are sorted and saved in Discord Embed variable type
    (sorted_buy_orders, request) : tuple
        Tuple of array of sorted buying orders in decreasing order and the string name of the requested item
    (sorted_sell_orders, request) : tuple
        Tuple of array of sorted selling orders in decreasing order and the string name of the requested item

    Warning
    -------
        Requesting invalid or non-existent item from warframe market will result in Error message
    """

    req = requests.get('https://api.warframe.market/v1/items/' + request + '/orders')
    content = req.content
    if req.status_code != 404:
        try:
            raw_data = json.loads(content)
            data_payload = raw_data["payload"]
            orders = data_payload["orders"]
            embed = discord.Embed(title=request, color=0x000475)
            buy_orders = {}
            sell_orders = {}
            buy_string = ""
            sell_string = ""
            max_orders = 5
            for Order in orders:
                try:
                    if Order["user"]["status"] == "ingame":
                        nickname = Order["user"]["ingame_name"]
                        price = int(Order["platinum"])

                        try:
                            rank = Order["mod_rank"]
                        except:
                            rank = -1
                        order_type = Order["order_type"]
                        if order_type == "buy":
                            if nickname in buy_orders:
                                if price > buy_orders[nickname][0]:
                                    buy_orders[nickname] = (price, rank)
                            else:
                                buy_orders[nickname] = (price, rank)
                        elif order_type == "sell":
                            if nickname in sell_orders:
                                if price > sell_orders[nickname][0]:
                                    sell_orders[nickname] = (price, rank)
                            else:
                                sell_orders[nickname] = (price, rank)
                except:
                    print("Parsing Error: ", Order)

            sorted_buy_orders = sorted(buy_orders.items(), key=lambda x: x[1][0], reverse=True)
            sorted_sell_orders = sorted(sell_orders.items(), key=lambda x: x[1][0])

            if len(sorted_buy_orders) > max_orders:
                buy_orders_amount = max_orders
            else:
                buy_orders_amount = len(sorted_buy_orders)

            if len(sorted_sell_orders) > max_orders:
                sell_orders_amount = max_orders
            else:
                sell_orders_amount = len(sorted_sell_orders)

            if buy_orders_amount > sell_orders_amount:
                max_orders_amount = buy_orders_amount
            else:
                max_orders_amount = sell_orders_amount
            for i in range(max_orders_amount):
                if buy_orders_amount > i:
                    buy_string += "**" + str(int(sorted_buy_orders[i][1][0])) + "** " + str(
                        sorted_buy_orders[i][0]) + "  (Rank " + str(sorted_buy_orders[i][1][1]) + ")\n\n"
                if sell_orders_amount > i:
                    sell_string += "**" + str(int(sorted_sell_orders[i][1][0])) + "**  " + str(
                        sorted_sell_orders[i][0]) + "  (Rank " + str(sorted_sell_orders[i][1][1]) + ")\n\n"

            embed.add_field(name="**Buys**", value=buy_string, inline=True)
            embed.add_field(name="**Sells**", value=sell_string, inline=True)
            return embed, (sorted_buy_orders, request), (sorted_sell_orders, request)
        except:
            print("Caught Error in order: ", request)

    embed = discord.Embed(title=request, color=0x000475)
    return embed, (0, "0"), (0, "0")


async def get_market_syndicate_weapons(file_name):
    """ Gets all orders for the chosen syndicate weapons

    Returns all syndicate weapons orders (buy/sell) from warframe.market in string format\n
    Syndicate is selected by inputting required syndicate file\n
    Available syndicate names: arbiters, loka, meridian, perrin, suda, veil\n

    Parameters
    ----------
    file_name : str
        File name of the file which contains warframe market item names,
        file name consists of "weapons_" + syndicate name + ".txt"
        (e.g. "weapons_loka.txt").
        File contents example:
            telos_akbolto
            telos_boltor
            telos_boltace

    Returns
    -------
    results_string : str
        All orders concatenated in one string:
            player_name sells/buys item_name for amount_of_platinum

    """

    max_tops = 4
    items = []
    top_buy_orders = []
    top_sell_orders = []
    results_string = ""

    weapons_file = open("Warframe/Syndicates/" + file_name, "r")
    for line in weapons_file:
        items.append(line.rstrip())

    for Item in items:
        embed, buys, sells = await get_market_orders(Item)

        for i in range(len(buys[0])):
            top_buy_orders.append((buys[0][i][0], buys[0][i][1][0], buys[1]))
        for i in range(len(sells[0])):
            top_sell_orders.append((sells[0][i][0], sells[0][i][1][0], sells[1]))

    sorted_top_buy_orders = sorted(top_buy_orders, key=lambda x: x[1][0], reverse=True)
    sorted_top_sell_orders = sorted(top_sell_orders, key=lambda x: x[1][0])

    results_string += await add_each_to_string(sorted_top_buy_orders, max_tops, " buys for **")

    results_string += "\n"

    results_string += await add_each_to_string(sorted_top_sell_orders, max_tops, " sells for **")

    return results_string


async def get_market_syndicate_offerings(file_name, message, mode="default"):
    """ Gets all orders for the chosen syndicate weapons

    Returns all syndicate offerings orders (buy/sell) from warframe.market in string format\n
    Syndicate is selected by inputting required syndicate file\n
    Available syndicate names: arbiters, loka, meridian, perrin, suda, veil\n

    Parameters
    ----------
    file_name : str
        File name of the file which contains warframe market item names,
        file name consists of "offerings_" + syndicate name + ".txt"
        (e.g. "offerings_perrin.txt").
        File contents example:
            onorix_handle
            phaedra_receiver
            centaur_blade

    message : discord_message
            Discord message for visual output of ongoing process

    mode : str
        Name of the mode (e.g. "chat")
        Changes the way function creates and outputs the result
        Chat mode generates a complete message,
        which can be copy pasted into the Warframe's trade chat

    Returns
    -------
    results_string : str
        All orders concatenated in one string:
            player_name sells/buys item_name for amount_of_platinum

    """

    max_tops = 10
    items = []
    top_buy_orders = []
    top_sell_orders = []
    results_string = ""

    offerings_file = open("Warframe/Syndicates/" + file_name, "r")
    for line in offerings_file:
        items.append(line.rstrip())

    print("")
    print("")
    syndicateofferingsmessage = await message.channel.send(
        "Getting syndicate offerings for " + str(file_name)[10:-4].capitalize() + "...")

    for Item in items:
        await syndicateofferingsmessage.edit(
            content="(" + str(items.index(Item) + 1) +
                    "/" + str(len(items)) +
                    ") Getting orders for " + str(Item) + "...")
        await asyncio.sleep(0.1)
        embed, buys, sells = await get_market_orders(Item)
        print(str((items.index(Item)) + 1) + "/" + str(len(items)) + " " + Item)
        for i in range(len(buys[0])):
            top_buy_orders.append((buys[0][i][0], buys[0][i][1][0], buys[0][i][1][1], buys[1]))
        for i in range(len(sells[0])):
            top_sell_orders.append((sells[0][i][0], sells[0][i][1][0], sells[0][i][1][1], sells[1]))

    await delete_message_after_delay(syndicateofferingsmessage, 0.2)

    sorted_top_buy_orders = sorted(top_buy_orders, key=lambda x: x[1], reverse=True)
    sorted_top_sell_orders = sorted(top_sell_orders, key=lambda x: x[1])

    if mode == "chat":
        results_string += await add_each_to_string_chat(sorted_top_buy_orders, max_tops)
    else:
        results_string += await add_each_to_string(sorted_top_buy_orders, max_tops, " buys **")
        results_string += "\n"
        results_string += await add_each_to_string(sorted_top_sell_orders, max_tops, " sells **")

    return results_string


async def get_market_file_orders(file_name, message):
    """ Gets all orders for the chosen array of items

    Returns all orders (buy/sell) from warframe.market in string format

    Parameters
    ----------
    file_name : str
        File name of the file which contains warframe market item names

    message : discord_message
        Discord message for visual output of ongoing process

    Returns
    -------
    results_string : str
        All orders concatenated in one string:
        player_name sells/buys item_name for amount_of_platinum

    """

    max_tops = 10
    items = []
    top_buy_orders = []
    top_sell_orders = []
    results_string = ""

    offerings_file = open("Warframe/Syndicates/" + file_name, "r")
    for line in offerings_file:
        items.append(line.rstrip())

    print("")
    print("")
    syndicateofferingsmessage = await message.channel.send(
        "Getting syndicate offerings for " + str(file_name)[10:-4].capitalize() + "...")

    for Item in items:
        await syndicateofferingsmessage.edit(
            content="(" + str(items.index(Item) + 1) +
                    "/" + str(len(items)) +
                    ") Getting orders for " + str(Item) + "...")
        await asyncio.sleep(0.1)
        embed, buys, sells = await get_market_orders(Item)
        print(str((items.index(Item)) + 1) + "/" + str(len(items)) + " " + Item)
        for i in range(len(buys[0])):
            top_buy_orders.append((buys[0][i][0], buys[0][i][1][0], buys[0][i][1][1], buys[1]))
        for i in range(len(sells[0])):
            top_sell_orders.append((sells[0][i][0], sells[0][i][1][0], sells[0][i][1][1], sells[1]))

    await delete_message_after_delay(syndicateofferingsmessage, 0.2)

    sorted_top_buy_orders = sorted(top_buy_orders, key=lambda x: x[1], reverse=True)
    sorted_top_sell_orders = sorted(top_sell_orders, key=lambda x: x[1])

    results_string += await add_each_to_string(sorted_top_buy_orders, max_tops, " buys **")

    results_string += "\n"

    results_string += await add_each_to_string(sorted_top_sell_orders, max_tops, " sells **")

    return results_string


async def add_each_to_string(dictionary, max_tops, buys_or_sells):
    """Concatenation function for the market orders functions

    Concatenates player name, buy/sell, item name, rank and price strings together

    Parameters
    ----------
    dictionary : list
        Orders for the earlier requested items in market orders functions

    max_tops : int
        Amount of best sell and buy orders (each) to save in the result string

    buys_or_sells : str
        Middle informational text to output between variables in the result string (usually "buys" or "sells")

    Returns
    -------
    results_string : str
        Resulting string of player name, buy/sell, item name, rank and price strings

    """
    results_string = ""
    if len(dictionary) > max_tops:
        for i in range(max_tops):
            results_string += dictionary[i][0] + buys_or_sells + str(dictionary[i][3]) + "** (Rank: " + str(
                dictionary[i][2]) + ") for **" + str(dictionary[i][1]) + "**\n"
    else:
        for i in range(len(dictionary)):
            results_string += dictionary[i][0] + buys_or_sells + str(dictionary[i][3]) + "** (Rank: " + str(
                dictionary[i][2]) + ") for **" + str(dictionary[i][1]) + "**\n"
    return results_string


async def add_each_to_string_chat(dictionary, max_tops):
    """Concatenation function for the market orders functions

    Concatenates player name, buy/sell, item name, rank and price strings together

    Parameters
    ----------
    dictionary : list
        Orders for the earlier requested items in market orders functions

    max_tops : int
        Amount of best sell and buy orders (each) to save in the result string

    Returns
    -------
    results_string : str
        Resulting string of player name, buy/sell, item name, rank and price strings

    """
    results_string = ""
    if len(dictionary) > max_tops:
        for i in range(max_tops):
            if dictionary[i][2] > 0:
                results_string += "/w " + dictionary[i][0] + " Hello, I am selling [" + str(
                    dictionary[i][3]).replace('_', ' ').title() + "] (Rank: " + str(
                    dictionary[i][2]) + ") for " + str(dictionary[i][1]) + " :platinum:\n"
            else:
                results_string += "/w " + dictionary[i][0] + " Hello, I am selling [" + str(
                    dictionary[i][3]).replace('_', ' ').title() + "] for " + str(
                    dictionary[i][1]) + " :platinum:\n"
    else:
        for i in range(len(dictionary)):
            if dictionary[i][2] > 0:
                results_string += "/w " + dictionary[i][0] + " Hello, I am selling [" + str(
                    dictionary[i][3]).replace('_', ' ').title() + "] (Rank: " + str(
                    dictionary[i][2]) + ") for " + str(dictionary[i][1]) + " :platinum:\n"
            else:
                results_string += "/w " + dictionary[i][0] + " Hello, I am selling [" + str(
                    dictionary[i][3]).replace('_', ' ').title() + "] for " + str(
                    dictionary[i][1]) + " :platinum:\n"
    return results_string


async def delete_message_after_delay(message, delay):
    """Deletes discord `message` after `delay` seconds

    Function to delete selected message after specific time

    Parameters
    ----------
    message : discord_message
        Discord message to delete

    delay : float
        Delay after which message will be deleted

    """
    await asyncio.sleep(delay)
    await message.delete()


async def get_baro(message):
    """Gets time left until Void Trader Baro arrives and his arrival location

        Parameters
        ----------
        message : discord.message
            Non-optional. User's sent command message.

        Warning
        -------
            Not passing a discord message will result in error.
        """

    result_string = ""
    req = requests.get('https://api.warframestat.us/pc/voidTrader')
    content = req.content
    void_trader_data = json.loads(content)
    result_string += "Void Trader arrives to " + void_trader_data["location"] + " in " \
                     + void_trader_data["startString"]
    await delete_message_after_delay(message, 0.5)
    await delete_message_after_delay(await message.channel.send(result_string), 30)


async def get_cycles(message):
    """Gets the information about remaining time on the Plains Of Eidolon, Orb Vallis and Cambion Drift

            Parameters
            ----------
            message : discord.message
                Non-optional. User's sent command message.

            Warning
            -------
                Not passing a discord message will result in error.
            """

    result_string = ""
    req = requests.get('https://api.warframestat.us/pc/cetusCycle')
    content = req.content
    cetus_data = json.loads(content)
    try:

        if cetus_data["state"] == "day" or cetus_data["state"] == "night":
            result_string += "Cetus: " + cetus_data["state"].capitalize() + " (" + cetus_data[
                "shortString"] + ")\n\n"
        else:
            result_string += "Cetus Cycle Error."

        req = requests.get('https://api.warframestat.us/pc/vallisCycle')
        content = req.content
        vallis_data = json.loads(content)
        if vallis_data["state"] == "cold" or vallis_data["state"] == "warm":
            result_string += "Orb Vallis: " + vallis_data["state"].capitalize() + " (" + vallis_data[
                "shortString"] + ")\n\n"
        else:
            result_string += "Orb Vallis Cycle Error."

        req = requests.get('https://api.warframestat.us/pc/cambionCycle')
        content = req.content
        cambion_data = json.loads(content)
        if cambion_data["active"] == "fass":
            result_string += "Cambion Drift: " + cambion_data["active"].capitalize() + " (" + \
                             cambion_data["timeLeft"] + " to Vome)"
        elif cambion_data["active"] == "vome":
            result_string += "Cambion Drift: " + cambion_data["active"].capitalize() + " (" + \
                             cambion_data["timeLeft"] + " to Fass)"
        else:
            result_string += "Cambion Drift Cycle Error."
    except:
        result_string = "Something went wrong on Warframestat.us. Try again in a few moments."

    await delete_message_after_delay(message, 0.5)
    await delete_message_after_delay(await message.channel.send(result_string), 10)


async def get_invasions(message):
    """Gets the information about invasions (rewards, completion% and location)

                Parameters
                ----------
                message : discord.message
                    Non-optional. User's sent command message.

                Warning
                -------
                    Not passing a discord message will result in error.
                """

    req = requests.get('https://api.warframestat.us/pc/invasions')
    content = req.content
    rewards_string = ""
    outer_list = json.loads(content)
    for Item in outer_list:
        if not Item["completed"]:
            rewards_string += str(Item["node"]) + "  " + str(round(Item["completion"], 1)) + "%\n"
            try:
                reward_data = Item["attackerReward"]["countedItems"][0]
                if reward_data["count"] > 1:
                    rewards_string += str(reward_data["count"]) + " x " + str(reward_data["key"])
                else:
                    rewards_string += str(reward_data["key"])

                    reward_data = Item["defenderReward"]["countedItems"][0]
                    rewards_string += " and "

                if reward_data["count"] > 1:
                    rewards_string += str(reward_data["count"]) + " x " + str(reward_data["key"])
                else:
                    rewards_string += str(reward_data["key"])
                rewards_string += "\n"

            except:
                reward_data = Item["defenderReward"]["countedItems"][0]
                if reward_data["count"] > 1:
                    rewards_string += str(reward_data["count"]) + " x " + str(reward_data["key"])
                else:
                    rewards_string += str(reward_data["key"])
                rewards_string += "\n"
            rewards_string += "\n"

    if "Orokin Reactor Blueprint" in rewards_string or "Orokin Catalyst Blueprint" in rewards_string:
        message.channel.send("<@&749224566022471690>" + " Orokin stuff detected.")

    await delete_message_after_delay(message, 0.5)
    await delete_message_after_delay(await message.channel.send(rewards_string), 30)


def sort_relic_rewards_by_rarity(relic):
    if len(relic) < 6:
        print("Invalid Relic (Need 6 elements. Found " + str(len(relic)) + ")")
    else:
        sorted_relic = relic
        for i_percent in range(6):
            sorted_relic[i_percent][1] = float(sorted_relic[i_percent][1][:-1])
        sorted_relic.sort(key=lambda x: x[1], reverse=True)
        return sorted_relic


def normalize_relic_rarity_string(relic_reward):
    rarity_string = str(relic_reward[1])
    rarity_string = rarity_string.replace("Common", '')
    rarity_string = rarity_string.replace("Uncommon", '')
    rarity_string = rarity_string.replace("Rare", '')
    rarity_string = rarity_string.replace("(", '')
    rarity_string = rarity_string.replace(")", '')
    rarity_string = rarity_string.replace(" ", '')
    normalized_relic_rarity = [relic_reward[0], rarity_string]
    return normalized_relic_rarity


def normalize_relic_name_string(relic_name_str):
    name_string = relic_name_str
    name_string = name_string.replace(" (Intact)", '')
    name_string = name_string.replace("]", '')
    name_string = name_string.replace("[", '')
    name_string = name_string.replace("'", '')
    return name_string


def parse_relic_rewards_table():
    current_relic_rewards = []
    relic_rewards_list = []
    tree = lxml.html.parse("Warframe/Warframe PC Drops.html")
    for elem in tree.xpath("body/table[2]/tbody/*"):
        if len(elem.xpath("th/text()")) > 0 and "(Intact)" in str(elem.xpath("th/text()")):
            counter = list(tree.xpath("body/table[2]/tbody/*")).index(elem)
            current_relic_rewards.clear()
            for i in range(6):
                reward_element = list(tree.xpath("body/table[2]/tbody/*"))[counter + i + 1]
                reward_text = reward_element.xpath("td/text()")
                normalized_reward_text = normalize_relic_rarity_string(reward_text)
                current_relic_rewards.append(normalized_reward_text)
            sorted_relic_rewards = list(sort_relic_rewards_by_rarity(current_relic_rewards))
            relic_name = normalize_relic_name_string(str(elem.xpath("th/text()")))
            sorted_relic_rewards.insert(0, relic_name)
            relic_rewards_list.append(sorted_relic_rewards)
    return relic_rewards_list


def find_reward_relics(reward_name, relic_rewards_db):
    result_str = ""
    for relic in relic_rewards_db:
        for relic_rewards in relic[1:]:
            if reward_name in relic_rewards[0]:
                print(str(relic[0]) + " (" + str(relic_rewards[0]).replace(' Blueprint', '') + ")")
                result_str = result_str + str(relic[0]) + " (" + str(relic_rewards[0]).replace(' Blueprint', '') + ")\n"
    return result_str
