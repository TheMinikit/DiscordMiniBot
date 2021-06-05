import os  # For Bot initialization
import requests  # For REST API requests
import discord  # Discord bot commands
import json  # For json parsing
import pytesseract  # For Image analysis
# import ffmpeg  # Sounds and videos
import asyncio  # Sleep function
import pyautogui  # Automation
import sys  # Exception catching
import pandas  # Excel output
from PIL import Image  # For Image analysis
from dotenv import load_dotenv
# from html.parser import HTMLParser

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

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
            rank = -1
            for Order in Orders:
                try:
                    if Order["user"]["status"] == "ingame":
                        nickname = Order["user"]["ingame_name"]
                        price = int(Order["platinum"])

                        try:
                            rank = Order["mod_rank"]
                        except:
                            rank = -1
                        type = Order["order_type"]
                        if type == "buy":
                            if nickname in BuyOrders:
                                if price > BuyOrders[nickname][0]:
                                    BuyOrders[nickname] = (price, rank)
                            else:
                                BuyOrders[nickname] = (price, rank)
                        elif type == "sell":
                            if nickname in SellOrders:
                                if price > SellOrders[nickname][0]:
                                    SellOrders[nickname] = (price, rank)
                            else:
                                SellOrders[nickname] = (price, rank)
                except:
                    print(str(sys.exc_info()), "\nParsing Error: ", Order)

            SortedBuyOrders = sorted(BuyOrders.items(), key=lambda x: x[1][0], reverse=True)
            SortedSellOrders = sorted(SellOrders.items(), key=lambda x: x[1][0])

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
                    BuyString += "**" + str(int(SortedBuyOrders[i][1][0])) + "** " + str(
                        SortedBuyOrders[i][0]) + "  (Rank " + str(SortedBuyOrders[i][1][1]) + ")\n\n"
                if SellOrdersAmount > i:
                    SellString += "**" + str(int(SortedSellOrders[i][1][0])) + "**  " + str(
                        SortedSellOrders[i][0]) + "  (Rank " + str(SortedSellOrders[i][1][1]) + ")\n\n"

            Embed.add_field(name="**Buys**", value=BuyString, inline=True)
            Embed.add_field(name="**Sells**", value=SellString, inline=True)
            return (Embed, (SortedBuyOrders, request), (SortedSellOrders, request))
        except:
            print("Caught Error in order: ", request)

    Embed = discord.Embed(title=request, color=0x000475)
    return (Embed, (0, "0"), (0, "0"))


async def GetMarketSyndicateWeapons(fileName):
    MaxTops = 4
    Items = []
    TopBuyOrders = []
    TopSellOrders = []
    ResultsString = ""

    weaponsFile = open("Warframe/Syndicates" + fileName, "r")
    for line in weaponsFile:
        Items.append(line.rstrip())

    for Item in Items:
        Embed, Buys, Sells = await GetMarketOrders(Item)

        for i in range(len(Buys[0])):
            TopBuyOrders.append((Buys[0][i][0], Buys[0][i][1][0], Buys[1]))
        for i in range(len(Sells[0])):
            TopSellOrders.append((Sells[0][i][0], Sells[0][i][1][0], Sells[1]))

    SortedTopBuyOrders = sorted(TopBuyOrders, key=lambda x: x[1][0], reverse=True)
    SortedTopSellOrders = sorted(TopSellOrders, key=lambda x: x[1][0])

    ResultsString += await AddEachToString(SortedTopBuyOrders, MaxTops, " buys for **")

    ResultsString += "\n"

    ResultsString += await AddEachToString(SortedTopSellOrders, MaxTops, " sells for **")

    return ResultsString


