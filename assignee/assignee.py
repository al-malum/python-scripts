#!/usr/lib/zabbix/externalscripts/.venv/bin/python3
# Указываем интерпретатор Python

import logging       # Импорт модуля для ведения логов
import requests      # Импорт модуля для выполнения HTTP-запросов
import os            # Импорт модуля для взаимодействия с операционной системой
import argparse      # Импорт модуля для обработки аргументов командной строки
from pathlib import Path   # Импорт модуля для работы с путями файлов

# Определяем имя файла для логирования
FILENAME = Path('/tmp/', 'data_non_assignee.log')


def arguments():
    """
    Функция для парсинга аргументов командной строки.
    Возвращает словарь с аргументами.
    """
    parser = argparse.ArgumentParser(description='ip')  # Создаем объект парсера
    parser.add_argument('--server', dest='server', type=str)  # Добавляем аргумент '--server'
    parser.add_argument('--host', dest='host', type=str)  # Добавляем аргумент '--host'
    parser.add_argument('--item', dest='item', type=str)  # Добавляем аргумент '--item'
    arg = parser.parse_args()  # Парсим переданные аргументы
    argument = {'host': arg.host, 'item': arg.item, 'server': arg.server}  # Формируем словарь с аргументами
    return argument  # Возвращаем словарь с аргументами


def req():
    """
    Функция для выполнения HTTP-запросов к API itilium.
    Возвращает словарь с данными о событиях.
    """
    logger = logging.getLogger('req')  # Создаем объект логгера
    logger.setLevel(logging.WARNING)  # Устанавливаем уровень логирования
    logger_handler = logging.FileHandler(f'{FILENAME}')  # Создаем файловый обработчик логов
    logger_handler.setLevel(logging.WARNING)  # Устанавливаем уровень логирования для обработчика
    logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')  # Создаем форматтер для логов
    logger_handler.setFormatter(logger_formatter)  # Применяем форматтер к обработчику
    logger.addHandler(logger_handler)  # Добавляем обработчик к логгеру

    # Формируем параметры запросов для различных статусов событий
    regis = 'status=%D0%97%D0%B0%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%BE'
    assignee = 'status=%D0%9D%D0%B0%D0%B7%D0%BD%D0%B0%D1%87%D0%B5%D0%BD%D0%BE'
    in_work = 'status=%D0%92_%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B5'
    hold = 'status=%D0%9E%D0%B6%D0%B8%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5'

    try:
        # Формируем URL для каждого статуса и выполняем GET-запросы
        url_reg = f'http://192.168.100.1:3000/api/itilium/events?{regis}'  
        url_assignee = f'http://192.168.100.1:3000/api/itilium/events?{assignee}'
        url_in_work = f'http://192.168.100.1:3000/api/itilium/events?{in_work}'
        url_hold = f'http://192.168.100.1:3000/api/itilium/events?{hold}'

        reg_data = requests.get(url_reg).json()  # Получаем данные о зарегистрированных событиях
        assignee_data = requests.get(url_assignee).json()  # Получаем данные о назначенных событиях
        in_work_data = requests.get(url_in_work).json()  # Получаем данные о событиях в работе
        hold_data = requests.get(url_hold).json()  # Получаем данные о событиях в ожидании

        # Возвращаем словарь с результатами запросов
        return {'regis': reg_data, 'assignee': assignee_data, 'in_work': in_work_data, 'hold': hold_data}

    except UnboundLocalError as error:  # Обрабатываем возможные исключения
        logger.warning(f'{error}')  # Логируем ошибку


def numb(data):
    """
    Функция для анализа данных о событиях и формирования списка номеров событий без назначенного ответственного.
    Возвращает строку с количеством таких событий и списком их номеров.
    """
    logger = logging.getLogger('handler')  # Создаем объект логгера
    logger.setLevel(logging.WARNING)  # Устанавливаем уровень логирования
    logger_handler = logging.FileHandler(f'{FILENAME}')  # Создаем файловый обработчик логов
    logger_handler.setLevel(logging.WARNING)  # Устанавливаем уровень логирования для обработчика
    logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')  # Создаем форматтер для логов
    logger_handler.setFormatter(logger_formatter)  # Применяем форматтер к обработчику
    logger.addHandler(logger_handler)  # Добавляем обработчик к логгеру

    result = {}  # Создаем пустой словарь для хранения результата
    listing = []  # Создаем пустой список для хранения номеров событий
    count = 0  # Счетчик событий

    for item in data.values():  # Проходимся по всем значениям словаря с данными о событиях
        for value in item:  # Проходимся по каждому событию
            try:
                # Проверяем, есть ли назначенный ответственный
                if value["AssigneeName"] == '' or value["AssignmentName"] == '':
                    listing.append(value["EventNumber"])  # Добавляем номер события в список
                    count = len(listing)  # Обновляем счетчик
            except TypeError as error:  # Обрабатываем возможные исключения
                logger.warning(f'{error}')  # Логируем ошибку

    # Формируем итоговую строку с результатом
    result["Count"] = str(count)  # Количество событий
    result["List"] = ','.join(listing)  # Список номеров событий через запятую
    result = str(result).replace("'", '"')  # Преобразуем одинарные кавычки в двойные
    return result  # Возвращаем результат


def main():
    """
    Основная функция программы.
    Выполняет все необходимые шаги: получение аргументов, выполнение запросов,
    анализ данных и отправку результатов в Zabbix.
    """
    data = arguments()  # Получаем аргументы командной строки
    host = data['host']  # Извлекаем хост
    item = data['item']  # Извлекаем элемент
    server = data['server']  # Извлекаем сервер
    data = req()  # Выполняем запросы к API
    listing = numb(data)  # Анализируем данные и формируем результат
    # Отправляем команду zabbix_sender для передачи данных в Zabbix
    os.system(f'zabbix_sender -z {server} -p 10051 -s {host} -k {item} -o {listing}')


if __name__ == '__main__':
    main()  # Запускаем основную функцию