#!/usr/bin/env python3

import mariadb
import requests
import telegram
import tweepy
import time
from datetime import datetime
from credentials import *
from config import *
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.contract import Contract


def main():
  print("PROJECT NAME: ", PROJECT)
  for chain in CHAINS:
    print("Current Blockchain:", chain.upper())
    conn = connectToMariaDB()
    cur = conn.cursor()
    bot = connectToTelegram()
    api = connectToTwitter()
    cur.execute(f"CREATE TABLE IF NOT EXISTS {PROJECT.lower()}_{chain}_tx_tracker (DateTime DateTime, TxHash varchar(66), BlockNumber bigint, TransactionType varchar(5), NativeAmount float, TokenAmount float, USDAmount float);")
    cur.execute(f"CREATE TABLE IF NOT EXISTS {PROJECT.lower()}_everswap_tracker (DateTime DateTime, TxHash varchar(66), Blockchain varchar(10), NativeAmount float, TokenAmount float, USDAmount float);")

#    UNCOMMENT TO RESET DATABASE
#    cur.execute(f"TRUNCATE {PROJECT.lower()}_{chain}_tx_tracker;")
#    cur.execute(f"TRUNCATE {PROJECT.lower()}_everswap_tracker;")
    
    cur.execute(f"SELECT BlockNumber FROM {PROJECT.lower()}_{chain}_tx_tracker;")
    start_block = int(cur.fetchall()[-1][0]) + START_BLOCK_OFFSET

