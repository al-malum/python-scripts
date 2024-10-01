import requests
import configparser
import logging

ZABBIX_API = 'http://192.168.122.76:8080/api_jsonrpc.php'


def log():
    pass


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


def get_hosts(access):
    req = requests.post(ZABBIX_API, json={

        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "name"],
            "filter": {"host": ""},
        },
        "id": 1,
        "auth": access
    })
    result = (req.json())
    result = result['result']
    return result


def get_template(access, host):
    req = requests.post(ZABBIX_API, json={

        "jsonrpc": "2.0",
        "method": "template.get",
        "params": {
            "hostids": f"{host}"
        },
        "id": 2,
        "auth": access
    })
    templates = req.json()
    return templates


def get_item_host(host, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "hostids": f"{host}",
            "inherited": "true"
        },
        "auth": f"{access}",
        "id": 3
    })
    item_host = req.json()
    return item_host


def get_item_template(template_id, host, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "templateids": f"{template_id}",  # получает только элементы шаблона, без элементов хоста
            "hostids": f"{host}",
            "templated": "true"
        },
        "auth": f"{access}",
        "id": 4
    })
    item_temp = req.json()
    return item_temp


def comparison_items(h_items, t_items, host):
    logger = logging.getLogger('items')
    logger.setLevel(logging.WARNING)
    logger_handler = logging.FileHandler('zbx_cmp.log')
    logger_handler.setLevel(logging.WARNING)
    logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)

    for host_item in h_items:
        for temp_item in t_items:
            if host_item['name'] == temp_item['name']:
                h_key = host_item['key_']
                h_history = host_item['history']
                h_trends = host_item['trends']
                h_delay = host_item['delay']
                h_timeout = host_item['timeout']
                h_name = host_item['name']

                t_key = temp_item['key_']
                t_history = temp_item['history']
                t_trends = temp_item['trends']
                t_delay = temp_item['delay']
                t_timeout = temp_item['timeout']
                t_name = temp_item['name']

                message = f'- Different item "{h_name}" at host "{host}"'
                if h_key == t_key:
                    pass
                else:
                    logger.warning(message + f': recovery mode - {h_key} and {t_name}')
                if h_history == t_history:
                    pass
                else:
                    logger.warning(message + f': priority - {h_history} and {t_history}')
                if h_trends == t_trends:
                    pass
                else:
                    logger.warning(message + f': event name - {h_trends} and {t_trends}')
                if h_delay == t_delay:
                    pass
                else:
                    logger.warning(message + f': operation data - {h_delay} and {t_delay}')
                if h_timeout == t_timeout:
                    pass
                else:
                    logger.warning(message + f': name - {h_timeout} and {t_timeout}')



def get_trigger_host(host_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "hostids": f"{host_id}",
            "output": "extend",
            "selectFunctions": "extend",
            "inherited": "true"
        },
        "auth": f"{access}",
        "id": 1
    })
    host_trigger = req.json()
    return host_trigger


def get_trigger_template(template_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "templateids": f"{template_id}",
            "output": "extend",
            "selectFunctions": "extend"
        },
        "auth": f"{access}",
        "id": 1
    })
    return req.json()


def comparison_trigger(h_triggers, t_triggers, host):
    logger = logging.getLogger('trigger')
    logger.setLevel(logging.WARNING)
    logger_handler = logging.FileHandler('zbx_cmp.log')
    logger_handler.setLevel(logging.WARNING)
    logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)


    for host_trigger in h_triggers:
        for template_trigger in t_triggers:
            if host_trigger['description'] == template_trigger['description']:
                host_name = host_trigger['description']
                host_data = host_trigger['opdata']
                host_event = host_trigger['event_name']
                host_priority = host_trigger['priority']

                template_name = template_trigger['description']
                template_data = template_trigger['opdata']
                template_event = template_trigger['event_name']
                template_priority = template_trigger['priority']

                check = 0
                for j in range(len(host_trigger['functions'])):
                    host_function = host_trigger['functions'][check]['function']
                    host_param = host_trigger['functions'][check]['parameter']
                    template_function = template_trigger['functions'][check]['function']
                    template_param = template_trigger['functions'][check]['parameter']

                    message = f'- Different trigger "{host_name}" at host "{host}"'
                    if host_name == template_name:
                        pass
                    else:
                        logger.warning(message + f': recovery mode - {host_name} and {template_name}')
                    if host_data == template_data:
                        pass
                    else:
                        logger.warning(message + f': priority - {host_data} and {template_data}')

                    if host_event == template_event:
                        pass
                    else:
                        logger.warning(message + f': event name - {host_event} and {template_event}')

                    if host_priority == template_priority:
                        pass
                    else:
                        logger.warning(message + f': operation data - {host_priority} and {template_priority}')

                    if host_function == template_function:
                        pass
                    else:
                        logger.warning(message + f': name - {host_function} and {template_function}')

                    if host_param == template_param:
                        pass
                    else:
                        logger.warning(message + f': name - {host_param} and {template_param}')
                    check += 1


