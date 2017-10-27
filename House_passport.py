#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from requests import get
from bs4 import BeautifulSoup
import pandas as pd


class Parser:

    def __init__(self, url):
        self.url = url
        self.check()
        self.table = self.get_info()

    def check(self):
        url = 'https://www.reformagkh.ru/myhouse/profile/view/'
        if url not in self.url:
            raise ValueError('Please try the correct link.')

    def get_info(self):
        text = get(self.url)
        if text.status_code == 200:
            info = BeautifulSoup(text.text, 'lxml')
            table_big = info.findAll(class_='subtab')
            return table_big
        else:
            raise ConnectionError('The page is not available')

    def get_text(self):
        array = []
        clean_array = []

        for el in self.table[:3]:
            for global_el in el.select('.col_list > tbody > tr > td > span'):
                array.append(global_el.text)

        for el in array:
            if ':' in el:
                array.remove(el)
                clean_array.append(el.replace('\n', ''))
            else:
                clean_array.append(el.replace('\n', ''))

        return clean_array

    def get_lifts(self):

        lifts = []
        text = self.table[3].find_all('tr')
        for el in text:
            td = el.find_all('td')
            lifts.append([i.text for i in td])

        return lifts


class Passport(Parser):

    def __init__(self, url, write=False):
        Parser.__init__(self, url)
        self.write = write
        self.write_table()

    def create_lr_lists(self):
        result = Parser.get_text(self)
        if len(result) % 2 == 0:
            first = result[1::2]
            second = result[0::2]
            return first, second
        else:
            raise ArithmeticError('List is not odd, something went wrong.')

    def create_table(self):
        first, second = self.create_lr_lists()

        lifts = self.get_lifts()

        res = pd.DataFrame({"indicators": first, "name": second},
                           columns=["name", "indicators"])

        lifts_res = pd.DataFrame(lifts[1:len(lifts)], columns=['Номер лифта','Номер подъезда',
                                                                'Тип лифта', 'Год ввода в эксплатацию'])\
            .set_index('Номер лифта')

        return res, lifts_res

    def write_table(self):
        res, lifts_res = self.create_table()

        if self.write is True:
            house_f = open('house_pasport.csv', 'w', encoding='utf-8-sig')
            lift_f = open('lifts.csv', 'w', encoding='utf-8-sig')
            res.to_csv(house_f, sep=';')
            lifts_res.to_csv(lift_f, sep=';')


inst = Passport(url='https://www.reformagkh.ru/myhouse/profile/view/9106808', write=True)
