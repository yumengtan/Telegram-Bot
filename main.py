#from secret import API_KEY, COIN_API_KEY
import telebot
import requests
import datetime
import pytz
import os
from requests import Session


API_KEY = os.environ.get('API_KEY')
COIN_API_KEY = os.environ.get('COIN_API_KEY')
STOCK_API_KEY = os.environ.get('STOCK_API_KEY')


bot = telebot.TeleBot(API_KEY)

print('Starting up bot')

def get_stock_price(stock_symbol):
  print("getting stock price for " + stock_symbol)  #check if data retrieval is correct
  try:
    url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}'.format(stock_symbol, STOCK_API_KEY)
    response = requests.get(url)
    text = response.json()
    price = text['Global Quote']['05. price']
    percentage = text['Global Quote']['10. change percent']
    percentage = percentage.rstrip(percentage[-1])
    listElem = [price, percentage]
    print(listElem)
    return listElem 
  except:
    return "Error getting stock price for {}".format(stock_symbol)

def get_stock_marketcap(stock_symbol):
  print("getting stock marketcap for " + stock_symbol)  #check if data retrieval is correct
  try:
    url = 'https://www.alphavantage.co/query?function=OVERVIEW&symbol={}&apikey={}'.format(stock_symbol, STOCK_API_KEY)
    response = requests.get(url)
    text = response.json()
    print(text)
    marketcap = text['MarketCapitalization']
    print(marketcap)
    return marketcap
  except:
    return "Error getting stock marketcap for {}".format(stock_symbol)

# credits: https://gist.github.com/SrNightmare09/c0492a8852eb172ebea6c93837837998
def get_crypto_price(crypto_symbol):
  print("getting crypto price for " + crypto_symbol)  #check if data retrieval is correct
  try:
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = { 'symbol': crypto_symbol, 'convert': 'USD' } # API parameters to pass in for retrieving specific cryptocurrency data 
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': COIN_API_KEY}
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    text = response.json()
    #print(text)
    price = text['data'][crypto_symbol]['quote']['USD']['price']
    percentage = text['data'][crypto_symbol]['quote']['USD']['percent_change_24h']
    listElem = [price, percentage]
    print(listElem)
    return listElem
  except:
    return "Error getting crypto price for {}".format(crypto_symbol)

def get_crypto_marketcap(crypto_symbol):
  print("Getting crypto mcap for " + crypto_symbol) #check if data retrieval is correct
  try:
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = { 'symbol': crypto_symbol, 'convert': 'USD' } # API parameters to pass in for retrieving specific cryptocurrency data 
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': COIN_API_KEY}
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    text = response.json()
    marketcap = text['data'][crypto_symbol]['quote']['USD']['market_cap']
    return marketcap
  except:
    return "Error getting crypto marketcap for {}".format(crypto_symbol)
  

@bot.message_handler(func=lambda message: message.text and message.text.startswith('$$'))
def handle_crypto_message(message):
  print("Handling crypto")
  print(message.text, message.text[2:])
  try:
    crypto_symbol = message.text[2:].upper()  # removes the "$$" symbols from the message
    elem = get_crypto_price(crypto_symbol)
    price = elem[0]
    percent = elem[1]
    current_time = datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime("%I:%M %p") #time in SGT 12hr format
    bot.send_message(
      message.chat.id,
      "The price of {} is ${:.4f} USD as at {} SGT. The percentage change is {:.4f}% from 24hrs".format(crypto_symbol, price, current_time, percent))
  except:
    bot.send_message(
      message.chat.id,
      "Invalid input format. Please input '$$' followed by the cryptocurrency symbol."
    )


