import sqlalchemy
from .db_session import SqlAlchemyBase


class Departments(SqlAlchemyBase):
    __tablename__ = 'departments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    chief = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=True)
    members = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String)
    add_by = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), default=1)
