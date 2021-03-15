import pandas as pd

from typing import List
from currency_converter import CurrencyConverter
from sortedcontainers import SortedList

from Object.Statement import Statement

FILE = 'eToroAccountStatement2020.xlsx'

def main():
    statement = Statement(FILE)
    statement.convert_to_Currency('EUR')
    print(sum_profit(positions))
    print(sum_rollover_fee(positions, transactions))


def sum_profit(positions:List[Position]) -> float:
    profit_sum = 0
    for position in positions:
        profit_sum += position.profit
    return profit_sum

def sum_rollover_fee(positions:List[Position], transactions:List[Transaction]) -> float:
    rolloverFee_sum = 0
    for position in positions:
        rolloverFee_sum += position.get_Rollover_fee()

    for transaction in transactions:
        if transaction.type == Transaction_Type.Rollover_fee:
            rolloverFee_sum += transaction.amount_USD
    return rolloverFee_sum

def load_xlsx(path:str) -> List[Position]:
    positions:List[Position] = SortedList(key=lambda x: x.ID)

    dataframe:pd.DataFrame = pd.read_excel(path, sheet_name='Closed Positions')
    values = dataframe.values

    for row in values:
        positions.add(Position(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16]))

    dataframe:pd.DataFrame = pd.read_excel(path, sheet_name='Transactions Report')
    values = dataframe.values

    transactions:List[Transaction] = []
    for row in values:
        tmp = Transaction(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
        try:
            position_index = positions.index(tmp)
            positions[position_index].transactions.append(tmp)
        except:
            transactions.append(tmp)

    return positions, transactions

if __name__ == "__main__":
    # execute only if run as a script
    main()

"""
pip install CurrencyConverter
pip install sortedcontainers
"""