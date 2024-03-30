# -*- coding: utf-8 -*-
import os
import sys
import asyncio

from typing import List

from alibabacloud_dyvmsapi20170525.client import Client as Dyvmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dyvmsapi20170525 import models as dyvmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from cryptography.hazmat.backends import default_backend


ALIBABA_CLOUD_ACCESS_KEY_ID = "*****************"
ALIBABA_CLOUD_ACCESS_KEY_SECRET = "************************"
# 语音通知模板ID 语音服务 -> 国内语音单呼 -> 语音通知 -> 文本转语音模板
TTS_CODE = "********"
# 呼叫显示号码 语音服务 -> 真实号服务 -> 真实号管理
SHOW_NUMBER = "*************"


class AliSingleCallByTts:
    def __init__(self):
        pass

    @staticmethod
    def createClient(access_key_id, access_key_secret):
        """
        使用AK&SK初始化账号Client
        :param access_key_id:
        :param access_key_secret:
        :return: Client
        :throws Exception
        """
        config = open_api_models.Config(
            # 必填，您的 AccessKey ID,
            access_key_id=access_key_id,
            # 必填，您的 AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # 访问的域名
        config.endpoint = f'dyvmsapi.aliyuncs.com'
        return Dyvmsapi20170525Client(config)

    @staticmethod
    async def doCall(mobile, group, info):
        """
        拨打电话
        :param mobile: 目标电话号码
        :param group: 告警项目中文名
        :param info: 告警信息
        :return: None
        :throws Exception
        """
        client = AliSingleCallByTts.createClient(ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET)
        single_call_by_tts_request = dyvmsapi_20170525_models.SingleCallByTtsRequest(
            called_number=mobile,
            tts_code=TTS_CODE,
            tts_param="{'hostgroup':'%s','info':'%s'}" %(group, info),
            called_show_number=SHOW_NUMBER
        )
        runtime = util_models.RuntimeOptions()
        try:
            await client.single_call_by_tts_with_options_async(single_call_by_tts_request, runtime)
        except Exception as error:
            UtilClient.assert_as_string(error.message)
            raise Exception("call failed,reason is %s", error.message)