def get_graph_host(host_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "graphprototype.get",
        "params": {
            "hostids": f"{host_id}"
        },
        "auth": f"{access}",
        "id": 3
    })
    data = req.json()
    return data


def get_graph_temp(template_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "graphprototype.get",
        "params": {
            "templateids": f"{template_id}",
        },
        "auth": f"{access}",
        "id": 3
    })
    data = req.json()
    return data


def comparison_graph(graph_h, graph_t, host):
    logger = logging.getLogger('graph')
    logger.setLevel(logging.WARNING)
    logger_handler = logging.FileHandler('zbx_cmp.log')
    logger_handler.setLevel(logging.WARNING)
    logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)


    for host_graph in graph_h:
        for temp_graph in graph_t:
            if host_graph['name'] == temp_graph['name']:
                h_name = host_graph['name']
                h_width = host_graph['width']
                h_height = host_graph['height']
                h_yaxismin = host_graph['yaxismin']
                h_yaxismax = host_graph['yaxismax']
                h_show_work_period = host_graph['show_work_period']
                h_show_triggers = host_graph['show_triggers']
                h_show_legend = host_graph['show_legend']
                h_flags = host_graph['flags']
                h_show_3d = host_graph['show_3d']

                t_name = temp_graph['name']
                t_width = host_graph['width']
                t_height = host_graph['height']
                t_yaxismin = host_graph['yaxismin']
                t_yaxismax = host_graph['yaxismax']
                t_show_work_period = host_graph['show_work_period']
                t_show_triggers = host_graph['show_triggers']
                t_show_legend = host_graph['show_legend']
                t_flags = host_graph['flags']
                t_show_3d = host_graph['show_3d']
                message = f'- Different graph prototype "{h_name}" at host "{host}"'

                if h_name == t_name:
                    pass
                else:
                    logger.warning(message + f': recovery mode - {h_name} and {t_name}')
                if h_width == t_width:
                    pass
                else:
                    logger.warning(message + f': priority - {h_width} and {t_width}')
                if t_height == h_height:
                    pass
                else:
                    logger.warning(message + f': event name - {h_height} and {t_height}')
                if h_yaxismin == t_yaxismin:
                    pass
                else:
                    logger.warning(message + f': operation data - {h_yaxismin} and {t_yaxismin}')
                if h_yaxismax == t_yaxismax:
                    pass
                else:
                    logger.warning(message + f': name - {h_yaxismax} and {t_yaxismax}')
                if h_show_work_period == t_show_work_period:
                    pass
                else:
                    logger.warning(message + f': name - {h_show_work_period} and {t_show_work_period}')
                if h_show_triggers == t_show_triggers:
                    pass
                else:
                    logger.warning(message + f': name - {h_show_triggers} and {t_show_triggers}')
                if h_show_legend == t_show_legend:
                    pass
                else:
                    logger.warning(message + f': name - {h_show_legend} and {t_show_legend}')
                if h_flags == t_flags:
                    pass
                else:
                    logger.warning(message + f': name - {h_flags} and {t_flags}')
                if h_show_3d == t_show_3d:
                    pass
                else:
                    logger.warning(message + f': name - {h_show_3d} and {t_show_3d}')



def get_lld_host(host_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "discoveryrule.get",
        "params": {
            "output": "extend",
            "hostids": f"{host_id}",
            "inherited": "true"
        },
        "auth": f"{access}",
        "id": 5
    })
    lld = req.json()
    return lld


def get_lld_template(template_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "discoveryrule.get",
        "params": {
            "output": "extend",
            "templateids": f"{template_id}"
        },
        "auth": f"{access}",
        "id": 6
    })
    lld = req.json()
    return lld


def get_host_lld_prototype(host_id, host_lld_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "discoveryrule.get",
        "params": {
            "output": "extend",
            "hostids": f"{host_id}",
            "selectItems": f"{host_lld_id}",
            "inherited": "true"
        },
        "auth": f"{access}",
        "id": 6
    })
    lld = req.json()
    return lld


