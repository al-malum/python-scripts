import smtplib
import configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication



def conf_pars_from():
    config = configparser.ConfigParser()
    config.read('sender.ini')
    sender = {}
    password = config['sender']['password']
    mail = config['sender']['mail']
    sender['passw'] = password
    sender['mail'] = mail
    return sender


def conf_pars_to():
    config = configparser.ConfigParser()
    config.read('users.ini')
    userlist = {}
    for user in config['users']:
        userlist.update({user: config['users'][user]})
    return userlist


def check_tax():
    config = configparser.ConfigParser()
    config.read('users.ini')
    paid = {}
    for user in config['paid']:
        user = {user: config['paid'][user]}
        paid.update(user)
    return paid


def counter(deleted, count):
    config = configparser.ConfigParser()
    config.read('users.ini')
    count = int(count)
    if count == 1:
        config.remove_option('paid', deleted)
        with open('users.ini', 'w') as obj:
            config.write(obj)
        return 1
    else:
        count = int(count) - 1
        count = str(count)
        #config.remove_option('paid', deleted)
        config.set('paid', str(deleted), count)
        with open('users.ini', 'w') as obj:
            config.write(obj)

        return 0


def send_email(body_email, header, data, user):
    """Функция логина и отправки сообщения"""

    addr_from = data['mail']
    password = data['passw']
    addr_to = user
    server = smtplib.SMTP('smtp.yandex.ru', 587)
    server.starttls()

    try:
        msg = MIMEMultipart()  # Создаем сообщение
        msg['From'] = addr_from  # Адресат
        msg['To'] = addr_to  # Получатель
        msg['Subject'] = header  # Тема
        msg.attach(MIMEText(body_email, 'plain'))


        part = MIMEApplication(open('image.jpg', 'rb').read())
        part.add_header('Content-Disposition', 'attachment', filename='image.jpg')
        msg.attach(part)
        server.login(addr_from, password)
        server.send_message(msg)
    except Exception as _ex:
        print(f'error: {_ex}')



if __name__ == '__main__':

    FILENAME = 'tax.ini'
    sender = conf_pars_from()
    users = conf_pars_to()
    header = 'Оплата VPN сервиса'  # Заголовок
    body_email = 'QR-код для оплаты во вложении'  # Тело сообщения
    paid = check_tax()
    print(paid)
    print(users)
    listing = []
    for i in range(len(paid)):
        for key, value in paid.items():
            if key in users:
                count = value
                trigger = counter(key, count)
                if trigger == 0:
                    del users[key]
                    #print(f'Вот он - {key}, оплатил')
                else:
                    pass

    for key, item in users.items():
        #print(f'Штатная оплата пользователем {key}')
        send_email(body_email, header, sender, item)
