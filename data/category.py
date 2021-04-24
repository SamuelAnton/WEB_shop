# Ипортируем нужные библиотеки
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


# Таблица категорий
class Categories(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'category'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=True)