def comparison_lld(h_lld, t_lld, host):
    logger = logging.getLogger('lld')
    logger.setLevel(logging.WARNING)
    logger_handler = logging.FileHandler('zbx_cmp.log')
    logger_handler.setLevel(logging.WARNING)
    logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)



    for host_l in h_lld:
        for temp_l in t_lld:
            if host_l['name'] == temp_l['name']:
                h_name = host_l['name']
                h_key = host_l['key_']
                h_history = host_l['history']
                h_trands = host_l['trends']
                h_delay = host_l['delay']
                h_timeout = host_l['timeout']

                t_name = temp_l['name']
                t_key = temp_l['key_']
                t_history = temp_l['history']
                t_trands = temp_l['trends']
                t_delay = temp_l['delay']
                t_timeout = temp_l['timeout']

                message = f'- Different lld "{h_name}" at host "{host}"'
                if h_key == t_key:
                    pass
                else:
                    logger.warning(message + f': recovery mode - {h_key} and {t_name}')
                if h_history == t_history:
                    pass
                else:
                    logger.warning(message + f': priority - {h_history} and {t_history}')
                if h_trands == t_trands:
                    pass
                else:
                    logger.warning(message + f': event name - {h_trands} and {t_trands}')
                if h_delay == t_delay:
                    pass
                else:
                    logger.warning(message + f': operation data - {h_delay} and {t_delay}')
                if h_timeout == t_timeout:
                    pass
                else:
                    logger.warning(message + f': name - {h_timeout} and {t_timeout}')



def get_host_item_prototype(host_id, lld_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "itemprototype.get",
        "params": {
            "hostids": f"{host_id}",
            "discoveryids": f"{lld_id}"

        },
        "auth": f"{access}",
        "id": 3
    })
    data = req.json()
    return data


def get_template_item_prototype(template_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "itemprototype.get",
        "params": {
            "templateids": f"{template_id}",
        },
        "auth": f"{access}",
        "id": 3
    })
    data = req.json()
    return data


def comparison_item_prototype(items_prototype_h, sum_item_prot_t, host):
    logger = logging.getLogger('item prototype')
    logger.setLevel(logging.WARNING)
    logger_handler = logging.FileHandler('zbx_cmp.log')
    logger_handler.setLevel(logging.WARNING)
    logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)


    for host_prototype in items_prototype_h:
        for temp_prototype in sum_item_prot_t:
            if host_prototype['name'] == temp_prototype['name']:
                h_name = host_prototype['name']
                h_key = host_prototype['key_']
                h_history = host_prototype['history']
                h_trends = host_prototype['trends']
                h_delay = host_prototype['delay']
                h_timeout = host_prototype['timeout']

                t_name = temp_prototype['name']
                t_key = temp_prototype['key_']
                t_history = temp_prototype['history']
                t_trends = temp_prototype['trends']
                t_delay = temp_prototype['delay']
                t_timeout = temp_prototype['timeout']

                message = f'- Different item prototype "{h_name}" at host "{host}"'
                if h_key == t_key:
                    pass
                else:
                    logger.warning(message + f': recovery mode - {h_key} and {t_name}')
                if h_history == t_history:
                    pass
                else:
                    logger.warning(message + f': priority - {h_history} and {t_history}')
                if h_trends == t_trends:
                    pass
                else:
                    logger.warning(message + f': event name - {h_trends} and {t_trends}')
                if h_delay == t_delay:
                    pass
                else:
                    logger.warning(message + f': operation data - {h_delay} and {t_delay}')
                if h_timeout == t_timeout:
                    pass
                else:
                    logger.warning(message + f': name - {h_timeout} and {t_timeout}')



def get_host_trigger_prototype(host_id, host_lld_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "triggerprototype.get",
        "params": {
            "hostids": f"{host_id}",
            "discoveryids": f"{host_lld_id}",
        },
        "auth": f"{access}",
        "id": 6
    })
    data = req.json()
    return data


def get_temp_trigger_prototype(template_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "triggerprototype.get",
        "params": {
            "templateids": f"{template_id}",
        },
        "auth": f"{access}",
        "id": 3
    })
    data = req.json()
    return data


