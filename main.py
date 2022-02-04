#!/usr/bin/python3
import yfinance as yf
#import matplotlib.pyplot as plt

Attack_tickers = ['SPY', 'VEA', 'VWO', 'AGG', 'QQQ']
#Attack_tickers = ['SPY', 'VEA', 'VWO', 'AGG']

Depense_tickers = ['SHY', 'IEF', 'LQD']
Period = '14y'
InitCash = 100000

class VAA:
    def __init__(self):
        self.attack = []
        self.depense = []

    def push(self, attack, depense):
        self.attack.append(attack)
        self.depense.append(depense)

    def run(self):
        if len(self.attack) < 15:
            return "None"
        # 1개월 수익
        profit = []
        for l in range(len(self.attack[-1])):
            profit.append(
                (self.attack[-1][l]['Close'] / self.attack[-1][l]['Open'] -
                 1.0) * 12)
            profit[-1] += (self.attack[-1][l]['Close'] /
                           self.attack[-4][l]['Close'] - 1.0) * 4
            profit[-1] += (self.attack[-1][l]['Close'] /
                           self.attack[-7][l]['Close'] - 1.0) * 2
            profit[-1] += (
                self.attack[-1][l]['Close'] / self.attack[-13][l]['Close'] -
                1.0)
            if profit[-1] < 0:
                break
        else:
            max_index = profit.index(max(profit))
            return Attack_tickers[max_index]

        profit = []
        for l in range(len(self.depense[-1])):
            profit.append(
                (self.depense[-1][l]['Close'] / self.depense[-1][l]['Open'] -
                 1.0) * 12)
            profit[-1] += (self.depense[-4][l]['Close'] /
                           self.depense[-1][l]['Close'] - 1.0) * 4
            profit[-1] += (self.depense[-7][l]['Close'] /
                           self.depense[-1][l]['Close'] - 1.0) * 2
            profit[-1] += (
                self.depense[-13][l]['Close'] / self.depense[-1][l]['Close'] -
                1.0)

        max_index = profit.index(max(profit))
        return Depense_tickers[max_index]


class Asset:
    def __init__(self, cash):
        self.cash = cash
        self.ticker = ''
        self.num = 0
        self.max = cash
        self.min = cash
        self.mdd = 0.

    def buy(self, ticker, num):
        self.cash = 0
        self.ticker = ticker
        self.num = num
        print('Buy ', ticker)

    def printCash(self, price):
        print('Cash : ', price * self.num)

    def sell(self, price):
        #self.cash = self.num * (price * 0.998)
        self.cash = self.num * price
        self.num = 0
        self.ticker = ''
        print(self.cash)
        if self.max < self.cash:
            self.max = self.cash
        t = (self.cash - self.max) / self.max
        if self.mdd > t:
            self.mdd = t


db = yf.Tickers(' '.join(Attack_tickers + Depense_tickers))

history = {}
for ticker in Attack_tickers + Depense_tickers:
  history[ticker] = db.tickers[ticker].history(period=Period, interval='1mo')

vaa = VAA()
is_NaN = history[Attack_tickers[0]].isnull()

asset = Asset(InitCash)

last_cash = 0
for index in is_NaN.index:
    if is_NaN.loc[index]['Open']:
        continue

    attack_data = []
    depense_data = []

    for i in Attack_tickers:
        attack_data.append(history[i].loc[index])
    for i in Depense_tickers:
        depense_data.append(history[i].loc[index])
    vaa.push(attack_data, depense_data)
    buy_ticker = vaa.run()
    if buy_ticker == 'None':
        continue

    if asset.ticker == buy_ticker:
        asset.printCash(history[buy_ticker].loc[index]['Close'])
        continue

    if asset.cash == 0:
      price = history[asset.ticker].loc[index]['Close']
      asset.sell(price)
        
    price = history[buy_ticker].loc[index]['Close']
    num = asset.cash / price
    print(index)
    asset.buy(buy_ticker, num)
last_cash = history[asset.ticker].iloc[-1]['Close'] * asset.num;
print('mdd : ', asset.mdd)
print('last cash : ', last_cash)
print('CAGR : ', (last_cash / InitCash) ** (1/14) - 1)
#CAGR : {(최종 가치 ÷ 시초 가치)(1/투자기간) – 1} × 100

