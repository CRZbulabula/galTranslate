#百度通用翻译API,不包含词典、tts语音合成等资源，如有相关需求请联系translate_api@baidu.com
# -*- coding: utf-8 -*-

import http.client
import hashlib
import urllib
import random
import json
from baiduocr import baiduOCR

def baidu(query, appid, secretKey):
	httpClient = None
	myurl = '/api/trans/vip/translate'

	fromLang = 'jp'
	toLang = 'zh'
	salt = random.randint(32768, 65536)
	sign = appid + query + str(salt) + secretKey
	sign = hashlib.md5(sign.encode()).hexdigest()
	myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(query) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

	try:
		httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
		httpClient.request('GET', myurl)


		# response是HTTPResponse对象
		response = httpClient.getresponse()
		result_all = response.read().decode("utf-8")
		result = json.loads(result_all)
		sentence = ''
		for item in result['trans_result']:
			sentence += item['dst']
		return sentence

	except Exception as e:
		print (e)
	
	finally:
		if httpClient:
			httpClient.close()

if __name__ == '__main__':
	baidu(baiduOCR())