def comparison_trigger_prototype(trg_prt_h, sum_trg_prt_t, host):
    logger = logging.getLogger('item prototype')
    logger.setLevel(logging.WARNING)
    logger_handler = logging.FileHandler('zbx_cmp.log')
    logger_handler.setLevel(logging.WARNING)
    logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)


    for host_trig in trg_prt_h:
        for tem_trig in sum_trg_prt_t:
            if host_trig['description'] == tem_trig['description'] and 'inodes' not in host_trig['description']:
                host_name = host_trig['description']
                host_data = host_trig['opdata']
                host_event = host_trig['event_name']
                host_priority = host_trig['priority']
                host_recovery = host_trig['recovery_mode']

                template_name = tem_trig['description']
                template_data = tem_trig['opdata']
                template_event = tem_trig['event_name']
                template_priority = tem_trig['priority']
                template_recovery = tem_trig['recovery_mode']


                message = f'- Different trigger prototype "{host_name}" at host "{host}"'
                if host_name == template_name:
                    pass
                else:
                    logger.warning(message + f': recovery mode - {host_recovery} and {template_priority}')
                if host_data == template_data:
                    pass
                else:
                    logger.warning(message + f': priority - {host_priority} and {template_priority}')
                if host_event == template_event:
                    pass
                else:
                    logger.warning(message + f': event name - {host_event} and {template_event}')
                if host_priority == template_priority:
                    pass
                else:
                    logger.warning(message + f': operation data - {host_data} and {template_data}')
                if host_recovery == template_recovery:
                    pass
                else:
                    logger.warning(message + f': name - {host_name} and {template_name}')



def get_graph_prot_host(host_id, lld_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "graphprototype.get",
        "params": {
            "hostids": f"{host_id}",
            "discoveryids": f"{lld_id}"

        },
        "auth": f"{access}",
        "id": 3
    })
    data = req.json()
    return data


def get_graph_prot_temp(template_id, access):
    req = requests.post(ZABBIX_API, json={
        "jsonrpc": "2.0",
        "method": "graphprototype.get",
        "params": {
            "templateids": f"{template_id}",
        },
        "auth": f"{access}",
        "id": 3
    })
    data = req.json()
    return data


def comparison_prot_graph(graph_prot_h, sum_graph_prot_t, host):
    logger = logging.getLogger('item prototype')
    logger.setLevel(logging.WARNING)
    logger_handler = logging.FileHandler('zbx_cmp.log')
    logger_handler.setLevel(logging.WARNING)
    logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)


    for host_graph in graph_prot_h:
        for temp_graph in sum_graph_prot_t:
            if host_graph['name'] == temp_graph['name']:
                h_name = host_graph['name']
                h_width = host_graph['width']
                h_height = host_graph['height']
                h_yaxismin = host_graph['yaxismin']
                h_yaxismax = host_graph['yaxismax']
                h_show_work_period = host_graph['show_work_period']
                h_show_triggers = host_graph['show_triggers']
                h_show_legend = host_graph['show_legend']
                h_flags = host_graph['flags']
                h_show_3d = host_graph['show_3d']


                t_name = temp_graph['name']
                t_width = host_graph['width']
                t_height = host_graph['height']
                t_yaxismin = host_graph['yaxismin']
                t_yaxismax = host_graph['yaxismax']
                t_show_work_period = host_graph['show_work_period']
                t_show_triggers = host_graph['show_triggers']
                t_show_legend = host_graph['show_legend']
                t_flags = host_graph['flags']
                t_show_3d = host_graph['show_3d']

                message = f'- Different graph prototype "{h_name}" at host "{host}"'
                if h_name == t_name:
                    pass
                else:
                    logger.warning(message + f': recovery mode - {h_name} and {t_name}')
                if h_width == t_width:
                    pass
                else:
                    logger.warning(message + f': priority - {h_width} and {t_width}')
                if t_height == h_height:
                    pass
                else:
                    logger.warning(message + f': event name - {h_height} and {t_height}')
                if h_yaxismin == t_yaxismin:
                    pass
                else:
                    logger.warning(message + f': operation data - {h_yaxismin} and {t_yaxismin}')
                if h_yaxismax == t_yaxismax:
                    pass
                else:
                    logger.warning(message + f': name - {h_yaxismax} and {t_yaxismax}')
                if h_show_work_period == t_show_work_period:
                    pass
                else:
                    logger.warning(message + f': name - {h_show_work_period} and {t_show_work_period}')
                if h_show_triggers == t_show_triggers:
                    pass
                else:
                    logger.warning(message + f': name - {h_show_triggers} and {t_show_triggers}')
                if h_show_legend == t_show_legend:
                    pass
                else:
                    logger.warning(message + f': name - {h_show_legend} and {t_show_legend}')
                if h_flags == t_flags:
                    pass
                else:
                    logger.warning(message + f': name - {h_flags} and {t_flags}')
                if h_show_3d == t_show_3d:
                    pass
                else:
                    logger.warning(message + f': name - {h_show_3d} and {t_show_3d}')






