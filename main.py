# Импортируем  библиотеки
from flask import Flask, render_template, redirect, jsonify
from data import db_session
from data.users import User
from data.items import Items
from data.baskets import Baskets
from data.active_basket import ActiveBaskets
from data.category import Categories
from forms.user import *
from forms.cat_filter import *
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask import make_response
import json
from pickle import loads, dumps


# Наше приложение
app = Flask(__name__)
# Секретный ключ
app.config['SECRET_KEY'] = 'super_secret_key'
# Инициализация LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


# Начальная страница приложения
@app.route('/index', methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
def index():
    # Форма фильтра товаров
    form1 = Filter()
    # Создаём сессия базы данных
    db_sess = db_session.create_session()
    tags = db_sess.query(Categories)
    b = False
    # Фильтр товаров
    if form1.validate_on_submit():
        a = []
        cats = [form1.brushes.data, form1.palettes.data, form1.erasers.data, form1.sharpeners.data,
                form1.albums.data, form1.paperboard.data, form1.canvases.data, form1.pencils.data,
                form1.markers.data, form1.chalk.data, form1.felt_pen.data, form1.paints.data]
        for i in range(len(cats)):
            if cats[i]:
                a.append(i + 1)
        items = db_sess.query(Items).filter(Items.category_id.in_(a))
        return render_template("index.html", items=items, tags=tags, form=form1)
    items = db_sess.query(Items).all()
    # Кнопка перехода в активную корзину
    if current_user.is_authenticated:
        a_basket = db_sess.query(ActiveBaskets).filter(ActiveBaskets.user_id == current_user.id).first()
        if a_basket:
            b = True
    # Вызываем html файл
    return render_template("index.html", items=items, tags=tags, form=form1, b=b)


# Вход в аккаунты пользователей
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Форма входа
    form2 = LoginForm()
    # Вход в аккаунт и проверка наличия такого пользователя
    if form2.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form2.email.data).first()
        if user and user.check_password(form2.password.data):
            login_user(user, remember=form2.remember_me.data)
            # Перенаправляем на начальную страницу
            return redirect("/")
        # Повторно вызываем html файл с сообщением об ошибке
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form2)
    # Вызываем html файл
    return render_template('login.html', title='Авторизация', form=form2)


# Регистрация новых пользователей
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    # Форма регистрации
    form3 = RegisterForm()
    # Регистрация пользователя и проверка наличия пользователя и совпадения паролей
    if form3.validate_on_submit():
        if form3.password.data != form3.password_again.data:
            # Повторно вызываем html файл с сообщением об ошибке
            return render_template('register.html', title='Регистрация',
                                   form=form3,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form3.email.data).first():
            # Повторно вызываем html файл с сообщением об ошибке
            return render_template('register.html', title='Регистрация',
                                   form=form3,
                                   message="Такой пользователь уже есть")
        # Регистрируем нового пользователя
        user = User()
        user.name = form3.name.data,
        user.email = form3.email.data,
        user.set_password(form3.password.data)
        db_sess.add(user)
        db_sess.commit()
        # Перенаправляем на страницу входа в аккаунт
        return redirect('/login')
    # Вызываем html файл
    return render_template('register.html', title='Регистрация', form=form3)


# Личный кабинет пользователя
@app.route('/self_lab/<int:id1>', methods=['GET', 'POST'])
@login_required
def self_lab(id1):
    # Собираем информацию о покупках и товарах в покупках пользователя
    db_sess = db_session.create_session()
    baskets = db_sess.query(Baskets).filter(Baskets.user_id == id1).all()
    items = {}
    num = {}
    for i in baskets:
        a = loads(i.items)
        num[i] = {}
        items[i] = db_sess.query(Items).filter(Items.id.in_(a)).all()
        for y in a:
            if db_sess.query(Items).filter(Items.id == y).first() in num[i]:
                num[i][db_sess.query(Items).filter(Items.id == y).first()] += 1
            else:
                num[i][db_sess.query(Items).filter(Items.id == y).first()] = 1
    # Вызываем html файл
    return render_template('self_lab.html', baskets=baskets, user=current_user, items=items, num=num)


