#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author : microfat
# @time   : 08/05/20 22:13:22
# @File   : parseData.py

import re
import unicodedata
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree
from urllib.parse import urlparse
from gne import GeneralNewsExtractor
from pyhanlp import HanLP

extractor = GeneralNewsExtractor()

class ParseData:
    def __init__(self):
        pass

    def get_city_code(self, source):
        soup = BeautifulSoup(source, 'lxml')
        city_dict = {}
        for group in soup.find('div', {'id':'work_position_click_center_right'})\
                         .find_all('div', {'class':'work_position_click_center_right_list de d3'})[3:]:
            group_dict = {}
            for city_source in group.find_all('em'):
                city_name = city_source.text
                city_code = city_source['data-value']
                group_dict[city_code] = city_name
            city_dict = {**city_dict, **group_dict}

        return city_dict

    def get_indtype_code(self, source):
        soup = BeautifulSoup(source, 'lxml')
        indtype_dict = {}
        indtype_key_dict = {}
        indtype_value_dict = {}
        for key_source in soup.find('ul', {'id':'indtype_click_center_left'})\
                .find_all('li'):
            indtype_key_key = key_source['data-value']
            indtype_key_value = key_source.text
            indtype_key_dict[indtype_key_key] = indtype_key_value
        for group in soup.find('div', {'id':'indtype_click_center_right'})\
                         .find_all('div', {'class':'indtype_click_center_right_list de d3'}):
            group_list = []
            for indtype_source in group.find_all('em'):
                indtype_key = indtype_source['data-navigation']
                indtype_value = indtype_source['data-value']
                indtype_value_value = indtype_source.text
                group_list.append(indtype_value)
                indtype_value_key = indtype_value
                indtype_value_dict[indtype_value_key] = indtype_value_value
            indtype_dict[indtype_key] = group_list

        return indtype_dict, indtype_key_dict, indtype_value_dict
    
    def get_province_code(self, source):
        soup = BeautifulSoup(source, 'lxml')
        province_dict = {}
        for province_source in soup.find('div', {'id':'work_position_click_center_right'})\
                                   .find('div', {'id':'work_position_click_center_right_list_030000'})\
                                   .find_all('em'):
            province_name = province_source.text
            province_code = province_source['data-value']
            province_dict[province_code] = province_name

        return province_dict      
    
    def get_page_num(self, source):
        page_num = int(source.json()['total_page'])

        return page_num

    def get_job_num(self, source):
        job_num = len(source.json()['engine_search_result'])

        return job_num
    
    def get_job_info(self, source):
        df = pd.DataFrame()
        for item in source.json()['engine_search_result']:
            df_item = pd.json_normalize(item)
            try:
                df_item.loc[:,'tags'] = df_item['tags'].map(lambda x: ','.join(a for a in x))
                df_item.loc[:,'jobwelf_list'] = df_item['jobwelf_list'].map(lambda x: ','.join(a for a in x))
                df_item.loc[:,'attribute_text'] = df_item['attribute_text'].map(lambda x: ','.join(a for a in x))
            except:
                pass
            df = df.append(df_item, ignore_index=True)
        return df
    
    def get_job_address(self, source):
        soup = BeautifulSoup(source.text.encode('iso-8859-1').decode('gbk'), 'lxml')
        address = soup.find('p', {'class':'msg ltype'}).text.split('\xa0\xa0|\xa0\xa0')[0]
        if 'ns' in HanLP.segment(address).toString():
            return address
        else:
            return ''
            
    def get_job_msg(self, source):
        tree = etree.HTML(source.text.encode('iso-8859-1').decode('gbk'))
        content = tree.xpath("//div[@class='cn']/p[2]/text()")
        content = [i.strip() for i in content]
        experience = ''.join([i for i in content if '经验' in i])
        education = ''.join([i for i in content if i in '本科大专应届生在校生硕士'])
        need_people = ''.join([i for i in content if '招' in i])
        publish_date = ''.join([i for i in content if '发布' in i])
        english = ''.join([i for i in content if '英语' in i])
        return experience, education, need_people, publish_date, english
    
    def get_job_detail(self, source):
        soup = BeautifulSoup(source.text.encode('iso-8859-1').decode('gbk'), 'lxml')
        # 提取正文
        html = soup.find('div', {'class':'bmsg job_msg inbox'})
        detail = extractor.extract(str(html))
        detail = detail['content'].replace('\n', ',').replace(' ', '')

        return detail
    
    def get_job_type(self, source):
        soup = BeautifulSoup(source.text.encode('iso-8859-1').decode('gbk'), 'lxml')
        job_type = ''
        for a in soup.find('div', {'class':'bmsg job_msg inbox'})\
                     .find('span', text = '职能类别：')\
                     .find_next_siblings('a'):
            job_type += '{},'.format(a.text)

        return job_type.strip(',')

    def get_job_keywords(self, source):
        soup = BeautifulSoup(source.text.encode('iso-8859-1').decode('gbk'), 'lxml')
        job_keywords = ''
        for a in soup.find('div', {'class':'bmsg job_msg inbox'})\
                     .find('span', text = '关键字：')\
                     .find_next_siblings('a'):
            job_keywords += '{},'.format(a.text)

        return job_keywords.strip(',')
    
    def get_job_location(self, source):
        soup = BeautifulSoup(source.text.encode('iso-8859-1').decode('gbk'), 'lxml')
        try:
            lng = soup.find('li', {'class':'chaxun_input_li_end'}).find('input')['lng']
            lat = soup.find('li', {'class':'chaxun_input_li_end'}).find('input')['lat']
            if lng == '0.000000' and lat == '0.000000':
                lng = ''
                lat = ''
        except:
            lng = ''
            lat = ''
        return lng, lat
    