if __name__ == '__main__':

    userdata = confparse()
    login = userdata['userdata']['login']
    password = userdata['userdata']['password']

    token = auth(login, password)  # получили токен из функции авторизации
    hosts = get_hosts(token)  # получаем список хостов с метаданными
    for i in hosts:
        sum_temp_item = []
        sum_temp_lld = []  # объявляются списки для суммирования данных всех шаблонов и хостов
        sum_temp_trigger = []
        sum_host_lld_prot = []
        sum_item_prot_temp = []
        itemid_lld_list = []
        itemid_proto_items = []
        buffer = []
        items_prototype_host = []
        trg_prt_host = []
        sum_trg_prt_temp = []
        graph_prot_host = []
        sum_graph_prot_temp = []
        sum_graph_temp = []



        hostname = i['name']
        hostid = i['hostid']  # достаем по одному айдишнику из списка
        print(hostid)
        template = get_template(token, hostid)['result']  # получаем шаблоны хоста с метаданными
        host_items = get_item_host(hostid, token)['result']  # получаем итемы хоста с метаданными
        host_triggers = get_trigger_host(hostid, token)['result']  # получаем триггеры хоста
        graph_host = get_graph_host(hostid, token)['result']
        host_lld = get_lld_host(hostid, token)['result']  # получаем список lld хоста

        # далее на основании lld id и host id будут получены прототипы данного ллд и хоста
        for item in host_lld:
            itemid_lld_list.append(item['itemid'])   # список id lld для передачи в запрос
        for one in itemid_lld_list:
            items_prototype_host = items_prototype_host + get_host_item_prototype(hostid, one, token)['result']
            trg_prt_host = trg_prt_host + get_host_trigger_prototype(hostid, one, token)['result']
            graph_prot_host = graph_prot_host + get_graph_prot_host(hostid, one, token)['result']



        for item in template:
            templateid = (item['templateid'])  # получаем айдишник шаблона
            template_items = get_item_template(templateid, hostid, token)  # получаем итемы шаблона с метаданными
            template_items = template_items['result']  # список итемов шаблона
            sum_temp_item += template_items  # заполняем список из всех итемов всех шаблонов хоста
            template_triggers = get_trigger_template(templateid, token)
            template_triggers = template_triggers['result']  # список триггеров шаблона
            sum_temp_trigger += template_triggers  # заполняем список из всех триггеров всех шаблонов хоста
            template_lld = get_lld_template(templateid, token)  # получаем lld шаблонов хоста с метаданными
            template_lld = template_lld['result']  # список lld шаблона
            sum_temp_lld += template_lld  # заполняем список из всех lld всех шаблонов хоста
            items_prototype_temp = get_template_item_prototype(templateid, token)['result']
            sum_item_prot_temp = sum_item_prot_temp + items_prototype_temp
            trg_prt_temp = get_temp_trigger_prototype(templateid, token)['result']    # триггер прототипы шаблона
            sum_trg_prt_temp = sum_trg_prt_temp + trg_prt_temp
            graph_prot_temp = get_graph_prot_temp(templateid, token)['result']
            sum_graph_prot_temp = sum_graph_prot_temp + graph_prot_temp
            graph_temp = get_graph_temp(templateid, token)['result']
            sum_graph_temp = sum_graph_temp + graph_temp


        comparison_items(host_items, sum_temp_item, hostname)  # сравниваем итемы хоста и итемы шаблона
        comparison_lld(host_lld, sum_temp_lld, hostname)  # сравниваем lld хоста и lld шаблона
        comparison_trigger(host_triggers, sum_temp_trigger, hostname)  # сравниваем триггеры хоста и триггеры шаблона
        comparison_item_prototype(items_prototype_host, sum_item_prot_temp, hostname)
        comparison_trigger_prototype(trg_prt_host, sum_trg_prt_temp, hostname)
        comparison_prot_graph(graph_prot_host, sum_graph_prot_temp, hostname)
        comparison_graph(graph_host, sum_graph_temp, hostname)
