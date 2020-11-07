import os  # For Bot initialization
import requests  # For REST API requests
import discord  # Discord bot commands
import json  # For json parsing
import asyncio  # Sleep function
import sys  # Exception catching
from dotenv import load_dotenv # Environment use

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()

# GENERAL#
async def DeleteMessageAfterDelay(message, delay):
    await asyncio.sleep(delay)
    await message.delete()

# WARFRAME#
async def GetMarketOrders(request):
    Req = requests.get('https://api.warframe.market/v1/items/' + request + '/orders')
    Content = Req.content
    if Req.status_code != 404:
        try:
            RawData = json.loads(Content)
            DataPayload = RawData["payload"]
            Orders = DataPayload["orders"]
            Embed = discord.Embed(title=request, color=0x000475)
            BuyOrders = {}
            SellOrders = {}
            BuyString = ""
            SellString = ""
            MaxOrders = 5
            nickname = ""
            price = 0
            type = ""
            for Order in Orders:
                try:
                    if Order["user"]["status"] == "ingame":
                        nickname = Order["user"]["ingame_name"]
                        price = Order["platinum"]
                        type = Order["order_type"]
                        if type == "buy":
                            if nickname in BuyOrders:
                                if price > BuyOrders[nickname]:
                                    BuyOrders[nickname] = price
                            else:
                                BuyOrders[nickname] = price
                        elif type == "sell":
                            if nickname in SellOrders:
                                if price > SellOrders[nickname]:
                                    SellOrders[nickname] = price
                            else:
                                SellOrders[nickname] = price
                except:
                    print("Error: ", Order)

            SortedBuyOrders = sorted(BuyOrders.items(), key=lambda x: x[1], reverse=True)
            SortedSellOrders = sorted(SellOrders.items(), key=lambda x: x[1])

            if len(SortedBuyOrders) > MaxOrders:
                BuyOrdersAmount = MaxOrders
            else:
                BuyOrdersAmount = len(SortedBuyOrders)

            if len(SortedSellOrders) > MaxOrders:
                SellOrdersAmount = MaxOrders
            else:
                SellOrdersAmount = len(SortedSellOrders)

            MaxOrdersAmount = 0
            if BuyOrdersAmount > SellOrdersAmount:
                MaxOrdersAmount = BuyOrdersAmount
            else:
                MaxOrdersAmount = SellOrdersAmount

            for i in range(MaxOrdersAmount):
                if BuyOrdersAmount > i:
                    BuyString += "**" + str(int(SortedBuyOrders[i][1])) + "** " + str(SortedBuyOrders[i][0]) + "\n\n"

                if SellOrdersAmount > i:
                    SellString += "**" + str(int(SortedSellOrders[i][1])) + "**  " + str(
                        SortedSellOrders[i][0]) + "\n\n"

            Embed.add_field(name="**Buys**", value=BuyString, inline=True)
            Embed.add_field(name="**Sells**", value=SellString, inline=True)
            return (Embed, (SortedBuyOrders, request), (SortedSellOrders, request))
        except:
            print("Caught Error in: ", request)

    Embed = discord.Embed(title=request, color=0x000475)
    return (Embed, (0, "0"), (0, "0"))


async def GetMarketSyndicateWeapons(fileName):
    MaxTops = 4
    Items = []
    TopBuyOrders = []
    TopSellOrders = []
    ResultsString = ""

    weaponsFile = open("Warframe/" + fileName, "r")
    for line in weaponsFile:
        Items.append(line.rstrip())

    for Item in Items:
        Embed, Buys, Sells = await GetMarketOrders(Item)
        for i in range(len(Buys[0])):
            TopBuyOrders.append((Buys[0][i][0], Buys[0][i][1], Buys[1]))
        for i in range(len(Sells[0])):
            TopSellOrders.append((Sells[0][i][0], Sells[0][i][1], Sells[1]))

    SortedTopBuyOrders = sorted(TopBuyOrders, key=lambda x: x[1], reverse=True)
    SortedTopSellOrders = sorted(TopSellOrders, key=lambda x: x[1])

    ResultsString = await AddEachToString(SortedTopBuyOrders, MaxTops, " buys for **", "**  (", ResultsString)

    ResultsString += "\n"

    ResultsString = await AddEachToString(SortedTopSellOrders, MaxTops, " sells for **", "**  (", ResultsString)

    return ResultsString


