# py_ufos_autotest
Сборка контейнера для организации автотестирования

Для организации автотестирования стенда:
1) Добавить файл conf_<имя_сервера_уфос>.json, в который внести информацию о тестировании. 
Например, для WL:
{
    "zabbix_server": "zabbix_proxy02",
    "ufos_url": "http://host5:8889/index.html",
    "ufos_user": "<имя пользователя>",
    "ufos_password": "<пароль пользователя>"
}
для Jetty
{
    "zabbix_server": "zabbix_proxy02",
    "ufos_url": "http://host6:18080/",
    "ufos_user": "<имя пользователя>",
    "ufos_password": "<пароль пользователя>"
}

2) В консоли Zabbix для проверяемого сервера требуется добавить шаблон "ui-tests",
так же обязательно проверить параметр Имя узла сети (Host name), обязательно имя сервера должно быть без доменов (.ru и .ru)


Методы запуска скрипта отдельно:
python3 py_autotest.py conf -c conf_host1.json
'-c', '--config', help='Input Config file name', default='config.json'

python3 py_autotest.py args -l ufos_user -p ufos_password -u host:8889/index.html
'-u', '--url', help='Input a stand URL with a port. Example http://stand-test:8889'
'-l', '--login', help='Input a Login'
'-p', '--password', help='Input a Password'

Результат выполнения скрипта направляется с помощью zabbix api в формате json:
успешный:
host:host1
Succesfuly sended result to Zabbix server
{'result': 'True', 'index_time': 3937, 'login_time': 4365, 'logoff_time': 4439, 'time_final': 12741}

с ошибкой:
host:host1
Something went wrong when sending test result for server: eb-exp-test-ufos-jetty, check present item jsonresu
{"processed": 0, "failed": 1, "total": 1, "time": "0.000032", "chunk": 1}
{'result': 'True', 'index_time': 4437, 'login_time': 3171, 'logoff_time': 3654, 'time_final': 11262}

Запись результата тестирования:
успешный:
{'result': 'True', 'index_time': 4437, 'login_time': 3171, 'logoff_time': 3654, 'time_final': 11262}
с ошибками
{'result': 'False', 'index_time': -1, 'login_time': -1, 'logoff_time': -1, 'time_final': -1}

result: True|False - Выполнение теста успешно или ошибка в процессе (в части работы самого скрипта)
index_time: 9999|-1 - Время открытия страницы ввода логина и пароля  (мс), -1 если произошла ошибка во время открытия страницы или ошибка по таймауту
login_time: 9999|-1 - Время входа в  до загрузки консоли управления (мс), -1 если произошла ошибка во время открытия страницы или ошибка по таймауту
logoff_time: 9999|-1 - Время выхода из  до загрузки страницы ввода логина и пароля (мс), -1 если произошла ошибка во время открытия страницы или ошибка по таймауту
time_final: 9999|-1 - Общее время выполнения проверки, index_time + login_time + logoff_time

Результат тестирования с помощью zabbix sender передается в элемент данных (item) сервера jsonresult в виде json строки, после разбивается на соответствующие элементы данных: index_time, login_time, logoff_time, time_final, result_test
по которым выполняется проверка триггеров "Автотест: Время выполнения логина больше 30 секунд", "Автотест: Недоступен  на сервере" и "Автотест: Нет данных от скрипта автотеста "

Автозапуск скрипта с файлами конфигураций  по времени производится спомощью python модуля devcron.py и файла crontab
Cкрипт сборки файла crontab проверяет параметры в файлах параметров в каталоге stand_configs и добавляет их в файл crontab

Сборка контейнера происходит автоматически после внесения изменений в сборку.
Адрес docker контейнера:
registry-gitlab:5005/admins/py_ufos_autotest
После сборки производится запуск контейнера, на текущий момент на сервере host-ansible с командой:
docker container run -d --restart on-failure --name py_ufos_autotest registry-gitlab:5005/admins/py_ufos_autotest:latest

Для проверка логов работы контейнера со скриптом на docker-хосте :
docker container logs py_ufos_autotest

