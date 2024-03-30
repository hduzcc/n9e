#!/bin/python
# -*- coding: utf-8 -*-
import pymysql
import time
import sys

"""
本脚本用于夜莺自动创建 项目 项目所属团队 项目告警机器人脚本，并生成其绑定关系
:use python3 create_project_for_n9e.py 伊洛纳 elona zhengcc
:param sys.argv[1] -> 项目中文名
       sys.argv[2] -> 项目英文名
       sys.argv[3] -> 项目负责人ldap账号 需要先登录过n9e
:other 执行完成后自动创建 机器人账号:{sys.argv[2]}_alert 密码:game.xxxx.com
:return: None
"""

project = sys.argv[1]
project_en = sys.argv[2]
user = sys.argv[3]
ntime = int(time.time())
conn = pymysql.connect(host="mysql", port=3306, user="root", passwd="1234", db="n9e_v6", charset="utf8mb4")

cursor = conn.cursor()
# 创建业务组
cursor.execute("insert into busi_group (name, label_enable, label_value, create_at, create_by, update_at, update_by) values( '%s', 0, '', %s, 'root', %s, 'root')" %(project, ntime, ntime))
# 创建团队
cursor.execute("insert into user_group (name, note, create_at, create_by, update_at, update_by) values('%s研发团队', '%s', %s, 'root', %s, 'root')" %(project, project_en, ntime, ntime))
# 创建机人
cursor.execute("insert into users(username, nickname, password, roles, contacts, maintainer, create_at, create_by, update_at, update_by) values('%s_alert','%s告警小助手','08896f097d2ff12ddf22ec6354023b9f', 'Guest', '{}', 0, %s, 'root', %s, 'root')" %(project_en, project, ntime, ntime))

# 找到 业务组id 团队id 机器人id 和项目负责人id 仅支持单线程操作
cursor.execute("select max(id) from busi_group") 
busi_group_id = cursor.fetchall()[0][0]
cursor.execute("select max(id) from user_group")
user_group_id = cursor.fetchall()[0][0]
cursor.execute("select max(id) from users")
robot_id = cursor.fetchall()[0][0]
cursor.execute("select id from users where username='%s'" %(user))
user_id = cursor.fetchall()[0][0]

# 创建业务组团队绑定关系
cursor.execute("insert into busi_group_member (busi_group_id, user_group_id, perm_flag) values (%s, %s, 'rw')" %(busi_group_id, user_group_id))
# 机器人 项目负责人归属于团队
cursor.execute("insert into user_group_member (group_id, user_id) values (%s, %s)" %(user_group_id, robot_id))
cursor.execute("insert into user_group_member (group_id, user_id) values (%s, %s)" %(user_group_id, user_id))

conn.commit()
cursor.close()
conn.close