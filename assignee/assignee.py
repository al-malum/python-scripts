#!/usr/lib/zabbix/externalscripts/.venv/bin/python3
import logging
import requests
import os
import argparse
from pathlib import Path


FILENAME = Path('/tmp/', 'data_non_assignee.log')


def arguments():
    parser = argparse.ArgumentParser(description='ip')
    parser.add_argument('--server', dest='server', type=str)
    parser.add_argument('--host', dest='host', type=str)
    parser.add_argument('--item', dest='item', type=str)
    arg = parser.parse_args()
    argument = {'host': arg.host, 'item': arg.item, 'server': arg.server}
    return argument


def req():
    logger = logging.getLogger('req')
    logger.setLevel(logging.WARNING)
    logger_handler = logging.FileHandler(f'{FILENAME}')
    logger_handler.setLevel(logging.WARNING)
    logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)

    regis = 'status=%D0%97%D0%B0%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%BE'
    assignee = 'status=%D0%9D%D0%B0%D0%B7%D0%BD%D0%B0%D1%87%D0%B5%D0%BD%D0%BE'
    in_work = 'status=%D0%92_%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B5'
    hold = 'status=%D0%9E%D0%B6%D0%B8%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5'
    try:

        url_reg = f'http://192.168.100.1:3000/api/itilium/events?{regis}'
        url_assignee = f'http://192.168.100.1:3000/api/itilium/events?{assignee}'
        url_in_work = f'http://192.168.100.1:3000/api/itilium/events?{in_work}'
        url_hold = f'http://192.168.100.1:3000/api/itilium/events?{hold}'

        reg_data = requests.get(url_reg).json()
        assignee_data = requests.get(url_assignee).json()
        in_work_data = requests.get(url_in_work).json()
        hold_data = requests.get(url_hold).json()

        return {'regis': reg_data, 'assignee': assignee_data, 'in_work': in_work_data, 'hold': hold_data}

    except UnboundLocalError as error:
        logger.warning(f'{error}')


def numb(data):
    logger = logging.getLogger('handler')
    logger.setLevel(logging.WARNING)
    logger_handler = logging.FileHandler(f'{FILENAME}')
    logger_handler.setLevel(logging.WARNING)
    logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)

    result = {}
    listing = []
    count = 0
    for item in data.values():
        
        
        for value in item:
            try:
                if value["AssigneeName"] == '' or value["AssignmentName"] == '':
                    listing.append(value["EventNumber"])
                    count = len(listing)
            except TypeError as error:
                logger.warning(f'{error}')

    result["Count"] = str(count)
    result["List"] = ','.join(listing)
    result = str(result).replace("'", '"')
    return result


def main():
    data = arguments()
    host = data['host']
    item = data['item']
    server = data['server']
    data = req()
    listing = numb(data)
    os.system(f'zabbix_sender -z {server} -p 10051 -s {host} -k {item} -o {listing}')


if __name__ == '__main__':
    main()
