import requests
import configparser
import argparse


#   Пример использования, регистр важен:
# python3 zbx_crete.py --host "Test" --temp "Linux by Zabbix agent" --ip "192.168.122.89" --group "Linux servers"
# python3 zabix_create2.py --host "test2" --temp "Aranet Cloud,Zabbix server health" --ip "192.168.122.89" --group "Hypervisors"

ZABBIX_API = 'http://192.168.122.76:8080/api_jsonrpc.php'  # адрес API заббикса


def arguments():  # функция считывает аргументы командной строки

    parser = argparse.ArgumentParser(description='file')
    parser.add_argument('--temp', dest='tmp', type=str)  # аргумент шаблона
    parser.add_argument('--host', dest='host', type=str)  # хостнейм
    parser.add_argument('--ip', dest='ip', type=str)  # аргумент ip адреса
    parser.add_argument('--group', dest='group', type=str)  # аргумент группы
    argument = parser.parse_args()
    template = argument.tmp
    ip_address = argument.ip
    hostname = argument.host
    grp_name = argument.group
    listing = {'template': template, 'host': hostname, 'ip': ip_address, 'group': grp_name}
    return listing


def confparse():  # парсится конфиг в формате ini с данными подключения
    config = configparser.ConfigParser()
    config.read('./files/zbx-config.conf')
    log = config['API']['login']
    pwd = config['API']['password']
    return {'userdata': {'login': log, 'password': pwd}}


def auth(log, pwd):  # происходит аутентификация и возврат токена доступа
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": log,
            "password": pwd},
        "id": 0
    })
    access = r.json()['result']
    return access


def get_template_id(template, access):  # получение id шаблона по его имени
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "template.get",
        "params": {
            "output": "extend",
            "filter": {
                "host": f"{template}"
            }
        },
        "auth": f"{access}",
        "id": 1
    })
    return r.json()


def get_template_host(hostname, access):  # исходя из имени хоста получаем имена и id его темплейтов

    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid"],
            "filter": {'host': hostname},
            "selectParentTemplates": [
                "templateid",
                "name"
            ]
        },
        "id": 1,
        "auth": f"{access}"
    })
    return r


def get_group_id(grp_name, access):  # получаем id группы из его названия
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "hostgroup.get",
        "params": {
            "output": "extend",
            "filter": {
                "name": f"{grp_name}"
            }
        },
        "auth": f"{access}",
        "id": 1
    })
    result = r.json()
    return result


def add_server(hostname, ip_addr, grp_id, access):  # функция добавления сервера
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "host.create",
        "params": {
            "host": f"{hostname}",
            "interfaces": [
                {
                    "type": 1,
                    "main": 1,
                    "useip": 1,
                    "ip": f"{ip_addr}",
                    "dns": "",
                    "port": "10050"
                }
            ],
            "groups": [
                {
                    "groupid": f"{grp_id}"
                }
            ],

            "inventory_mode": 0,
            "inventory": {
                "macaddress_a": "01234",
                "macaddress_b": "56768"
            }
        },
        "auth": f"{access}",
        "id": 10
    })
    result = r.json()
    print(result)
    return result


def link_template(host_id, template, access):
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "host.massadd",
        "params": {
            "templates": [
                {
                    "templateid": f"{template}"
                }
            ],
            "hosts": [
                {
                    "hostid": f"{host_id}"
                }
            ]
        },
        "auth": f"{access}",
        "id": 1
    })

    print(r.json())


def get_hosts(hostname, access):
    req = requests.post(ZABBIX_API, json={

        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "name"],
            "filter": {"host": f"{hostname}"},
        },
        "id": 1,
        "auth": access
    })
    result = (req.json())
    result = result['result']
    return result



if __name__ == '__main__':

    arg = arguments()  # получаем аргументы командной строки
    host = arg['host']  # получение имени хоста из cli
    tmp = arg['template'].split(',')  # получение имени шаблона из cli

    group = arg['group']   # получение имени группы из cli
    ip = arg['ip']  # получение ip адреса хоста из cli
    userdata = confparse()  # получаем данные конфигурационного файла
    login = userdata['userdata']['login']
    password = userdata['userdata']['password']
    token = auth(login, password)  # получение токена доступа к api


    template_host = get_template_host(host, token).json()  # получение шаблонов хоста



    lst = []  # список под id шаблонов хоста
    group_id = get_group_id(group, token)['result'][0]['groupid']
    templates_id = []


    for i in tmp:
        try:
            templates_id.append(get_template_id(i, token)['result'][0]['templateid'])  # получаем id шабл, указанного через cli

        except IndexError:
            print('Не правильно введен один из шаблонов.')


    if template_host['result'] == []:  # если хоста с таким именем нет в заббиксе
        print('Хоста нет в zabbix, он будет добавлен')
        add_server(host, ip, group_id, token)      # добавляем хост
        host_id = get_hosts(host, token)[0]['hostid']  # получаем айдишник нового хоста
        print(host_id)
        for i in templates_id:
            link_template(host_id, i, token)    # вешаем шаблоны
    else:
        print('Хост есть в zabbix. Добавление шаблонов.')
        host_id = get_hosts(host, token)[0]['hostid']
        for i in templates_id:
            link_template(host_id, i, token)