#    UNCOMMENT TO RESET DATABASE
#    start_block = 0

    if(chain == "bsc"):
      chain2 = "BNB Chain"
      native = "BNB"
      native_id = "wbnb"
      web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
      web3.middleware_onion.inject(geth_poa_middleware, layer=0)
      factory_contract = BNB_FACTORY
      factory_abi = BNB_FACTORY_ABI
      wrapped_native = WRAPPED_BNB
      EVERSWAP = BSC_EVERSWAP
      factory_contract = web3.eth.contract(address=factory_contract, abi=factory_abi)
      pair_address = factory_contract.functions.getPair(CONTRACT_ADDRESS, wrapped_native).call()
      print("Pair Address: ", pair_address)
      pair_abi_request_url = API_URL_BSC + API_URL_GETABI + pair_address + "&apikey=" + BSC_API_KEY
      pair_abi_data = requests.get(pair_abi_request_url).json()["result"]
      pair_address_contract = web3.eth.contract(address=pair_address, abi=pair_abi_data)
      reserves = pair_address_contract.functions.getReserves().call()
      price_in_native = int(reserves[0])/int(reserves[1])
      hash_source = " *TX Hash:* [BSCScan](https://bscscan.com/tx/"
      transaction_request_url = API_URL_BSC + API_URL_TOKENTX + CONTRACT_ADDRESS + "&address=" + pair_address + "&startblock=" + str(start_block) + API_URL_ENDBLOCK + BSC_API_KEY

    if(chain == "eth"):
      chain2 = "Ethereum"
      native = "ETH"
      native_id = "weth"
      web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/719d3797a5b74a2696ced6a409350788"))
      factory_contract = ETH_FACTORY
      factory_abi = ETH_FACTORY_ABI
      wrapped_native = WRAPPED_ETH
      factory_contract = web3.eth.contract(address=factory_contract, abi=factory_abi)
      pair_address = factory_contract.functions.getPair(CONTRACT_ADDRESS, wrapped_native).call()
      print("Pair Address: ", pair_address)
      pair_abi_request_url = API_URL_ETH + API_URL_GETABI + pair_address + "&apikey=" + ETH_API_KEY
      pair_abi_data = requests.get(pair_abi_request_url).json()["result"]
      pair_address_contract = web3.eth.contract(address=pair_address, abi=pair_abi_data)
      reserves = pair_address_contract.functions.getReserves().call()
      price_in_native = int(reserves[0])/int(reserves[1])
      hash_source = " *TX Hash:* [EtherScan](https://etherscan.io/tx/"
      transaction_request_url = API_URL_ETH + API_URL_TOKENTX + CONTRACT_ADDRESS + "&address=" + pair_address + "&startblock=" + str(start_block) + API_URL_ENDBLOCK + ETH_API_KEY

    if(chain == "poly"):
      chain2 = "Polygon"
      native = "MATIC"
      native_id = "wmatic"
      web3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com/"))
      factory_contract = POLY_FACTORY
      factory_abi = POLY_FACTORY_ABI
      wrapped_native = WRAPPED_MATIC
      factory_contract = web3.eth.contract(address=factory_contract, abi=factory_abi)
      pair_address = factory_contract.functions.getPair(CONTRACT_ADDRESS, wrapped_native).call()
      print("Pair Address: ", pair_address)
      pair_abi_request_url = API_URL_POLY + API_URL_GETABI + pair_address + "&apikey=" + POLY_API_KEY
      pair_abi_data = requests.get(pair_abi_request_url).json()["result"]
      pair_address_contract = web3.eth.contract(address=pair_address, abi=pair_abi_data)
      reserves = pair_address_contract.functions.getReserves().call()
      price_in_native = int(reserves[0])/int(reserves[1])
      hash_source = " *TX Hash:* [PolygonScan](https://polygonscan.com/tx/"
      transaction_request_url = API_URL_POLY + API_URL_TOKENTX + CONTRACT_ADDRESS + "&address=" + pair_address + "&startblock=" + str(start_block) + API_URL_ENDBLOCK + POLY_API_KEY

    if(chain == "ftm"):
      chain2 = "Fantom"
      native = "FTM"
      native_id = "wrapped-fantom"
      web3 = Web3(Web3.HTTPProvider("https://rpcapi.fantom.network"))
      web3.middleware_onion.inject(geth_poa_middleware, layer=0)
      factory_contract = FTM_FACTORY
      factory_abi = FTM_FACTORY_ABI
      wrapped_native = WRAPPED_FTM
      factory_contract = web3.eth.contract(address=factory_contract, abi=factory_abi)
      pair_address = factory_contract.functions.getPair(CONTRACT_ADDRESS, wrapped_native).call()
      print("Pair Address: ", pair_address)
      pair_abi_request_url = API_URL_FTM + API_URL_GETABI + pair_address + "&apikey=" + FTM_API_KEY
      pair_abi_data = requests.get(pair_abi_request_url).json()["result"]
      pair_address_contract = web3.eth.contract(address=pair_address, abi=pair_abi_data)
      reserves = pair_address_contract.functions.getReserves().call()
      price_in_native = int(reserves[0])/int(reserves[1])
      hash_source = " *TX Hash:* [FTMScan](https://ftmscan.com/tx/"
      transaction_request_url = API_URL_FTM + API_URL_TOKENTX + CONTRACT_ADDRESS + "&address=" + pair_address + "&startblock=" + str(start_block) + API_URL_ENDBLOCK + FTM_API_KEY

    if(chain == "avax"):
      chain2 = "Avalanche"
      native = "AVAX"
      native_id = "wrapped-avax"
      web3 = Web3(Web3.HTTPProvider("https://avalanche.public-rpc.com/"))
      web3.middleware_onion.inject(geth_poa_middleware, layer=0)
      factory_contract = AVAX_FACTORY
      factory_abi = AVAX_FACTORY_ABI
      wrapped_native = WRAPPED_AVAX
      factory_contract = web3.eth.contract(address=factory_contract, abi=factory_abi)
      pair_address = factory_contract.functions.getPair(CONTRACT_ADDRESS, wrapped_native).call()
      print("Pair Address: ", pair_address)
      pair_abi_request_url = API_URL_AVAX + API_URL_GETABI + pair_address + "&apikey=" + AVAX_API_KEY
      pair_abi_data = requests.get(pair_abi_request_url).json()["result"]
      pair_address_contract = web3.eth.contract(address=pair_address, abi=pair_abi_data)
      reserves = pair_address_contract.functions.getReserves().call()
      price_in_native = int(reserves[0])/int(reserves[1])
      hash_source = " *TX Hash:* [SnowTrace](https://snowtrace.io/tx/"
      transaction_request_url = API_URL_AVAX + API_URL_TOKENTX + CONTRACT_ADDRESS + "&address=" + pair_address + "&startblock=" + str(start_block) + API_URL_ENDBLOCK + AVAX_API_KEY

    coingecko_request_url = "https://api.coingecko.com/api/v3/simple/price?ids=" + native_id + "&vs_currencies=usd"
    coingecko_price = requests.get(coingecko_request_url).json()[native_id]["usd"]
    print("CoinGecko Price: ", coingecko_price)

    tx_result = requests.get(transaction_request_url).json()["result"]

    print("Starting at Block: ", start_block)
    for item in tx_result:
      if item['from'] == pair_address.lower():
        if item['to'] == BURN_WALLET:
          tx_datetime = datetime.utcfromtimestamp(int(item['timeStamp']))
          token_amount = int(item['value'])/(10 ** DECIMALS)
          native_amount = token_amount * price_in_native
          usd_price = price_in_native * coingecko_price
          usd_amount = token_amount * usd_price
          telegram_message = f"🔥 *{chain2} SWURN ALERT: Swap and Burn!*\n🔥 *{PROJECT} Amount:* " + str("{:,}".format(round(token_amount,2))) + "\n🔥" + hash_source + str(item['hash']) + ")"
          twitter_message = f"#{PROJECT} {SYMBOL}\n🔥 {chain2} SWURN ALERT: Swap and Burn!\n🔥 {PROJECT} Amount: " + str("{:,}".format(token_amount)) + "\n🔥 TX Hash: " + str(item['hash'])
          cur.execute(f"INSERT INTO {PROJECT.lower()}_{chain}_tx_tracker (DateTime, TxHash, BlockNumber, TransactionType, NativeAmount, TokenAmount, USDAmount) VALUES (?, ?, ?, ?, ?, ?, ?)", (tx_datetime, item['hash'], item['blockNumber'], "Swurn", native_amount, token_amount, usd_amount))
          conn.commit()
        else:
          tx_datetime = datetime.utcfromtimestamp(int(item['timeStamp']))
          token_amount = int(item['value'])/(10 ** DECIMALS)
          native_amount = token_amount * price_in_native
          usd_price = price_in_native * coingecko_price
          usd_amount = token_amount * usd_price
          bubble_message = getBubbles(usd_amount, "buy")
          if item['to'] == EVERSWAP:
            telegram_message = f"🟢 *{chain2} Buy on EverSwap*\n🟢 *Date/Time:* " + str(tx_datetime) + "\n🟢" + hash_source + str(item['hash']) + ")\n🟢 *USD Amount:* $" + str("{:,}".format(round(usd_amount,2))) +  f"\n🟢 *{native} Amount:* " + str(round(native_amount,6)) + f"\n🟢 *{PROJECT} Amount:* " + str("{:,}".format(round(token_amount,2))) + str(bubble_message)
            twitter_message = f"#{PROJECT}\n🟢 #{chain2} Buy on #EverSwap\n🟢 Date/Time: " + str(tx_datetime) + "\n🟢 TX Hash: " + str(item['hash']) + "\n🟢 USD Amount: $" + str("{:,}".format(round(usd_amount,2))) +  f"\n🟢 {native} Amount: " + str(round(native_amount,6)) + "\n🟢 RISE Amount: " + str("{:,}".format(token_amount))
            cur.execute(f"INSERT INTO {PROJECT.lower()}_everswap_tracker (DateTime, TxHash, Blockchain, NativeAmount, TokenAmount, USDAmount) VALUES (?, ?, ?, ?, ?, ?)", (tx_datetime, item['hash'], chain.upper(), native_amount, token_amount, usd_amount))
            conn.commit()
          else:
            telegram_message = f"🟢 *{chain2} Buy*\n🟢 *Date/Time:* " + str(tx_datetime) + "\n🟢" + hash_source + str(item['hash']) + ")\n🟢 *USD Amount:* $" + str("{:,}".format(round(usd_amount,2))) +  f"\n🟢 *{native} Amount:* " + str(round(native_amount,6)) + f"\n🟢 *{PROJECT} Amount:* " + str("{:,}".format(round(token_amount,2))) + str(bubble_message)
            twitter_message = f"#{PROJECT} {SYMBOL}\n🟢 #{chain2} Buy\n🟢 Date/Time: " + str(tx_datetime) + "\n🟢 TX Hash: " + str(item['hash']) + "\n🟢 USD Amount: $" + str("{:,}".format(round(usd_amount,2))) +  f"\n🟢 {native} Amount: " + str(round(native_amount,6)) + f"\n🟢 {PROJECT} Amount: " + str("{:,}".format(round(token_amount,2)))
          cur.execute(f"INSERT INTO {PROJECT.lower()}_{chain}_tx_tracker (DateTime, TxHash, BlockNumber, TransactionType, NativeAmount, TokenAmount, USDAmount) VALUES (?, ?, ?, ?, ?, ?, ?)", (tx_datetime, item['hash'], item['blockNumber'], "Buy", native_amount, token_amount, usd_amount))
          conn.commit()
      if item['to'] == pair_address.lower():
        tx_datetime = datetime.utcfromtimestamp(int(item['timeStamp']))
        token_amount = round(int(item['value'])/(10 ** DECIMALS),2)
        native_amount = token_amount * price_in_native
        usd_price = price_in_native * coingecko_price
        usd_amount = token_amount * usd_price        
        bubble_message = getBubbles(usd_amount, "sell")
        if item['from'] == EVERSWAP:
          telegram_message = f"🔴 *{chain2} Sell on EverSwap*\n🔴 *Date/Time:* " + str(tx_datetime) + "\n🔴" + hash_source + str(item['hash']) + ")\n🔴 *USD Amount:* $" + str("{:,}".format(round(usd_amount,2))) +  f"\n🔴 *{native} Amount:* " + str(round(native_amount,6)) + f"\n🔴 *{PROJECT} Amount:* " + str("{:,}".format(round(token_amount,2))) + str(bubble_message)
          twitter_message = f"#{PROJECT}\n🔴 #{chain2} Sell on #EverSwap\n🔴 Date/Time: " + str(tx_datetime) + "\n🔴 TX Hash: " + str(item['hash']) + "\n🔴 USD Amount: $" + str("{:,}".format(round(usd_amount,2))) +  f"\n🔴 {native} Amount: " + str(round(native_amount,6)) + "\n🔴 RISE Amount: " + str("{:,}".format(round(token_amount,2)))
          cur.execute(f"INSERT INTO {PROJECT.lower()}_everswap_tracker (DateTime, TxHash, Blockchain, NativeAmount, TokenAmount, USDAmount) VALUES (?, ?, ?, ?, ?, ?)", (datetime.utcfromtimestamp(int(item['timeStamp'])),item['hash'],chain.upper(),native_amount,token_amount,usd_amount))
          conn.commit()
        else:
          telegram_message = f"🔴 *{chain2} Sell*\n🔴 *Date/Time:* " + str(tx_datetime) + "\n🔴" + hash_source + str(item['hash']) + ")\n🔴 *USD Amount:* $" + str("{:,}".format(round(usd_amount,2))) +  f"\n🔴 *{native} Amount:* " + str(round(native_amount,6)) + f"\n🔴 *{PROJECT} Amount:* " + str("{:,}".format(round(token_amount,2))) + bubble_message
          twitter_message = f"#{PROJECT} {SYMBOL}\n🔴 #{chain2} Sell\n🔴 Date/Time: " + str(tx_datetime) + "\n🔴 TX Hash: " + str(item['hash']) + "\n🔴 USD Amount: $" + str("{:,}".format(round(usd_amount,2))) +  f"\n🔴 {native} Amount: " + str(round(native_amount,6)) + f"\n🔴 {PROJECT} Amount: " + str("{:,}".format(round(token_amount,2)))
        cur.execute(f"INSERT INTO {PROJECT.lower()}_{chain}_tx_tracker (DateTime, TxHash, BlockNumber, TransactionType, NativeAmount, TokenAmount, USDAmount) VALUES (?, ?, ?, ?, ?, ?, ?)", (datetime.utcfromtimestamp(int(item['timeStamp'])),item['hash'], item['blockNumber'],"Sell", native_amount, token_amount, usd_amount))
        conn.commit()
      print(telegram_message.replace('*',''))
      if (not TELEGRAM_MUTE):
        bot.send_message(chat_id=CHAT_ID, text=telegram_message, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
        time.sleep(1)
      if(not TWITTER_MUTE):
        api.update_status(status=twitter_message)
        time.sleep(1)

def connectToMariaDB():
    print("Connecting to MariaDB Instance...")
    try:
      conn = mariadb.connect(
        user=MARIADB_USER,
        password=MARIADB_PW,
        host=MARIADB_HOST,
        port=3306,
        database=MARIADB_DB
      )
      print("Success!")
    except mariadb.Error as e:
      print(f"Error connecting to MariaDB Platform: {e}")
    return conn

def connectToTelegram():
    print("Connecting to Telegram Bot...")
    try:
      bot = telegram.Bot(token=TELEGRAM_API_KEY)
      print("Success!")
    except telegram.Error as e:
      print(f"Error connecting to Telegram: {e}")
    return bot

def connectToTwitter():
    print("Connecting to Twitter...")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    print("Success!")
    return api

def getBubbles(usd_amount, type):
    bubble_quantity = int(usd_amount / BASE_AMOUNT)
    if type == "buy":
      bubble_message = "\n🟢"
      for bubble in range(bubble_quantity):
        bubble_message += "🟢"
    if type == "sell":
      bubble_message = "\n🔴"
      for bubble in range(bubble_quantity):
        bubble_message += "🔴"
    return bubble_message

if __name__ == "__main__":
  main()
