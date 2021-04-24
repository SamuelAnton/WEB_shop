from flask import Flask, render_template, redirect, jsonify
from data import db_session, items_api
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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/index', methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
def index():
    form = Filter()
    db_sess = db_session.create_session()
    tags = db_sess.query(Categories)
    b = False
    if form.validate_on_submit():
        a = []
        cats = [form.brushes.data, form.palettes.data, form.erasers.data, form.sharpeners.data,
                form.albums.data, form.paperboard.data, form.canvases.data, form.pencils.data,
                form.markers.data, form.chalk.data, form.felt_pen.data, form.paints.data]
        for i in range(len(cats)):
            if cats[i]:
                a.append(i + 1)
        items = db_sess.query(Items).filter(Items.category_id.in_(a))
        return render_template("index.html", items=items, tags=tags, form=form)
    items = db_sess.query(Items).all()
    if current_user.is_authenticated:
        a_basket = db_sess.query(ActiveBaskets).filter(ActiveBaskets.user_id == current_user.id).first()
        if a_basket:
            b = True
    return render_template("index.html", items=items, tags=tags, form=form, b=b)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/self_lab/<int:id>', methods=['GET', 'POST'])
@login_required
def self_lab(id):
    db_sess = db_session.create_session()
    baskets = db_sess.query(Baskets).filter(Baskets.user_id == id).all()
    items = {}
    for i in baskets:
        items[i] = db_sess.query(Items).filter(Items.id.in_(loads(i.items))).all()
    return render_template('self_lab.html', baskets=baskets, user=current_user, items=items)


@app.route('/add_item/<int:id>', methods=['GET', 'POST'])
@login_required
def add_item(id):
    db_sess = db_session.create_session()
    a_basket = db_sess.query(ActiveBaskets).filter(ActiveBaskets.user_id == current_user.id).first()
    item = db_sess.query(Items).filter(Items.id == id).first()
    if a_basket:
        a_basket.price += item.price
        a_basket.items = dumps(loads(a_basket.items) + [id])
    else:
        a_basket = ActiveBaskets()
        a_basket.price = item.price
        a_basket.items = dumps([id])
        a_basket.user_id = current_user.id
        db_sess.add(a_basket)
    db_sess.commit()
    return redirect('/index')


@app.route('/active_basket/<int:id>', methods=['GET', 'POST'])
@login_required
def active_basket(id):
    db_sess = db_session.create_session()
    basket = db_sess.query(ActiveBaskets).filter(ActiveBaskets.user_id == id).first()
    a = loads(basket.items)
    items = db_sess.query(Items).filter(Items.id.in_(a)).all()
    price = basket.price
    return render_template('active_busket.html', user=current_user, items=items, price=price)


@app.route('/active_basket/buy', methods=['GET', 'POST'])
@login_required
def buy():
    db_sess = db_session.create_session()
    a_busket = db_sess.query(ActiveBaskets).filter(ActiveBaskets.user_id == current_user.id).first()
    busket = Baskets()
    busket.price = a_busket.price
    busket.items = a_busket.items
    busket.user_id = a_busket.user_id
    db_sess.add(busket)
    db_sess.query(ActiveBaskets).filter(ActiveBaskets.user_id == current_user.id).delete()
    db_sess.commit()
    return redirect('/index')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(items_api.blueprint)
    add_categorys()
    app.run()


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


def add_items():
    db_sess = db_session.create_session()
    if len(db_sess.query(Items).all()) != 0:
        return
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


if __name__ == '__main__':
    main()
