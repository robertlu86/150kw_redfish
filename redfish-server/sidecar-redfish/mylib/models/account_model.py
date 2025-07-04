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
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean
from mylib.db.extensions import db
from mylib.models.my_orm_base_model import MyOrmBaseModel
from werkzeug.security import generate_password_hash, check_password_hash
import random,string,re
from datetime import datetime
from mylib.auth.TokenProvider import TokenProvider
from mylib.models.setting_model import SettingModel
from typing import Optional
from pydantic import (
    BaseModel,
    ConfigDict,
    Field, 
    computed_field,
    model_validator,
    #validator, # deprecated
    field_validator,
)

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
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pass_change_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_pass_err_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    pass_err_times: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    redfish_sessions: Mapped[List["SessionModel"]] = relationship('SessionModel', back_populates='account')
 
    def __init__(self, user_name, role, password):
        self.user_name = user_name
        self.role = role
        self.password = password
 
    def __repr__(self):
        return f"AccountModel(id={self.id}, user_name={self.user_name}, role_id={self.role_id}, role={self.role}, enabled={self.enabled}, locked={self.locked})"
    
    def check_if_unlocked(self):
        """
        Check if the account is locked and if the lockout duration has passed.
        If the account is locked and the lockout duration has passed, unlock the account.
        """
        lock_out_duration = int(SettingModel.get_by_key('AccountService.AccountLockoutDuration').value)
        if self.locked and self.last_pass_err_time:
            time_difference = datetime.now() - self.last_pass_err_time
            if time_difference.total_seconds() > lock_out_duration:
                self.locked = False
                self.pass_err_times = 0
                self.last_pass_err_time = None
                db.session.commit()
                return True
        return False
 


    def add_pass_err_times(self):
        lock_out_threshold = int(SettingModel.get_by_key('AccountService.AccountLockoutThreshold').value)
        lock_out_duration = int(SettingModel.get_by_key('AccountService.AccountLockoutDuration').value)
        lock_reset_after = int(SettingModel.get_by_key('AccountService.AccountLockoutCounterResetAfter').value)

        if lock_out_duration == 0 or lock_out_threshold == 0:
            return
        
        if self.locked:
            if lock_out_duration > 0 and self.last_pass_err_time:
                time_difference = datetime.now() - self.last_pass_err_time
                if time_difference.total_seconds() > lock_out_duration:
                    self.locked = False
                    self.pass_err_times = 0
                    self.last_pass_err_time = None

        if lock_reset_after > 0 and self.last_pass_err_time:
            time_difference = datetime.now() - self.last_pass_err_time
            if time_difference.total_seconds() > lock_reset_after:
                self.pass_err_times = 1
            else:
                self.pass_err_times += 1
        else:
            self.pass_err_times += 1
        

        if self.pass_err_times >= lock_out_threshold:
            self.locked = True
        self.last_pass_err_time = datetime.now()
        db.session.commit()
        return
    
    def reset_pass_err_times(self):
        """
        Reset the password error times and last error time.
        """
        self.pass_err_times = 0
        self.last_pass_err_time = None
        db.session.commit()

    @staticmethod
    def validate_name(user_name):
        # Check basic pattern: starts and ends with alphanumeric, 2-16 chars total
        pattern = r'^[A-Za-z0-9][A-Za-z0-9@_.-]{0,14}[A-Za-z0-9]$'
        return bool(re.match(pattern, user_name))
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Validate if the given password meets requirements.
        
        Redfish password requirements:
        - Valid passwords are strings containing chars of at least 3 categories (a-z, A-Z, 0-9, special).
        - Allowed special characters may include: ! $ % & () * + . / < = > ? @ [] ^ _ ` {} | ~ ( : # - ;
        
        Args:
            password (str): The password to validate.
        
        Returns:
            bool: True if the password is valid, False otherwise.
        """
        import re
        
        if not isinstance(password, str):
            return False
        
        # Count the number of categories present in the password
        categories = 0
        if re.search(r'[A-Z]', password):
            categories += 1
        if re.search(r'[a-z]', password):
            categories += 1
        if re.search(r'\d', password):
            categories += 1
        if re.search(r'[!$%&()*+./<=>?@\[\]^_`{}|~:#-]', password):
            categories += 1

        return categories >= 3
    
    #if pass return 0 else return min password length
    @staticmethod    
    def password_len_validation(password: str):
        # Password length validation
        min_password_length_setting = SettingModel.get_by_key('AccountService.MinPasswordLength')
        max_password_length_setting = SettingModel.get_by_key('AccountService.MaxPasswordLength')
        if min_password_length_setting:
            min_password_length = int(min_password_length_setting.value)
            if len(password) < min_password_length:
                print(f"Password length {len(password)} is less than minimum required {min_password_length}.")
                return ">=", min_password_length
        if max_password_length_setting:
            max_password_length = int(max_password_length_setting.value)
            if len(password) > max_password_length:
                print(f"Password length {len(password)} is greater than maximum allowed {max_password_length}.")
                return "<=", max_password_length
        return "ok", 0

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
        
class AccountBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    user_name: Optional[str] = Field(default=None,alias = 'UserName', description="The name of the user.")
    role_id: Optional[int] = Field(default=None, alias ='RoleId', description="The ID of the role assigned to the user.")
    password: Optional[str] = Field(default=None,alias = 'Password', description="The password for the user.")
    
    @field_validator('password',mode='before')
    @classmethod
    def validate_password(cls, value):
        if not AccountModel.validate_password(value):
            raise ValueError("should be containing chars of at least 3 categories (a-z, A-Z, 0-9, special)")
        ret_res,ret_val = AccountModel.password_len_validation(value)
        if ret_res != 'ok':
            raise ValueError(f"length should {ret_res} {ret_val}")
        return value

    @field_validator('password',mode='after')
    @classmethod
    def generate_hash_password(cls, value):
        return generate_password_hash(value)
    
    @field_validator('role_id',mode='before')
    @classmethod
    def validate_role_id(cls, value):
        if not isinstance(value, str):
            raise ValueError("format does not meet requirements.")
        role = RoleModel.get_by_id(value)
        if not role:
            raise ValueError(f"{value} does not exist.")
        return role.id
    
    @field_validator('user_name',mode='before')
    @classmethod
    def validate_user_name(cls, value):
        if not AccountModel.validate_name(value):
            raise ValueError("must contain only characters from A–Z,a–z,0–9,@,_,.,and -")
        return value

class AccountUpdateModel(AccountBaseModel):
    enabled: Optional[bool] = Field(default=None, alias='Enabled', 
                            description="Indicates whether the account is enabled.")
    locked: Optional[bool] = Field(default=None, alias='Locked', 
                            description="Indicates whether the account is locked.")
    pass_change_required: Optional[bool] = Field(default=None, alias='PasswordChangeRequired', 
                            description="Indicates whether the account needs to update the password.")
    
    @model_validator(mode='before')
    def check_at_least_one_field(cls, values):
        enabled = values.get('Enabled')
        locked = values.get('Locked')
        pass_change_required = values.get('PasswordChangeRequired')
        user_name = values.get('UserName')
        password = values.get('Password')
        role_id = values.get('RoleId')

        if enabled is None and locked is None and pass_change_required is None and \
           user_name is None and password is None and role_id is None:
            raise ValueError(f"{values} must contain at least one valid field to update.")
        if password is not None:
            values['PasswordChangeRequired'] = False
        return values
    
    @field_validator('locked',mode='before')
    @classmethod
    def validate_locked(cls, value):
        if not isinstance(value, bool):
            raise ValueError("format does not meet requirements.")
        if value == True:
            raise ValueError(f"{value} is not allowed.")
        return value

class AccountCreateModel(AccountBaseModel):
    user_name: str = Field(default=..., alias='UserName', description="The name of the user.")
    role_id: int = Field(default=..., alias='RoleId', description="The ID of the role assigned to the user.")
    password: str = Field(default=..., alias='Password', description="The password for the user.")
    

        
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
        ret_sessions = db.session.query(cls).all()
        # check if session timeout
        timeout = SettingModel.get_by_key('SessionService.SessionTimeout')
        if timeout:
            timeout = int(timeout.value)
            for session in ret_sessions:
                if (datetime.now() - session.last_request_time).total_seconds() > timeout:
                    db.session.delete(session)
                    db.session.commit()
                    ret_sessions.remove(session)
        return ret_sessions
    
    @classmethod
    def get_by_id(cls, session_id):
        stmt = db.select(SessionModel).filter_by(session_id=session_id)
        session = db.session.execute(stmt).scalar_one_or_none()
        # check if session timeout
        if session:
            timeout = SettingModel.get_by_key('SessionService.SessionTimeout')
            if timeout:
                timeout = int(timeout.value)
                if (datetime.now() - session.last_request_time).total_seconds() > timeout:
                    db.session.delete(session)
                    db.session.commit()
                    return None
                else:
                    session.last_request_time = datetime.now()
                    db.session.commit()
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