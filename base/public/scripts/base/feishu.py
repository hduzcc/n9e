#!/bin/python
# -*- coding: utf-8 -*-
import json
import requests
class FeishuTalk:
    def __init__(self, token):
        feishu_token = token
        self.url = "https://open.feishu.cn/open-apis/bot/v2/hook/%s" %(feishu_token)
        
    def sendTextmessage(self,content):
        """
        发送告警信息至飞书
        :param content: 发送的文本信息
        :return 调用飞书api接口的返回信息
        """
        headers = {
            "Content-Type": "application/json; charset=utf-8",
        }
        payload_message = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        response = requests.post(url=self.url, data=json.dumps(payload_message), headers=headers)
        return response.json
    def sendInteractive(self, level, color, content, project, alertname):
        """
        飞书告警消息卡片
        :param content: 发送的主体信息
        :return 调用飞书api接口的返回信息
        """
        message = {
          "header": {
            "template": color,
            "title": {
              "tag": "plain_text",
              "content": "告警级别 %s" %(level)
            }
          },
          "elements": [
            {
              "tag": "column_set",
              "flex_mode": "none",
              "background_style": "default",
              "columns": [
                {
                  "tag": "column",
                  "width": "weighted",
                  "weight": 1,
                  "vertical_align": "top",
                  "elements": content
                }
              ]
            },
            {
              "tag": "div",
              "text": {
                "content": " [临时屏蔽1小时](http://n9e.xxxx.com:51001/lqiOKoFku2kBT6Hip8Cv3f6o?project=%s&alertname=%s) |  [录入报警处理过程](https://xxxx.feishu.cn/)" %(project, alertname),
                "tag": "lark_md"
              }
            }
          ]
        }
        headers = {
            "Content-Type": "application/json; charset=utf-8",
        }
        payload_message = {
            "msg_type": "interactive",
            "card": json.dumps(message)
        }
        response = requests.post(url=self.url, data=json.dumps(payload_message), headers=headers)
        return response.text