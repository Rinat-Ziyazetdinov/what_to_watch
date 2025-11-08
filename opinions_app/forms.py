# Новые импорты для работы с формами:
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional

# Добавьте новый импорт класса к списку импортов для загрузки картинок.
from flask_wtf.file import FileAllowed, MultipleFileField


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
    # Поле в форме для картинок.
    # Допишите FileAllowed в качестве валидатора, укажите ему нужные аргументы.
    images = MultipleFileField(
        validators=[
            FileAllowed(
                # Список разрешенных расширений для файлов.
                ['jpg', 'jpeg', 'png', 'PNG', 'gif', 'bmp'],
                # Сообщение, в случае если расширение не совпадает.
                message=(
                    'Выберите файлы с расширением '
                    '.jpg, .jpeg, .png, .gif или .bmp'
                )
            )
        ]
    )
    submit = SubmitField('Добавить')
