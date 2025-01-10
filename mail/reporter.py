#!/usr/bin/python3
import smtplib
import os
import configparser
import argparse
import json
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Адрес Elasticsearch сервера
ELIP = '192.168.100.5'
# Пути к файлам для сохранения данных (JSON и CSV)
JSON = '/tmp/dump.json'
CSV = '/tmp/dump.csv'
# Тип контента для HTTP-запроса (JSON)
CONTENT = 'Content-type: application/json'
# Запрос к Elasticsearch для получения данных за последний день
QUERY = '{"query": {"range": {"@timestamp": {"time_zone": "+03:00","gte": "now-1d/d","lte": "now/d"}}}}'
# Максимально возможное количество документов для извлечения
SIZE = 100  

# Функция для обработки аргументов командной строки
def arguments():
    # Инициализация парсера аргументов
    parser = argparse.ArgumentParser(description='email')
    # Добавление аргументов для отправителя, получателя, пароля и индекса
    parser.add_argument('-f', dest='from_mail', type=str)
    parser.add_argument('-t', dest='dest', type=str)
    parser.add_argument('-p', dest='passw', type=str)
    parser.add_argument('-i', dest='index', type=str)
    # Разбор аргументов
    arg = parser.parse_args()
    # Составление словаря с аргументами
    listing = {'from': arg.from_mail, 'to': arg.dest, 'passw': arg.passw, 'index': arg.index}
    return listing

# Функция для чтения конфигурации из файла
def conf_pars():
    # Инициализация парсера конфигурационного файла
    config = configparser.ConfigParser()
    config.read('/opt/reporter/conf.ini')
    # Считывание нужных значений из конфигурации
    data = {}
    password = config['mail']['password']
    mail_from = config['mail']['from']
    mail_to = config['mail']['to']
    log_el = config['mail']['log_el']
    pass_el = config['mail']['pass_el']
    # Заполнение словаря данными из конфигурации
    data['passw'] = password
    data['from'] = mail_from
    data['to'] = mail_to
    data['log_el'] = log_el
    data['pass_el'] = pass_el
    return data

# Функция для отправки email с приложением
def send_email(body_email, header, data):
    """Функция логина и отправки сообщения"""
    addr_from = data['from']  # Адрес отправителя
    addr_to = data['to']      # Адрес получателя
    password = data['passw']  # Пароль отправителя
    # Устанавливаем SMTP-сервер для отправки почты
    server = smtplib.SMTP('smail.company.ru', 587)
    server.starttls()  # Устанавливаем защищенное соединение

    try:
        # Создаем multipart-сообщение (для отправки как текста, так и вложений)
        msg = MIMEMultipart()
        msg['From'] = addr_from  # Адрес отправителя
        msg['To'] = addr_to      # Адрес получателя
        msg['Subject'] = header  # Тема письма
        msg.attach(MIMEText(body_email, 'plain'))  # Тело письма (в формате plain text)

        # Чтение содержимого файла CSV и добавление его как вложения
        with open(CSV) as obj:
            file = MIMEText(obj.read())

        # Добавление заголовка для вложения с именем файла CSV
        file.add_header('content-disposition', 'attachment', filename=CSV)
        msg.attach(file)  # Прикрепляем файл к сообщению
        server.login(addr_from, password)  # Логинимся на SMTP сервере
        server.send_message(msg)  # Отправляем сообщение
    except Exception as _ex:
        print(f'error: {_ex}')  # В случае ошибки выводим сообщение об ошибке

# Функция для конвертации данных из JSON в CSV
def converter(JSON, CSV):
    cols = ['num_doc', 'message', 'time']  # Заголовки для CSV
    CHECK = 0  # Счётчик документов
    with open(JSON) as obj:
        js = json.load(obj)  # Загружаем данные из JSON
        js = js['hits']['hits']  # Извлекаем данные о документах из ответа
        print(js)  # Выводим данные для отладки
    if type(js) is list:  # Если данные - это список документов
        with open(CSV, 'a') as obj:
            cv = csv.DictWriter(obj, fieldnames=cols)
            cv.writeheader()  # Записываем заголовки CSV
            for i in js:
                CHECK += 1
                # Извлекаем нужные поля и записываем их в CSV
                data = {'num_doc': CHECK, 'message': i['_source']['message'], 'time': i['_source']['@timestamp']}
                cv.writerow(data)  # Записываем одну строку в CSV
    else:  # Если данные не являются списком (один документ)
        CHECK = 1
        data = {'num_doc': CHECK, 'message': js['_source']['message'], 'time': js['_source']['@timestamp']}
        with open(CSV, 'a') as obj:
            cv = csv.DictWriter(obj, fieldnames=cols)
            cv.writeheader()  # Записываем заголовки CSV
            cv.writerow(data)  # Записываем одну строку в CSV

# Основной блок исполнения скрипта
# Основной блок исполнения скрипта
if __name__ == '__main__':
    # Считываем конфигурацию
    config = conf_pars()
    log_el = config['log_el']
    pass_el = config['pass_el']
    # Заголовок и текст письма
    header = 'Письмо с данными Elasticsearch'  # Тема письма
    body_email = 'Выгрузка в формате CSV находится во вложении данного письма.'  # Тело письма
    # Получаем аргументы командной строки
    data = arguments()
    # Получаем индекс для Elasticsearch
    index = data['index']
    # Формируем URL для запроса к Elasticsearch
    url = f'http://{log_el}:{pass_el}@{ELIP}:9200/{index}/_search?size={SIZE}'

    # Выполняем запрос к Elasticsearch с помощью curl и сохраняем ответ в JSON
    os.system(f"curl -X POST '{url}' -H '{CONTENT}' -d '{QUERY}' -o {JSON}")
    # Конвертируем полученные данные из JSON в CSV
    converter(JSON, CSV)

    # Используем словарь для подстановки значений
    email_data = {
        'from': data['from'] or config['from'],
        'to': data['to'] or config['to'],
        'passw': data['passw'] or config['passw']
    }

    # Проверяем, что все необходимые данные присутствуют
    if email_data['from'] and email_data['to'] and email_data['passw']:
        send_email(body_email, header, email_data)
        os.system(f'rm {JSON} {CSV}')  # Удаляем временные файлы после отправки письма
    else:
        print('Некорректные данные. Пожалуйста, укажите отправителя, получателя и пароль.')