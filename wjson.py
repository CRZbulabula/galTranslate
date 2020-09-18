import json

dic = {}
result = []
filename = './config/config.json'

dic['tId'] = 'AKIDoP5VdUJdr538wTppa4UdwytZyxfO967s'
dic['tKey'] = 'e4FH2X5NQGp9MIxsYzB9vVrxiKitvjkg'
dic['gap'] = 1
result.append(dic)

with open(filename, 'w') as f:
    json.dump(result, f)