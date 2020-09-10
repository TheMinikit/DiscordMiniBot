import os
import requests
import discord
import json
import pytesseract
import ffmpeg
import asyncio
from PIL import Image
#from html.parser import HTMLParser
TOKEN = 'NjUzODk0NDMwNTM2NzYxMzQ0.Xe9opQ.XxkhQLgmzI_-GnNLbCyNrkZKoZg'

client = discord.Client()
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\TesseractOCR\\tesseract.exe'


#TO-DO LIST#
#Fix Heroku Crash
#Parse TerrariaWiki HTML Data
#
#
#

#WARFRAME#
async def GetMarketPerrinWeapons():
    MaxTops = 4
    TopBuyOrders = []
    TopSellOrders = []
    ResultsString = ""

    Embed, ReturnString, Buys, Sells = await GetMarketOrders("secura_dual_cestra")
    ResultsString += ReturnString
    for i in range(len(Buys[0])):
        TopBuyOrders.append((Buys[0][i][0], Buys[0][i][1], Buys[1]))
    for i in range(len(Sells[0])):
        TopSellOrders.append((Sells[0][i][0], Sells[0][i][1], Sells[1]))

    Embed, ReturnString, Buys, Sells = await GetMarketOrders("secura_lecta")
    ResultsString += ReturnString
    for i in range(len(Buys[0])):
        TopBuyOrders.append((Buys[0][i][0], Buys[0][i][1], Buys[1]))
    for i in range(len(Sells[0])):
        TopSellOrders.append((Sells[0][i][0], Sells[0][i][1], Sells[1]))

    Embed, ReturnString, Buys, Sells = await GetMarketOrders("secura_penta")
    ResultsString += ReturnString
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
            ResultsString += SortedTopSellOrders[i][0] + " sells for **" + str(int(SortedTopSellOrders[i][1])) + "**  (" + \
                                 SortedTopSellOrders[i][2] + ")\n"
    else:
        for i in range(len(SortedSellOrders)):
            ResultsString += SortedTopSellOrders[i][0] + " sells for **" + str(int(SortedTopSellOrders[i][1])) + "**  (" + \
                                 SortedTopSellOrders[i][2] + ")\n"

    return ResultsString


async def GetMarketOrders(request):
    Req = requests.get('https://api.warframe.market/v1/items/' + request + '/orders')
    Content = Req.content
    if Req.status_code != 404:
        RawData = json.loads(Content)
        DataPayload = RawData["payload"]
        Orders = DataPayload["orders"]
        Embed = discord.Embed(title=request, color=0x000475)
        ResultString = ""
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
                SellString += "**" + str(int(SortedSellOrders[i][1])) + "**  " + str(SortedSellOrders[i][0]) + "\n\n"

        Embed.add_field(name="**Buys**", value=BuyString, inline=True)
        Embed.add_field(name="**Sells**", value=SellString, inline=True)
        return (Embed, ResultString, (SortedBuyOrders, request), (SortedSellOrders, request))
    Embed = discord.Embed(title=request, color=0x000475)
    return (Embed, "0", (0,"0"), (0,"0"))

#TERRARIA#
async def ScreenshotAndSound(message, oldString):
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save("one.png")
    img = Image.open("one.png")
    #newImg = img.crop((0,696,200,715))
    newImg = img.crop((0,696,200,710))
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
            await print("Ready")
            return oldString
        except:
            print("Error")
    return oldString


#@bot.command(name="dum")
async def PlaySound(message, soundfile):
    voice_channel = message.author.voice.channel
    channel = None
    #print(client.voice_clients)
    if voice_channel != None:
        channel = voice_channel.name
        vc = await voice_channel.connect()
        vc.play(discord.FFmpegPCMAudio(executable="C:/Users/XPS/Desktop/Discord/Python/ffmpeg/bin/ffmpeg.exe", source="C:/Users/XPS/Desktop/Discord/Python/Sounds/" + soundfile + ".wav"))
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
    if message.content == "wf invasions":
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
            Role = client.guild.roles.mention('name', 'Warframe')
            message.channel.send(Role.mention() + " Orokin stuff detected.")


        await message.channel.send(RewardsString)

    if message.content == "wf cycles":
        ResultString = ""

        Req = requests.get('https://api.warframestat.us/pc/cetusCycle')
        Content = Req.content
        CetusData = json.loads(Content)
        if CetusData["state"] == "day" or CetusData["state"] == "night":
            ResultString += "Cetus: " + CetusData["state"].capitalize() + " (" + CetusData["shortString"] + ")\n\n"
        else:
            ResultString += "Cetus Cycle Error."

        Req = requests.get('https://api.warframestat.us/pc/vallisCycle')
        Content = Req.content
        VallisData = json.loads(Content)
        if VallisData["state"] == "cold" or VallisData["state"] == "warm":
            ResultString += "Orb Vallis: " + VallisData["state"].capitalize() + " (" + VallisData["shortString"] + ")\n\n"
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

        await message.channel.send(ResultString)


    if message.content == "wf perrin":
        ResultsString = await GetMarketPerrinWeapons()
        await message.channel.send(ResultsString)


    if message.content == "TERRARIA":
        oldString = ""
        while(True):
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
        #ParsedData = HTMLParser.feed(ParseData)
        print(ParsedData)
        await message.delete()


    if message.content == "bot help":
        await message.channel.send("General:\n"
                                   "bot help : Get all available bot commands\n"
                                   "\n"
                                   "Warframe:\n"
                                   "wf invasions : Get Invasions Data \n"
                                   "wf cycles : Get World Cycles Data \n"
                                   "wf perrin : Get Perrin Sequence Weapons Buy/Sell Orders from Warframe Market \n"
                                   "wf market <weapon> : Get Weapon Buy/Sell Orders from Warframe Market\n"
                                   "\n"
                                   "Local Use Only:\n"
                                   "p list : Get all available sounds to play\n"
                                   "p <sound> : Play sound in your voice channel")


    if len(message.content.split()) > 1:

        if message.content.split()[0] == "p":
            if message.content.split()[1] == "list":
                FileList = os.listdir("C:/Users/XPS/Desktop/Discord/Python/Sounds")
                FileListString = ""
                for File in FileList:
                    FileListString += File + "\n"
                await message.channel.send(FileListString)
            else:
                soundfile = message.content.split()[1]
                await PlaySound(message, soundfile)


    if len(message.content.split()) > 2:

        if message.content.split()[0] == "wf" and message.content.split()[1] == "market":
            try:
                Embed, ReturnString, Buys, Sells = await GetMarketOrders(message.content.split()[2])
                if ReturnString != "0":
                    await message.channel.send(embed=Embed)
            except:
                await message.channel.send("Error!")



client.run(TOKEN)
