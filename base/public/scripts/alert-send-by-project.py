#!/bin/python
# -*- coding: utf-8 -*-
import os
import time
import requests
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from base.db_utils import POOL
from base.feishu import FeishuTalk
from base.call import AliSingleCallByTts
import logging

"""
用于对夜莺告警事件进行告警分发
"""
infodict = {
    "rulename": "告警规则",
    "project": "项目",
    "env": "环境",
    "region": "地域",
    "namespace": "命名空间",
    "node": "node节点",
    "ident": "上报主机",
    "job_name": "任务名称",
    "instance_name": "实例",
    "dist_id": "区组id",
    "dist": "区组",
    "server": "服务",
    "server_id": "区组id",
    "server_name": "区组名",
    "device": "文件系统",
    "persistentvolume": "pv",
    "persistentvolumeclaim": "pvc",
    "phase": "阶段",
    "condition": "条件",
    "reason": "原因",
    "pod": "pod",
    "container": "container",
    "zone": "地区"
}
eventdict = {
    1: ["致命", "red"],
    2: ["严重", "yellow"],
    3: ["警告", "blue"]
}
logfile = "/app/src/alert_send_by_project.log"
logging.basicConfig(filename=logfile, level=logging.INFO)

class AlertDispatch:
    # 定义发送线程池大小 cachefile用于存储告警事件id避免重复发送相同告警信息
    def __init__(self, cachefile = "/app/src/eventid", poolsize = 16):
        """
        初始化线程池大小和缓存配置
        :param cachefile: 缓存配置信息 poolsize: 异步线程池大小
        :return: 
        """
        self.pool = ThreadPoolExecutor(max_workers=poolsize)
        self.cachefile = cachefile
        self.dbpool = POOL()
        # 用于初始化 eventid 避免告警重复发送
        conn = self.dbpool.connection()
        cursor = conn.cursor()
        cursor.execute("SELECT IFNULL(MAX(id) - 1, 0) FROM alert_cur_event")
        event = cursor.fetchall()
        self.result = event[0][0]
        cursor.close()
        conn.close()

    def getEventIdCache(self):
        """
        用于获取event缓存配置中的缓存id
        :param
        :return: eventid 
        """
        if os.path.exists(self.cachefile):
            f = open(self.cachefile, mode='r', encoding= 'utf-8')
            result = f.readline()
            if not result:
                result = self.result
            else:
                result = int(result)
            f.close()
        else:
            os.mknod(self.cachefile)
            result = self.result
        return result

    def saveEventIdCache(self,eventid):
        """
        用于缓存获取到的事件id
        :param eventid: 数据库中的事件id 为自增id
        :return:
        """
        f = open(self.cachefile, mode='w', encoding= 'utf-8')
        f.write(str(eventid))
        return  
        

    def consumeOne(self,event):
        """
        单个告警信息的处理逻辑
        通过告警事件中的项目名与数据库中的团队标签进行匹配，获取对应团队下的飞书机器人进行告警分发
        :param event: [事件id(str), 告警级别(int), 标签(str), 告警触发值(str), 告警时间(timestamp)]
        :return:
        """
        def initContent(content):
            # 初始化消息卡片正文
            res = {
                  "tag": "div",
                  "text": {
                  "content": content,
                  "tag": "lark_md"
                  }
                }
            return res
        # 将event[2] 告警事件所带标签转字典格式
        tags = event[2]
        tag_dict = dict()
        # 将事件内容转字典格式
        for tag in tags.split(",,"):
            tag = tag.split("=")
            tag_dict[tag[0]] = tag[1]
        if not tag_dict.get("project"):
            logging.error("事件id=%s 不存在project标签，请确认", event[0])
            return
        # 初始化告警文本信息 content
        level = eventdict[event[1]][0]
        color = eventdict[event[1]][1]
        project = tag_dict.get("project")
        alertname = tag_dict.get("alertname")
        content = list()
        for k in infodict.keys():
            if tag_dict.get(k):
                content.append(initContent("** %s：**%s" %(infodict[k], tag_dict[k])))
        content.append(initContent("** 告警触发值：**%s" %(event[3])))
        content.append(initContent("** 告警时间：**%s" %(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event[4])))))
        logging.info("飞书发送字典值为 %s", tag_dict)
        # 通过 project 获取所属团队下的用户 注意需要给团队打上标签，标签名与project一致
        conn = self.dbpool.connection()
        cursor = conn.cursor()
        try:
            # 只有prod环境或不带env标签的项目下的致命告警才会调用电话通知
            if event[1] == 1 and ((tag_dict.get("env") and tag_dict["env"] == "prod") or not tag_dict.get("env")):
                content.append(initContent("<at id=all></at>"))
                cursor.execute("select phone from users where phone!='' and id in \
                          (select user_id from user_group_member where group_id in \
                          (select id from user_group where note=%s))", tag_dict["project"])
                presult = cursor.fetchall()
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                loop = asyncio.get_event_loop()
                for phone in presult:
                    loop.run_until_complete(AliSingleCallByTts.doCall(phone[0], tag_dict["project"], tag_dict["rulename"]))
                loop.close()
            # 查询项目下告警机器人携带的飞书 token 并发送告警信息
            cursor.execute("select contacts from users where contacts is not NULL and id in \
                          (select user_id from user_group_member where group_id in \
                          (select id from user_group where note=%s))", tag_dict["project"])
            result = cursor.fetchall()
            for tokens in result:
                token = json.loads(tokens[0]).get("feishu_robot_token")
                if token:
                    print(project,alertname)
                    FeishuTalk(token).sendInteractive(level, color, content, project, alertname)
            logging.info("事件内容:%s  webhook:%s", tags, result)
        except Exception as e:
            logging.error("consumeOneError reason is %s", e)
        finally:
            cursor.close()
            conn.close()

    # 告警事件处理逻辑
    def consume(self):
        """
        告警事件处理逻辑
        查询数据库中比缓存的事件id大的告警事件，对其进行告警分发
        :param
        :return:
        """
        conn = self.dbpool.connection()
        cursor = conn.cursor()
        last_eventid = self.getEventIdCache()
        cursor.execute("SELECT id,severity,tags,trigger_value,trigger_time FROM alert_cur_event WHERE id > %s LIMIT 100", last_eventid)
        events = cursor.fetchall()
        cursor.close()
        conn.close()
        for event in events:
            # 事件信息可能很多 需要使用多线程处理
            self.pool.submit(self.consumeOne,event)
        # 保留最后的事件id
        if len(events) > 0:
            self.saveEventIdCache(event[0]) 

alert = AlertDispatch()
while True:
    alert.consume()
    time.sleep(30)