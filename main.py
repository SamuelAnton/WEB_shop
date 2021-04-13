from flask import Flask, render_template, redirect, jsonify
from data import db_session, items_api
from data.users import User
from data.items import Items
from data.baskets import Baskets
from data.active_basket import ActiveBaskets
from data.category import Categories
from forms.user import *
from flask_login import LoginManager, login_user, current_user
from flask import make_response
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    items = db_sess.query(Items)
    tags = db_sess.query(Categories)
    return render_template("index.html", items=items, tags=tags)


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
    add_items()
    app.run()


def add_categorys():
    db_sess = db_session.create_session()
    if len(db_sess.query(Categories).all()) != 0:
        return
    categories = ['Brushes', 'Erasers', 'Palettes', 'Sharpeners', 'Albums',
                  'Cardboard', 'Canvases', 'Pencils', 'Markers', 'Chalk',
                  'Felt-tip pens', 'Paints']
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
