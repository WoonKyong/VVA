#!/usr/bin/python3
import yfinance as yf
#import matplotlib.pyplot as plt

Attack_tickers = ['IVV', 'VEA', 'VWO', 'AGG', 'QQQ']
#Attack_tickers = ['IVV', 'VEA', 'VWO', 'AGG']
#Attack_tickers = ['SPY', 'VEA', 'VWO', 'AGG']
#Attack_tickers = ['VEA', 'VWO', 'AGG', 'QQQ']

Defense_tickers = ['SHY', 'IEF', 'LQD']
Period = 14
InitCash = 10000
Fee = 0.0004


class VAA:
    def __init__(self):
        self.data = []

    def push(self, data):
        self.data.append(data)

    def run(self):
        if len(self.data) < 14:
            return str('')
        best_ticket = self.__best_score_ticket(Attack_tickers, True)
        if best_ticket:
            return best_ticket
        best_ticket = self.__best_score_ticket(Defense_tickers)
        return best_ticket

    def __best_score_ticket(self, tickers, negative_check=False):
        scores = {}
        for t in tickers:
            scores[t] = ((self.data[-1][t]['Close'] / self.data[-2][t]['Close'] - 1.0) * 12 +
                         (self.data[-1][t]['Close'] / self.data[-4][t]['Close'] - 1.0) * 4 +
                         (self.data[-1][t]['Close'] / self.data[-7][t]['Close'] - 1.0) * 2 +
                         (self.data[-1][t]['Close'] / self.data[-13][t]['Close'] - 1.0))

            if negative_check and scores[t] < 0:
                return str('')
        else:
            return max(scores, key=scores.get)


class Asset:
    def __init__(self, cash):
        self.cash = cash
        self.ticker = ''
        self.num = 0
        self.max = cash
        self.min = cash
        self.mdd = 0.
        self.buy_record = dict.fromkeys(Attack_tickers + Defense_tickers, 0)

    def buy(self, ticker, num):
        self.cash = 0
        self.ticker = ticker
        self.num = num
        print('Buy ', ticker)
        self.buy_record[ticker] += 1

    def holding(self):
        self.buy_record[self.ticker] += 1

    def printCash(self, price):
        print('Cash : ', price * self.num)

    def sell(self, price):
        self.cash = self.num * price * (1.0 - Fee)
        self.num = 0
        self.ticker = ''
        if self.max < self.cash:
            self.max = self.cash
        t = (self.cash - self.max) / self.max
        if self.mdd > t:
            self.mdd = t


db = yf.Tickers(' '.join(Attack_tickers + Defense_tickers))

history = {}
for ticker in Attack_tickers + Defense_tickers:
    history[ticker] = db.tickers[ticker].history(
        period=str(Period) + 'y', interval='1mo')

vaa = VAA()
is_NaN = history[Attack_tickers[0]].isnull()
asset = Asset(InitCash)

for index in is_NaN.index:
    if index.day is not 1:
        continue

    if is_NaN.loc[index]['Open']:
        continue

    data = {k: history[k].loc[index] for k in history.keys()}

    vaa.push(data)
    buy_ticker = vaa.run()
    if not buy_ticker:
        continue

    print('----- %s -----' % index)
    if asset.ticker == buy_ticker:
        print("Holding", asset.ticker)
        asset.holding()
        asset.printCash(history[buy_ticker].loc[index]['Close'])
        continue

    if asset.cash == 0:
        price = history[asset.ticker].loc[index]['Close']
        asset.sell(price)

    price = history[buy_ticker].loc[index]['Close']
    num = asset.cash / price
    asset.buy(buy_ticker, num)
    asset.printCash(history[buy_ticker].loc[index]['Close'])

print('\n\n******* Result *******')
last_cash = history[asset.ticker].iloc[-1]['Close'] * asset.num
print('Cash change: %d -> %d' % (InitCash, round(last_cash)))
print('MDD : ', round(asset.mdd * 100, 2))
print('CAGR : ', round(((last_cash / InitCash) ** (1 / Period) - 1) * 100, 2))
print('Statistics: ', asset.buy_record)
# CAGR : {(최종 가치 ÷ 시초 가치)(1/투자기간) – 1} × 100
