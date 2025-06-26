from mylib.db.extensions import db


class MyOrmBaseModel(db.Model):
    __abstract__ = True
    def to_dict(self) -> dict:
        return {
            c.name: getattr(self, c.name) 
            for c in self.__table__.columns
        }