# Функция добавления товара в корзину
@app.route('/add_item/<int:id>', methods=['GET', 'POST'])
@login_required
def add_item(id2):
    db_sess = db_session.create_session()
    a_basket = db_sess.query(ActiveBaskets).filter(ActiveBaskets.user_id == current_user.id).first()
    item = db_sess.query(Items).filter(Items.id == id2).first()
    # Если у пользователя уже есть активная корзина, то добавляем товар туда
    if a_basket:
        a_basket.price += item.price
        a_basket.items = dumps(loads(a_basket.items) + [id2])
    # Если нет, создаём корзину и добовляем туда товар
    else:
        a_basket = ActiveBaskets()
        a_basket.price = item.price
        a_basket.items = dumps([id2])
        a_basket.user_id = current_user.id2
        db_sess.add(a_basket)
    db_sess.commit()
    # Перенапрвляем на главную страницу сайта
    return redirect('/index')


# Просмотр корзины
@app.route('/active_basket/<int:id>', methods=['GET', 'POST'])
@login_required
def active_basket(id3):
    # Собираем информацию о товарах в корзине
    db_sess = db_session.create_session()
    basket = db_sess.query(ActiveBaskets).filter(ActiveBaskets.user_id == id3).first()
    a = loads(basket.items)
    num = {}
    items = db_sess.query(Items).filter(Items.id.in_(a)).all()
    for i in a:
        if db_sess.query(Items).filter(Items.id == i).first() in num:
            num[db_sess.query(Items).filter(Items.id == i).first()] += 1
        else:
            num[db_sess.query(Items).filter(Items.id == i).first()] = 1
    price = basket.price
    # Вызываем html файл
    return render_template('active_busket.html', user=current_user, items=items, price=price, num=num)


# Покупка товаров в корзине
@app.route('/active_basket/buy', methods=['GET', 'POST'])
@login_required
def buy():
    db_sess = db_session.create_session()
    a_busket = db_sess.query(ActiveBaskets).filter(ActiveBaskets.user_id == current_user.id).first()
    # Проверка есть ли указанное количество товаров на складе
    num = {}
    for i in loads(a_busket.items):
        if i in num:
            num[i] += 1
        else:
            num[i] = 1
    for y in num:
        if db_sess.query(Items).filter(Items.id == y).first().number < num[y]:
            # Перенаправляем на страницу с ошибкой
            return render_template('end.html')
    # Удаляем товары со склада
    for r in num:
        db_sess.query(Items).filter(Items.id == r).first().number -= num[r]
    # Добавляем корзину в оплаченные покупки
    busket = Baskets()
    busket.price = a_busket.price
    busket.items = a_busket.items
    busket.user_id = a_busket.user_id
    db_sess.add(busket)
    # Удаляем активную корзину
    db_sess.query(ActiveBaskets).filter(ActiveBaskets.user_id == current_user.id).delete()
    db_sess.commit()
    # Перенаправляем на главную страницу
    return redirect('/index')


# Выйти из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    # Перенаправляем на главную страницу
    return redirect("/")


# Удалить товар из корзины
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id4):
    db_sess = db_session.create_session()
    a = db_sess.query(ActiveBaskets).filter(ActiveBaskets.user_id == current_user.id).first()
    b = loads(a.items)
    for i in range(len(b)):
        if id4 == b[i]:
            # Удаление товара
            del b[i]
            a.items = dumps(b)
            db_sess.commit()
            # Перенаправление на страницу просмотра корзины
            return redirect('/active_basket/' + str(current_user.id))


# Загрузка пользователя
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Обработчик ошибок
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# Основная функция программы
def main():
    db_session.global_init("db/blogs.db")
    # Добавляем товары и категории в базу данных
    add_items()
    add_categorys()
    app.run()


# Добавить категории если их нет в базе данных
def add_categorys():
    db_sess = db_session.create_session()
    if len(db_sess.query(Categories).all()) != 0:
        return
    categories = ['Кисти', 'Стёрки', 'Палитры', 'Точилки', 'Альбомы',
                  'Картон', 'Холсты', 'Карандаши', 'Маркеры', 'Мел',
                  'Фломастеры', 'Краски']
    for i in categories:
        cat = Categories()
        cat.category = i
        db_sess.add(cat)
        db_sess.commit()


# Добавить товары в ьазу данных, если их нет
def add_items():
    db_sess = db_session.create_session()
    if len(db_sess.query(Items).all()) != 0:
        return
    # Загружаем информацию о товарах из json файла
    with open('storage.json', 'r') as file:
        data = json.load(file)
        for i in data:
            item = Items()
            item.name = i['name']
            item.description = i['description']
            item.number = i['number']
            item.price = i['price']
            item.category_id = i['category_id']
            db_sess.add(item)
            db_sess.commit()


# Начало программы
if __name__ == '__main__':
    main()