async def GetMarketSyndicateOfferings(fileName):
    MaxTops = 10
    Items = []
    TopBuyOrders = []
    TopSellOrders = []
    ResultsString = ""

    offeringsFile = open("Warframe/" + fileName, "r")
    for line in offeringsFile:
        Items.append(line.rstrip())

    print("")
    print("")
    for Item in Items:
        await asyncio.sleep(0.1)
        Embed, Buys, Sells = await GetMarketOrders(Item)
        print(Item)
        for i in range(len(Buys[0])):
            TopBuyOrders.append((Buys[0][i][0], Buys[0][i][1], Buys[1]))
        for i in range(len(Sells[0])):
            TopSellOrders.append((Sells[0][i][0], Sells[0][i][1], Sells[1]))

    print(ResultsString)

    SortedTopBuyOrders = sorted(TopBuyOrders, key=lambda x: x[1], reverse=True)
    SortedTopSellOrders = sorted(TopSellOrders, key=lambda x: x[1])

    ResultsString = await AddEachToString(SortedTopBuyOrders, MaxTops, " buys for **", "**  (", ResultsString)

    ResultsString += "\n"

    ResultsString = await AddEachToString(SortedTopSellOrders, MaxTops, " sells for **", "**  (", ResultsString)

    return ResultsString


async def AddEachToString(Dictionary, MaxTops, Text1, Text2, ResultsString):
    if len(Dictionary) > MaxTops:
        for i in range(MaxTops):
            ResultsString += Dictionary[i][0] + Text1 + str(int(Dictionary[i][1])) + Text2 + Dictionary[i][2] + ")\n"
    else:
        for i in range(len(Dictionary)):
            ResultsString += Dictionary[i][0] + Text1 + str(int(Dictionary[i][1])) + Text2 + Dictionary[i][2] + ")\n"
    return ResultsString



@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print("")


