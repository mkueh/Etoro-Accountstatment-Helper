import datetime
from enum import Enum
from currency_converter import CurrencyConverter

from typing import List


class Transaction_Type(Enum):
    Account_balance_to_mirror = 1
    Adjustment = 2
    Deposit = 3
    Open_Position = 4
    Profit_Loss_of_Trade = 5
    Rollover_fee = 6
    Start_Copy = 7
    Stop_Copy = 8
    NOT_DEFINE = -1

class Transaction():
    date:datetime
    account_Balance: float
    type:str
    details:str
    ID: int
    amount_USD:float
    realized_Equity_Change_USD: float
    realized_Equity_USD: float
    NWA: str

    def __init__(self, date:str, account_Balance:float, type:str, details:str, ID:int, amount:float, realized_Equity_Change:float, realized_Equity:float, NWA:str):
        self.date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        self.account_Balance = float(account_Balance)
        self.type = self._convert_type(type)
        self.details = details
        self.ID = ID
        self.amount_USD = amount
        self.realized_Equity_USD = float(realized_Equity)
        self.realized_Equity_Change_USD = float(realized_Equity_Change)
        self.NWA = NWA

    def _convert_type(self, type:str):
        if 'Profit/Loss of Trade' in type:
            return Transaction_Type.Profit_Loss_of_Trade
        elif 'Adjustment' in type:
            return Transaction_Type.Adjustment
        elif 'Account balance to mirror' in type:
            return Transaction_Type.Account_balance_to_mirror
        elif 'Deposit' in type:
            return Transaction_Type.Deposit
        elif 'Open Position' in type:
            return Transaction_Type.Open_Position
        elif 'Rollover Fee' in type:
            return Transaction_Type.Rollover_fee
        elif 'Start Copy' in type:
            return Transaction_Type.Start_Copy
        elif 'Stop Copy' in type:
            return Transaction_Type.Stop_Copy
        else:
            print(f'found a transaction tpye that is not define ({type})')

    def convert_toCurrency(self, toCurrency:str, cc:CurrencyConverter, default_currency:str='USD'):
        self.account_Balance = cc.convert(self.account_Balance, default_currency, toCurrency, date=self.date)
        self.amount_USD = cc.convert(self.amount_USD, default_currency, toCurrency, date=self.date)
        self.realized_Equity_USD = cc.convert(self.realized_Equity_USD, default_currency, toCurrency, date=self.date)
        self.realized_Equity_Change_USD = cc.convert(self.realized_Equity_Change_USD, default_currency, toCurrency, date=self.date)
