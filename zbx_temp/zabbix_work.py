import configparser
from pyzabbix import ZabbixAPI


ZABBIX_API = 'https://zabbix.company.ru/api_jsonrpc.php'
WIN_TEMP = 10081
WIN_GRP = 516
LIN_TEMP = 10698
LIN_GRP = 2



def confparse():
    config = configparser.ConfigParser()
    config.read('zbx-config.conf')
    log = config['API']['login']
    pwd = config['API']['password']
    return {'login': log, 'password': pwd}


def create_api(log, pwd):
    zapi = ZabbixAPI('http://192.168.100.1:8080/api_jsonrpc.php', user=log, password=pwd)
    return zapi


def win_link(win_host, zapi):
    for w in win_host:
        print(zapi.do_request("hostgroup.massadd", {
            "groups": [
                 {
                     "groupid": f"{WIN_GRP}"
                 }
             ],
             "hosts": [
                 {
                     "hostid": f"{w['hostid']}"
                 }
             ]
        }))



def lin_link(lin_host, zapi):
    for l in lin_host:
        print(zapi.do_request("hostgroup.massadd", {
            "groups": [
                 {
                     "groupid": f"{LIN_GRP}"
                 }
             ],
             "hosts": [
                 {
                     "hostid": f"{l['hostid']}"
                 }
             ]
        }))


def get_host(zapi):
    win_host = zapi.host.get(templateids=WIN_TEMP)
    lin_host = zapi.host.get(templateids=LIN_TEMP)
    return {'win': win_host, 'lin': lin_host}


if __name__ == '__main__':
    cred = confparse()
    log = cred['login']
    pwd = cred['password']
    zapi = create_api(log, pwd)
    hosts = get_host(zapi)
    lin_host = hosts['lin']
    win_host = hosts['win']
    win_link(win_host, zapi)
    lin_link(lin_host, zapi)
