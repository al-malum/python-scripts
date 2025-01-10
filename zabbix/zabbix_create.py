# Импорт необходимых библиотек
import requests  # Для отправки HTTP-запросов
import configparser  # Для работы с конфигурационными файлами
import argparse  # Для обработки аргументов командной строки


# Пример использования:
# python3 zbx_create.py --host "Test" --temp "Linux by Zabbix agent" --ip "192.168.122.89" --group "Linux servers"
# python3 zabix_create2.py --host "test2" --temp "Aranet Cloud,Zabbix server health" --ip "192.168.122.89" --group "Hypervisors"

ZABBIX_API = 'http://192.168.122.76:8080/api_jsonrpc.php'  # URL для подключения к Zabbix API


# Функция для получения аргументов командной строки
def arguments():
    parser = argparse.ArgumentParser(description='file')

    # Определяем аргументы командной строки: шаблон (--temp), хост (--host), IP-адрес (--ip), группа (--group)
    parser.add_argument('--temp', dest='tmp', type=str)
    parser.add_argument('--host', dest='host', type=str)
    parser.add_argument('--ip', dest='ip', type=str)
    parser.add_argument('--group', dest='group', type=str)

    # Считываем аргументы из командной строки
    argument = parser.parse_args()

    # Разделяем аргументы на отдельные переменные
    template = argument.tmp
    ip_address = argument.ip
    hostname = argument.host
    grp_name = argument.group

    # Возвращаем все аргументы в виде словаря
    listing = {'template': template, 'host': hostname, 'ip': ip_address, 'group': grp_name}
    return listing


# Функция для чтения конфигурационного файла и извлечения данных о пользователе (логин и пароль)
def confparse():
    config = configparser.ConfigParser()
    config.read('./files/zbx-config.conf')

    # Чтение логина и пароля из конфигурационного файла
    log = config['API']['login']
    pwd = config['API']['password']

    # Возвращаем данные для аутентификации
    return {'userdata': {'login': log, 'password': pwd}}


# Функция для аутентификации пользователя в Zabbix API и получения токена доступа
def auth(log, pwd):
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",  # Версия JSON-RPC
        "method": "user.login",  # Метод для аутентификации
        "params": {
            "user": log,  # Логин
            "password": pwd  # Пароль
        },
        "id": 0  # Идентификатор запроса
    })
    
    # Извлекаем токен из ответа и возвращаем его
    access = r.json()['result']
    return access


# Функция для получения ID шаблона по имени шаблона
def get_template_id(template, access):
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",  # Версия JSON-RPC
        "method": "template.get",  # Метод для получения шаблона
        "params": {
            "output": "extend",  # Получаем все данные шаблона
            "filter": {
                "host": f"{template}"  # Фильтруем по имени шаблона
            }
        },
        "auth": f"{access}",  # Токен авторизации
        "id": 1  # Идентификатор запроса
    })
    
    # Возвращаем результат запроса (ID шаблона)
    return r.json()


# Функция для получения ID шаблонов, которые уже привязаны к хосту
def get_template_host(hostname, access):
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",  # Версия JSON-RPC
        "method": "host.get",  # Метод для получения хостов
        "params": {
            "output": ["hostid"],  # Получаем ID хоста
            "filter": {'host': hostname},  # Фильтруем по имени хоста
            "selectParentTemplates": [
                "templateid",  # Запрашиваем ID привязанных шаблонов
                "name"
            ]
        },
        "id": 1,
        "auth": f"{access}"  # Токен авторизации
    })
    
    # Возвращаем результат запроса
    return r


# Функция для получения ID группы хостов по названию группы
def get_group_id(grp_name, access):
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",  # Версия JSON-RPC
        "method": "hostgroup.get",  # Метод для получения групп хостов
        "params": {
            "output": "extend",  # Получаем все данные о группах
            "filter": {
                "name": f"{grp_name}"  # Фильтруем по имени группы
            }
        },
        "auth": f"{access}",  # Токен авторизации
        "id": 1  # Идентификатор запроса
    })
    
    # Возвращаем ID группы
    result = r.json()
    return result


