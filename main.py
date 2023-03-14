from secret import API_KEY, COIN_API_KEY
import telebot
import requests
import datetime
import pytz
from requests import Session
from bs4 import BeautifulSoup


bot = telebot.TeleBot(API_KEY)

print('Starting up bot')

def get_stock_price(stock_symbol):
  print("getting stock data")  #check if data retrieval is correct
  try:
    url = "https://finance.yahoo.com/quote/{}".format(stock_symbol)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    price_element = soup.find(
      "span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"})
    return price_element.text
  except:
    return "Error getting stock price for {}".format(stock_symbol)


def get_crypto_price(crypto_symbol):
  print("getting crypto data")  #check if data retrieval is correct
  try:
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = { 'slug': 'bitcoin', 'convert': 'USD' } # API parameters to pass in for retrieving specific cryptocurrency data
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': COIN_API_KEY}
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    text = response.json()
    price = text['data']['1']['quote']['USD']['price']
    return price
  except:
    return "Error getting crypto price for {}".format(crypto_symbol)


@bot.message_handler(func=lambda message: message.text[:2] == "$$")
def handle_crypto_message(message):
  print("Handling crypto")
  print(message.text, message.text[2:])
  try:
    crypto_symbol = message.text[2:].upper()  # removes the "$$" symbols from the message
    price = get_crypto_price(crypto_symbol)
    current_time = datetime.datetime.now(pytz.timezone('Asia/Singapore')).strftime("%I:%M %p") #time in SGT 12hr format
    bot.send_message(
      message.chat.id,
      "The current price of {} is ${:.2f} USD as at {} SGT".format(crypto_symbol, price, current_time))
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


@bot.message_handler(commands=['help'])
def help(message):
  bot.send_message(
    message.chat.id,
    "To get the stock price, please input '$' followed by the ticker symbol.")


@bot.message_handler(commands=['hello'])
def hello(message):
  username = message.from_user.username
  bot.send_message(message.chat.id, "Hello, @{}".format(username))


bot.polling()
