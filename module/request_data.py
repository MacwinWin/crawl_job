#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author : microfat
# @time   : 08/05/20 22:13:22
# @File   : requestData.py

import traceback
import time
import random
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class RequestData:

    WEBSITE = "https://search.51job.com"

    # 构造函数
    def __init__(self):
        self.url_search = RequestData.WEBSITE + '/list'

    # 发送http请求
    def send_request(self, headers, city_code = '', keyword = '', page_num = '', request_url = '', jobid = ''):
        if request_url == '':
            request_url = self.url_search + '/{},000000,0000,00,9,99,{},2,{}.html'.format(city_code, keyword, page_num)
        time.sleep(random.random() + random.randint(0, 1))
        count = 0
        while True:
            if count <= 2:
                try:
                    if jobid != '':
                        res = requests.get(request_url, headers=headers, params={'jobid': jobid}, verify =False)
                    else:
                        res = requests.get(request_url, headers=headers, verify =False)
                    if res.status_code >= 400:
                        raise Exception('请求错误！', res)
                    else:
                        #res.encoding = res.apparent_encoding
                        return res
                except:
                    traceback.print_exc()
                    time.sleep(5)
                    print('retry!')
                    count += 1
                    continue
            else:
                break
            
if __name__ == "__main__":
    test = RequestData()
    res = test.send_request('010000', 'python', '1')
    #res.encoding = res.apparent_encoding
    #res.encoding = 'gbk'
    print(res.text.encode('iso-8859-1').decode('gbk'))
