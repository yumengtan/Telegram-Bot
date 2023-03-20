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
  print("getting stock data for " + stock_symbol)  #check if data retrieval is correct
  try:
    url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey={STOCK_API_KEY}'.format(STOCK_API_KEY)
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

# credits: https://gist.github.com/SrNightmare09/c0492a8852eb172ebea6c93837837998
def get_crypto_price(crypto_symbol):
  print("getting crypto data for " + crypto_symbol)  #check if data retrieval is correct
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
  print("Getting crypto mcap")
  try:
    print("getting market cap for " + crypto_symbol)
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
    price = get_stock_price(stock_symbol)
    bot.send_message(
      message.chat.id,
      "The current price of {} is ${}".format(stock_symbol, price))
  except:
    bot.send_message(
      message.chat.id,
      "Invalid input format. Please input '$' followed by the ticker symbol.")


@bot.message_handler(func=lambda message: message.text.startswith('/mcap'))
def marketcap(message):
    user_message = message.text[6:]
    print(user_message[0])

    if not user_message:
        bot.reply_to(message, "Please provide a stock or crypto symbol after the /mcap command.")
        return
    
    elif user_message.startswith('!$'):

        stock_symbol = user_message[1:].upper()
        #market_cap = get_stock_market_cap(symbol)
        # Send the market cap back to the user
        #bot.reply_to(message, f"The market cap for {symbol} is {market_cap}.")

    elif user_message.startswith('$$'):
        crypto_symbol = user_message[2:].upper()
        print(crypto_symbol)
        # Call the function to get the market cap for the crypto symbol
        market_cap = int(get_crypto_marketcap(crypto_symbol))

        # Send the market cap back to the user
        bot.reply_to(message, f"The market cap for {crypto_symbol} is ${market_cap}.")

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