@client.event
async def on_message(message):

    if len(message.content.split()) > 1:

        if message.content.split()[0] == "bot":
            if message.content.split()[1] == "help":
                await DeleteMessageAfterDelay(message, 0.5)
                await DeleteMessageAfterDelay(await message.channel.send(
                    "General:\n"
                    "  bot help : Get all available bot commands\n"
                    "\n"
                    "Warframe:\n"
                    "  wf invasions : Get Invasions Data \n"
                    "  wf cycles : Get World Cycles Data \n"
                    "  wf syndicate:\n"
                    "      <syndicate> weapons: Get <syndicate> Weapons Buy/Sell Orders from Warframe Market \n"
                    "      <syndicate> offerings: Get <syndicate> Augments and Arch parts Buy/Sell Orders from Warframe Market \n"
                    "  wf market <weapon> : Get Weapon Buy/Sell Orders from Warframe Market\n"), 30)
            else:
                await DeleteMessageAfterDelay(await message.channel.send("No such Bot Command.\n"
                                                                         "Use bot help for available commands."), 5)

        elif message.content.split()[0] == "wf":

            if message.content.split()[1] == "invasions":
                Req = requests.get('https://api.warframestat.us/pc/invasions')
                Content = Req.content
                RewardsList = []
                RewardsString = ""
                Reward = " "
                OuterList = json.loads(Content)
                for Item in OuterList:
                    if Item["completed"] == False:
                        RewardsString += str(Item["node"]) + "  " + str(round(Item["completion"], 1)) + "% completed\n"
                        try:
                            RewardData = Item["attackerReward"]["countedItems"][0]
                            if RewardData["count"] > 1:
                                RewardsString += str(RewardData["count"]) + " x " + str(RewardData["key"])
                            else:
                                RewardsString += str(RewardData["key"])

                            RewardData = Item["defenderReward"]["countedItems"][0]
                            RewardsString += " and "

                            if RewardData["count"] > 1:
                                RewardsString += str(RewardData["count"]) + " x " + str(RewardData["key"])
                            else:
                                RewardsString += str(RewardData["key"])

                            RewardsString += "\n"

                        except:
                            RewardData = Item["defenderReward"]["countedItems"][0]
                            if RewardData["count"] > 1:
                                RewardsString += str(RewardData["count"]) + " x " + str(RewardData["key"])
                            else:
                                RewardsString += str(RewardData["key"])
                            RewardsString += "\n"
                        RewardsString += "\n"

                await DeleteMessageAfterDelay(message, 0.5)
                await DeleteMessageAfterDelay(await message.channel.send(RewardsString), 60)

            elif message.content.split()[1] == "cycles":
                ResultString = ""
                Req = requests.get('https://api.warframestat.us/pc/cetusCycle')
                Content = Req.content
                CetusData = json.loads(Content)
                if CetusData["state"] == "day" or CetusData["state"] == "night":
                    ResultString += "Cetus: " + CetusData["state"].capitalize() + " (" + CetusData[
                        "shortString"] + ")\n\n"
                else:
                    ResultString += "Cetus Cycle Error."

                Req = requests.get('https://api.warframestat.us/pc/vallisCycle')
                Content = Req.content
                VallisData = json.loads(Content)
                if VallisData["state"] == "cold" or VallisData["state"] == "warm":
                    ResultString += "Orb Vallis: " + VallisData["state"].capitalize() + " (" + VallisData[
                        "shortString"] + ")\n\n"
                else:
                    ResultString += "Orb Vallis Cycle Error."

                Req = requests.get('https://api.warframestat.us/pc/cambionCycle')
                Content = Req.content
                CambionData = json.loads(Content)
                if CambionData["active"] == "fass":
                    ResultString += "Cambion Drift: " + CambionData["active"].capitalize() + " (??m to Vome)"
                elif CambionData["active"] == "vome":
                    ResultString += "Cambion Drift: " + CambionData["active"].capitalize() + " (??m to Fass)"
                else:
                    ResultString += "Cambion Drift Cycle Error."

                await DeleteMessageAfterDelay(message, 0.5)
                await DeleteMessageAfterDelay(await message.channel.send(ResultString), 10)

            elif message.content.split()[1] == "syndicate":
                Syndicates = ["meridian", "arbiters", "suda", "perrin", "veil", "loka"]
                if len(message.content.split()) > 2:
                    if (message.content.split()[2] in Syndicates) and (len(message.content.split()) > 3):

                        if message.content.split()[3] == "weapons":
                            ResultsString = await GetMarketSyndicateWeapons("weapons_" + message.content.split()[2] + ".txt")
                            await DeleteMessageAfterDelay(message, 0.5)
                            await DeleteMessageAfterDelay(await message.channel.send(ResultsString), 120)
                        elif message.content.split()[3] == "offerings":
                            ResultsString = await GetMarketSyndicateOfferings("offerings_" + message.content.split()[2] + ".txt")
                            await DeleteMessageAfterDelay(message, 0.5)
                            await DeleteMessageAfterDelay(await message.channel.send(ResultsString), 120)
                        else:
                            await DeleteMessageAfterDelay(message, 5)
                            await DeleteMessageAfterDelay(await message.channel.send("No such Warframe command.\nCheck bot help for available commands"), 5)
                    else:
                        await DeleteMessageAfterDelay(message, 0.5)
                        await DeleteMessageAfterDelay(await message.channel.send("No such Syndicate"), 10)
                else:
                    await DeleteMessageAfterDelay(message, 0.5)
                    await DeleteMessageAfterDelay(
                        await message.channel.send("Wrong input. use wf syndicate <syndicate> <action> format."), 10)

            elif message.content.split()[1] == "market":
                if len(message.content.split()) > 2:
                    await DeleteMessageAfterDelay(message, 0.5)
                    try:
                        Embed, Buys, Sells = await GetMarketOrders(message.content.split()[2])
                        await DeleteMessageAfterDelay(await message.channel.send(embed=Embed), 60)
                    except:
                        await DeleteMessageAfterDelay(await message.channel.send(str(sys.exc_info()) + " Error!"), 10)
                else:
                    await DeleteMessageAfterDelay(
                        await message.channel.send("Error! Please use format: wf market <item>"), 10)

            else:
                await DeleteMessageAfterDelay(await message.channel.send("No such Warframe command.\n"
                                                                         "Check bot help for available commands"), 5)


client.run(TOKEN)
