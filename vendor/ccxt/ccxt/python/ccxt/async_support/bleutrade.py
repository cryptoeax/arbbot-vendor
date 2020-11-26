# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.bittrex import bittrex
import math
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidOrder


class bleutrade (bittrex):

    def describe(self):
        return self.deep_extend(super(bleutrade, self).describe(), {
            'id': 'bleutrade',
            'name': 'Bleutrade',
            'countries': ['BR'],  # Brazil
            'rateLimit': 1000,
            'version': 'v2',
            'has': {
                'CORS': True,
                'fetchTickers': True,
                'fetchOrders': True,
                'fetchClosedOrders': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30303000-b602dbe6-976d-11e7-956d-36c5049c01e7.jpg',
                'api': {
                    'public': 'https://bleutrade.com/api',
                    'account': 'https://bleutrade.com/api',
                    'market': 'https://bleutrade.com/api',
                },
                'www': 'https://bleutrade.com',
                'doc': 'https://bleutrade.com/help/API',
                'fees': 'https://bleutrade.com/help/fees_and_deadlines',
            },
            'fees': {
                'funding': {
                    'withdraw': {
                        'ADC': 0.1,
                        'BTA': 0.1,
                        'BITB': 0.1,
                        'BTC': 0.001,
                        'BCC': 0.001,
                        'BTCD': 0.001,
                        'BTG': 0.001,
                        'BLK': 0.1,
                        'CDN': 0.1,
                        'CLAM': 0.01,
                        'DASH': 0.001,
                        'DCR': 0.05,
                        'DGC': 0.1,
                        'DP': 0.1,
                        'DPC': 0.1,
                        'DOGE': 10.0,
                        'EFL': 0.1,
                        'ETH': 0.01,
                        'EXP': 0.1,
                        'FJC': 0.1,
                        'BSTY': 0.001,
                        'GB': 0.1,
                        'NLG': 0.1,
                        'HTML': 1.0,
                        'LTC': 0.001,
                        'MONA': 0.01,
                        'MOON': 1.0,
                        'NMC': 0.015,
                        'NEOS': 0.1,
                        'NVC': 0.05,
                        'OK': 0.1,
                        'PPC': 0.1,
                        'POT': 0.1,
                        'XPM': 0.001,
                        'QTUM': 0.1,
                        'RDD': 0.1,
                        'SLR': 0.1,
                        'START': 0.1,
                        'SLG': 0.1,
                        'TROLL': 0.1,
                        'UNO': 0.01,
                        'VRC': 0.1,
                        'VTC': 0.1,
                        'XVP': 0.1,
                        'WDC': 0.001,
                        'ZET': 0.1,
                    },
                },
            },
            'commonCurrencies': {
                'EPC': 'Epacoin',
            },
            'exceptions': {
                'Insufficient fundsnot ': InsufficientFunds,
                'Invalid Order ID': InvalidOrder,
                'Invalid apikey or apisecret': AuthenticationError,
            },
            'options': {
                'parseOrderStatus': True,
            },
        })

    async def fetch_markets(self):
        markets = await self.publicGetMarkets()
        result = []
        for p in range(0, len(markets['result'])):
            market = markets['result'][p]
            id = market['MarketName']
            baseId = market['MarketCurrency']
            quoteId = market['BaseCurrency']
            base = self.common_currency_code(baseId)
            quote = self.common_currency_code(quoteId)
            symbol = base + '/' + quote
            precision = {
                'amount': 8,
                'price': 8,
            }
            active = self.safe_string(market, 'IsActive')
            if active == 'true':
                active = True
            elif active == 'false':
                active = False
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'active': active,
                'info': market,
                'lot': math.pow(10, -precision['amount']),
                'precision': precision,
                'limits': {
                    'amount': {
                        'min': market['MinTradeSize'],
                        'max': None,
                    },
                    'price': {
                        'min': None,
                        'max': None,
                    },
                    'cost': {
                        'min': 0,
                        'max': None,
                    },
                },
            })
        return result

    def parse_order_status(self, status):
        statuses = {
            'OK': 'closed',
            'OPEN': 'open',
            'CANCELED': 'canceled',
        }
        if status in statuses:
            return statuses[status]
        else:
            return status

    async def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        # Possible params
        # orderstatus(ALL, OK, OPEN, CANCELED)
        # ordertype(ALL, BUY, SELL)
        # depth(optional, default is 500, max is 20000)
        await self.load_markets()
        market = None
        if symbol is not None:
            await self.load_markets()
            market = self.market(symbol)
        else:
            market = None
        response = await self.accountGetOrders(self.extend({'market': 'ALL', 'orderstatus': 'ALL'}, params))
        return self.parse_orders(response['result'], market, since, limit)

    async def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        response = await self.fetch_orders(symbol, since, limit, params)
        return self.filter_by(response, 'status', 'closed')

    def get_order_id_field(self):
        return 'orderid'

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        request = {
            'market': self.market_id(symbol),
            'type': 'ALL',
        }
        if limit is not None:
            request['depth'] = limit  # 50
        response = await self.publicGetOrderbook(self.extend(request, params))
        orderbook = self.safe_value(response, 'result')
        if not orderbook:
            raise ExchangeError(self.id + ' publicGetOrderbook() returneded no result ' + self.json(response))
        return self.parse_order_book(orderbook, None, 'buy', 'sell', 'Rate', 'Quantity')
