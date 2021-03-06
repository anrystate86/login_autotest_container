import time
import argparse
import sys
import socket
import os
import logging
from logging.handlers import RotatingFileHandler
import json
from pyzabbix import ZabbixMetric, ZabbixSender
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

if not (os.path.exists('log')):
    os.mkdir('log')

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
chrome_options = Options()                                                                                                 
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
platform = sys.platform[0]
if platform == 'w':
    driver = webdriver.Chrome(os.path.dirname(os.path.abspath(__file__)) + '\\chromedriver.exe', options=chrome_options)
    log_file = "log\\autotest.log"
    if not (os.path.exists(log_file)):
        open(log_file, 'a').close()
else:
    driver = webdriver.Chrome(os.path.dirname(os.path.abspath(__file__)) + '/chromedriver', options=chrome_options)
    log_file = "log/autotest.log"
    if not (os.path.exists(log_file)):
        open(log_file, 'a').close()

log_handler = RotatingFileHandler(log_file, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

auto_log = logging.getLogger('root')
auto_log.setLevel(logging.INFO)
auto_log.addHandler(log_handler)

def return_result(result, conf): #Отправка результата в Zabbix
    driver.quit()
    jresult = json.dumps(result)
    auto_log.info('Send result'+jresult)
    host = (url.hostname).replace(".otr.ru","").replace(".pds","")
    print("host:" + host)
#    print("jresult:" + jresult)
#    zabbix_sender = ZabbixSender(zabbix_server='zabbix_proxy02')
    zabbix_sender = ZabbixSender(zabbix_server=conf['zabbix_server'])
    metrics = []
    m = ZabbixMetric(host, "jsonresult", jresult)
    metrics.append(m)
    send = zabbix_sender.send(metrics)
    if send.failed:
        print('Something went wrong when sending test result for server: ' + host + ', check present item jsonresult for server or wait 1 hour after adding it')
        print(send)
        auto_log.error('Something went wrong when sending test result for server: ' + host + ', check present item jsonresult for server or wait 1 hour after adding it')
    else:
        print('Succesfuly sended result to Zabbix server')
        auto_log.info('Succesfuly sended result to Zabbix server')
    print(result)
    exit()

def mknow(): #Получение текущего времени в микросекундах для Zabbix
    return int(round(time.time() * 1000))

def get_config(cfile):
    try:
        cfile = open(cfile,'r')
        config = json.loads(cfile.read())
        cfile.close
    except Exception as error:
        print(error)
        auto_log.warning("Can't read config file config.json, will use starting arguments")
        return False
    auto_log.info("Reading config file config.json")
    return config

def createParser(): #Парсер параметров запуска
    config = {'ufos_url':'host1' ,'ufos_user':'user' , 'ufos_password':'pass', 'zabbix_server':'zabbix_proxy02'}
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    conf_parser = subparsers.add_parser('conf')
    conf_parser.add_argument('-c', '--config', help='Input Config file name')

    args_parser = subparsers.add_parser('args')
    args_parser.add_argument('-u', '--url', required=True, help='Input a stand URL with a port. Example http://stand-test:8889', type=str) 
    args_parser.add_argument('-l', '--login', required=True, help='Input a Login', type=str) 
    args_parser.add_argument('-p', '--password', required=True, help='Input a Password') 
    args_parser.add_argument('-z', '--zabbix', help='Input a Zabbix proxy server', type=str, default=config['zabbix_server'])


    args = parser.parse_args()
    if args.command == 'conf':
        conf = get_config(args.config)
    elif args.command == 'args':
        conf['ufos_url'] = args.url
        conf['ufos_user'] = args.login
        conf['ufos_password'] = args.password
        conf['zabbix_server'] = args.zabbix
    else:
        print('using script ...')
        exit(1)
    return conf

def open_url(driver, url, result): #Проверка на открытие индексной страницы
    index_time = mknow()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 120)
        wait.until(expected_conditions.element_to_be_clickable((By.ID,"user")))
    except Exception as error:
        auto_log.exception('Error on testing open URL ' + url)
        auto_log.exception(error)
        #print(error)
        return False
    result['result'] = 'True'
    result['index_time'] = mknow() - index_time
    result['time_final'] = result['index_time'] + result['login_time'] + result['logoff_time']
    auto_log.info('Open URL successfuly tested')
    return True

def login_url(driver, result): #Проверка на логин в 
    login_time = mknow()
    try:
        driver.find_element(By.ID,"user").click()
        driver.find_element(By.ID, "user").send_keys(config['ufos_user'])
        driver.find_element(By.ID, "psw").click()
        driver.find_element(By.ID, "psw").send_keys(config['ufos_password'])
        driver.find_element(By.ID, "okButton").click()
        wait = WebDriverWait(driver, 120)
        wait.until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[contains(.,'Настройки')]")))
    except Exception as error:
        auto_log.exception('Error on testing login to UFOS')
        auto_log.exception(error)
        #print(error)
        return False
    result['result'] = 'True'
    result['login_time'] = mknow() - login_time
    result['time_final'] = result['index_time'] + result['login_time'] + result['logoff_time']
    auto_log.info('Login to Ufos successfuly tested')
    return True

def exit_url(driver, result): #Проверка на выход из
    logoff_time = mknow()
    try:
        wait = WebDriverWait(driver, 120)
        wait.until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[contains(.,'Настройки')]")))
        driver.find_element(By.XPATH, "//span[contains(.,'Настройки')]").click()
        driver.find_element(By.XPATH, "//span[contains(.,'Выйти')]").click()
        wait.until(expected_conditions.element_to_be_clickable((By.ID,"user")))
    except Exception as error:
        auto_log.exception('Error on testing logoff from UFOS')
        auto_log.exception(error)
        #print(error)
        return False
    result['logoff_time'] = mknow() - logoff_time
    result['result'] = 'True'
    result['time_final'] = result['index_time'] + result['login_time'] + result['logoff_time']
    auto_log.info('Logoff from Ufos successfuly tested')
    return True

if __name__ == "__main__":
    times = {'result':'False', 'index_time':-1, 'login_time':-1, 'logoff_time':-1, 'time_final':-1}
    auto_log.info('')
    auto_log.info('Starting autotest script')

    config = createParser()

    ufos_url_stend = config['ufos_url']
    url = urlparse(ufos_url_stend)
    if url.port == 8889:
        ufos_url = "http://" + url.netloc + "/index.html"
    else:
        ufos_url = "http://" + url.netloc
    
    auto_log.info('Will testing url ' + ufos_url)

    if not (open_url(driver, ufos_url, times)):
        return_result(times, config)
    
    if not (login_url(driver, times)):
        return_result(times, config)

    if not (exit_url(driver, times)):
        return_result(times, config)
 
    return_result(times, config)
