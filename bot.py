import os  # Bot initialization
import io  # Converting Bytes to Zip
import sys  # Exception catching
import mwu  # Personal module for warframe utilities
import pandas  # Excel output
import asyncio  # Sleep function
import discord  # Discord bot commands
import zipfile  # For Zip file processing
import requests  # API requests
import pytesseract  # Image analysis
from PIL import Image  # Image analysis
from dotenv import load_dotenv  # Env module
import xlsxwriter
import jinja2


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
client = discord.Client()
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\TesseractOCR\\tesseract.exe'


async def delete_message_after_delay(message, delay):
    await asyncio.sleep(delay)
    await message.delete()


def pandas_excel_map_warframe_frame(x):
    if isinstance(x, int):
        if x > 20:
            return 'background-color: #95FF80'
        elif x <= 5:
            return 'background-color: #EDC374'
        else:
            return 'background-color: transparent'


def pandas_excel_map_warframe_weapon(x):
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
                    await delete_message_after_delay(message, 0.5)
                    await delete_message_after_delay(await message.channel.send(
                        "General:\n"
                        "  bot help : Get all available bot commands\n"
                        "\n"
                        "Warframe Status:\n"
                        "  wf invasions : Get invasions data \n"
                        "  wf baro : Get information about void trader\n"
                        "  wf cycles : Get world cycles data \n"
                        "\n"
                        "Warframe Market:\n"
                        "  wf syndicate:\n"
                        "      <syndicate> weapons: Get <syndicate> weapons buy/sell orders\n"
                        "      <syndicate> offerings: Get <syndicate> augments and arch parts buy/sell orders\n"
                        "  wf market <item> : Get item buy/sell orders\n"
                        "\n"
                        "Warframe Drops:\n"
                        "  wf relic <item_name>: Get list of relics which contain the item\n"), 30)
                else:
                    await delete_message_after_delay(await message.channel.send("No such Bot Command.\n"
                                                                                "Use bot help for available commands."),
                                                     5)

            elif message.content.split()[0] == "wf":

                if message.content.split()[1] == "invasions":
                    await mwu.get_invasions(message)

                elif message.content.split()[1] == "baro":
                    await mwu.get_baro(message)

                elif message.content.split()[1] == "cycles":
                    await mwu.get_cycles(message)

                elif message.content.split()[1] == "syndicate":
                    syndicates = ["meridian", "arbiters", "suda", "perrin", "veil", "loka"]
                    if len(message.content.split()) > 2:
                        if (message.content.split()[2] in syndicates) and (len(message.content.split()) > 3):

                            if message.content.split()[3] == "weapons":
                                results_string = await mwu.get_market_syndicate_weapons(
                                    "weapons_" + message.content.split()[2] + ".txt")
                                await delete_message_after_delay(message, 0.5)
                                await delete_message_after_delay(await message.channel.send(results_string), 120)

                            elif message.content.split()[3] == "offerings":
                                if len(message.content.split()) > 4:
                                    if message.content.split()[4] == "chat":
                                        results_string = await mwu.get_market_syndicate_offerings(
                                            "offerings_" + message.content.split()[2] + ".txt", message, "chat")
                                        await delete_message_after_delay(await message.channel.send(results_string),
                                                                         120)
                                    await delete_message_after_delay(message, 0.5)
                                else:
                                    results_string = await mwu.get_market_syndicate_offerings(
                                        "offerings_" + message.content.split()[2] + ".txt", message)
                                    await delete_message_after_delay(message, 0.5)
                                    await delete_message_after_delay(await message.channel.send(results_string), 120)
                            else:
                                await delete_message_after_delay(message, 5)
                                await delete_message_after_delay(await message.channel.send(
                                    "No such Warframe command.\nCheck bot help for available commands"), 5)
                        else:
                            await delete_message_after_delay(message, 0.5)
                            await delete_message_after_delay(await message.channel.send("No such Syndicate"), 10)
                    else:
                        await delete_message_after_delay(message, 0.5)
                        await delete_message_after_delay(
                            await message.channel.send("Wrong input. use wf syndicate <syndicate> <action> format."),
                            10)

                elif message.content.split()[1] == "market":
                    if len(message.content.split()) > 2:
                        await delete_message_after_delay(message, 0.5)
                        try:
                            embed, buys, sells = await mwu.get_market_orders(message.content.split()[2])
                            await delete_message_after_delay(await message.channel.send(embed=embed), 60)
                        except:
                            await delete_message_after_delay(
                                await message.channel.send(str(sys.exc_info()) + " Error!"), 10)
                    else:
                        await delete_message_after_delay(
                            await message.channel.send("Error! Please use format: wf market <item>"), 10)

                elif message.content.split()[1] == "primecheck":
                    await delete_message_after_delay(message, 0.5)
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
                        # x_pos = inventory_offset_x
                        # y_pos = inventory_offset_y

                        images = []
                        image_text_data = []
                        primes = {}
                        warframes = []
                        dictionary = {}
                        cropped_images = []

                        warframes_array = []
                        weapons_array = []

                        # top_sell_price = 0
                        # top_sell_player = ""
                        # top_buy_price = 0
                        # top_buy_player = ""

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
                                image_text_data.append(cropped_img_string)
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
                            repeats_name = image_text_data[0].split('_')[0]

                            for i in range(len(image_text_data)):
                                if image_text_data[i].split('_')[0].capitalize() in primes:
                                    print(image_text_data[i].split('_')[0] + " " + repeats_name)
                                    if image_text_data[i].split('_')[0] == repeats_name:
                                        repeats_num += 1
                                    else:
                                        print("else:" + primes[repeats_name.capitalize()] + " " + str(repeats_num))
                                        if primes[repeats_name.capitalize()] == str(repeats_num):
                                            if repeats_name.capitalize() == "Dual":
                                                image_text_data.insert(i, "dual_kamas_prime_set")
                                            elif repeats_name.capitalize() == "Silva":
                                                image_text_data.insert(i, "silva_and_aegis_prime_set")
                                            elif repeats_name.capitalize() == "Nami":
                                                image_text_data.insert(i, "nami_skyla_prime_set")
                                            else:
                                                image_text_data.insert(i, repeats_name + "_prime_set")
                                        repeats_name = image_text_data[i].split('_')[0]
                                        repeats_num = 1

                            print()
                            print("Getting market orders...")
                            await primecheckmessage.edit(
                                content="Getting market orders... (0/" + str(len(image_text_data)) + ")")

                            for i in range(len(image_text_data)):
                                try:
                                    print(str(i + 1) + "/" + str(len(image_text_data)) + "  " + str(image_text_data[i]))
                                    await primecheckmessage.edit(
                                        content="Getting market orders... (" + str(i + 1) + "/" + str(
                                            len(image_text_data)) + ")")
                                    embed, buys_req, sells_req = await mwu.get_market_orders(image_text_data[i])
                                    await asyncio.sleep(0.3)
                                    top_buy_price = 0
                                    top_buy_player = "< None >"
                                    top_sell_price = 0
                                    top_sell_player = "< None >"
                                    buys, b_request = buys_req
                                    for player, (price, rank) in buys:
                                        if top_buy_price == 0:
                                            top_buy_price = price
                                            top_buy_player = player
                                        elif price > top_buy_price:
                                            top_buy_price = price
                                            top_buy_player = player

                                    sells, s_request = sells_req
                                    for player, (price, rank) in sells:
                                        if top_sell_price == 0:
                                            top_sell_price = price
                                            top_sell_player = player
                                        elif price < top_sell_price:
                                            top_sell_price = price
                                            top_sell_player = player

                                    if str(image_text_data[i].split('_')[0]) in warframes:
                                        warframes_array.append(image_text_data[i])
                                        top_warframe_buy_price_array.append(top_buy_price)
                                        top_warframe_buy_player_array.append(top_buy_player)
                                        top_warframe_sell_price_array.append(top_sell_price)
                                        top_warframe_sell_player_array.append(top_sell_player)
                                    else:
                                        weapons_array.append(image_text_data[i])
                                        top_weapon_buy_price_array.append(top_buy_price)
                                        top_weapon_buy_player_array.append(top_buy_player)
                                        top_weapon_sell_price_array.append(top_sell_price)
                                        top_weapon_sell_player_array.append(top_sell_player)
                                except:
                                    print("Encountered Error with: " + str(image_text_data[i]) + str(sys.exc_info()))
                                    if image_text_data[i].split('_')[0] in warframes:
                                        warframes_array.append(image_text_data[i])
                                        top_warframe_buy_price_array.append('-')
                                        top_warframe_buy_player_array.append('-')
                                        top_warframe_sell_price_array.append('-')
                                        top_warframe_sell_player_array.append('-')
                                    else:
                                        weapons_array.append(image_text_data[i])
                                        top_weapon_buy_price_array.append('-')
                                        top_weapon_buy_player_array.append('-')
                                        top_weapon_sell_price_array.append('-')
                                        top_weapon_sell_player_array.append('-')

                            print("Market data collected...")
                            await primecheckmessage.edit(content="Market data collected...")
                        except:
                            print("Error! ", str(sys.exc_info()) + " " + str(sys.exc_info()[2].tb_lineno))

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

                        df = df.style \
                            .applymap(pandas_excel_map_warframe_frame, subset=['Frame Sell Price']) \
                            .applymap(pandas_excel_map_warframe_weapon, subset=['Weapon Sell Price'])
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
                        await delete_message_after_delay(primecheckmessage, 5)
                        await delete_message_after_delay(excelmessage, 60)

                elif message.content.split()[1] == "relic":
                    if len(message.content.split()) == 3:
                        relic_rewards_list = mwu.parse_relic_rewards_table()
                        result_string = mwu.find_reward_relics(message.content.split()[2], relic_rewards_list)
                        if len(result_string) == 0:
                            result_string = "Could not find relics for '" + message.content.split()[2] + "'"
                        await delete_message_after_delay(message, 0.5)
                        await delete_message_after_delay(await message.channel.send(result_string), 20)
                    else:
                        await delete_message_after_delay(message, 0.5)
                        await delete_message_after_delay(
                            await message.channel.send("Wrong input. Please use 'wf relic <item_name>' format."), 10)

                else:
                    await delete_message_after_delay(
                        await message.channel.send("No such Warframe command.\n"
                                                   "Check bot help for available commands"), 5)

client.run(TOKEN)