async def GetMarketSyndicateOfferings(fileName):
    MaxTops = 10
    Items = []
    TopBuyOrders = []
    TopSellOrders = []
    ResultsString = ""

    offeringsFile = open("Warframe/Syndicates" + fileName, "r")
    for line in offeringsFile:
        Items.append(line.rstrip())

    print("")
    print("")
    for Item in Items:
        await asyncio.sleep(0.1)
        Embed, Buys, Sells = await GetMarketOrders(Item)
        print(str((Items.index(Item)) + 1) + "/" + str(len(Items)) + " " + Item)
        for i in range(len(Buys[0])):
            TopBuyOrders.append((Buys[0][i][0], Buys[0][i][1][0], Buys[0][i][1][1], Buys[1]))
        for i in range(len(Sells[0])):
            TopSellOrders.append((Sells[0][i][0], Sells[0][i][1][0], Sells[0][i][1][1], Sells[1]))

    SortedTopBuyOrders = sorted(TopBuyOrders, key=lambda x: x[1], reverse=True)
    SortedTopSellOrders = sorted(TopSellOrders, key=lambda x: x[1])

    ResultsString += await AddEachToString(SortedTopBuyOrders, MaxTops, " buys **")

    ResultsString += "\n"

    ResultsString += await AddEachToString(SortedTopSellOrders, MaxTops, " sells **")

    return ResultsString


