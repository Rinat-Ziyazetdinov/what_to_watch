from datetime import datetime, timezone

# Импортировать функцию для выбора случайного значения.
from random import randrange

from flask import Flask, flash, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

# Новые импорты для работы с формами:
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional

app = Flask(__name__, static_folder='static_dev')  # ссылка на папку статики

# Подключить БД SQLite.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
# Создать экземпляр SQLAlchemy и в качестве параметра
# передать в него экземпляр приложения Flask.
db = SQLAlchemy(app)
# Задаем свой ключ для расширение Flask-WTF.
app.config['SECRET_KEY'] = 'SUPER_STRONG_KEY'


class Opinion(db.Model):
    # ID — целое число, первичный ключ.
    id = db.Column(db.Integer, primary_key=True)
    # Название фильма — строка длиной 128 символов, не может быть пустым.
    title = db.Column(db.String(128), nullable=False)
    # Мнение о фильме — большая строка, не может быть пустым, 
    # должно быть уникальным.
    text = db.Column(db.Text, unique=True, nullable=False)
    # Ссылка на сторонний источник — строка длиной 256 символов.
    source = db.Column(db.String(256))
    # Дата и время — текущее время, 
    # по этому столбцу база данных будет проиндексирована.
    timestamp = db.Column(
        db.DateTime,
        index=True,
        default=lambda: datetime.now(timezone.utc)
    )


# Класс формы должен быть описан сразу после модели Opinion.
class OpinionForm(FlaskForm):
    title = StringField(
        'Введите название фильма',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 128)]
    )
    text = TextAreaField(
        'Напишите мнение',
        validators=[DataRequired(message='Обязательное поле')]
    )
    source = URLField(
        'Добавьте ссылку на подробный обзор фильма',
        validators=[Length(1, 256), Optional()]
    )
    submit = SubmitField('Добавить')


@app.route('/')
def index_view():
    # Определить количество мнений в базе данных.
    quantity = Opinion.query.count()
    # Если мнений нет...
    if not quantity:
        # ...то вернуть сообщение:
        return 'В базе данных мнений о фильмах нет.'
    # Иначе выбрать случайное число в диапазоне от 0 до quantity...
    offset_value = randrange(quantity)
    # Извлечь все записи, пропуская первые offset_value записей
    # и взять первую запись из получившегося набора.
    opinion = Opinion.query.offset(offset_value).first()
    # Передать в шаблон весь объект opinion.
    return render_template('opinion.html', opinion=opinion)


@app.route('/add', methods=['GET', 'POST'])
def add_opinion_view():
    # Создать новый экземпляр формы.
    form = OpinionForm()
    # Если ошибок не возникло...
    if form.validate_on_submit():
        text = form.text.data
        # Если в БД уже есть мнение с текстом, который ввёл пользователь...
        if Opinion.query.filter_by(text=text).first() is not None:
            # ...вызвать функцию flash и передать соответствующее сообщение.
            flash('Такое мнение уже было оставлено ранее!')
            # Вернуть пользователя на страницу «Добавить новое мнение».
            return render_template('add_opinion.html', form=form)
        # ...то нужно создать новый экземпляр класса Opinion...
        opinion = Opinion(
            # ...и передать в него данные, полученные из формы.
            title=form.title.data,
            text=form.text.data,
            source=form.source.data
        )
        # Затем добавить его в сессию работы с базой данных...
        db.session.add(opinion)
        # ...и зафиксировать изменения.
        db.session.commit()
        # Затем переадресовать пользователя на страницу добавленного мнения.
        return redirect(url_for('opinion_view', id=opinion.id))
    # Если валидация не пройдена - просто отрисовать страницу с формой.
    return render_template('add_opinion.html', form=form)


# Тут указывается конвертер пути для id.
@app.route('/opinions/<int:id>')
# Параметром указывается имя переменной.
def opinion_view(id):
    # Теперь можно запросить нужный объект по id...
    # Метод get() заменён на get_or_404():
    opinion = Opinion.query.get_or_404(id)
    # ...и передать его в шаблон (шаблон - тот же, что и для главной страницы).
    return render_template('opinion.html', opinion=opinion)


if __name__ == '__main__':
    app.run()
