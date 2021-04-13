import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class ActiveBaskets(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'active_baskets'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    items = sqlalchemy.Column(sqlalchemy.Integer,
                              sqlalchemy.ForeignKey("items.id"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
