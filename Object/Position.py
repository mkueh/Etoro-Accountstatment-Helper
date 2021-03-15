import datetime
from enum import Enum
from currency_converter import CurrencyConverter
from .Transaction import Transaction, Transaction_Type

from typing import List

class Position_Action(Enum):
    BUY = 1
    SELL = 2
    NOT_DEFINE = -1

class Position():

    ID:int
    action:str
    copyTraderName: str
    amount_in_USD: float
    units: float
    open_Rate_marketCurrency: float
    close_Rate_marketCurrency: float
    spread: float
    profit: float
    open_date: datetime
    close_date: datetime
    take_profit_rate_marketCurrency:float
    stop_LossRate_marketCurrency: float
    rolloverFees_and_dividends: float
    isReal: bool
    leverage: float
    notes: str
    transactions: List[Transaction]

    def __init__(self, ID: int, action: str, copyTraderName: str, amount: float, units: float, open_Rate: float,
                 close_Rate: float, spread: float, profit: float, open_date: str, close_date: str,
                 take_profit_rate: float, stop_LossRate: float, rolloverFees_and_dividends: float, isReal: str,
                 leverage: float, notes: str):
        self.ID = ID
        self.action = self._convert_action(action)
        self.copyTraderName = copyTraderName
        self.amount_in_USD = float(amount.replace(',', '.'))
        self.units = float(units.replace(',', '.'))
        self.open_Rate_marketCurrency = float(open_Rate.replace(',', '.'))
        self.close_Rate_marketCurrency = float(close_Rate.replace(',', '.'))
        self.spread = float(spread.replace(',', '.'))
        self.profit = float(profit.replace(',', '.'))
        self.open_date = open_date
        self.close_date = close_date
        self.take_profit_rate_marketCurrency = float(take_profit_rate.replace(',', '.'))
        self.stop_LossRate_marketCurrency = float(stop_LossRate.replace(',', '.'))
        self.rolloverFees_and_dividends = float(rolloverFees_and_dividends.replace(',', '.'))
        self.isReal = isReal
        self.leverage = float(leverage)
        self.notes = str(notes)
        self.transactions = []

        self._convert_date()
        self._convert_real()
        self.action = self._convert_action(action)

    def __eq__(self, other):
        if isinstance(other, Position):
            if self.ID == other.ID:
                return True
        elif isinstance(other, int):
            if self.ID == other:
                return True
        elif isinstance(other, Transaction):
            if self.ID == other.ID:
                return True
        else:
            return False

    def _convert_date(self):
        self.open_date = datetime.datetime.strptime(self.open_date, '%d.%m.%Y %H:%M')
        self.close_date = datetime.datetime.strptime(self.close_date, '%d.%m.%Y %H:%M')

    def _convert_real(self):
        if self.isReal == 'CFD':
            self.isReal = False
        elif self.isReal == 'Real':
            self.isReal = True
        else:
            self.isReal = 'columne Is Real contains a unkown value'
            print('columne Is Real contains a unkown value')

    def _convert_action(self, action:str):
        if 'Buy' in action[:4]:
            return Position_Action.BUY
        elif 'Sell' in action[:4]:
            return Position_Action.SELL
        else:
            print(f'found a position action that is not define ({action})')
            return Position_Action.NOT_DEFINE

    def get_Rollover_fee(self):
        rollover_fee = 0
        for transaction in self.transactions:
            if transaction.type == Transaction_Type.Rollover_fee:
                rollover_fee += transaction.amount_USD
        return rollover_fee

    def convert_toCurrency(self, toCurrency:str, cc:CurrencyConverter, default_currency:str='USD'):
        investment_start_USD = self.amount_in_USD
        investment_stop_USD = self.amount_in_USD + self.profit

        investment_start_newCurrency = cc.convert(investment_start_USD, default_currency, toCurrency, date=self.open_date)
        investment_stop_newCurrency = cc.convert(investment_stop_USD, default_currency, toCurrency, date=self.close_date)

        for transaction in self.transactions:
            transaction.convert_toCurrency(toCurrency, cc, default_currency)

        self.profit = investment_stop_newCurrency - investment_start_newCurrency

