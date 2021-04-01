import os
import json

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError as e:
    return False
  return True

def checkit(file): #Проверка наличия параметров в файле конфигурации УФОС
    f = open('./stand_configs/'+file, 'r')
    conf = f.read()
    f.close()
    try:
        json_object = json.loads(conf)
    except ValueError as e:
        print('Check config file for json standarts:'+file)
        return False
    if json_object['zabbix_server'] == '':
        print('Check config file for zabbix_server parameter:'+file)
        return False
    if json_object['ufos_url'] == '':
        print('Check config file for ufos_url parameter:'+file)
        return False
    if json_object['ufos_user'] == '':
        print('Check config file for ufos_user parameter:'+file)
        return False
    if json_object['ufos_password'] == '':
        print('Check config file for ufos_password parameter:'+file)
        return False
    
    return True

if __name__ == "__main__":
    #configs = os.listdir("./stand_configs")
    configs = []
    for i in os.listdir("./stand_configs"):
        if (i.split("_")[0] == 'conf') and checkit(i):
            configs.append(i)
            checkit(i)

    crontab = ''
    for j in configs:
        crontab+='*/10 * * * * python3 /build/ufos_autotest.py conf -c /build/stand_configs/' + j + '\n'
    
    if crontab != '':
        os.remove('crontab')
        f = open('crontab', 'w')
        f.write(crontab)
        f.close()
        print('True')
    else:
        print('False')
    #print(crontab)