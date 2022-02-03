#!/usr/bin/python
import yfinance as yf
#import matplotlib.pyplot as plt

Attack_tickers = ['SPY', 'VEA', 'VWO', 'AGG', 'QQQ']
Depense_tickers = ['SHY', 'IEF', 'LQD']
Period = '14y'


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
        print(ticker, num)

    def update(self, price):
        print(price * ticker.num)

    def sell(self, price):
        self.cash = self.num * (price * 0.998)
        self.num = 0
        self.ticker = ''
        print(self.cash)
        if self.max < self.cash:
            self.max = self.cash
        t = (self.cash - self.max) / self.max
        if self.mdd > t:
            self.mdd = t


db = yf.Tickers(' '.join(Attack_tickers + Depense_tickers))
print(db)