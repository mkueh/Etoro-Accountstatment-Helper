import pickle

import pandas as pd
import datetime

from typing import List, Callable
from currency_converter import CurrencyConverter
from sortedcontainers import SortedList

from Object.Position import Position, Position_Type, Pair_Type
from Object.Transaction import Transaction, Transaction_Type

from .EtoroAssetHelperPyCache import EtoroAssetHelperPyCache

class Statement():
    positions: List[Position]
    not_closed_positions: List[Transaction]

    _current_currency = 'USD'

    def __init__(self, xlsx_file_of_statement: str):
        investpy_cache = EtoroAssetHelperPyCache()
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
            position.fill_infos_with_Transaction(investpy_cache)

        func: Callable[[Position], datetime] = lambda position: position.close_date
        positions: List[Position] = SortedList(positions,key=func)

        self.positions = positions
        self.unknown_transactions = unknown_transactions

    def convert_to_Currency(self, to_currency: str):
        cc = CurrencyConverter('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip',fallback_on_missing_rate=True, fallback_on_missing_rate_method='last_known')
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

    def get_CFT_statistic(self, start_date, end_date):
        sum_cft_lost = 0.0
        sum_cft_win = 0.0
        sum_cft_profit = 0.0
        sum_cft_rollover = 0.0
        sum_cft_dividend = 0.0

        for p in self.positions:
            if p.close_date >= start_date:
                value = p.get_Profit()

                if p.isReal == Position_Type.CFD:
                    sum_cft_profit += value
                    if value < 0:
                        sum_cft_lost += value
                        if p.close_date > end_date:
                            break
                    else:
                        sum_cft_win += value
                        if p.close_date > end_date:
                            break

                    sum_cft_dividend += p.devidende
                    sum_cft_rollover += p.rollover_fee
        return {'cft_profit': sum_cft_profit, 'cft_lost': sum_cft_lost, 'cft_win': sum_cft_win, 'cft_rollover': sum_cft_rollover, 'cft_dividend': sum_cft_dividend}

    def get_ETF_statistic(self, start_date, end_date):
        sum_eft_lost = 0.0
        sum_eft_win = 0.0
        sum_cft_profit = 0.0
        sum_cft_rollover = 0.0
        sum_cft_dividend = 0.0

        for p in self.positions:
            if p.close_date >= start_date:
                value = p.get_Profit()

                if p.pair_type == Pair_Type.ETF:
                    sum_cft_profit += value
                    if value < 0:
                        sum_eft_lost += value
                        if p.close_date > end_date:
                            break
                    else:
                        sum_eft_win += value
                        if p.close_date > end_date:
                            break

                    sum_cft_dividend += p.devidende
                    sum_cft_rollover += p.rollover_fee
        return {'eft_profit': sum_cft_profit, 'eft_lost': sum_eft_lost, 'eft_win': sum_eft_win, 'eft_rollover': sum_cft_rollover, 'eft_dividend': sum_cft_dividend}

    def get_shares_statistic(self, start_date, end_date):
        sum_eft_lost = 0.0
        sum_eft_win = 0.0
        sum_cft_profit = 0.0
        sum_cft_rollover = 0.0
        sum_cft_dividend = 0.0

        for p in self.positions:
            if p.close_date >= start_date:
                value = p.get_Profit()

                if p.pair_type == Pair_Type.STOCK and p.isReal == Position_Type.REAL:
                    sum_cft_profit += value
                    if value < 0:
                        sum_eft_lost += value
                        if p.close_date > end_date:
                            break
                    else:
                        sum_eft_win += value
                        if p.close_date > end_date:
                            break

                    sum_cft_dividend += p.devidende
                    sum_cft_rollover += p.rollover_fee
        return {'shares_profit': sum_cft_profit, 'shares_lost': sum_eft_lost, 'shares_win': sum_eft_win, 'shares_rollover': sum_cft_rollover, 'shares_dividend': sum_cft_dividend}

    def get_total_dividend(self, start_date, end_date):
        pass

    def sum_total_lost(self, start_date, end_date):
        sum_lost = 0.0

        for p in self.positions:
            if p.close_date >= start_date:
                value = p.get_Profit()
                if value < 0:
                    sum_lost += value
                    if p.close_date > end_date:
                        break
        return sum_lost

    def sum_total_win(self, start_date, end_date):
        sum_win = 0.0

        for p in self.positions:
            if p.close_date >= start_date:
                value = p.get_Profit()
                if value > 0:
                    sum_win += value
                    if p.close_date > end_date:
                        break
        return sum_win

    def sum_devidende(self, start_date, end_date):
        sum_devidende = 0.0

        for p in self.positions:
            if p.close_date >= start_date:
                value = p.devidende
                sum_devidende += value
                if p.close_date > end_date:
                    break
        return sum_devidende

