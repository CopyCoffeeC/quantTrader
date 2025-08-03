import yfinance
from alpaca.common import APIError
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
import asyncio
from alpaca.data.live.stock import StockDataStream
from alpaca.data.enums import DataFeed
from ta.utils import dropna
from ta import add_all_ta_features
import time
import warnings
warnings.simplefilter("ignore", category=FutureWarning)



API_KEY = "PKLRE6GOC9RU31AFBECQ"
API_SECRET = "6YRgmhGJh4bqpYOSCCC6HMKCcXp25xlVuswlzELA"

trading_client = TradingClient(API_KEY, API_SECRET , paper=True)

watchlist = ["AAPL", "MSFT", "AMZN", "GOOGL", "SOFI","HOOD", "PG", "NVDA",
             "V", "MSTR", "META", "BROS", "KSS", "DNUT", "PLTR", "FIG",
             "JOBY", "SPOT", "FICO", "ORCL", "CSCO","PTLO", "RUN", "BLDR",
             "CPRX", "ENPH","SEDG", "NTLA", "TDOC", "MARA", "SPY"]

buylist = []

def buyOrder(ticker):
  try:
    market_order = trading_client.submit_order(
      MarketOrderRequest(
        symbol=ticker,
        notional= 50,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )
  )
  except APIError as e:
     print(e, "could not buy")

def sellOrder(ticker):
  try:
    position = trading_client.get_open_position(ticker)
    quantity = float(position.qty)

    market_order = trading_client.submit_order(
      MarketOrderRequest(
        symbol=ticker,
        qty = quantity,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.DAY
    )
  )
  except APIError as e:
    print(e, "could not sell")

def streamStock(ticker):
  def message_handler(message):
    price = message['price']
    print(price)
  with yfinance.WebSocket() as ws:
      ws.subscribe(ticker)
      ws.listen(message_handler)

def getRSI(ticker):
  hist = yfinance.download(ticker, period="1d", interval="1m", auto_adjust=False)
  hist.columns = hist.columns.droplevel(1)
  df = dropna(hist)
  df = add_all_ta_features(
    df,
    open="Open",
    high="High",
    low="Low",
    close="Close",
    volume="Volume",
    fillna=True
  )
  # <30
  return df["momentum_rsi"].tail(1).values[0]

def getBB(ticker):
  hist = yfinance.download(ticker, period="1d", interval="1m", auto_adjust=False)
  hist.columns = hist.columns.droplevel(1)
  df = dropna(hist)
  df = add_all_ta_features(
    df,
    open="Open",
    high="High",
    low="Low",
    close="Close",
    volume="Volume",
    fillna=True
  )
  #1
  return df["volatility_bbhi"].tail(1).values[0]

def getMACD(ticker):
  hist = yfinance.download(ticker, period="1d", interval="1m", auto_adjust=False)
  hist.columns = hist.columns.droplevel(1)
  df = dropna(hist)
  df = add_all_ta_features(
    df,
    open="Open",
    high="High",
    low="Low",
    close="Close",
    volume="Volume",
    fillna=True
  )
  #>-.5
  return df["trend_macd"].tail(1).values[0]


def getSTC(ticker):
  hist = yfinance.download(ticker, period="1d", interval="1m", auto_adjust=False)
  hist.columns = hist.columns.droplevel(1)
  df = dropna(hist)
  df = add_all_ta_features(
    df,
    open="Open",
    high="High",
    low="Low",
    close="Close",
    volume="Volume",
    fillna=True
  )
  #>50
  return df["trend_stc"].tail(1).values[0]

def getKST(ticker):
  hist = yfinance.download(ticker, period="1d", interval="1m", auto_adjust=False)
  hist.columns = hist.columns.droplevel(1)
  df = dropna(hist)
  df = add_all_ta_features(
    df,
    open="Open",
    high="High",
    low="Low",
    close="Close",
    volume="Volume",
    fillna=True
  )
  #>0
  return df["trend_kst"].tail(1).values[0]

def getCCI(ticker):
  hist = yfinance.download(ticker, period="1d", interval="1m", auto_adjust=False)
  hist.columns = hist.columns.droplevel(1)
  df = dropna(hist)
  df = add_all_ta_features(
    df,
    open="Open",
    high="High",
    low="Low",
    close="Close",
    volume="Volume",
    fillna=True
  )
  #>0
  return df["trend_cci"].tail(1).values[0]

def main():
  while True:
    for tick in buylist:
      if (getRSI(tick) > 65 or getKST(tick) < .25):
        sellOrder(tick)
        buylist.remove(tick)
        watchlist.append(tick)
        print("sold KST: ", tick)
      elif (getRSI(tick) > 65  and (100 < getCCI(tick) or  getCCI(tick) < 0)):
        sellOrder(tick)
        buylist.remove(tick)
        watchlist.append(tick)
        print("sold TSI: ", tick)
      elif (getRSI(tick) > 80):
        sellOrder(tick)
        buylist.remove(tick)
        watchlist.append(tick)
        print("sold TSI: ", tick)

    for ticker in watchlist:
      if(getBB(ticker) == 1):
        buyOrder(ticker)
        buylist.append(ticker)
        watchlist.remove(ticker)
        print("bought BB: ", ticker)
      elif(getRSI(ticker) < 50 and getKST(ticker) > 0):
        buyOrder(ticker)
        buylist.append(ticker)
        watchlist.remove(ticker)
        print("bought KST: ", ticker)
      elif(getRSI(ticker) < 50 and ((-140 < getCCI(ticker) < -60)  or  (0 < getCCI(ticker) < 30))):
        buyOrder(ticker)
        buylist.append(ticker)
        watchlist.remove(ticker)
        print("bought CCI: ", ticker)
      elif (getRSI(ticker) < 25):
        buyOrder(ticker)
        buylist.append(ticker)
        watchlist.remove(ticker)
        print("bought RSI: ", ticker)

    time.sleep(120)


if __name__ == '__main__':
  main()


