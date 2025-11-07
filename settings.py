import os


# Подключить БД SQLite.
# Задаем свой ключ для расширение Flask-WTF.
class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
