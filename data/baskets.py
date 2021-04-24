# Импортируем нужные библиотеки
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
import datetime


# Таблица купленных корзин
class Baskets(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'baskets'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    items = sqlalchemy.Column(sqlalchemy.PickleType,
                              sqlalchemy.ForeignKey("items.id"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
