from enum import Enum
from typing import Dict, List
import json
import requests


class EtoroAssetHelperPyCache():

    #API links
    instruments_link = 'https://api.etorostatic.com/sapi/app-data/web-client/app-data/instruments-groups.json'
    data_link = 'https://api.etorostatic.com/sapi/instrumentsmetadata/V1.1/instruments/bulk?bulkNumber=1&totalBulks=1'

    _item_dict_asName: Dict = {}
    _item_dict_asSymbol: Dict = {}
    _caching_mathces = Dict = {}

    def __init__(self):

        self._item_dict = {}

        response = requests.get(self.instruments_link)
        parsed_types = json.loads(response.text)

        # Divide types
        instruments = parsed_types['InstrumentTypes']
        exchanges = parsed_types['ExchangeInfo']
        stocks = parsed_types['StocksIndustries']
        crypto = parsed_types['CryptoCategories']

        response = requests.get(self.data_link)
        response_json = json.loads(response.text)['InstrumentDisplayDatas']

        # We collect the instruments with their attributes here
        inst = []

        # Loop through all the instruments
        for entry in response_json:

            # Gather the necessary data about the instrument
            instrument_typeID = entry['InstrumentTypeID']
            name = entry['InstrumentDisplayName']
            exchangeID = entry['ExchangeID']
            symbol = entry['SymbolFull']


            for item in instruments:
                if item['InstrumentTypeID'] == instrument_typeID:
                    instrument_type = item['InstrumentTypeDescription']

            industry = '-'
            if 'StocksIndustryID' in entry:
                industryID = entry['StocksIndustryID']
                for item in stocks:
                    if item['IndustryID'] == industryID:
                        industry = item['IndustryName']

            exchange = '-'
            if 'ExchangeID' in entry:
                industryID = entry['ExchangeID']
                for item in exchanges:
                    if item['ExchangeID'] == industryID:
                        exchange = item['ExchangeDescription']

            symbol:str = symbol.lower().strip()
            name:str = name.lower().strip()

            item = {
                'name': name,
                'symbol': symbol,
                'instrument type': instrument_type,
                'exchange': exchange,
                'industry': industry
            }

            self._item_dict_asSymbol[symbol] = item
            self._item_dict_asName[name] = item


    def get_pairType(self, action:str, item_name:str):
        action = action.lower().strip()
        item_name = item_name.lower().strip()

        if action in self._item_dict_asSymbol:
            return self._item_dict_asSymbol[action]
        elif action in self._item_dict_asName:
            return self._item_dict_asName[action]

        """
        # remove currency at the end
        tmp_action = action[:len(action) - 4].strip()
        if tmp_action in self._item_dict_asSymbol:
            return self._item_dict_asSymbol[tmp_action]
        elif tmp_action in self._item_dict_asName:
            return self._item_dict_asName[tmp_action]
        """

        if item_name in self._item_dict_asSymbol:
            return self._item_dict_asSymbol[item_name]
        elif item_name in self._item_dict_asName:
            return self._item_dict_asName[item_name]

        print(f'Asset ({action} , {item_name}) could not be found in the current database')
        return None

