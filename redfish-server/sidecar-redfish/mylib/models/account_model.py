"""
flask-sqlalchemy model
@see https://flask-sqlalchemy.readthedocs.io/en/stable/models/

Add @dataclass for serialize sqlalchemy to dict
@see https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
@note:
    1.必須使用dataclass，否則flask-sqlalchemy無法正確序列化
    2.必須加上data type hint，否則dataclass無法正確序列化
    3.加上`@dataclass`裝飾器，在jsonify()時會主動找 `__dict__`這個magic function
"""
from typing import List
from dataclasses import dataclass
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime
from mylib.db.extensions import db
from mylib.models.my_orm_base_model import MyOrmBaseModel
from werkzeug.security import generate_password_hash, check_password_hash
import random,string,re
from datetime import datetime
from mylib.auth.TokenProvider import TokenProvider
from mylib.models.setting_model import SettingModel


@dataclass
class RoleModel(MyOrmBaseModel):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True,unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64),unique=True, nullable=False)
    assigned_privileges: Mapped[str] = mapped_column(String(255),nullable=False)
    accounts: Mapped[List["AccountModel"]] = relationship("AccountModel", back_populates="role")
    
    def __repr__(self):
        return f"RoleModel(id={self.id}, name=\"{self.name}\", assigned_privileges=\"{self.assigned_privileges}\")"
    
    @classmethod
    def all(cls):
        ret = db.session.query(cls).all()
        return ret
    
    @classmethod
    def get_by_id(cls, rold_id):
        stmt = db.select(RoleModel).where(RoleModel.name == rold_id)
        role = db.session.execute(stmt).scalar_one_or_none()
        return role

@dataclass
class AccountModel(MyOrmBaseModel):
    # new version: https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
    __tablename__ = 'accounts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True,unique=True, nullable=False)
    user_name: Mapped[str] = mapped_column(String(255),unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255),nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"),nullable=False)
    role: Mapped["RoleModel"] = relationship("RoleModel", back_populates="accounts")
    redfish_sessions: Mapped[List["SessionModel"]] = relationship('SessionModel', back_populates='account')
    
    def __init__(self, user_name, role, password):
        self.user_name = user_name
        self.role = role
        self.password = generate_password_hash(password)
    
    def __repr__(self):
        return f"AccountModel(id={self.id}, user_name={self.user_name}, role_id={self.role_id}, role={self.role})"
    

    @staticmethod
    def validate_name(user_name):
        pattern =  r'^[A-Za-z][A-Za-z0-9@_.-]{0,14}[A-Za-z0-9]$'
        return bool(re.match(pattern, user_name))
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Validate if the given password meets requirements.
        
        Redfish password requirements:
        - Minimum length: 8 characters
        - Maximum length: 64 characters
        - Must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.
        
        Args:
            password (str): The password to validate.
        
        Returns:
            bool: True if the password is valid, False otherwise.
        """
        import re
        
        if not isinstance(password, str):
            return False
        if not (8 <= len(password) <= 64):
            return False
        
        # Check for at least one uppercase letter, one lowercase letter, one digit, and one special character
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False

        return True
    
    @classmethod
    def all(cls):
        ret = db.session.query(cls).all()
        return ret
    
    @classmethod
    def get_by_id(cls, account_id):
        stmt = db.select(AccountModel).filter_by(user_name=account_id)
        account = db.session.execute(stmt).scalar_one_or_none()
        return account
        
    
    def check_password(self, password: str) -> bool:
        """
        Check if the given password matches the hashed password.
        
        Args:
            password (str): The password to check.
        
        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password, password)

    @classmethod
    def insert_many(cls, example_models: List):
        db.session.add_all(example_models)
        db.session.commit()
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
        
@dataclass
class SessionModel(MyOrmBaseModel):
    __tablename__ = 'redfish_sessions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True,unique=True, nullable=False)
    session_id: Mapped[str] = mapped_column(String(255),unique=True, nullable=False)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"),nullable=False)
    account: Mapped["AccountModel"] = relationship("AccountModel", back_populates="redfish_sessions")
    token: Mapped[str] = mapped_column(String(),nullable=False)
    first_request_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_request_time: Mapped[datetime] = mapped_column(DateTime, nullable=False) 
    
    def __init__(self, assign_account):
        

        self.account_id = assign_account.id
        self.session_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        str_list = assign_account.role.assigned_privileges.split(",") if assign_account.role.assigned_privileges else []
        self.token = TokenProvider.issue_token(assign_account.user_name,
                                            assign_account.role.name,
                                            str_list)
        current_time = datetime.now()
        self.first_request_time = current_time
        self.last_request_time = current_time
        
        
    
    def __repr__(self):
        return (f"SessionModel(id={self.id}, session_id={self.session_id}, "
                f"acount_id={self.account_id}, account={self.account}, "
                f"token={self.token}, first_request_time={self.first_request_time}, "
                f"last_request_time={self.last_request_time})")
        
    @classmethod
    def all(cls):
        ret = db.session.query(cls).all()
        return ret
    
    @classmethod
    def get_by_id(cls, session_id):
        stmt = db.select(SessionModel).filter_by(session_id=session_id)
        session = db.session.execute(stmt).scalar_one_or_none()
        return session
    
    @classmethod
    def get_by_token(cls, token):
        try:
            info = TokenProvider.decode_token(token)
            stmt = db.select(SessionModel).filter_by(token=token)
            fetched_session = db.session.execute(stmt).scalar_one_or_none()
            if fetched_session:
                if fetched_session.account.user_name == info['sub']:
                    timeout = SettingModel.get_by_key('SessionService.SessionTimeout')
                    if timeout:
                        timeout = int(timeout.value)
                        if (datetime.now() - fetched_session.last_request_time ).total_seconds() > timeout:
                            db.session.delete(fetched_session)
                            db.session.commit()
                            return None
                        else:
                            fetched_session.last_request_time = datetime.now()
                            db.session.commit()
                            return fetched_session
                    else:
                        return None
            return None
        except Exception as e:
            print(f"Token decode error: {e}")
            return None