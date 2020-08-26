import os
import requests
import discord
import json
TOKEN = 'NjUzODk0NDMwNTM2NzYxMzQ0.Xe9opQ.XxkhQLgmzI_-GnNLbCyNrkZKoZg'

client = discord.Client()

def GetMarketOrders(request):
    Req = requests.get('https://api.warframe.market/v1/items/' + request + '/orders')
    Content = Req.content
    RawData = json.loads(Content)
    DataPayload = RawData["payload"]
    Orders = DataPayload["orders"]
    ResultString = ""
    BuyOrders = {}
    SellOrders = {}
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

    SortedSellOrders = sorted(SellOrders.items(), key=lambda x: x[1], reverse=True)
    SortedBuyOrders = sorted(BuyOrders.items(), key=lambda x: x[1], reverse=True)
    ResultString += "(" + request + ")" + "\n"
    if len(SortedBuyOrders) > MaxOrders:
        for i in range(MaxOrders):
            ResultString += SortedBuyOrders[i][0] + " buys for " + str(int(SortedBuyOrders[i][1])) + "\n"
    elif len(SortedBuyOrders) > 0:
        for Nickname, Price in SortedBuyOrders:
            ResultString += Nickname + " buys for " + str(int(Price)) + "\n"
    else:
        ResultString += "No Buy Orders." + "\n"

    ResultString += "\n"

    if len(SortedSellOrders) > MaxOrders:
        for i in range(MaxOrders):
            ResultString += SortedSellOrders[i][0] + " sells for " + str(int(SortedSellOrders[i][1])) + "\n"
    elif len(SortedSellOrders) > 0:
        for Nickname, Price in SortedSellOrders:
            ResultString += Nickname + " sels for " + str(int(Price)) + "\n"
    else:
        ResultString += "No Sell Orders." + "\n"

    ResultString += "\n"
    return (ResultString, (SortedBuyOrders, request), (SortedSellOrders, request))

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
                RewardsString += str(Item["node"]) + "\n"
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
        await message.channel.send(RewardsString)

    if message.content == "wf cetus":
        Req = requests.get('https://api.warframestat.us/pc/cetusCycle')
        Content = Req.content
        CetusData = json.loads(Content)
        await message.channel.send(CetusData["shortString"])

    if message.content == "wf perrin":
        ResultsString = ""
        MaxTops = 4
        TopBuyOrders = []
        TopSellOrders = []

        ReturnString, Buys, Sells = GetMarketOrders("secura_dual_cestra")
        ResultsString += ReturnString
        for i in range(len(Buys[0])):
            TopBuyOrders.append((Buys[0][i][0], Buys[0][i][1], Buys[1]))
        for i in range(len(Sells[0])):
            TopSellOrders.append((Sells[0][i][0], Sells[0][i][1], Sells[1]))

        ReturnString, Buys, Sells = GetMarketOrders("secura_lecta")
        ResultsString += ReturnString
        for i in range(len(Buys[0])):
            TopBuyOrders.append((Buys[0][i][0], Buys[0][i][1], Buys[1]))
        for i in range(len(Sells[0])):
            TopSellOrders.append((Sells[0][i][0], Sells[0][i][1], Sells[1]))

        ReturnString, Buys, Sells = GetMarketOrders("secura_penta")
        ResultsString += ReturnString
        for i in range(len(Buys[0])):
            TopBuyOrders.append((Buys[0][i][0], Buys[0][i][1], Buys[1]))
        for i in range(len(Sells[0])):
            TopSellOrders.append((Sells[0][i][0], Sells[0][i][1], Sells[1]))

        SortedTopBuyOrders = sorted(TopBuyOrders, key=lambda x:x[1], reverse=True)
        SortedTopSellOrders = sorted(TopSellOrders, key=lambda x:x[1])

        if len(SortedTopBuyOrders) > MaxTops:
            for i in range(MaxTops):
                ResultsString += SortedTopBuyOrders[i][0] + " buys for " + str(SortedTopBuyOrders[i][1]) + "  (" + SortedTopBuyOrders[i][2] + ")\n"
        else:
            for i in range(len(SortedTopBuyOrders)):
                ResultsString += SortedTopBuyOrders[i][0] + " buys for " + str(SortedTopBuyOrders[i][1]) + "  (" + SortedTopBuyOrders[i][2] + ")\n"

        ResultsString += "\n"

        if len(SortedTopSellOrders) > MaxTops:
            for i in range(MaxTops):
                ResultsString += SortedTopSellOrders[i][0] + " sells for " + str(SortedTopSellOrders[i][1]) + "  (" + SortedTopSellOrders[i][2] + ")\n"
        else:
            for i in range(len(SortedSellBuyOrders)):
                ResultsString += SortedTopSellOrders[i][0] + " sells for " + str(SortedTopSellOrders[i][1]) + "  (" + SortedTopSellOrders[i][2] + ")\n"

        await message.channel.send(ResultsString)

    if message.content == "wf help":
        await message.channel.send("wf invasions : Invasions data \n"
                                   "wf cetus : Cetus cycle data \n"
                                   "wf perrin : Get Syndicate weapons orders")
    

client.run(TOKEN)
