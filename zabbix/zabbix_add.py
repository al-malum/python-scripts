import requests
import configparser
import argparse

ZABBIX_API = 'http://192.168.122.76:8080/api_jsonrpc.php'


def arguments():

    parser = argparse.ArgumentParser(description='file')
    parser.add_argument('--temp', dest='tmp', type=str)
    parser.add_argument('--host', dest='host', type=str)
    arg = parser.parse_args()
    templ = arg.tmp.split()
    host = arg.host.split()
    listing = {'template': templ, 'host': host}
    return listing



def confparse():
    config = configparser.ConfigParser()
    config.read('./files/zbx-config.conf')
    log = config['API']['login']
    pwd = config['API']['password']
    return {'userdata': {'login': log, 'password': pwd}}


def auth(log, pwd):
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


def get_groupid(access):
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "hostgroup.get",
        "params": {
            "output": "extend",
            "filter": {
                "name": [
                    "Zabbix servers",
                    "Linux servers"
                ]
            }
        },
        "auth": access,
        "id": 5
        })
    print(r.json()['result'])


def get_templateid(access):
    r = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "template.get",
        "params": {
            "output": "extend",
            "filter": {
                "host": [
                    "Template OS Linux",
                    "Linux by Zabbix agent"
                ]
            }
        },
        "auth": f"{access}",
        "id": 3
        })
    print(r.json()['result'])


def add_server(check, access):
    r = requests.post(ZABBIX_API, json={
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": f"Linux server{check}",
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": "127.0.0.1",
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": [
                    {
                        "groupid": "2"
                    }
                ],
                "templates": [
                    {
                        "templateid": "10001"
                    }
                ],
                "inventory_mode": 0,
                "inventory": {
                    "macaddress_a": "01234",
                    "macaddress_b": "56768"
                }
            },
            "auth": f"{access}",
            "id": 1
        })
    access = r.json()['result']
    return access


if __name__ == '__main__':


    userdata = confparse()
    login = userdata['userdata']['login']
    password = userdata['userdata']['password']

    token = auth(login, password)

    get_groupid(token)
    get_templateid(token)

    for i in range(20):
        add_server(i, token)
