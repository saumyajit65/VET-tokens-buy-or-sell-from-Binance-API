import ccxt
#import seaborn as sns
import pplyr
import config
import pandas as pd
import psutil
pd.set_option("display.max_rows", None, "display.max_columns", None) #to set no limit for columns and rows
import streamlit as st
import warnings
import altair as alt
warnings.filterwarnings('ignore')

#Binance details
#from binance import Client
from binance.spot import Spot
from binance.spot import Spot as Pilent
BINANCE_API_KEY1 = '' #put the api keys from your account here...No brackets or codes needed
BINANCE_SECRET_KEY1 = '' #put the api keys from your account here...No brackets or codes needed

import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.animation import FuncAnimation
from matplotlib import interactive
import numpy as np
from datetime import datetime
import time

#references
#https://towardsdatascience.com/learn-what-a-depth-chart-is-and-how-to-create-it-in-python-323d065e6f86
#https://www.youtube.com/watch?v=KdoGekqz2hg&list=PLXWyO3HSkNw6Qa2KjrYUNa_YZeLbIXOd2&index=4&ab_channel=Algovibes
#https://www.youtube.com/watch?v=KdoGekqz2hg&ab_channel=Algovibes


#Data extraction 1 declarations
exchange = ccxt.binance({  #this is not binanceus but only binance
    "apiKey": config.BINANCE_API_KEY,
    "secret": config.BINANCE_SECRET_KEY
})
asset = 'VET/BUSD'

#Data extraction 1 for Volume and price
def getdataextraction1():
    Data = exchange.fetch_ohlcv(asset, timeframe='1m', limit=60, params={})
    df = pd.DataFrame(Data[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Europe/Berlin')
    df['Avg price'] = (df['high'] + df['low']) / 2
    df['difference'] = df['close'] - df['open']
    # df['difference'] = df['Avg price'].diff()
    df['abs_difference'] = abs(df['difference'])
    df['factor'] = df['difference'] / df['abs_difference']
    df = df.fillna(1)
    df['volume'] = df['volume'] * df['factor']
    pd.set_option('expand_frame_repr', False)  # to print dataframe in one line
    df = df.set_index('timestamp')
    df = df.astype(float)
    return df

#Data extraction 2 for Bids and asks ... A depth chart is a kind of visualization that informs us about the demand and supply of a particular asset
#Data extractions 2 in dataframe format
def getdataextraction2():
    df_list = []
    client1 = Spot()
    client1 = Spot(key=BINANCE_API_KEY1, secret=BINANCE_SECRET_KEY1)
    # print(client1.account())
    client1 = Spot(base_url='https://testnet.binance.vision')
    spot_client = Pilent(base_url="https://api3.binance.com")
    depth_dict = spot_client.depth("VETBUSD", limit=100)  # limit shall give 100 bids and 100 asks
    for side in ["bids", "asks"]:
        df = pd.DataFrame(depth_dict[side], columns=["price", "quantity"], dtype=float)
        df["side"] = side
        df['Amount'] = df['price'] * df['quantity']
        df_list.append(df)

    df2 = pd.concat(df_list).reset_index(drop=True)
    df2=df2.drop(['price', 'quantity'], axis=1)
    return df2



#For plotting the prices
plt.style.use('ggplot')

def dataplot1(i):
    data1_volume = getdataextraction1()
    plt.cla()  # clear the axes to avoid getting graphs for every step
    colors = ['g' if m > 0 else 'r' for m in data1_volume['volume']]
    plt.plot(data1_volume.index, data1_volume['volume'])
    plt.xlabel("Timestamp of 60 minutes window (Update every 60 seconds)... Remember fibonacci retracement, a fall after a big pump ")
    plt.ylabel("Token Bought or Sold ('VET/BUSD')")
    plt.title(f"LIVE VET Tokens traded ('VET/BUSD')... Take risk during huge volume pump")
    plt.tight_layout()


def dataplot2(j):
    data2_bidask = getdataextraction2()
    data2_bidask = data2_bidask.groupby('side').Amount.sum().reset_index()  # reset index makes the groupby result into a dataframe :D
    plt.cla()  # clear the axes to avoid getting graphs for every step
    plt.plot( data2_bidask['side'],data2_bidask['Amount'] )
    plt.xlabel("If above pattern shape ='Forward Slash' then BID > ASK, viceversa for pattern='Backslash'")
    plt.ylabel("Cumulative amount (Qty*price)")
    plt.title(f"SCENARIO OF 6% VARIANCE (@timewindow 100minutes) FROM CURRENT PRICE for Cumulative BIDS vs ASKS (VET/BUSD)")
    plt.tight_layout()



f1 = plt.figure(1)
Dataplot_show1 = FuncAnimation(plt.gcf(),dataplot1,8000)
plt.tight_layout()
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)
plt.show()


#Plot of bids and asks
#fig, ax = plt.subplots(figsize=(18, 5))
#    ax.set_title(f"VETUSDT BID & ASK Histogram")
#    sns.histplot(x="price", hue="side", weights="quantity",
#                 data=data2_bidask, palette=["green", "red"],
#                 ax=ax)
#    ax.set_xlabel("Price")
#    ax.set_ylabel("Qty")
#    plt.ticklabel_format(style='plain')
#    plt.gcf().autofmt_xdate()
#    plt.tight_layout()

#Plot volume graph

#schedule.every(10).seconds.do()

#.........check my balance as of now
#print(exchange.fetch_balance())
#print(exchange.fetch_order_book())







