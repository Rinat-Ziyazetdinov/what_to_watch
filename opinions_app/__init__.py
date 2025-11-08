# Он объединит файлы в пакет, и именно этот пакет будет выступать в роли
# приложения Flask. В нём будут подключаться настройки, создаваться экземпляр
# приложения Flask и экземпляр базы данных.

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from settings import Config

app = Flask(__name__, static_folder='static_dev')  # ссылка на папку статики
app.config.from_object(Config)
# Создать экземпляр SQLAlchemy и в качестве параметра
# передать в него экземпляр приложения Flask.
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Модули, подключаемые в конце, опираются в своей работе на экземпляры классов,
# которые созданы в начале. Если подключить эти модули до создания экземпляров
# классов, то ничего работать не будет.
# Новый импорт — api_views.
from . import api_views, cli_commands, error_handlers, views