async def AddEachToString(Dictionary, MaxTops, Text1):
    ResultsString = ""
    if len(Dictionary) > MaxTops:
        for i in range(MaxTops):
            ResultsString += Dictionary[i][0] + Text1 + str(Dictionary[i][3]) + "** (Rank: " + str(
                Dictionary[i][2]) + ") for **" + str(Dictionary[i][1]) + "**\n"
    else:
        for i in range(len(Dictionary)):
            ResultsString += Dictionary[i][0] + Text1 + str(Dictionary[i][3]) + "** (Rank: " + str(
                Dictionary[i][2]) + ") for **" + str(Dictionary[i][1]) + "**\n"
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
                try:

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
                except:
                    ResultString = "Something went wrong on Warframestat.us. Try again in a few moments."

                await DeleteMessageAfterDelay(message, 0.5)
                await DeleteMessageAfterDelay(await message.channel.send(ResultString), 10)

            elif message.content.split()[1] == "syndicate":
                Syndicates = ["meridian", "arbiters", "suda", "perrin", "veil", "loka"]
                if len(message.content.split()) > 2:
                    if (message.content.split()[2] in Syndicates) and (len(message.content.split()) > 3):

                        if message.content.split()[3] == "weapons":
                            ResultsString = await GetMarketSyndicateWeapons(
                                "weapons_" + message.content.split()[2] + ".txt")
                            await DeleteMessageAfterDelay(message, 0.5)
                            await DeleteMessageAfterDelay(await message.channel.send(ResultsString), 120)
                        elif message.content.split()[3] == "offerings":
                            ResultsString = await GetMarketSyndicateOfferings(
                                "offerings_" + message.content.split()[2] + ".txt")
                            await DeleteMessageAfterDelay(message, 0.5)
                            await DeleteMessageAfterDelay(await message.channel.send(ResultsString), 120)
                        else:
                            await DeleteMessageAfterDelay(message, 5)
                            await DeleteMessageAfterDelay(await message.channel.send(
                                "No such Warframe command.\nCheck bot help for available commands"), 5)
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

            elif message.content.split()[1] == "primecheck":
                await DeleteMessageAfterDelay(message, 0.5)

                print("Starting Prime Check...")

                singleInventoryCellSize = 169
                singleInventorySpaceSizeX = 42
                singleInventorySpaceSizeY = 31
                inventoryOffsetX = 97
                inventoryOffsetY = 199
                xPos = inventoryOffsetX
                yPos = inventoryOffsetY

                images = []
                ImageTextData = []
                primes = {}
                dictionary = {}
                croppedImages = []

                TopSellPrice = 0
                TopSellPlayer = ""
                TopSellPriceArray = []
                TopSellPlayerArray = []
                TopBuyPrice = 0
                TopBuyPlayer = ""
                TopBuyPriceArray = []
                TopBuyPlayerArray = []

                Rlimits = [0, 40]
                Glimits = [80, 130]
                Blimits = [130, 220]

                # Orange Limits
                # R = 200 - 250
                # G = 100 - 140
                # B = 15 - 70

                # Blue Limits
                # R = 25 - 40
                # G = 79 - 130
                # B = 130 - 220

                whiteListColors = []
                whiteListColorsImages = []

                # img = Image.open("Warframe/wfprimetest5.jpg")
                # print(os.listdir("Warframe/Screenshots"))
                for imgs in os.listdir("Warframe/Screenshots"):
                    image = Image.open("Warframe/Screenshots/" + str(imgs))
                    image = image.convert('RGB')
                    images.append(image)
                primesFile = open("Warframe/primes.txt", "r")
                dictionaryFile = open("Warframe/dictionary.txt", "r")
                # newImg = img
                # newImg = newImg.convert('RGB')

                print()
                print(str(len(images)) + " screenshots to read...")

                '''
                whiteListColorsImages.append("A.png")
                whiteListColorsImages.append("B.png")
                whiteListColorsImages.append("e.png")
                whiteListColorsImages.append("l.png")
                whiteListColorsImages.append("r.png")
                whiteListColorsImages.append("P.png")
                whiteListColorsImages.append("orangetemplate.png")
                '''

                try:

                    for prime in primesFile:
                        primes[prime[:-3]] = prime[-2]

                    for word in dictionaryFile:
                        dictionary[word.split(' ')[0].strip()] = word.split(' ')[1].strip()

                    '''    
                    for image in whiteListColorsImages:
                        testImg = Image.open("Warframe/" + image)
                        for i in range(testImg.size[0]):
                            for j in range(testImg.size[1]):
                                if testImg.getpixel((i, j)) != (255, 255, 255):
                                #r, g, b = testImg.getpixel((i,j))
                                    #print(str(r) + " " + str(g) + " " + str(b))
                                    if testImg.getpixel((i, j)) not in whiteListColors:
                                        whiteListColors.append(testImg.getpixel((i, j)))

                    print("Whitelist created.(Size: " + str(len(whiteListColors)) + ")")
                    '''

                    for img in images:
                        yPos = inventoryOffsetY
                        for i in range(4):
                            xPos = inventoryOffsetX
                            for j in range(6):
                                croppedImg = img.crop(
                                    (xPos, yPos, xPos + singleInventoryCellSize, yPos + singleInventoryCellSize))
                                croppedImages.append(croppedImg)
                                croppedImg.save("Warframe/Crops/" + str(i) + " " + str(j) + ".jpg")
                                xPos += singleInventoryCellSize + singleInventorySpaceSizeX
                            yPos += singleInventoryCellSize + singleInventorySpaceSizeY

                    print()
                    print("Coloring to Black & White...")

                    counter = 0
                    for cropImage in croppedImages:
                        for i in range(cropImage.size[0]):
                            for j in range(cropImage.size[1]):
                                # if cropImage.getpixel((i,j)) in whiteListColors:
                                r, g, b = cropImage.getpixel((i, j))
                                if (Rlimits[0] <= r <= Rlimits[1]) and (Glimits[0] <= g <= Glimits[1]) and (
                                        Blimits[0] <= b <= Blimits[1]):
                                    cropImage.putpixel((i, j), (0, 0, 0))
                                else:
                                    cropImage.putpixel((i, j), (255, 255, 255))

                        cropImage.save("Warframe/Crops/" + str(counter) + ".jpg")
                        counter = counter + 1

                    print()
                    print("Reading text from cropped B&W images...")
                    print()

                    for croppedBWImage in croppedImages:
                        CroppedImgString = pytesseract.image_to_string(croppedBWImage)
                        CroppedImgString = CroppedImgString.rstrip()
                        CroppedImgString = CroppedImgString.replace(' _', '')
                        CroppedImgString = CroppedImgString.replace('4 ', '')
                        CroppedImgString = CroppedImgString.replace('\n', ' ')
                        CroppedImgString = CroppedImgString.replace('\t', ' ')
                        CroppedImgString = CroppedImgString.replace(' ', '_')
                        CroppedImgString = CroppedImgString.lower()
                        for string in CroppedImgString.split('_'):
                            if string in dictionary.keys():
                                CroppedImgString = CroppedImgString.replace(string, dictionary[string])
                        if "blueprint" in CroppedImgString.split('_'):
                            if CroppedImgString.split('_')[CroppedImgString.split('_').index("blueprint") - 1] != "prime" and CroppedImgString.split('_')[CroppedImgString.split('_').index("blueprint") - 1] != "collar":
                                CroppedImgString = CroppedImgString.replace('_blueprint', '')
                        ImageTextData.append(CroppedImgString)

                    print()
                    print("Checking for sets...")

                    repeatsNum = 0
                    repeatsName = ImageTextData[0].split('_')[0]

                    for i in range(len(ImageTextData)):
                        if ImageTextData[i].split('_')[0].capitalize() in primes:
                            if ImageTextData[i].split('_')[0] == repeatsName:
                                repeatsNum += 1
                            else:
                                if primes[repeatsName.capitalize()] == str(repeatsNum):
                                    ImageTextData.insert(i, repeatsName + "_prime_set")
                                repeatsName = ImageTextData[i].split('_')[0]
                                repeatsNum = 1

                    print()
                    print("Getting market orders...")

                    for i in range(len(ImageTextData)):
                        try:
                            print(str(i + 1) + "/" + str(len(ImageTextData)) + "  " + str(ImageTextData[i]))
                            Embed, BuysReq, SellsReq = await GetMarketOrders(ImageTextData[i])
                            await asyncio.sleep(0.3)
                            TopBuyPrice = 0
                            TopBuyPlayer = "< None >"
                            TopSellPrice = 0
                            TopSellPlayer = "< None >"
                            Buys, BRequest = BuysReq
                            for player, (price, rank) in Buys:
                                if TopBuyPrice == 0:
                                    TopBuyPrice = price
                                    TopBuyPlayer = player
                                elif price > TopBuyPrice:
                                    TopBuyPrice = price
                                    TopBuyPlayer = player

                            Sells, SRequest = SellsReq
                            for player, (price, rank) in Sells:
                                if TopSellPrice == 0:
                                    TopSellPrice = price
                                    TopSellPlayer = player
                                elif price < TopSellPrice:
                                    TopSellPrice = price
                                    TopSellPlayer = player

                            TopBuyPriceArray.append(TopBuyPrice)
                            TopBuyPlayerArray.append(TopBuyPlayer)
                            TopSellPriceArray.append(TopSellPrice)
                            TopSellPlayerArray.append(TopSellPlayer)
                        except:
                            print("Encountered Error with: " + str(ImageTextData[i]) + str(sys.exc_info()))
                            TopBuyPriceArray.append('-')
                            TopBuyPlayerArray.append('-')
                            TopSellPriceArray.append('-')
                            TopSellPlayerArray.append('-')
                    print("Done.")
                except:
                    print("Error! ", str(sys.exc_info()) + " " + str(sys.exc_info()[2].tb_lineno))

                '''
                print("PartName: " + str(len(ImageTextData)))
                print("SellPlayer: " + str(len(TopSellPlayerArray)))
                print("SellPrice: " + str(len(TopSellPriceArray)))
                print("BuyPlayer: " + str(len(TopBuyPlayerArray)))
                print("BuyPrice: " + str(len(TopBuyPriceArray)))
                '''

                df = pandas.DataFrame({'Part Name': ImageTextData, 'Selling Price': TopSellPriceArray,
                                       'Selling Player': TopSellPlayerArray, 'Buying Price': TopBuyPriceArray,
                                       'Buying Player': TopBuyPlayerArray})
                writer = pandas.ExcelWriter("PrimeResults.xlsx", engine='xlsxwriter')
                df.to_excel(writer, sheet_name="Primes")
                worksheet = writer.sheets['Primes']
                worksheet.set_column('B:B', 30)
                worksheet.set_column('C:C', 14)
                worksheet.set_column('D:D', 23)
                worksheet.set_column('E:E', 14)
                worksheet.set_column('F:F', 23)
                writer.save()

                print()
                print("Results saved in PrimeResults.xlsx.")

                await client.logout()

            else:
                await DeleteMessageAfterDelay(await message.channel.send("No such Warframe command.\n"
                                                                         "Check bot help for available commands"), 5)


client.run(TOKEN)
