# Имортируем нужные библиоткеи
from flask_wtf import FlaskForm
from wtforms import *


# Класс формы фильтра товаров
class Filter(FlaskForm):
    brushes = BooleanField('Кисти')
    palettes = BooleanField('Палитры')
    erasers = BooleanField('Стёрки')
    sharpeners = BooleanField('Точилки')
    albums = BooleanField('Альбомы')
    paperboard = BooleanField('Картон')
    canvases = BooleanField('Холсты')
    pencils = BooleanField('Карандаши')
    markers = BooleanField('Маркеры')
    chalk = BooleanField('Мел')
    felt_pen = BooleanField('Фломастеры')
    paints = BooleanField('Краски')
    submit = SubmitField('Применить')
