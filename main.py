import pandas as pd
import datetime as dt

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

    date_time_str = '2020-06-30 23:59:59'
    stop = dt.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

    profit = round(statement.sum_profit(start, stop),2)
    rollover = round(statement.sum_rollover(start, stop),2)
    print(f'Profit {profit} {currency}')
    print(f'Rollover {rollover} {currency}')

if __name__ == "__main__":
    # execute only if run as a script
    main()

"""
pip install CurrencyConverter
pip install sortedcontainers
"""