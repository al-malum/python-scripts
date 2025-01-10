import smtplib
import configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


# Функция для чтения конфигурации отправителя
def conf_pars_from():
    config = configparser.ConfigParser()  # Инициализация парсера конфигурации
    config.read('sender.ini')  # Чтение файла конфигурации отправителя
    sender = {}  # Создание словаря для данных отправителя
    password = config['sender']['password']  # Получение пароля из конфигурации
    mail = config['sender']['mail']  # Получение почтового адреса отправителя из конфигурации
    sender['passw'] = password  # Сохраняем пароль в словарь
    sender['mail'] = mail  # Сохраняем адрес почты в словарь
    return sender  # Возвращаем данные отправителя

# Функция для чтения конфигурации получателей
def conf_pars_to():
    config = configparser.ConfigParser()  # Инициализация парсера конфигурации
    config.read('users.ini')  # Чтение файла конфигурации пользователей
    userlist = {}  # Создание словаря для списка пользователей
    for user in config['users']:  # Проходим по всем пользователям в конфигурации
        userlist.update({user: config['users'][user]})  # Добавляем каждого пользователя в словарь
    return userlist  # Возвращаем словарь пользователей

# Функция для проверки статуса оплаты пользователей
def check_tax():
    config = configparser.ConfigParser()  # Инициализация парсера конфигурации
    config.read('users.ini')  # Чтение файла конфигурации пользователей
    paid = {}  # Создание словаря для пользователей, которые оплатили
    for user in config['paid']:  # Проходим по всем пользователям, которые оплатили
        user = {user: config['paid'][user]}  # Добавляем информацию о пользователе в словарь
        paid.update(user)  # Обновляем словарь с оплаченными пользователями
    return paid  # Возвращаем словарь оплаченных пользователей

# Функция для обновления количества оплат пользователя в конфигурации
def counter(deleted, count):
    config = configparser.ConfigParser()  # Инициализация парсера конфигурации
    config.read('users.ini')  # Чтение файла конфигурации пользователей
    count = int(count)  # Преобразуем количество оплат в целое число
    if count == 1:  # Если количество оплат равно 1, удаляем пользователя из секции 'paid'
        config.remove_option('paid', deleted)  # Удаляем пользователя из секции 'paid'
        with open('users.ini', 'w') as obj:  # Открываем конфигурационный файл для записи
            config.write(obj)  # Записываем изменения в файл
        return 1  # Возвращаем 1, чтобы указать, что пользователь был удален
    else:
        count = int(count) - 1  # Если оплат больше 1, уменьшаем количество оплат на 1
        count = str(count)  # Преобразуем количество обратно в строку
        #config.remove_option('paid', deleted)  # Этот код закомментирован, но возможно предназначен для удаления опции
        config.set('paid', str(deleted), count)  # Обновляем количество оплат в секции 'paid'
        with open('users.ini', 'w') as obj:  # Открываем файл для записи изменений
            config.write(obj)  # Записываем изменения
        return 0  # Возвращаем 0, чтобы указать, что пользователь остался в списке

# Функция для отправки email-сообщений
def send_email(body_email, header, data, user):
    """Функция логина и отправки сообщения"""

    addr_from = data['mail']  # Адрес отправителя
    password = data['passw']  # Пароль отправителя
    addr_to = user  # Адрес получателя
    server = smtplib.SMTP('smtp.yandex.ru', 587)  # Устанавливаем соединение с SMTP сервером Yandex
    server.starttls()  # Запускаем защищенное соединение

    try:
        # Создаем мультичастное сообщение (для текстовой части и вложений)
        msg = MIMEMultipart()
        msg['From'] = addr_from  # Устанавливаем адрес отправителя
        msg['To'] = addr_to  # Устанавливаем адрес получателя
        msg['Subject'] = header  # Устанавливаем тему письма
        msg.attach(MIMEText(body_email, 'plain'))  # Прикрепляем текстовое тело письма

        # Открываем изображение (например, QR-код для оплаты) и прикрепляем его к письму
        part = MIMEApplication(open('image.jpg', 'rb').read())  # Открываем изображение для прикрепления
        part.add_header('Content-Disposition', 'attachment', filename='image.jpg')  # Устанавливаем заголовок для вложения
        msg.attach(part)  # Прикрепляем изображение к сообщению

        server.login(addr_from, password)  # Логинимся на SMTP сервере
        server.send_message(msg)  # Отправляем сообщение
    except Exception as _ex:
        print(f'error: {_ex}')  # В случае ошибки выводим сообщение об ошибке

# Основной блок выполнения программы
if __name__ == '__main__':
    sender = conf_pars_from()  # Загружаем данные отправителя
    users = conf_pars_to()  # Загружаем список пользователей
    header = 'Оплата VPN сервиса'  # Заголовок письма
    body_email = 'QR-код для оплаты во вложении'  # Текст письма
    paid = check_tax()  # Проверяем список пользователей, которые оплатили
    print(paid)  # Выводим информацию об оплаченных пользователях (для отладки)
    print(users)  # Выводим информацию о пользователях (для отладки)
    listing = []  # Список для дальнейшей обработки

    # Обрабатываем пользователей, которые оплатили
    for i in range(len(paid)):
        for key, value in paid.items():
            if key in users:  # Если пользователь есть в списке пользователей
                count = value  # Получаем количество оплат для пользователя
                trigger = counter(key, count)  # Обновляем информацию об оплатах
                if trigger == 0:
                    del users[key]  # Если оплат больше 1, удаляем пользователя из списка
                else:
                    pass  # Если оплат 1, оставляем пользователя в списке

    # Отправляем email всем пользователям, которые не оплатили
    for key, item in users.items():
        send_email(body_email, header, sender, item)  # Отправляем email с QR-кодом для оплаты
