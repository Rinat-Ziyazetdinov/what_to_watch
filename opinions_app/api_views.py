# Импортировать метод jsonify.
from flask import jsonify, request

from . import app, db
from .models import Opinion
from .views import random_opinion

# Импорт исключения.
from .error_handlers import InvalidAPIUsage


# Явно разрешить метод GET.
@app.route('/api/opinions/<int:id>/', methods=['GET'])
def get_opinion(id):
    # Получить объект по id или выбросить ошибку 404.
    opinion = Opinion.query.get(id)
    if opinion is None:
        # Выбросить собственное исключение.
        raise InvalidAPIUsage('Мнение с указанным id не найдено', 404)
    return jsonify(opinion.to_dict()), 200


@app.route('/api/opinions/<int:id>/', methods=['PATCH'])
def update_opinion(id):
    data = request.get_json()
    if (
        'text' in data and
        Opinion.query.filter_by(text=data['text']).first() is not None
    ):
        # Выбросить собственное исключение.
        raise InvalidAPIUsage('Такое мнение уже есть в базе данных')
    # Если метод get.get не найдёт указанный ID,
    # он выбросит исключение 404:
    opinion = Opinion.query.get(id)
    opinion.title = data.get('title', opinion.title)
    opinion.text = data.get('text', opinion.text)
    opinion.source = data.get('source', opinion.source)
    opinion.added_by = data.get('added_by', opinion.added_by)
    # Все изменения нужно сохранить в базе данных.
    # Объект opinion добавлять в сессию не нужно.
    # Этот объект получен из БД методом get.get() и уже хранится в сессии.
    db.session.commit()
    # При изменении объекта нужно вернуть сам объект и код 200.
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=['DELETE'])
def delete_opinion(id):
    opinion = Opinion.query.get(id)
    db.session.delete(opinion)
    db.session.commit()
    # При удалении принято возвращать только код ответа 204.
    return '', 204


@app.route('/api/opinions/', methods=['GET'])
def get_opinions():
    # Запросить список объектов.
    opinions = Opinion.query.all()
    # Поочерёдно сериализовать каждый объект,
    # а потом все объекты поместить в список opinions_list.
    opinions_list = [opinion.to_dict() for opinion in opinions]
    return jsonify(opinions_list), 200  # можно и так
    # return jsonify({'opinions': opinions_list}), 200


@app.route('/api/opinions/', methods=['POST'])
def add_opinion():
    # Получить данные из запроса в виде словаря.
    data = request.get_json()
    # Если нужных ключей нет в словаре...
    if 'title' not in data or 'text' not in data:
        # Выбросить собственное исключение.
        # Второй параметр (статус-код) в этом обработчике можно не передавать:
        # нужно вернуть код 400, а он и так возвращается по умолчанию.
        raise InvalidAPIUsage('В запросе отсутствуют обязательные поля')
    # Если в базе данных уже есть объект с таким же значением поля text...
    if Opinion.query.filter_by(text=data['text']).first() is not None:
        # Выбросить собственное исключение.
        raise InvalidAPIUsage('Такое мнение уже есть в базе данных')
    # Создать новый пустой экземпляр модели.
    opinion = Opinion()
    # Наполнить экземпляр данными из запроса.
    opinion.from_dict(data)
    # Добавить новую запись в сессию.
    db.session.add(opinion)
    # Сохранить изменения.
    db.session.commit()
    return jsonify(opinion.to_dict()), 201
    # return jsonify({'opinion': opinion.to_dict()}), 201


@app.route('/api/get-random-opinion/', methods=['GET'])
def get_random_opinion():
    opinion = random_opinion()
    # Если мнение найдено (переменная opinion не равна None),
    # оно возвращается в виде JSON-объекта с кодом ответа 200 (OK).
    if opinion is not None:
        return jsonify(opinion.to_dict()), 200
    # Если мнение не найдено (opinion равен None),
    # вызывается исключение InvalidAPIUsage с сообщением об ошибке
    # и кодом ответа 404 (Not Found).
    raise InvalidAPIUsage('В базе данных нет мнений', 404)
