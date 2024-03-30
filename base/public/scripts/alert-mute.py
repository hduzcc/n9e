#!/bin/python
# -*- coding: utf-8 -*-
import requests
import socket
import time
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from base.db_utils import POOL
"""
用于告警屏蔽
"""
logfile = "/usr/local/n9e/alert_mute.log"
logging.basicConfig(filename=logfile, level=logging.INFO)

class HttpServer:
    def __init__(self, address='0.0.0.0', port=51001):
        """
        初始化参数
        :param address webhook绑定地址
               port webhook监听端口
        """
        self.address = address
        self.port = port
        self.dbpool = POOL()

    def alertMute(self, vardict):
        """
        告警屏蔽模块
        :param vardict 屏蔽规则字典
        """
        def getSql():
            now = int(time.time())
            note, cause = "临时屏蔽规则", "屏蔽原因"
            tags = []
            btime, etime = now, now + 3600
            for k,v in vardict.items():
                tempdict = {}
                tempdict["func"], tempdict["key"], tempdict["value"] = "==", k , v
                tags.append(tempdict)
            tags = json.dumps(json.dumps(tags))
            verifysql = "select 1 from alert_mute where tags=%s" %(tags)
            return insertsql, verifysql
        insertsql, verifysql = getSql()
        conn = self.dbpool.connection()
        cursor = conn.cursor()
        cursor.execute(verifysql)
        verifyres = cursor.fetchall()
        if verifyres:
            body = "你已经屏蔽过这个告警了"
        else:
            cursor.execute(insertsql)
            body = "已新建告警规则"
        conn.commit()
        cursor.close()
        conn.close()
        return body

    def code200(self, body="操作成功"):
        header = 'HTTP/1.1 200\r\n'
        header += 'Content-Type: text/html;charset=utf-8 \r\n'
        header += '\r\n'
        body = ' <h1>%s</h1>' %(body)
        return header + body

    def code400(self):
        header = 'HTTP/1.1 403\r\n'
        header += 'Content-Type: text/html;charset=utf-8 \r\n'
        header += '\r\n'
        body = ' <h1>403 Forbidden</h1>'
        return header + body

    def listen(self):
        """
        webhook 监听函数
        :param address webhook绑定地址
               path url请求接口
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        """
        初始化参数
        :param address webhook绑定地址
               port webhook监听端口
        """
        self.address = address
        self.port = port
        self.dbpool = POOL()

    def alertMute(self, vardict):
        """
        告警屏蔽模块
        :param vardict 屏蔽规则字典
        """
        def getSql():
            now = int(time.time())
            note, cause = "临时屏蔽规则", "屏蔽原因"
            tags = []
            btime, etime = now, now + 3600
            for k,v in vardict.items():
                tempdict = {}
                tempdict["func"], tempdict["key"], tempdict["value"] = "==", k , v
                tags.append(tempdict)
            tags = json.dumps(json.dumps(tags))
            verifysql = "select 1 from alert_mute where tags=%s" %(tags)
            insertsql = "insert into alert_mute (group_id, prod, note, cate, cluster, datasource_ids, tags, cause, btime, etime, disabled, mute_time_type, periodic_mutes, severities, create_at, create_by, update_at, update_by) values (8, \"metric\", \"临时屏蔽规则\", \"prometheus\", 0, \"[0]\", %s, \"\", %s, %s, 0, 0, '[{\"enable_stime\":\"00:00\",\"enable_etime\":\"00:00\",\"enable_days_of_week\":\"1 2 3 4 5 6 0\"}]', '[1,2,3]', %s, \"root\", %s, \"root\" )" %(tags, btime, etime, now, now)
            return insertsql, verifysql
        insertsql, verifysql = getSql()
        conn = self.dbpool.connection()
        cursor = conn.cursor()