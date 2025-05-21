from mylib.models.account_model import AccountModel,SessionModel
from enum import Enum

class AuthStatus(Enum):
    SUCCESS = 1        #successful authentication
    USERNAME_NOT_FOUND = 2  #username not found
    PASSWORD_INCORRECT = 3  #password incorrect
    

def check_basic_auth(username, password):
    
    fetched_account = AccountModel.get_by_id(username)
    if fetched_account is None:
        return AuthStatus.USERNAME_NOT_FOUND
    
    if not fetched_account.check_password(password):
        return AuthStatus.PASSWORD_INCORRECT
    return AuthStatus.SUCCESS

def check_session_auth(token):
    fetched_session = SessionModel.get_by_token(token)
    if fetched_session is None:
        return AuthStatus.USERNAME_NOT_FOUND
    return AuthStatus.SUCCESS