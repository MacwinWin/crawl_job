#!/usr/bin/env python3
# -*-coding: utf-8 -*-
# @author : microfat
# @time   : 08/23/20 15:22:28
# @File   : mongodb_api.py

import time
import pymongo

class APIUtils:
    def __init__(self):
        pass
    
    # 创建数据库connection
    def create_connection(self, user, password, address, port, databass, collection):
        count = 0
        while True:
            if count < 2:
                try:
                    myclient = pymongo.MongoClient('mongodb://{}:{}/'.format(address, port))
                    mydb = myclient[databass]
                    mydb.authenticate(user, password)
                    mycol = mydb[collection]
                    return mycol
                except Exception as e:
                    count += 1
                    print('Retry')
                    print(e)
                    time.sleep(5)
                    continue
            else:
                print('Fail!')
                raise Exception('Fail!')
    
    # 更新数据
    def update_one_data(self, mycol, myquery, newvalues):
        count = 0
        while True:
            if count < 2:
                try:
                    x = mycol.update_one(myquery, newvalues, True)
                    return x
                except Exception as e:
                    count += 1
                    print('Retry')
                    print(e)
                    time.sleep(5)
                    continue
            else:
                print('Fail!')
                raise Exception('Fail!')

    # 插入多条数据
    def insert_many_data(self, mycol, data):
        count = 0
        while True:
            if count < 2:
                try:
                    x = mycol.insert_many(data)
                    return x
                except Exception as e:
                    count += 1
                    print('Retry')
                    print(e)
                    time.sleep(5)
                    continue
            else:
                print('Fail!')
                raise Exception('Fail!')