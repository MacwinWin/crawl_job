#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author : microfat
# @time   : 08/05/20 22:13:22
# @File   : crawl.py

import pandas as pd
from module import request_data, parse_data, mongodb_api

import argparse

args = argparse.ArgumentParser(description = 'command')
args.add_argument('-kw', '--keyword', type = str, help = 'job keyword')

args = args.parse_args()

mongo_api = mongodb_api.APIUtils()

class Spider:
    
    def __init__(self):
        self.keyword = args.keyword
        self.mongo_connection = mongo_api.create_connection(
            'mongo', 
            'mongo', 
            'crawl_job_db', 
            '27017', 
            'job', 
            self.keyword)

    def get_list(self):
        data_request = request_data.RequestData()
        data_parse = parse_data.ParseData()

        # 全国代码
        country_dict = {
            '000000': '全国'
        }

        # 循环获取
        total_page_num = 0
        for code, name in country_dict.items():
            print('{}:'.format(name))
            # 获取页数
            headers = {
                "Accept":"application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding":"gzip, deflate, br",
                "Accept-Language":"zh-CN,zh;q=0.9",
                "Connection":"keep-alive",
                "Host":"search.51job.com",
                "Referer":"https://search.51job.com/list/030000,000000,0000,00,9,99,python,2,1.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare=",
                "Sec-Fetch-Dest":"empty",
                "Sec-Fetch-Mode":"cors",
                "Sec-Fetch-Site":"same-origin",
                "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
                "X-Requested-With":"XMLHttpRequest",
            }
            page_1_source = data_request.send_request(headers, code, self.keyword, '1')
            page_num = data_parse.get_page_num(page_1_source)
            job_num = data_parse.get_job_num(page_1_source)
            print('{}页, {}条'.format(page_num, job_num))
            total_page_num += page_num
            if job_num != 0:
                for page_n in range(page_num):
                    page_n += 1
                    if page_n == 1:
                        df_page_n_info = data_parse.get_job_info(page_1_source)
                    else:
                        page_n_source = data_request.send_request(headers, code, self.keyword, str(page_n))
                        df_page_n_info = data_parse.get_job_info(page_n_source)
                    dic_page_n_info = df_page_n_info.to_dict('records')
                    mongo_api.insert_many_data(self.mongo_connection, dic_page_n_info)
                    #print('\r', page_n, end='', flush=True)
        print('共计{}页'.format(total_page_num))

    def get_detail(self):
        data_request = request_data.RequestData()
        data_parse = parse_data.ParseData()

        count = 0
        for row in self.mongo_connection.find():
            url = row['job_href']
            if 'jobs.51job.com' in url:
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.13 Safari/537.36'}
                try:
                    source = data_request.send_request(headers, request_url = url)
                    address = data_parse.get_job_address(source)
                    location_source = data_request.send_request(headers, request_url = 'https://search.51job.com/jobsearch/bmap/map.php', jobid = row['jobid'])
                    lng, lat = data_parse.get_job_location(location_source)
                    row['lng'] = lng
                    row['lat'] = lat
                except:
                    print(url)
                    continue
                if address != '':
                    row['workarea_text'] = address
                experience, education, need_people, publish_date, english = data_parse.get_job_msg(source)
                row['experience'] = experience
                row['education'] = education
                row['need_people'] = need_people
                row['publish_date'] = publish_date
                row['english'] = english
                detail = data_parse.get_job_detail(source)
                row['detail'] = detail
                job_type = data_parse.get_job_type(source)
                row['type'] = job_type
                job_keywords = data_parse.get_job_type(source)
                row['keywords'] = job_keywords
                query_dict = {
                    "_id": row['_id']
                }
                data_dict = {"$set":row}
                mongo_api.update_one_data(self.mongo_connection, query_dict, data_dict)
                count += 1
                #print('\r', count, end='', flush=True)
            else:
                pass
    
    def run(self):
        if self.keyword == None:
            raise Exception('请输入关键字!')
        else:
            self.get_list()
            self.get_detail()

if __name__ == '__main__':
    spider = Spider()
    spider.run()
