# Импортировать функцию для выбора случайного значения.
from random import randrange

from flask import Flask, abort, flash, redirect, render_template, url_for

from . import app, db
from .forms import OpinionForm
from .models import Opinion


# вынесли в отдельную ф-ю в соотв-и с DRY (используется также в API)
def random_opinion():
    # Определить количество мнений в базе данных.
    quantity = Opinion.query.count()
    # выбрать случайное число в диапазоне от 0 до quantity...
    if quantity:
        # Извлечь все записи, пропуская первые offset_value записей
        # и взять первую запись из получившегося набора.
        offset_value = randrange(quantity)
        opinion = Opinion.query.offset(offset_value).first()
        # Передать в шаблон объект opinion.
        return opinion


@app.route('/')
def index_view():
    opinion = random_opinion()
    # Если random_opinion() вернула None, значит, в БД нет записей.
    if opinion is None:
        # Если в базе пусто - при запросе к главной странице
        # пользователь увидит ошибку 500.
        abort(500)
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
