import os  # For Bot initialization
import requests  # For REST API requests
import discord  # Discord bot commands
import json  # For json parsing
import pytesseract  # For Image analysis
import ffmpeg  # Sounds and videos
import asyncio  # Sleep function
import pyautogui  # Automation
import sys  # Exception catching
from PIL import Image  # For Image analysis

# from html.parser import HTMLParser
TOKEN = 'NjUzODk0NDMwNTM2NzYxMzQ0.Xe9opQ.XxkhQLgmzI_-GnNLbCyNrkZKoZg'

client = discord.Client()
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\TesseractOCR\\tesseract.exe'


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

    weaponsFile = open(fileName, "r")
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

    if len(SortedTopBuyOrders) > MaxTops:
        for i in range(MaxTops):
            ResultsString += SortedTopBuyOrders[i][0] + " buys for **" + str(int(SortedTopBuyOrders[i][1])) + "**  (" + \
                             SortedTopBuyOrders[i][2] + ")\n"
    else:
        for i in range(len(SortedTopBuyOrders)):
            ResultsString += SortedTopBuyOrders[i][0] + " buys for **" + str(int(SortedTopBuyOrders[i][1])) + "**  (" + \
                             SortedTopBuyOrders[i][2] + ")\n"

    ResultsString += "\n"

    if len(SortedTopSellOrders) > MaxTops:
        for i in range(MaxTops):
            ResultsString += SortedTopSellOrders[i][0] + " sells for **" + str(
                int(SortedTopSellOrders[i][1])) + "**  (" + \
                             SortedTopSellOrders[i][2] + ")\n"
    else:
        for i in range(len(SortedTopSellOrders)):
            ResultsString += SortedTopSellOrders[i][0] + " sells for **" + str(
                int(SortedTopSellOrders[i][1])) + "**  (" + \
                             SortedTopSellOrders[i][2] + ")\n"

    return ResultsString


async def GetMarketSyndicateOfferings(fileName):
    MaxTops = 10
    Items = []
    TopBuyOrders = []
    TopSellOrders = []
    ResultsString = ""

    offeringsFile = open(fileName, "r")
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

    ResultsString = await AddEachToString(SortedTopBuyOrders, MaxTops, " sell for **", "**  (", ResultsString)

    ResultsString += "\n"

    ResultsString = await AddEachToString(SortedTopSellOrders, MaxTops, " sell for **", "**  (", ResultsString)

    return ResultsString


async def AddEachToString(Dictionary, MaxTops, Text1, Text2, ResultsString):
    if len(Dictionary) > MaxTops:
        for i in range(MaxTops):
            ResultsString += Dictionary[i][0] + Text1 + str(int(Dictionary[i][1])) + Text2 + Dictionary[i][2] + ")\n"
    else:
        for i in range(len(Dictionary)):
            ResultsString += Dictionary[i][0] + Text1 + str(int(Dictionary[i][1])) + Text2 + Dictionary[i][2] + ")\n"
    return ResultsString


# TERRARIA#
async def ScreenshotAndSound(message, oldString):
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save("one.png")
    img = Image.open("one.png")
    # newImg = img.crop((0,696,200,715))
    newImg = img.crop((0, 696, 200, 710))
    newImg.save("two.png")
    ScreenshotString = pytesseract.image_to_string(newImg)
    ScreenshotString = ScreenshotString[:-1]
    if oldString != ScreenshotString and "<" in ScreenshotString and ">" in ScreenshotString:
        try:
            print("ScreenshotString", ScreenshotString)
            soundfile = ScreenshotString.split()[-1]
            oldString = ScreenshotString
            await PlaySound(message, soundfile)
            await asyncio.sleep(5)
            # await print("Ready")
            return oldString
        except:
            print("Error")
    return oldString


# @bot.command(name="dum")
async def PlaySound(message, soundfile):
    voice_channel = message.author.voice.channel
    channel = None
    # print(client.voice_clients)
    if voice_channel != None:
        channel = voice_channel.name
        vc = await voice_channel.connect()
        vc.play(discord.FFmpegPCMAudio(executable="C:/Users/XPS/Desktop/Discord/Python/ffmpeg/bin/ffmpeg.exe",
                                       source="C:/Users/XPS/Desktop/Discord/Python/Sounds/" + soundfile + ".wav"))
        while vc.is_playing():
            await asyncio.sleep(.5)
        await vc.disconnect()
    else:
        await message.channel.send(str(message.author.name) + "is not in a channel.")
    await message.delete()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print("")


@client.event
async def on_message(message):
    if message.content == "saysounds":
        oldString = ""
        while (True):
            if oldString == "<Kit> goodnightbot":
                break
            oldString = await ScreenshotAndSound(message, oldString)
            await asyncio.sleep(.25)

    if message.content == "goodnight":
        await message.delete()
        await client.logout()

    if message.content == "terra":
        Req = requests.get('https://terraria.gamepedia.com/api.php?action=parse&format=json&page=Titanium_Crate')
        Content = Req.content
        RewardsList = []
        RewardsString = ""
        Reward = " "
        PageData = json.loads(Content)
        ParseData = PageData["parse"]["text"]["*"]
        # ParsedData = HTMLParser.feed(ParseData)
        # print(ParsedData)
        await message.delete()

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
                    "  wf market <weapon> : Get Weapon Buy/Sell Orders from Warframe Market\n"
                    "\n"
                    "Local Use Only:\n"
                    "  p list : Get all available sounds to play\n"
                    "  p <sound> : Play sound in your voice channel"),
                                              30)
            else:
                await DeleteMessageAfterDelay(await message.channel.send("No such Bot Command.\n"
                                                                         "Use bot help for available commands."), 5)

        elif message.content.split()[0] == "p":
            if message.content.split()[1] == "list":
                FileList = os.listdir("C:/Users/XPS/Desktop/Discord/Python/Sounds")
                FileListString = ""
                for File in FileList:
                    FileListString += File + "\n"
                await message.channel.send(FileListString)
            else:
                soundfile = message.content.split()[1]
                await PlaySound(message, soundfile)
                await DeleteMessageAfterDelay(message, 0.5)

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
                        RewardsString += str(Item["node"]) + "  " + str(round(Item["completion"], 1)) + "%\n"
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

                if "Orokin Reactor Blueprint" in RewardsString or "Orokin Catalyst Blueprint" in RewardsString:
                    message.channel.send("<@&749224566022471690>" + " Orokin stuff detected.")

                await DeleteMessageAfterDelay(message, 0.5)
                await DeleteMessageAfterDelay(await message.channel.send(RewardsString), 30)

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
