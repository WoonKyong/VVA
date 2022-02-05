#!/usr/bin/python3
import yfinance as yf

Period = 14 # 14 year
Monitor_tickers = ['VWO', 'BND']
Attack_tickers = ['SPY', 'IWM', 'QQQ', 'VGK', 'EWJ', 'VWO', 'VNQ', 'GSG', 'GLD', 'TLT', 'HYG', 'LQD']
#Defense_tickers = ['SHV', 'IEF', 'UST']
Defense_tickers = ['SHV', 'IEF', 'LQD']
db = yf.Tickers(' '.join(Monitor_tickers + Attack_tickers + Defense_tickers))

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
            if s < 0:
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
        self.tickers = tickers
        for t in tickers:
            self.tickers[t] = self.cash / len(tickers) / self.algo.get_price(t)
            self.buy_record[t] += 1
'''
    def print_cash(self, price):
        print('Cash : ', price * self.num)
    def sell(self):
        self.cash = self.num * price * (1.0 - Fee)
        self.num = 0
        self.ticker = ''
        if self.max < self.cash:
            self.max = self.cash
        t = (self.cash - self.max) / self.max
        if self.mdd > t:
            self.mdd = t
'''

history = {}
for ticker in Monitor_tickers + Attack_tickers +  Defense_tickers:
    history[ticker] = db.tickers[ticker].history(
        period=str(Period) + 'y', interval='1mo')
daa = DAA()

for index in history[Monitor_tickers[0]].index:
    if index.day != 1:
        continue
    try:
        data = {k: history[k].loc[index] for k in history.keys()} # index가 있는지 확인 후 추가하도록 수정할것.
    except:
        print("!!! error !!!", index)
        continue
    daa.push(data)
    buy_ticker = daa.run()
    if not buy_ticker:
        continue
    print(buy_ticker)







'''
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
    if index.day != 1:
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
'''