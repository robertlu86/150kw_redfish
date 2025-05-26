
#from mylib.models.account_model import AccountModel, RoleModel
from mylib.db.extensions import db
from mylib.utils.rf_error import  *
from werkzeug.security import generate_password_hash
from mylib.models.setting_model import SettingModel
from mylib.models.account_model import AccountModel,SessionModel
from mylib.auth.TokenProvider import TokenProvider

class RfSessionService():
    
    @classmethod
    def fetch_session_service(cls):
        json_data = cls.session_service_data
        json_data['SessionTimeout'] = int(SettingModel.get_by_key('SessionService.SessionTimeout').value)
        return cls.session_service_data

    @classmethod
    def create(cls, json_input):
        if 'UserName' not in json_input:
            return error_response('No key of UserName', 400, 'Base.PropertyMissing')
        
        if not AccountModel.validate_name(json_input['UserName']):
            return ERROR_USERNAME_FORMAT
        
        # default password of admin accoount can't pass the validation
        # if not AccountModel.validate_password(json_input['Password']):
        #     return ERROR_PASSWORD_FORMAT
        
        find_account = AccountModel.get_by_id(json_input['UserName'])
        
        if not find_account:
            return ERROR_RESOURCE_NOT_FOUND
        
        if not find_account.check_password(json_input['Password']):
            return ERROR_RESOURCE_NOT_FOUND
        redfish_session = SessionModel(find_account)
        db.session.add(redfish_session)
        db.session.commit()
        return cls.fetch_session_by_id(redfish_session.session_id)
    
    @classmethod
    def fetch_sessions(cls):
        json_data = cls.sessions_basic_data
        all_sessions = SessionModel.all()
        json_data['Members@odata.count']=len(all_sessions)
        json_data['Members']=[]
        for session in all_sessions:
            json_data['Members'].append({'@odata.id':"/redfish/v1/SessionService/Sessions/{id}".format(id=session.session_id)})
        return json_data
    
    @classmethod
    def fetch_session_by_id(cls, session_id):
        json_data = cls.session_basic_data
        fetched_session = SessionModel.get_by_id(session_id)
        if fetched_session is None:
            return None
        else: 
            json_data["@odata.id"]=f"/redfish/v1/SessionService/Sessions/{fetched_session.session_id}"
            json_data['Id']=str(fetched_session.session_id)
            json_data['Name'] = f"{fetched_session.account.user_name } Session"
            json_data['UserName'] = fetched_session.account.user_name
            json_data['token'] = fetched_session.token
            return  json_data
        
    @classmethod
    def delete(cls, session_id):
        existing_session = SessionModel.query.filter_by(session_id=session_id).first()
        if not existing_session:
            return ERROR_RESOURCE_NOT_FOUND
        db.session.delete(existing_session)
        db.session.commit()
        return ERROR_DELETE_SUCCESS
    
    session_service_data = {
        "@odata.type": "#SessionService.v1_1_9.SessionService",
        "Id": "SessionService",
        "Name": "Session Service",
        "Description": "Session Service",
        "Status": {
            "State": "Enabled",
            "Health": "OK"
        },
        "ServiceEnabled": True,
        "SessionTimeout": 300,
        "Sessions": {
            "@odata.id": "/redfish/v1/SessionService/Sessions"
        },
        "@odata.id": "/redfish/v1/SessionService"
    }
    
    sessions_basic_data = {
        "@odata.type": "#SessionCollection.SessionCollection",
        "@odata.id": "/redfish/v1/SessionService/Sessions",
        "Name": "Session Collection",
        "Members@odata.count": 0,
        "Members": [],
    
    }
    
    session_basic_data = {
        "@odata.type": "#Session.v1_4_0.Session",
        "@odata.id": "/redfish/v1/SessionService/Sessions/",
        "Id": "",
        "Name": "admin Session",
        "UserName": "admin"
    }
    

    
    