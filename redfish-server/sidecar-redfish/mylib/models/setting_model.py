from typing import List
from dataclasses import dataclass
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from mylib.db.extensions import db
from mylib.models.my_orm_base_model import MyOrmBaseModel


@dataclass
class SettingModel(MyOrmBaseModel):
    __tablename__ = 'settings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True,unique=True, nullable=False)
    key : Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    value : Mapped[str] = mapped_column(String(255), nullable=False)
        
    def __repr__(self):
        return f"SettingModel(key={self.key}, value=\"{self.value}\")"
    
    @classmethod
    def all(cls):
        ret = db.session.query(cls).all()
        return ret
    
    @classmethod
    def get_by_key(cls, key):
        stmt = db.select(SettingModel).where(SettingModel.key == key)
        setting = db.session.execute(stmt).scalar_one()
        return setting