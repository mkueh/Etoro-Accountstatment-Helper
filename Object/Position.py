import datetime, investpy
from enum import Enum
from currency_converter import CurrencyConverter
from .Transaction import Transaction, Transaction_Type
from .EtoroAssetHelperPyCache import EtoroAssetHelperPyCache

from typing import List

class Pair_Type(Enum):
    STOCK = 1
    CURRENCY = 2
    CRYPTO = 3
    ETF = 4
    INDICIES = 5
    CERTIFICATES = 6
    COMMODITIES = 7
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
    _assetHelper: EtoroAssetHelperPyCache
    _currencyConverter: CurrencyConverter

    #Data from the xlsx
    ID:int
    copyTraderName: str
    units: float
    open_Rate_marketCurrency: float
    close_Rate_marketCurrency: float
    open_date: datetime
    close_date: datetime
    take_profit_rate_marketCurrency: float
    leverage: float
    notes: str

    #generated data
    positionType: Position_Type
    action:Position_Action
    pair_type: Pair_Type
    pair_info: investpy.search.SearchObj
    item_name: str
    _transactions: List[Transaction]

    start_amount: float = 0
    change_amount: float = 0
    rollover_fee: float = 0
    devidende: float = 0

    def __init__(self, ID: int, action: str, copyTraderName: str, units: float, open_Rate: float,
                 close_Rate: float, open_date: str, close_date: str,
                 take_profit_rate: float, stop_LossRate: float, isReal: str,
                 leverage: float, notes: str, assetHelper:EtoroAssetHelperPyCache, currencyConverter:CurrencyConverter):
        self._assetHelper = assetHelper
        self._currencyConverter = currencyConverter

        self.ID = ID
        self.action = self._convert_action(action)
        self.item_name = action[4:].strip()  #remove BUY/SELL

        self.copyTraderName = copyTraderName
        self.units = float(units.replace(',', '.'))
        self.open_Rate_marketCurrency = float(open_Rate.replace(',', '.'))
        self.close_Rate_marketCurrency = float(close_Rate.replace(',', '.'))

        self.open_date = self._convert_date(open_date, '%d.%m.%Y %H:%M')
        self.close_date = self._convert_date(close_date, '%d.%m.%Y %H:%M')

        self.take_profit_rate_marketCurrency = float(take_profit_rate.replace(',', '.'))
        self.stop_LossRate_marketCurrency = float(stop_LossRate.replace(',', '.'))

        self.positionType = self._convert_real(isReal)
        self.leverage = float(leverage)
        self.notes = str(notes) #always empty?
        self._transactions = []

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

    #DATA TO ENUM
    def _convert_date(self, date:datetime, format:str = '%d.%m.%Y %H:%M'):
        return datetime.datetime.strptime(date, format)

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

    def _convert_pairType_str(self, pairType:str):
        if pairType == 'Stocks':
            return Pair_Type.STOCK
        elif pairType == 'ETF':
            return Pair_Type.ETF
        elif pairType == 'Currencies':
            return Pair_Type.CURRENCY
        elif pairType == 'Indices':
            return Pair_Type.INDICIES
        elif pairType == 'Cryptocurrencies':
            return Pair_Type.CRYPTO
        elif pairType == 'Commodities':
            return Pair_Type.COMMODITIES
        else:
            return Pair_Type.NOT_DEFINE

    def _convert_pairType(self):
        base_transition = None
        #try with openP
        ts_open_position = self.get_transactions(Transaction_Type.Open_Position)
        if len(ts_open_position) > 0:
            base_transition_details = ts_open_position[0]
        else:
            #try with closePosition
            ts_close_position = self.get_transactions(Transaction_Type.Profit_Loss_of_Trade)
            if len(ts_close_position) > 0:
                base_transition_details = ts_close_position[0]

        if base_transition_details is None:
            print('found an position without open or close transaction')
            print('without this information, no pair type can be setten')
            self.pair_type = Pair_Type.NOT_DEFINE
            self.pair_info = None
            return

        type, info = self._get_pair_infos_by_transaction(base_transition_details, self.item_name, self._assetHelper)
        self.pair_type = type
        self.pair_info = info

    def _get_pair_infos_by_transaction(self, transaction: Transaction, item_name:str, investPyCache:EtoroAssetHelperPyCache):
        default_details = transaction.details
        etoro_assets_info = investPyCache.get_pairType(default_details, item_name)

        if not etoro_assets_info is None:
            type = self._convert_pairType_str(etoro_assets_info['instrument type'])
            return type, etoro_assets_info
        else:
            return None, None

    # DATA TO ENUM

    def set_transactions(self, transactions:List[Transaction]):
        self._transactions = transactions
        self._convert_pairType()
        self._calc_values()

    # recalc values with transactions
    def _calc_values(self):
        self.start_amount = 0
        self.change_amount = 0
        self.rollover_fee = 0
        self.devidende = 0

        for trans in self._transactions:
            if trans.type == Transaction_Type.Open_Position:
                self.start_amount = trans.amount
            elif trans.type == Transaction_Type.Profit_Loss_of_Trade:
                self.change_amount = trans.amount
            elif trans.type == Transaction_Type.Rollover_fee:
                self.rollover_fee += trans.amount
            elif trans.type == Transaction_Type.Dividende:
                self.devidende += trans.amount

    def get_transactions(self, type:Transaction_Type):
        out: List[Transaction] = []
        for t in self._transactions:
            if t.type == type:
                out.append(t)
        return out

    # public area
    def get_Rollover_fee(self):
        return self.rollover_fee

    def get_Profit(self, check_divdende:(datetime, datetime) = None):
        return_value = self.change_amount
        if check_divdende is not None:
            start_date = check_divdende[0]
            stop_date = check_divdende[1]

            for transaction in self._transactions:
                if transaction.type == Transaction_Type.Dividende:
                    if not (transaction.date >= start_date and transaction.date <= stop_date):
                        return_value -= transaction.amount

        return return_value

    def convert_toCurrency(self, toCurrency:str, default_currency:str='USD'):
        for transaction in self._transactions:
            transaction.convert_toCurrency(toCurrency, self._currencyConverter, default_currency)
        self._calc_values()


