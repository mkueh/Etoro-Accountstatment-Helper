import pandas as pd
import datetime

from typing import List, Callable
from currency_converter import CurrencyConverter
from sortedcontainers import SortedList

from Object.Position import Position
from Object.Transaction import Transaction, Transaction_Type

class Statement():
    positions: List[Position]
    not_closed_positions: List[Transaction]

    _current_currency = 'USD'

    def __init__(self, xlsx_file_of_statement: str):
        positions: List[Position] = SortedList(key=lambda x: x.ID)

        dataframe: pd.DataFrame = pd.read_excel(xlsx_file_of_statement, sheet_name='Closed Positions')

        for index, row in dataframe.iterrows():
            positions.add(
                Position(row['Position ID'], row['Action'], row['Copy Trader Name'], row['Units'],
                         row['Open Rate'], row['Close Rate'], row['Open Date'],
                         row['Close Date'], row['Take Profit Rate'], row['Stop Loss Rate'],
                         row['Is Real'], row['Leverage'], row['Notes']))

        dataframe: pd.DataFrame = pd.read_excel(xlsx_file_of_statement, sheet_name='Transactions Report')

        unknown_transactions: List[Transaction] = []
        for index, row in dataframe.iterrows():
            tmp = Transaction(row['Date'], row['Account Balance'], row['Type'], row['Details'], row['Position ID'],
                              row['Amount'], row['Realized Equity Change'], row['Realized Equity'], row['NWA'])
            try:
                position_index = positions.index(tmp)
                positions[position_index].transactions.append(tmp)
            except:
                unknown_transactions.append(tmp)

        for position in positions:
            position.recalc_values()

        func: Callable[[Position], datetime] = lambda position: position.close_date
        positions: List[Position] = SortedList(positions,key=func)

        self.positions = positions
        self.unknown_transactions = unknown_transactions

    def convert_to_Currency(self, to_currency: str):
        cc = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_missing_rate_method='last_known')
        for position in self.positions:
            position.convert_toCurrency(to_currency, cc, self._current_currency)

        for transaction in self.unknown_transactions:
            transaction.convert_toCurrency(to_currency, cc, self._current_currency)

        self._current_currency = to_currency

    def sum_rollover(self, start_date, end_date, closed:bool = True):
        sum_rollover = 0.0

        for p in self.positions:
            if p.close_date >= start_date:
                sum_rollover += p.get_Rollover_fee()
                if p.close_date > end_date:
                    break
        return sum_rollover

    def sum_profit(self, start_date, end_date):
        sum_profit = 0.0

        for p in self.positions:
            if p.close_date >= start_date:
                sum_profit += p.get_Profit(check_divdende=(start_date,end_date))
                if p.close_date > end_date:
                    break
        return sum_profit



