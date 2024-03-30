#!/bin/python
# -*- coding: utf-8 -*-
import requests
import json
from base.feishu import FeishuTalk
"""
用于发送告警聚合信息到公共聊天组中
"""

feishutoken = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

class GetApiMessage:

    def __init__(self, username = "root", password = "xxxxxxx"):
        self.username = username
        self.password = password
        self.token = ""

    def getToken(self):
        try:
            url = "http://n9e:17000/api/n9e/auth/login"
            data = {"username": self.username, "password": self.password}
            response = requests.post(url = url, json = data)
            target = json.loads(response.text)
            self.token = target['dat']['access_token']
        except Exception as e:
            print("update n9e token error, reason is %s", e)
        finally:
            return

    def getAlert(self):
        try:
            url = 'http://n9e:17000/api/n9e/alert-cur-events/card?hours=24&rule=tagkey:project'
            headers = {"Authorization": "Bearer %s" %(self.token)}
            response = requests.get(url = url, headers = headers)
            target = json.loads(response.text)
            title = "近24小时未恢复告警汇总\n"
            content = ""
            end = "详见: http://n9e.leiting.com/alert-cur-events"
            for event in target["dat"]:
                project = event["title"]
                nums = event["total"]
                content += "项目:" + project + " 异常告警数:" + str(nums) + "\n"
            if content:
                FeishuTalk(feishutoken).sendTextmessage(title + content + end)
        except Exception as e:
            print("get n9e alert error, reason is %s", e)
        finally:
            return


n9e = GetApiMessage()
n9e.getToken()
n9e.getAlert()