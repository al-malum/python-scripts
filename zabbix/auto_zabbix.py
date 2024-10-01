import os





'''______________ПАРСИНГ ФАЙЛА СО СПИСКОМ ХОСТОВ____________'''

def read():
    with open('files/req.txt') as obj:
        text = obj.read()
    text = text.split()
    return(text)


def parse(text):
    hosts = []
    for i in range(int(len(text)/3)):

        host = text[0:3]
        del(text[0:3])


        hosts.append(host)
    return(hosts)


def req(hosts, URL, number):
    trigger = len(hosts)
    for i in range(trigger):
        host = hosts[0:3]
        host_ip = host[0]
        hostname = host[1]
        cname = host[2]
        del hosts[0:3]
        request = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": f"{hostname}",
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": f"{host_ip}",
                        "dns": f"{hostname}.int.sblogistica.ru",
                        "port": "10050"
                    }
                ],
                "groups": [
                    {
                        "groupid": "50"
                    }
                ],
                "tags": [
                    {
                        "tag": f"Host name",
                        "value": f"{cname}"
                    }
                ],
                "templates": [
                    {
                        "templateid": "20045"
                    }
                ],
                "macros": [
                    {
                        "macro": "{$USER_ID}",
                        "value": "123321"
                    },
                    {
                        "macro": "{$USER_LOCATION}",
                        "value": "0:0:0",
                        "description": f"Хост поставлен на мониторинг по наряду {number}"
                    }
                ],
                "inventory_mode": 0,
                "inventory": {
                    "macaddress_a": "01234",
                    "macaddress_b": "56768"
                }
            },
            "auth": "038e1d7b1735c6a5436ee9eae095879e",
            "id": 1
        }

        os.system(f'curl -X POST {URL} -H Content-Type: application/json-rpc -d {request}')


if __name__ == '__main__':
    number = input('Номер наряда: ')
    URL = 'URL'
    text = read()
    hosts = parse(text)



