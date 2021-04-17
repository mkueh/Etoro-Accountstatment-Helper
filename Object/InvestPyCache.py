from enum import Enum
import investpy

from typing import Dict, List

class InvestPyCache():

    _cache:Dict

    def __init__(self):
        self._cache = {}

    def get_pairType(self, action:str) -> List[investpy.search.SearchObj]:
        if action in self._cache:
            return self._cache[action]
        else:
            try:
                response = investpy.search_quotes(action)

                if isinstance(response, list):
                    self._cache[action] = response
                    return response
                else:
                    self._cache[action] = [response]
                    return [response]
            except:
                return [None]
