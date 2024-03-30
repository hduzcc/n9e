import pymysql
from dbutils.pooled_db import PooledDB

def POOL(host = "mysql", user = "root", pwd = "1234", db = "n9e_v6", port = 3306, maxconn = 16):
    res = PooledDB(
        # 使用连接数据库的模块
        creator = pymysql,
        # 最大连接数
        maxconnections = maxconn,
        # 初始化连接数
        mincached = maxconn,
        # 最多闲置的连接 0 为不限制
        maxcached = 0,
        # 最多共享的连接数 0为不限制
        maxshared = 0,
        # 如果没有可用连接是否阻塞
        blocking = True,
        # 一个连接最多可以被重复使用的次数 None 为无限制
        maxusage = None,
        # 开始会话前执行的命令列表 比如说["set time zone"]
        setsession = [],
        # 检查服务是否可用方式
        ping = 0,
        host = host,
        port = port,
        user = user,
        password = pwd,
        database = db,
        charset = 'utf8mb4'
    )
    return res
