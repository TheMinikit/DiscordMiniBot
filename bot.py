import os  # Bot initialization
import io  # Converting Bytes to Zip
import sys  # Exception catching
import mwu  # Personal module for warframe utilities
import json  # Json parsing
import lxml.html  # HTML Parsing
import pandas  # Excel output
import asyncio  # Sleep function
import discord  # Discord bot commands
import zipfile  # For Zip file processing
import requests  # API requests
import pytesseract  # Image analysis
from PIL import Image  # Image analysis
from dotenv import load_dotenv  # Env module

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\TesseractOCR\\tesseract.exe'


# GENERAL #
async def DeleteMessageAfterDelay(message, delay):
    await asyncio.sleep(delay)
    await message.delete()


# PANDAS #
def pandasExcelMapWarframeFrame(x):
    if isinstance(x, int):
        if x > 20:
            return 'background-color: #95FF80'
        elif x <= 5:
            return 'background-color: #EDC374'
        else:
            return 'background-color: transparent'


def pandasExcelMapWarframeWeapon(x):
    if isinstance(x, int):
        if x > 20:
            return 'background-color: #95FF80'
        elif x <= 5:
            return 'background-color: #EDC374'
        else:
            return 'background-color: transparent'


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print("")


@client.event
async def on_message(message):
    #  Channel check. Message must come from 'bot' channel
    if message.channel.id == 865532738688647168:

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
                        "      <syndicate> offerings: Get <syndicate> Augments and Arch parts"
                        " Buy/Sell Orders from Warframe Market \n"
                        "  wf market <weapon> : Get Weapon Buy/Sell Orders from Warframe Market\n"
                        "  wf relic <item_name>: Get list of relics which contain the item\n"), 30)
                else:
                    await DeleteMessageAfterDelay(await message.channel.send("No such Bot Command.\n"
                                                                             "Use bot help for available commands."), 5)

            elif message.content.split()[0] == "wf":

                if message.content.split()[1] == "invasions":
                    Req = requests.get('https://api.warframestat.us/pc/invasions')
                    Content = Req.content
                    RewardsString = ""
                    OuterList = json.loads(Content)
                    for Item in OuterList:
                        if not Item["completed"]:
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
                                ResultsString = await mwu.get_market_syndicate_weapons(
                                    "weapons_" + message.content.split()[2] + ".txt")
                                await DeleteMessageAfterDelay(message, 0.5)
                                await DeleteMessageAfterDelay(await message.channel.send(ResultsString), 120)
                            elif message.content.split()[3] == "offerings":
                                ResultsString = await mwu.get_market_syndicate_offerings(
                                    "offerings_" + message.content.split()[2] + ".txt", message)
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
                            await message.channel.send("Wrong input. use wf syndicate <syndicate> <action> format."),
                            10)

                elif message.content.split()[1] == "market":
                    if len(message.content.split()) > 2:
                        await DeleteMessageAfterDelay(message, 0.5)
                        try:
                            Embed, Buys, Sells = await mwu.get_market_orders(message.content.split()[2])
                            await DeleteMessageAfterDelay(await message.channel.send(embed=Embed), 60)
                        except:
                            await DeleteMessageAfterDelay(await message.channel.send(str(sys.exc_info()) + " Error!"),
                                                          10)
                    else:
                        await DeleteMessageAfterDelay(
                            await message.channel.send("Error! Please use format: wf market <item>"), 10)

                elif message.content.split()[1] == "primecheck":
                    await DeleteMessageAfterDelay(message, 0.5)
                    if message.attachments:
                        att = message.attachments
                        zippedimgs = zipfile.ZipFile(io.BytesIO(requests.get(att[0].url).content), "r")
                        zippedimgs.extractall("Warframe/Screenshots")
                        primecheckmessage = await message.channel.send("Starting Prime Check...")
                        print("Starting Prime Check...")

                        single_inventory_cell_size = 169
                        single_inventory_space_size_x = 42
                        single_inventory_space_size_y = 31
                        inventory_offset_x = 97
                        inventory_offset_y = 199
                        x_pos = inventory_offset_x
                        y_pos = inventory_offset_y

                        images = []
                        ImageTextData = []
                        primes = {}
                        warframes = []
                        dictionary = {}
                        cropped_images = []

                        warframes_array = []
                        weapons_array = []

                        top_sell_price = 0
                        top_sell_player = ""
                        top_buy_price = 0
                        top_buy_player = ""

                        top_warframe_sell_price_array = []
                        top_warframe_sell_player_array = []
                        top_warframe_buy_price_array = []
                        top_warframe_buy_player_array = []

                        top_weapon_sell_price_array = []
                        top_weapon_sell_player_array = []
                        top_weapon_buy_price_array = []
                        top_weapon_buy_player_array = []

                        rlimits = [0, 40]
                        glimits = [80, 130]
                        blimits = [130, 220]

                        # Orange Limits
                        # R = 200 - 250
                        # G = 100 - 140
                        # B = 15 - 70

                        # Blue Limits
                        # R = 25 - 40
                        # G = 79 - 130
                        # B = 130 - 220

                        '''
                        whiteListColors = []
                        whiteListColorsImages = []
                        '''

                        # img = Image.open("Warframe/wfprimetest5.jpg")
                        for imgs in os.listdir("Warframe/Screenshots"):
                            image = Image.open("Warframe/Screenshots/" + str(imgs))
                            image = image.convert('RGB')
                            images.append(image)

                        primes_file = open("Warframe/primes.txt", "r")
                        dictionary_file = open("Warframe/dictionary.txt", "r")
                        warframes_file = open("Warframe/warframes.txt", "r")

                        print()
                        print(str(len(images)) + " screenshots to read...")
                        await primecheckmessage.edit(content=str(len(images)) + " screenshots to read...")

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

                            for prime in primes_file:
                                primes[prime[:-3]] = prime[-2]

                            for word in dictionary_file:
                                dictionary[word.split(' ')[0].strip()] = word.split(' ')[1].strip()

                            for warframe in warframes_file:
                                warframes.append(warframe.rstrip())

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
                                y_pos = inventory_offset_y
                                for i in range(4):
                                    x_pos = inventory_offset_x
                                    for j in range(6):
                                        cropped_img = img.crop(
                                            (x_pos, y_pos,
                                             x_pos + single_inventory_cell_size,
                                             y_pos + single_inventory_cell_size))
                                        cropped_images.append(cropped_img)
                                        cropped_img.save("Warframe/Crops/" + str(i) + " " + str(j) + ".jpg")
                                        x_pos += single_inventory_cell_size + single_inventory_space_size_x
                                    y_pos += single_inventory_cell_size + single_inventory_space_size_y

                            print()
                            print("Coloring to Black & White...")
                            await primecheckmessage.edit(content="Coloring to Black & White...")

                            counter = 0
                            for cropImage in cropped_images:
                                for i in range(cropImage.size[0]):
                                    for j in range(cropImage.size[1]):
                                        # if cropImage.getpixel((i,j)) in whiteListColors:
                                        r, g, b = cropImage.getpixel((i, j))
                                        if (rlimits[0] <= r <= rlimits[1]) and (glimits[0] <= g <= glimits[1]) and (
                                                blimits[0] <= b <= blimits[1]):
                                            cropImage.putpixel((i, j), (0, 0, 0))
                                        else:
                                            cropImage.putpixel((i, j), (255, 255, 255))

                                cropImage.save("Warframe/Crops/" + str(counter) + ".jpg")
                                counter = counter + 1

                            cropped_bw_imagecounter = 0

                            print()
                            print("Reading text from cropped B&W images...(0/" + str(len(cropped_images)) + ")")
                            await primecheckmessage.edit(content="Reading text from cropped B&W images...(0/" +
                                                                 str(len(cropped_images)) + ")")

                            for croppedBWImage in cropped_images:
                                cropped_img_string = pytesseract.image_to_string(croppedBWImage)
                                cropped_img_string = cropped_img_string.rstrip()
                                cropped_img_string = cropped_img_string.replace(' _', '')
                                cropped_img_string = cropped_img_string.replace('4 ', '')
                                cropped_img_string = cropped_img_string.replace('\n', ' ')
                                cropped_img_string = cropped_img_string.replace('\t', ' ')
                                cropped_img_string = cropped_img_string.replace(' ', '_')
                                cropped_img_string = cropped_img_string.lower()
                                for string in cropped_img_string.split('_'):
                                    if string in dictionary.keys():
                                        cropped_img_string = cropped_img_string.replace(string, dictionary[string])
                                if "blueprint" in cropped_img_string.split('_'):
                                    if cropped_img_string.split('_')[
                                        cropped_img_string.split('_').index("blueprint") - 1] != "prime" and \
                                            cropped_img_string.split('_')[
                                                cropped_img_string.split('_').index("blueprint") - 1] != "collar":
                                        cropped_img_string = cropped_img_string.replace('_blueprint', '')
                                ImageTextData.append(cropped_img_string)
                                cropped_bw_imagecounter = cropped_bw_imagecounter + 1
                                print("Reading text from cropped B&W images...(" + str(cropped_bw_imagecounter) +
                                      "/" + str(len(cropped_images)) + ")")

                                await primecheckmessage.edit(content="Reading text from cropped B&W images...(" +
                                                                     str(cropped_bw_imagecounter) +
                                                                     "/" + str(len(cropped_images)) + ")")

                            print()
                            print("Checking for sets...")
                            await primecheckmessage.edit(content="Checking for sets...")

                            repeats_num = 0
                            repeats_name = ImageTextData[0].split('_')[0]

                            for i in range(len(ImageTextData)):
                                if ImageTextData[i].split('_')[0].capitalize() in primes:
                                    print(ImageTextData[i].split('_')[0] + " " + repeats_name)
                                    if ImageTextData[i].split('_')[0] == repeats_name:
                                        repeats_num += 1
                                    else:
                                        print("else:" + primes[repeats_name.capitalize()] + " " + str(repeats_num))
                                        if primes[repeats_name.capitalize()] == str(repeats_num):
                                            if repeats_name.capitalize() == "Dual":
                                                ImageTextData.insert(i, "dual_kamas_prime_set")
                                            elif repeats_name.capitalize() == "Silva":
                                                ImageTextData.insert(i, "silva_and_aegis_prime_set")
                                            elif repeats_name.capitalize() == "Nami":
                                                ImageTextData.insert(i, "nami_skyla_prime_set")
                                            else:
                                                ImageTextData.insert(i, repeats_name + "_prime_set")
                                        repeats_name = ImageTextData[i].split('_')[0]
                                        repeats_num = 1

                            print()
                            print("Getting market orders...")
                            await primecheckmessage.edit(
                                content="Getting market orders... (0/" + str(len(ImageTextData)) + ")")

                            for i in range(len(ImageTextData)):
                                try:
                                    print(str(i + 1) + "/" + str(len(ImageTextData)) + "  " + str(ImageTextData[i]))
                                    await primecheckmessage.edit(
                                        content="Getting market orders... (" + str(i + 1) + "/" + str(
                                            len(ImageTextData)) + ")")
                                    Embed, BuysReq, SellsReq = await mwu.get_market_orders(ImageTextData[i])
                                    await asyncio.sleep(0.3)
                                    top_buy_price = 0
                                    top_buy_player = "< None >"
                                    top_sell_price = 0
                                    top_sell_player = "< None >"
                                    Buys, BRequest = BuysReq
                                    for player, (price, rank) in Buys:
                                        if top_buy_price == 0:
                                            top_buy_price = price
                                            top_buy_player = player
                                        elif price > top_buy_price:
                                            top_buy_price = price
                                            top_buy_player = player

                                    Sells, SRequest = SellsReq
                                    for player, (price, rank) in Sells:
                                        if top_sell_price == 0:
                                            top_sell_price = price
                                            top_sell_player = player
                                        elif price < top_sell_price:
                                            top_sell_price = price
                                            top_sell_player = player

                                    if str(ImageTextData[i].split('_')[0]) in warframes:
                                        warframes_array.append(ImageTextData[i])
                                        top_warframe_buy_price_array.append(top_buy_price)
                                        top_warframe_buy_player_array.append(top_buy_player)
                                        top_warframe_sell_price_array.append(top_sell_price)
                                        top_warframe_sell_player_array.append(top_sell_player)
                                    else:
                                        weapons_array.append(ImageTextData[i])
                                        top_weapon_buy_price_array.append(top_buy_price)
                                        top_weapon_buy_player_array.append(top_buy_player)
                                        top_weapon_sell_price_array.append(top_sell_price)
                                        top_weapon_sell_player_array.append(top_sell_player)
                                except:
                                    print("Encountered Error with: " + str(ImageTextData[i]) + str(sys.exc_info()))
                                    if ImageTextData[i].split('_')[0] in warframes:
                                        warframes_array.append(ImageTextData[i])
                                        top_warframe_buy_price_array.append('-')
                                        top_warframe_buy_player_array.append('-')
                                        top_warframe_sell_price_array.append('-')
                                        top_warframe_sell_player_array.append('-')
                                    else:
                                        weapons_array.append(ImageTextData[i])
                                        top_weapon_buy_price_array.append('-')
                                        top_weapon_buy_player_array.append('-')
                                        top_weapon_sell_price_array.append('-')
                                        top_weapon_sell_player_array.append('-')

                            print("Market data collected...")
                            await primecheckmessage.edit(content="Market data collected...")
                        except:
                            print("Error! ", str(sys.exc_info()) + " " + str(sys.exc_info()[2].tb_lineno))

                        '''
                        print("PartName: " + str(len(ImageTextData)))
                        print("SellPlayer: " + str(len(TopSellPlayerArray)))
                        print("SellPrice: " + str(len(TopSellPriceArray)))
                        print("BuyPlayer: " + str(len(TopBuyPlayerArray)))
                        print("BuyPrice: " + str(len(TopBuyPriceArray)))
                        '''
                        print()
                        print("Creating results Excel file...")
                        await primecheckmessage.edit(content="Creating results Excel file...")

                        if len(weapons_array) > len(warframes_array):
                            for i in range(len(weapons_array) - len(warframes_array)):
                                warframes_array.append('')
                                top_warframe_buy_price_array.append('')
                                top_warframe_buy_player_array.append('')
                                top_warframe_sell_price_array.append('')
                                top_warframe_sell_player_array.append('')
                        else:
                            for i in range(len(warframes_array) - len(weapons_array)):
                                weapons_array.append('')
                                top_weapon_buy_price_array.append('')
                                top_weapon_buy_player_array.append('')
                                top_weapon_sell_price_array.append('')
                                top_weapon_sell_player_array.append('')

                        df = pandas.DataFrame({'Warframe Name': warframes_array,
                                               'Frame Sell Price': top_warframe_sell_price_array,
                                               'Frame Sell Player': top_warframe_sell_player_array,
                                               'Frame Buy Price': top_warframe_buy_price_array,
                                               'Frame Buy Player': top_warframe_buy_player_array,
                                               '': '',
                                               'Weapon Name': weapons_array,
                                               'Weapon Sell Price': top_weapon_sell_price_array,
                                               'Weapon Sell Player': top_weapon_sell_player_array,
                                               'Weapon Buy Price': top_weapon_buy_price_array,
                                               'Weapon Buy Player': top_weapon_buy_player_array})

                        writer = pandas.ExcelWriter("PrimeResults.xlsx", engine='xlsxwriter')
                        '''
                        df = df.style.applymap(
                            lambda x: 'background-color: #95FF80' if x > 20 else 'background-color: transparent',
                            subset=['Frame Sell Price'])
                        '''
                        df = df.style \
                            .applymap(pandasExcelMapWarframeFrame, subset=['Frame Sell Price']) \
                            .applymap(pandasExcelMapWarframeWeapon, subset=['Weapon Sell Price'])
                        df.to_excel(writer, sheet_name="Primes", engine='openpyxl', index=False)
                        worksheet = writer.sheets['Primes']
                        worksheet.set_column('A:A', 27)  # Warframe Name
                        worksheet.set_column('B:B', 7)  # Frame Sell Price
                        worksheet.set_column('C:C', 21)  # Frame Sell Player
                        worksheet.set_column('D:D', 7)  # Frame Buy Price
                        worksheet.set_column('E:E', 21)  # Frame Buy Player
                        worksheet.set_column('F:F', 5)  # Empty Column
                        worksheet.set_column('G:G', 30)  # Weapon Name
                        worksheet.set_column('H:H', 8)  # Weapon Sell Price
                        worksheet.set_column('I:I', 21)  # Weapon Sell Player
                        worksheet.set_column('J:J', 8)  # Weapon Buy Price
                        worksheet.set_column('K:K', 21)  # Weapon Buy Player
                        writer.save()

                        print()
                        print("Results saved in PrimeResults.xlsx...")
                        await primecheckmessage.edit(content="Results saved in PrimeResults.xlsx...")

                        print()
                        print("Deleting screenshots...")
                        await primecheckmessage.edit(content="Deleting screenshots...")
                        for imgs in os.listdir("Warframe/Screenshots"):
                            os.remove("Warframe/Screenshots/" + imgs)

                        print()
                        print("Prime check complete.")

                        await primecheckmessage.edit(content="Prime check complete.")
                        excelmessage = await message.channel.send(file=discord.File("PrimeResults.xlsx"))
                        await DeleteMessageAfterDelay(primecheckmessage, 5)
                        await DeleteMessageAfterDelay(excelmessage, 60)

                elif message.content.split()[1] == "relic":
                    if len(message.content.split()) == 3:
                        relic_rewards_list = mwu.parse_relic_rewards_table()
                        result_string = mwu.find_reward_relics(message.content.split()[2], relic_rewards_list)
                        if len(result_string) == 0:
                            result_string = "Could not find relics for '" + message.content.split()[2] + "'"

                        await DeleteMessageAfterDelay(message, 0.5)
                        await DeleteMessageAfterDelay(await message.channel.send(result_string), 20)

                    else:
                        await DeleteMessageAfterDelay(message, 0.5)
                        await DeleteMessageAfterDelay(
                            await message.channel.send("Wrong input. Please use 'wf relic <item_name>' format."), 10)

                else:
                    await DeleteMessageAfterDelay(
                        await message.channel.send("No such Warframe command.\n"
                                                   "Check bot help for available commands"), 5)


client.run(TOKEN)