# Функция для добавления нового хоста (сервера) в Zabbix
def add_server(hostname, ip_addr, grp_id, access):
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",  # Версия JSON-RPC
        "method": "host.create",  # Метод для создания хоста
        "params": {
            "host": f"{hostname}",  # Имя хоста
            "interfaces": [
                {
                    "type": 1,  # Тип интерфейса (для агента)
                    "main": 1,  # Главный интерфейс
                    "useip": 1,  # Используем IP
                    "ip": f"{ip_addr}",  # IP-адрес хоста
                    "dns": "",  # DNS (пусто)
                    "port": "10050"  # Порт для Zabbix агента
                }
            ],
            "groups": [
                {
                    "groupid": f"{grp_id}"  # ID группы хоста
                }
            ],
            "inventory_mode": 0,  # Режим инвентаризации
            "inventory": {
                "macaddress_a": "01234",  # MAC-адрес
                "macaddress_b": "56768"
            }
        },
        "auth": f"{access}",  # Токен авторизации
        "id": 10  # Идентификатор запроса
    })
    
    # Возвращаем результат запроса
    result = r.json()
    print(result)
    return result


# Функция для привязки шаблона к хосту
def link_template(host_id, template, access):
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",  # Версия JSON-RPC
        "method": "host.massadd",  # Метод для массового добавления шаблонов
        "params": {
            "templates": [
                {
                    "templateid": f"{template}"  # ID шаблона
                }
            ],
            "hosts": [
                {
                    "hostid": f"{host_id}"  # ID хоста
                }
            ]
        },
        "auth": f"{access}",  # Токен авторизации
        "id": 1  # Идентификатор запроса
    })

    # Печатаем результат привязки шаблона
    print(r.json())


# Функция для получения информации о хостах
def get_hosts(hostname, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",  # Версия JSON-RPC
        "method": "host.get",  # Метод для получения хостов
        "params": {
            "output": ["hostid", "name"],  # Запрашиваем ID и имя хоста
            "filter": {"host": f"{hostname}"},  # Фильтруем по имени хоста
        },
        "id": 1,
        "auth": access  # Токен авторизации
    })
    
    # Возвращаем результат запроса
    result = (req.json())
    result = result['result']
    return result


# Основная часть программы
if __name__ == '__main__':
    arg = arguments()  # Получаем аргументы командной строки
    host = arg['host']  # Имя хоста
    tmp = arg['template'].split(',')  # Шаблоны (может быть несколько, разделенных запятой)
    group = arg['group']   # Имя группы
    ip = arg['ip']  # IP-адрес хоста

    userdata = confparse()  # Получаем данные для аутентификации
    login = userdata['userdata']['login']
    password = userdata['userdata']['password']
    token = auth(login, password)  # Получаем токен доступа к Zabbix API

    # Получаем шаблоны, которые уже привязаны к хосту
    template_host = get_template_host(host, token).json()

    # Получаем ID группы хостов
    group_id = get_group_id(group, token)['result'][0]['groupid']

    # Получаем ID шаблонов из командной строки
    templates_id = []
    for i in tmp:
        try:
            templates_id.append(get_template_id(i, token)['result'][0]['templateid'])
        except IndexError:
            print('Ошибка: неправильно введен один из шаблонов.')

    # Если хоста нет в Zabbix, добавляем его
    if template_host['result'] == []:
        print('Хоста нет в Zabbix, он будет добавлен.')
        add_server(host, ip, group_id, token)      # Добавляем новый сервер
        host_id = get_hosts(host, token)[0]['hostid']  # Получаем ID нового хоста
        print(host_id)
        # Привязываем шаблоны к хосту
        for i in templates_id:
            link_template(host_id, i, token)
    else:
        print('Хост есть в Zabbix. Добавление шаблонов.')
        # Получаем ID хоста и привязываем шаблоны
        host_id = get_hosts(host, token)[0]['hostid']
        for i in templates_id:
            link_template(host_id, i, token)
