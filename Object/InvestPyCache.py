from enum import Enum
import investpy

class PairTypeCache():

    class Pair_Type(Enum):
        STOCK = 1
        CURRENCY = 2
        CRYPTO = 3
        ETF = 4
        INDICIES = 5
        NOT_DEFINE = -1

    def __init__(self):
        pass

    def get_pairType(self):
        return