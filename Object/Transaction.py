import datetime
from enum import Enum
from currency_converter import CurrencyConverter

from typing import List


class Transaction_Type(Enum):
    Account_balance_to_mirror = 10
    Adjustment = 20
    Deposit = 30
    Open_Position = 40
    Profit_Loss_of_Trade = 50
    Rollover_fee = 60
    Dividende = 61
    Start_Copy = 70
    Stop_Copy = 80
    Mirror_balance_to_account = 90
    Edit_Stop_Loss = 91
    Pause_Copy = 92
    Resume_Copy = 93
    NOT_DEFINE = -1

class Transaction():
    date:datetime
    account_Balance: float
    type:Transaction_Type
    details:str
    ID: int
    amount:float
    realized_Equity_Change: float
    realized_Equity: float
    NWA: str

    def __init__(self, date:str, account_Balance:float, type:str, details:str, ID:int, amount:float, realized_Equity_Change:float, realized_Equity:float, NWA:str):
        self.date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        self.account_Balance = float(account_Balance)
        self.type = self._convert_type(type, details)
        self.details = details
        self.ID = ID
        self.amount = amount
        self.realized_Equity = float(realized_Equity)
        self.realized_Equity_Change = float(realized_Equity_Change)
        self.NWA = NWA

    def _convert_type(self, type:str, details:str):
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
            if 'dividend' in details:
                return Transaction_Type.Dividende
            else:
                return Transaction_Type.Rollover_fee
        elif 'Start Copy' in type:
            return Transaction_Type.Start_Copy
        elif 'Stop Copy' in type:
            return Transaction_Type.Stop_Copy
        elif 'Mirror balance to account' in type:
            return Transaction_Type.Mirror_balance_to_account
        elif 'Edit Stop Loss' in type:
            return Transaction_Type.Edit_Stop_Loss
        elif 'Pause Copy' in type:
            return Transaction_Type.Pause_Copy
        elif 'Resume Copy' in type:
            return Transaction_Type.Resume_Copy
        else:
            print(f'found a transaction tpye that is not define ({type})')

    def convert_toCurrency(self, toCurrency:str, cc:CurrencyConverter, default_currency:str='USD'):
        self.account_Balance = self._round(self.account_Balance, toCurrency, cc, default_currency)
        self.amount = self._round(self.amount, toCurrency, cc, default_currency, True)
        self.realized_Equity = self._round(self.realized_Equity, toCurrency, cc, default_currency)
        self.realized_Equity_Change = self._round(self.realized_Equity_Change, toCurrency, cc, default_currency)

    def _round(self, value:float, toCurrency:str, cc:CurrencyConverter, default_currency:str='USD', not_null=False):
        converted_value = cc.convert(value, default_currency, toCurrency, date=self.date)
        return converted_value