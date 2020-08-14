# -*- coding: utf-8 -*-

import base64, json, re

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.tmt.v20180321 import tmt_client, models

def tencent(imageB64, tId, tKey):
	secretID = tId
	secretKey = tKey
	result = ''

	if (not secretID) or (not secretKey):
		result = '腾讯翻译：请注册API'
	else:
		try:
			cred = credential.Credential(secretID, secretKey)
			httpProfile = HttpProfile()
			httpProfile.endpoint = "tmt.tencentcloudapi.com"

			clientProfile = ClientProfile()
			clientProfile.httpProfile = httpProfile
			client = tmt_client.TmtClient(cred, "ap-guangzhou", clientProfile)

			req = models.ImageTranslateRequest()
			params = {"Data" : imageB64.decode(), "Source" : "ja", "Target" : "zh", "Scene" : "doc", "SessionUuid" : "session-00001", "ProjectId" : 0}
			req._deserialize(params)
			resp = client.ImageTranslate(req)
			#print(resp.to_json_string())
			sentence = re.findall(r'"TargetText": "(.+?)"', resp.to_json_string())
			for sentences in sentence:
				result += sentences
			#print(result)

		except TencentCloudSDKException as err:
			print(err)

	return result

if __name__ == '__main__':
	with open('./test.png', 'rb') as f:  # 以二进制读取图片
		data = f.read()
		encodestr = base64.b64encode(data) # 得到 byte 编码的数据
	#print(encodestr)
	tencent(encodestr)