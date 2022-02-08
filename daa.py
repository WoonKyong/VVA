#!/usr/bin/python3
import yfinance as yf

Period = 14 # 14 year
Monitor_tickers = ['VWO', 'BND']
Attack_tickers = ['SPY', 'IWM', 'QQQ', 'VGK', 'EWJ', 'VWO', 'VNQ', 'GSG', 'GLD', 'TLT', 'HYG', 'LQD']
#Defense_tickers = ['SHV', 'IEF', 'UST']
Defense_tickers = ['SHV', 'IEF', 'LQD']

db = yf.Tickers(' '.join(Monitor_tickers + Attack_tickers + Defense_tickers))
InitCash = 10000

class DAA:
    def __init__(self):
        self.data = []

    def push(self, data):
        self.data.append(data)

    def run(self):
        if len(self.data) < 14:
            return {}
        buy_candidate = Attack_tickers
        buy_num = 2
        for t in Monitor_tickers:
            s = self.__get_score(t)
            if s < 0.0:
                print(t, s)
                buy_candidate = Defense_tickers
                buy_num = 1
                break
        scores = {}
        for t in buy_candidate:
            scores[t] = self.__get_score(t)
        buy_tickers = sorted(scores, key=scores.get, reverse=True)[:buy_num]
        return buy_tickers

    def get_price(self, ticket):
        return self.data[-1][ticket]['Close']

    def __get_score(self, t):
        return ((self.data[-1][t]['Close'] / self.data[-2][t]['Close'] - 1.0) * 12 +
                     (self.data[-1][t]['Close'] / self.data[-4][t]['Close'] - 1.0) * 4 +
                     (self.data[-1][t]['Close'] / self.data[-7][t]['Close'] - 1.0) * 2 +
                     (self.data[-1][t]['Close'] / self.data[-13][t]['Close'] - 1.0))


class Asset:
    def __init__(self, cash, algo):
        self.cash = cash
        self.algo = algo
        self.tickers = {}

        self.max = cash
        self.min = cash
        self.mdd = 0.
        self.buy_record = dict.fromkeys(Attack_tickers + Defense_tickers, 0)

    def buy(self, tickers):
        print('Buy ', tickers)
        if self.cash == 0:
            for t in self.tickers.keys():
                self.cash += self.tickers[t] * self.algo.get_price(t)
        if self.max < self.cash:
            self.max = self.cash
        mdd = (self.cash - self.max) / self.max
        if self.mdd > mdd:
            self.mdd = mdd

        self.tickers.clear()
        for t in tickers:
            print(self.cash, len(tickers), self.algo.get_price(t))
            l = self.cash / len(tickers) / self.algo.get_price(t)
            self.tickers[t] = self.cash / len(tickers) / self.algo.get_price(t)
            self.buy_record[t] += 1
        self.cash = 0

    def print_cash(self):
        cash = 0.
        for t in self.tickers.keys():
            cash += self.tickers[t] * self.algo.get_price(t)
        print("Cash : ", cash)

    def get_current_asset(self):
        cash = 0.
        for t in self.tickers.keys():
            cash += self.tickers[t] * self.algo.get_price(t)
        return cash


history = {}
for ticker in Monitor_tickers + Attack_tickers +  Defense_tickers:
    history[ticker] = db.tickers[ticker].history(
        period=str(Period) + 'y', interval='1mo')

daa = DAA()
asset = Asset(InitCash, daa)

for index in history[Monitor_tickers[0]].index:
    if index.day != 1:
        continue

    try:
        data = {k: history[k].loc[index] for k in history.keys()}
    except:
        print("!!! error !!!", index)
        continue
    daa.push(data)
    buy_ticker = daa.run()
    if not buy_ticker:
        continue
    print(buy_ticker)
    asset.buy(buy_ticker)

print('\n\n******* Result *******')
last_cash = asset.get_current_asset()
print('Cash change: %d -> %d' % (InitCash, round(last_cash)))
print('MDD : ', round(asset.mdd * 100, 2))
print('CAGR : ', round(((last_cash / InitCash) ** (1 / Period) - 1) * 100, 2))
print('Statistics: ', asset.buy_record)
# CAGR : {(최종 가치 ÷ 시초 가치)(1/투자기간) – 1} × 100