@bot.message_handler(func=lambda message: message.text[0] == "$")
def handle_stock_message(message):
  print("Handling stock")
  try:
    stock_symbol = message.text[1:]  # removes the "$" symbol from the message
    elem = get_stock_price(stock_symbol)
    print(elem)
    price = elem[0]
    percent = elem[1]
    tz_sg = pytz.timezone('Asia/Singapore')
    current_time = datetime.datetime.now(tz_sg)
    market_open = current_time.replace(hour=21, minute=30, second=0, microsecond=0)
    market_close = current_time.replace(hour=4, minute=0, second=0, microsecond=0)
    market_close_start = current_time.replace(hour=8, minute=0, second=0, microsecond=0)
    market_close_end = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
    if current_time < market_close_end and current_time > market_close_start:
            bot.send_message(
                message.chat.id,
                "The market is currently closed. The last known price of {} is ${:.4f}.".format(stock_symbol, price))
    else: 
      if current_time < market_open:
         market_status = "premarket"
      elif current_time > market_close:
         market_status = "aftermarket"
      else:
         market_status = "regular trading"
      current = datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime("%I:%M %p") #time in SGT 12hr format
      print(current)
      percent = float(percent)
      damessage = f"The price of {stock_symbol} is ${price:.4f} USD as at {current_time} SGT ({market_status}). The stock is down {abs(percent):.4f}% from 24hrs."
      print(damessage)
      print("no")
      if percent >= 0:
        print("positive")
        bot.send_message("The price of {} is ${:.2f} USD as at {} SGT ({}). The stock is up {:.4f}% from 24hrs".format(stock_symbol, price, current, market_status, percent))
      else:
        print("negative")
        percent = abs(percent)
        bot.send_message(message.chat.id, "The price of {} is ${:.2f} USD as at {} SGT ({}). The stock is down {:.4f}% from 24hrs.".format(stock_symbol, price, current, market_status, percent))

  except:
    bot.send_message(
      message.chat.id,
      "Invalid input format. Please input '$' followed by the ticker symbol.")


@bot.message_handler(func=lambda message: message.text.startswith('/mcap'))
def marketcap(message):
    user_message = message.text[6:]
    if not user_message:
        bot.reply_to(message, "Please provide a stock or crypto symbol after the /mcap command.")
        return
    
    elif len(user_message) > 1 and user_message.startswith('$$'):
        crypto_symbol = user_message[2:].upper()
        print(crypto_symbol)
        # Call the function to get the market cap for the crypto symbol
        market_cap = int(get_crypto_marketcap(crypto_symbol))

        # Send the market cap back to the user
        bot.reply_to(message, f"The market cap for {crypto_symbol} is ${market_cap}.")

    elif user_message.startswith('$'):
        stock_symbol = user_message[1:]
        market_cap = get_stock_marketcap(stock_symbol)
        # Send the market cap back to the user
        bot.reply_to(message, f"The market cap for {stock_symbol} is {market_cap}.")


    else:
        # Send an error message back to the user
        bot.reply_to(message, "Sorry, I didn't understand your request. Please enter /mcap $[symbol] for stocks or /mcap $$[symbol] for cryptocurrencies to get the market cap.")


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hi there! I am a bot that can provide you with the current stock and crypto prices.\n"
                     + "To get the stock price, please input '$' followed by the ticker symbol. To get the crypto price, please input '$$' followed by the cryptocurrency symbol. For example, *'$$BTC'*.\n"
                     + "More commands will be added if time permits:)\n"
                     + "*Commands*\n"
                     + "- /chart $[symbol] Plot of the stocks movement for the past 1 month. 📊\n- /mcap $[symbol] Market Capitalization of symbol. 💰\n- /help Get some help using the bot.🆘\n", parse_mode= 'Markdown' )

@bot.message_handler(commands=['help'])
def help(message):
  bot.send_message(
    message.chat.id,
    "To get the stock price, please input '$' followed by the ticker symbol e.g. $spy\n"
    + "To get the cryptocurrency price, please input '$$' followed by the ticker symbol. e.g. $$btc")


@bot.message_handler(commands=['hello'])
def hello(message):
  username = message.from_user.username
  bot.send_message(message.chat.id, "Hello, @{}".format(username))


bot.polling()
