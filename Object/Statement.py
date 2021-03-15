import pandas as pd

from typing import List
from currency_converter import CurrencyConverter
from sortedcontainers import SortedList

from Object.Position import Position
from Object.Transaction import Transaction, Transaction_Type


class Statement():
    positions: List[Position]
    unknown_transactions: List[Transaction]

    _current_currency = 'USD'

    def __init__(self, xlsx_file_of_statement: str):
        positions: List[Position] = SortedList(key=lambda x: x.ID)

        dataframe: pd.DataFrame = pd.read_excel(xlsx_file_of_statement, sheet_name='Closed Positions')
        values = dataframe.values

        for row in values:
            positions.add(
                Position(row['Position ID'], row['Action'], row['Copy Trader Name'], row['Amount'], row['Units'],
                         row['Open Rate'], row['Close Rate'], row['Spread'], row['Profit'], row['Open Date'],
                         row['Close Date'],
                         row['Take Profit Rate'], row['Stop Loss Rate'], row['Rollover Fees And Dividends'],
                         row['Is Real'], row['Leverage'], row['Notes']))

        dataframe: pd.DataFrame = pd.read_excel(xlsx_file_of_statement, sheet_name='Transactions Report')
        values = dataframe.values

        unknown_transactions: List[Transaction] = []
        for row in values:
            tmp = Transaction(row['Date'], row['Account Balance'], row['Type'], row['Details'], row['Position ID'],
                              row['Amount'], row['Realized Equity Change'], row['Realized Equity'], row['NWA'])
            try:
                position_index = positions.index(tmp)
                positions[position_index].transactions.append(tmp)
            except:
                unknown_transactions.append(tmp)

        positions: List[Position] = SortedList(key=lambda x: x.ID)

        self.positions = positions
        self.unknown_transactions = unknown_transactions

    def convert_to_Currency(self, to_currency: str):
        cc = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_missing_rate_method='last_known')
        for position in self.positions:
            position.convert_toCurrency(to_currency, cc, self._current_currency)

        for transaction in self.unknown_transactions:
            transaction.convert_toCurrency(to_currency, cc, self._current_currency)

        self._current_currency = to_currency

    def sum_profit(self, start_date, end_date):
