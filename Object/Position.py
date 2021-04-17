import datetime, investpy
from enum import Enum
from currency_converter import CurrencyConverter
from .Transaction import Transaction, Transaction_Type
from .InvestPyCache import InvestPyCache

from typing import List

class Pair_Type(Enum):
    STOCK = 1
    CURRENCY = 2
    CRYPTO = 3
    ETF = 4
    INDICIES = 5
    NOT_DEFINE = -1


class Position_Action(Enum):
    BUY = 1
    SELL = 2
    NOT_DEFINE = -1

class Position_Type(Enum):
    REAL = 1
    CFD = 2
    NOT_DEFINE = -1

class Position():

    ID:int
    action:Position_Action

    pair_type: Pair_Type
    pair_info: investpy.search.SearchObj
    item_name: str

    copyTraderName: str
    units: float
    open_Rate_marketCurrency: float
    close_Rate_marketCurrency: float
    open_date: datetime
    close_date: datetime
    take_profit_rate_marketCurrency: float
    isReal: bool
    leverage: float
    notes: str
    transactions: List[Transaction]

    start_amount: float = 0
    change_amount: float = 0
    rollover_fee: float = 0
    devidende: float = 0

    def __init__(self, ID: int, action: str, copyTraderName: str, units: float, open_Rate: float,
                 close_Rate: float, open_date: str, close_date: str,
                 take_profit_rate: float, stop_LossRate: float, isReal: str,
                 leverage: float, notes: str):
        self.ID = ID
        self.action = self._convert_action(action)
        self.item_name = action[4:]

        self.copyTraderName = copyTraderName
        self.units = float(units.replace(',', '.'))
        self.open_Rate_marketCurrency = float(open_Rate.replace(',', '.'))
        self.close_Rate_marketCurrency = float(close_Rate.replace(',', '.'))

        self.open_date = self._convert_date(open_date, '%d.%m.%Y %H:%M')
        self.close_date = self._convert_date(close_date, '%d.%m.%Y %H:%M')

        self.take_profit_rate_marketCurrency = float(take_profit_rate.replace(',', '.'))
        self.stop_LossRate_marketCurrency = float(stop_LossRate.replace(',', '.'))

        self.isReal = self._convert_real(isReal)
        self.leverage = float(leverage)
        self.notes = str(notes)
        self.transactions = []

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

    def _convert_date(self, date:datetime, format:str):
        return datetime.datetime.strptime(date, '%d.%m.%Y %H:%M')

    def _convert_real(self, isReal:str):
        if isReal == 'CFD':
            return Position_Type.CFD
        elif isReal == 'Real':
            return Position_Type.REAL
        else:
            return Position_Type.NOT_DEFINE
            print('columne Is Real contains a unkown value')

    def _convert_action(self, action:str):
        if 'Buy' in action[:4]:
            return Position_Action.BUY
        elif 'Sell' in action[:4]:
            return Position_Action.SELL
        else:
            print(f'found a position action that is not define ({action})')
            return Position_Action.NOT_DEFINE

    def recalc_values(self):
        self.start_amount = 0
        self.change_amount = 0
        self.rollover_fee = 0
        self.devidende = 0

        for trans in self.transactions:
            if trans.type == Transaction_Type.Open_Position:
                self.start_amount = trans.amount
            elif trans.type == Transaction_Type.Profit_Loss_of_Trade:
                self.change_amount = trans.amount
            elif trans.type == Transaction_Type.Rollover_fee:
                self.rollover_fee += trans.amount
            elif trans.type == Transaction_Type.Dividende:
                self.devidende += trans.amount

    def get_Transactions(self, type:Transaction_Type):
        out: List[Transaction] = []
        for t in self.transactions:
            if t.type == type:
                out.append(t)
        return out

    def fill_infos_with_Transaction(self, investPyCache:InvestPyCache):
        base_transition = None

        #try with openP
        ts_open_position = self.get_Transactions(Transaction_Type.Open_Position)
        if len(ts_open_position) > 0:
            base_transition_details = ts_open_position[0]
        else:
            #try with closePosition
            ts_close_position = self.get_Transactions(Transaction_Type.Profit_Loss_of_Trade)
            if len(ts_close_position) > 0:
                base_transition_details = ts_close_position[0]

        if base_transition_details is None:
            self.pair_type = Pair_Type.NOT_DEFINE
            self.pair_info = None
            return

        type, info = self._get_pair_infos_by_transaction(base_transition_details, investPyCache)
        self.pair_type = type
        self.pair_info = info


    def _get_pair_infos_by_transaction(self, transaction: Transaction, investPyCache:InvestPyCache):
        default_details = transaction.details
        respone = investPyCache.get_pairType(default_details)

        if not respone[0] is None:
            type = self._match_pairType(respone[0].pair_type)


    def _match_pairType(self, str_pairType:str) -> Pair_Type:
        if str_pairType == 'stocks':
            return Pair_Type.STOCK
        else:
            return Pair_Type.NOT_DEFINE


    def get_Rollover_fee(self):
        return self.rollover_fee

    def get_Profit(self, check_divdende:(datetime, datetime) = None):
        return_value = self.change_amount
        if check_divdende is not None:
            start_date = check_divdende[0]
            stop_date = check_divdende[1]

            for transaction in self.transactions:
                if transaction.type == Transaction_Type.Dividende:
                    if not (transaction.date >= start_date and transaction.date <= stop_date):
                        return_value -= transaction.amount

        return return_value

    def convert_toCurrency(self, toCurrency:str, cc:CurrencyConverter, default_currency:str='USD'):
        for transaction in self.transactions:
            transaction.convert_toCurrency(toCurrency, cc, default_currency)
        self.recalc_values()


