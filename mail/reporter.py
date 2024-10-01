#!/usr/bin/python3
import smtplib
import os
import configparser
import argparse
import json
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ELIP='192.168.100.5'
JSON = '/tmp/dump.json'
CSV = '/tmp/dump.csv'
CONTENT = 'Content-type: application/json'
QUERY = '{"query": {"range": {"@timestamp": {"time_zone": "+03:00","gte": "now-1d/d","lte": "now/d"}}}}'
SIZE = 100  # максимально возможное количество документов к отправке, можно крутить


def arguments():
    parser = argparse.ArgumentParser(description='email')
    parser.add_argument('-f', dest='from_mail', type=str)
    parser.add_argument('-t', dest='dest', type=str)
    parser.add_argument('-p', dest='passw', type=str)
    parser.add_argument('-i', dest='index', type=str)
    arg = parser.parse_args()
    listing = {'from': arg.from_mail, 'to': arg.dest, 'passw': arg.passw, 'index': arg.index}
    return (listing)


def conf_pars():
    config = configparser.ConfigParser()
    config.read('/opt/reporter/conf.ini')
    data = {}
    password = config['mail']['password']
    mail_from = config['mail']['from']
    mail_to = config['mail']['to']
    log_el = config['mail']['log_el']
    pass_el = config['mail']['pass_el']
    data['passw'] = password
    data['from'] = mail_from
    data['to'] = mail_to
    data['log_el'] = log_el
    data['pass_el'] = pass_el
    return (data)


def send_email(body_email, header, data):
    """Функция логина и отправки сообщения"""

    addr_from = data['from']
    addr_to = data['to']
    password = data['passw']
    server = smtplib.SMTP('smail.company.ru', 587)
    server.starttls()

    try:
        msg = MIMEMultipart()  # Создаем сообщение
        msg['From'] = addr_from  # Адресат
        msg['To'] = addr_to  # Получатель
        msg['Subject'] = header  # Тема
        msg.attach(MIMEText(body_email, 'plain'))

        with open(CSV) as obj:
            file = MIMEText(obj.read())

        file.add_header('content-disposition', 'attachment', filename=CSV)
        msg.attach(file)
        server.login(addr_from, password)
        server.send_message(msg)
    except Exception as _ex:
        print(f'error: {_ex}')


def converter(JSON, CSV):
    cols = ['num_doc', 'message', 'time']
    CHECK = 0
    with open(JSON) as obj:
        js = json.load(obj)
        js = js['hits']['hits']
        print(js)
    if type(js) is list:
        with open(CSV, 'a') as obj:
            cv = csv.DictWriter(obj, fieldnames=cols)
            cv.writeheader()
            for i in js:
                CHECK += 1
                data = {'num_doc': CHECK, 'message': i['_source']['message'], 'time': i['_source']['@timestamp']}
                cv.writerow(data)
    else:
        CHECK = 1
        data = {'num_doc': CHECK, 'message': js['_source']['message'], 'time': js['_source']['@timestamp']}
        with open(CSV, 'a') as obj:
            cv = csv.DictWriter(obj, fieldnames=cols)
            cv.writeheader()
            cv.writerow(data)


if __name__ == '__main__':
    config = conf_pars()
    log_el = config['log_el']
    pass_el = config['pass_el']
    header = 'Письмо с данными Elasticsearch'  # Заголовок
    body_email = 'Выгрузка в формате CSV находится во вложении данного письма.'  # Тело сообщения
    data = arguments()
    index = data['index']
    url = f'http://{log_el}:{pass_el}@{ELIP}:9200/{index}/_search?size={SIZE}'

    os.system(f"curl -X POST '{url}' -H '{CONTENT}' -d '{QUERY}' -o {JSON}")
    converter(JSON, CSV)
    if data['from'] and data['to'] and data['passw']:
        send_email(body_email, header, data)
        os.system(f'rm {JSON} {CSV}')

    elif data['from'] and data['to']:
        data['passw'] = config['passw']
        send_email(body_email, header, data)
        os.system(f'rm {JSON} {CSV}')

    elif data['from'] and data['passw']:
        data['to'] = config['passw']
        send_email(body_email, header, data)
        os.system(f'rm {JSON} {CSV}')

    elif data['from']:
        data['passw'] = config['passw']
        data['to'] = config['to']
        send_email(body_email, header, data)
        os.system(f'rm {JSON} {CSV}')

    elif data['to']:
        data['passw'] = config['passw']
        data['from'] = config['from']
        send_email(body_email, header, data)
        os.system(f'rm {JSON} {CSV}')


    elif data['passw']:
        print('Inorrect. Try again')


    else:
        data['to'] = config['to']
        data['passw'] = config['passw']
        data['from'] = config['from']
        send_email(body_email, header, data)
        os.system(f'rm {JSON} {CSV}')

