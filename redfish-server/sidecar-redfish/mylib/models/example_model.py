"""
flask-sqlalchemy model
@see https://flask-sqlalchemy.readthedocs.io/en/stable/models/
"""
from dataclasses import dataclass
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from mylib.db.extensions import db
from mylib.models.my_orm_base_model import MyOrmBaseModel
from typing import List

"""
Add @dataclass for serialize sqlalchemy to dict
@see https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
@note:
    1.必須使用dataclass，否則flask-sqlalchemy無法正確序列化
    2.必須加上data type hint，否則dataclass無法正確序列化
    3.加上`@dataclass`裝飾器，在jsonify()時會主動找 `__dict__`這個magic function
"""
@dataclass
class ExampleModel(MyOrmBaseModel):
    # new version: https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
    __tablename__ = 'examples'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(32))


    @classmethod
    def all(cls):
        return db.session.query(cls).all()
    
    @classmethod
    def get_by_id(cls, example_id):
        # stmt = db.select(ExampleModel).filter_by(id=example_id)
        stmt = db.select(ExampleModel).where(ExampleModel.id == example_id)
        example_model = db.session.execute(stmt).scalar_one()
        return example_model

    @classmethod
    def insert_many(cls, example_models: List):
        db.session.add_all(example_models)
        db.session.commit()
    
    def insert(self):
        db.session.add(self)
        db.session.commit()