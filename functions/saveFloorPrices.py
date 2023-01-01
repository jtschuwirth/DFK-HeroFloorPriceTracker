import requests
from datetime import datetime
from decimal import Decimal

graph_url = "https://defi-kingdoms-community-api-gateway-co06z8vi.uc.gateway.dev/graphql"
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0'
}

classes = [
    "Warrior",
    "Knight",
    "Thief",
    "Archer",
    "Priest",
    "Wizard",
    "Monk",
    "Pirate",
    "Berserker",
    "Seer",
    "Legionnaire",
    "Scholar",
    "Paladin",
    "DarkKnight",
    "Summoner",
    "Ninja",
    "Shapeshifter",
    "Bard",
    "Dragoon",
    "Sage",
    "SpellBow",
    "DreadKnight"
]

def saveAllFloorPrices(network, table):
    results = {}
    now = int(datetime.now().timestamp())

    response = table.query(
        KeyConditionExpression = "mainClass_ = :class AND date_ BETWEEN :startdate AND :enddate",
        ExpressionAttributeValues={
            ":class": "Knight",
            ":startdate": int(now - 60*60*48),
            ":enddate": int(now),
        }
    )
    if response["Items"]:
        last_entry = response["Items"][-1]
        if int(last_entry["date_"]) > now-60*50:
            return "data has been renewed in less than 50 minutes"

    for mainClass in classes:
        profession_prices = saveFloorPrices(mainClass, network, table)
        results[mainClass] = profession_prices

    return results

def saveFloorPrices(mainClass, network, table):
    query = """
          query($mainClass: String, $network: String) {
              heroes(orderBy: salePrice, where: {
                  network: $network,
                  salePrice_not: null,
                  mainClass: $mainClass,
                  privateAuctionProfile: null
              }) {
                  salePrice
                  profession
              }
          }
      """

    variables = {
        "mainClass": mainClass,
        "network": network
    }

    prices = {}
    now = int(datetime.now().timestamp())
    
    response = requests.post(graph_url, json={"query":query, "variables":variables}, headers=headers)
    for hero in response.json()["data"]["heroes"]:
        if not hero["profession"] in prices:
            prices[hero["profession"]] = int(hero["salePrice"])/10**18
        if "mining" in prices and "fishing" in prices and "foraging" in prices and "gardening" in prices:
            break
    table.put_item(Item={
        "mainClass_": mainClass,
        "date_": now,
        "network_": network,
        "mining_": Decimal(str(round(prices["mining"], 2))),
        "fishing_": Decimal(str(round(prices["fishing"], 2))),
        "foraging_": Decimal(str(round(prices["foraging"], 2))),
        "gardening_": Decimal(str(round(prices["gardening"], 2))),
    })
        
    return prices