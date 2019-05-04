from typing import Union

import datefinder
import dateutil.parser
import re

_fiscal_number_regexp = '[U+0400–U+04FF]{2}(\s)*\d{5,}'
_cachier_number_regexp = r'(ПН|П\p{IsCyrillic}|\p{IsCyrillic}Н) \d{12}'
_date_regexp = "\d{1,2}[\/\\-. ]\d{1,2}[\/\\-. ]\d{2,4}"
_time_regexp = r'(\d{1,2}[: ]\d{1,2}[: ]\d{1,2}|\d{1,2}[: ]\d{1,2})'



class Data:

    def __init__(self) -> None:
        self._info = dict()

    def __str__(self):
        mapped = list()
        for desc, info in self._info.items():
            desc_info_str = Data.to_str(desc, info)
            if desc_info_str != '':
                mapped.append(desc_info_str)
        return '{' + ', '.join(mapped) + '}'

    @staticmethod
    def to_str(decs: str, info):
        if info is None:
            return ''
        return '{}: {}'.format(decs, info)

    def add_info(self, desc: str, info):
        self._info[desc] = info


def _get_date(text: str):
    # with finder
    # matches = datefinder.find_dates(text)
    # for match in matches:
    #     print('found date: {}'.format(match))
    #     return match

    # with dateutil
    # result = dateutil.parser.parse("Today is Nov 30 12", fuzzy_with_tokens=True)
    # return result[0]

    # with regexp
    matches = re.findall(_date_regexp, text)
    return list(map(str, matches))


def _get_name(text: str):
    return None


def _get_time(text: str):
    matches = re.findall(_time_regexp, text)
    return list(map(str, matches))


def _get_sum_paid(text: str):
    return None


def _get_match(pattern: str, text: str):
    matches = re.findall(pattern, text)
    return list(map(str, matches))


def parse(text: str):
    result = Data()
    result.add_info('fiscal number', _get_match(_fiscal_number_regexp, text))
    result.add_info('cachier number', _get_match(_cachier_number_regexp, text))
    result.add_info('date', _get_date(text))
    result.add_info('time', _get_time(text))
    return result
