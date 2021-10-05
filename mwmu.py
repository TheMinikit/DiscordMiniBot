"""Minikit's Warframe Market Utilities Module

Module that uses warframe.market's API to get useful data and parse it into a convenient way to read and understand
Includes function to get market orders for one specific items or set of items

"""

import discord
import requests
import asyncio
import json


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

    weapons_file = open("Warframe/Syndicates" + file_name, "r")
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


async def get_market_syndicate_offerings(file_name, message):
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


async def delete_message_after_delay(message, delay):
    """Deletes discord `message` after `delay`

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
