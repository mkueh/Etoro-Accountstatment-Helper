import pandas as pd
import datetime as dt
import pickle

from typing import List
from currency_converter import CurrencyConverter
from sortedcontainers import SortedList

from Object.Statement import Statement
from Object.Position import Position
from Object.Transaction import Transaction, Transaction_Type

FILE = 'eToroAccountStatement2020.xlsx'

def main():
    statement = Statement(FILE)
    currency = 'EUR'
    statement.convert_to_Currency(currency)

    date_time_str = '2020-01-01 00:00:00'
    start = dt.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

    date_time_str = '2020-12-31 23:59:59'
    stop = dt.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

    profit = round(statement.sum_profit(start, stop),2)
    rollover = round(statement.sum_rollover(start, stop),2)
    devidende = round(statement.sum_devidende(start, stop),2)
    total_lost = round(statement.sum_total_lost(start,stop), 2)
    total_win = round(statement.sum_total_win(start,stop), 2)

    cft_statistics = statement.get_CFT_statistic_closed(start, stop)
    etf_statistics = statement.get_ETF_statistic_closed(start, stop)
    shares_statistics = statement.get_shares_statistic_closed(start, stop)


    print(f'Profit {profit} {currency}')
    print(f'Total lost {total_lost} {currency}')
    print(f'Total win {total_win} {currency}')
    print('-------------------------------------------------')
    print(f'Rollover {rollover} {currency}')
    print(f'Devidende {devidende} {currency}')
    print('-------------------------------------------------')
    sum_cft_lost = round(cft_statistics['cft_lost'], 2)
    sum_cft_win = round(cft_statistics['cft_win'], 2)
    sum_cft_profit = round(cft_statistics['cft_profit'], 2)
    sum_cft_rollover = round(cft_statistics['cft_rollover'], 2)
    sum_cft_dividend = round(cft_statistics['cft_dividend'], 2)
    print(f'Total CFT win {sum_cft_win} {currency}')
    print(f'Total CFT lost {sum_cft_lost} {currency}')
    print(f'Total CFT profit {sum_cft_profit} {currency}')
    print(f'Total CFT rollover {sum_cft_rollover} {currency}')
    print(f'Total CFT dividend {sum_cft_dividend} {currency}')
    print('-------------------------------------------------')
    sum_etf_lost = round(etf_statistics['eft_lost'], 2)
    sum_etf_win = round(etf_statistics['eft_win'], 2)
    sum_etf_profit = round(etf_statistics['eft_profit'], 2)
    sum_etf_rollover = round(etf_statistics['eft_rollover'], 2)
    sum_etf_dividend = round(etf_statistics['eft_dividend'], 2)
    print(f'Total EFT win {sum_etf_win} {currency}')
    print(f'Total EFT lost {sum_etf_lost} {currency}')
    print(f'Total EFT profit {sum_etf_profit} {currency}')
    print(f'Total EFT rollover {sum_etf_rollover} {currency}')
    print(f'Total EFT dividend {sum_etf_dividend} {currency}')
    print('-------------------------------------------------')
    sum_shares_lost = round(shares_statistics['shares_lost'], 2)
    sum_shares_win = round(shares_statistics['shares_win'], 2)
    sum_shares_profit = round(shares_statistics['shares_profit'], 2)
    sum_shares_rollover = round(shares_statistics['shares_rollover'], 2)
    sum_shares_dividend = round(shares_statistics['shares_dividend'], 2)
    print(f'Total shares win {sum_shares_win} {currency}')
    print(f'Total shares lost {sum_shares_lost} {currency}')
    print(f'Total shares profit {sum_shares_profit} {currency}')
    print(f'Total shares rollover {sum_shares_rollover} {currency}')
    print(f'Total shares dividend {sum_shares_dividend} {currency}')
    print('-------------------------------------------------')
    sum_devidend = round(statement.get_total_dividend(start, stop), 2)
    print(f'Total devidend this time {sum_devidend} {currency}')

if __name__ == "__main__":
    # execute only if run as a script
    main()

"""
pip install CurrencyConverter
pip install sortedcontainers
"""