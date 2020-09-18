# -*- coding: utf-8 -*-
import requests
import base64

def getAccessToken(client_id, client_secret):
	host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret
	response = requests.get(host)
	response = response.json()
	if 'access_token' in response:
		return response['access_token']
	else:
		return 'Error OCR client!'

def baiduOCR(imageB64, ocrId, ocrKey, ocrToken):
	request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
	result = ''

	if ocrToken[0] != '':
		access_token = ocrToken[0]
	else:
		access_token = getAccessToken(ocrId, ocrKey)
		ocrToken[0] = access_token

	if access_token == 'Error OCR client':
		return '百度OCR: 请注册并输入正确的OCR账户'

	params = {"image": imageB64, "language_type": "JAP"}
	request_url = request_url + "?access_token=" + access_token
	headers = {'content-type': 'application/x-www-form-urlencoded'}
	response = requests.post(request_url, data = params, headers = headers)
	response = response.json()
	for sentence in response['words_result']:
		result += sentence['words']
	return result

if __name__ == '__main__':
	baiduOCR()