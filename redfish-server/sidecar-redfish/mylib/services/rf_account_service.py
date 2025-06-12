
from mylib.models.account_model import (
    AccountModel,AccountCreateModel, AccountUpdateModel, RoleModel)
from mylib.db.extensions import db
from mylib.utils.rf_error import *
from werkzeug.security import generate_password_hash
from mylib.models.rf_account_service_model import RfAccountServiceModel,RfAccountServiceUpdateModel
from mylib.models.setting_model import SettingModel
import copy

class RfAccountService():
    
    @classmethod
    def fetch_service(cls):
        """
        Get account service.
        """
        acc_ser = copy.deepcopy(cls.account_service_data)
        acc_ser_patch = RfAccountServiceModel.fetch_from_settings()
        acc_ser.update(acc_ser_patch.model_dump(exclude_none=True))
        return acc_ser
    
    @classmethod
    def update_service(cls, json_input):
        """
        Update account service from settings.
        """
        try:
            acc_ser = RfAccountServiceUpdateModel(**json_input)
            if acc_ser.save_to_settings() == False:
                return error_response('Failed to save account service settings', 500, 'Base.GeneralError')
            return cls.fetch_service(), 200
        except ValueError as ve:
            # Check which field might have failed
            for error in ve.errors():
                if not error['loc']:
                    return error_response(msg=error['msg'],http_status=400,code='Base.PropertyValueFormatError')
                err_msg= (f"{error['loc'][0]}: {error['msg']}")#
                return error_response(msg=err_msg,http_status=400,code='Base.PropertyValueFormatError')
            return ERROR_PROPERTY_FORMAT
        except Exception as e:
            return error_response('Failed to update account service', 500, 'Base.GeneralError')
            
    
    @classmethod
    def fetch_roles(cls):
        json_data = copy.deepcopy(cls.roles_basic_data)
        all_roles = RoleModel.all()
        json_data['Members@odata.count']=len(all_roles)
        json_data['Members']=[]
        for role in all_roles:
            json_data['Members'].append({'@odata.id':"/redfish/v1/AccountService/Roles/{id}".format(id=role.name)})
        return json_data

    @classmethod
    def fetch_accounts(cls):
        json_data = copy.deepcopy(cls.accounts_basic_data)
        all_users = AccountModel.all()
        json_data['Members@odata.count']=len(all_users)
        json_data['Members']=[]
        for user in all_users:
            json_data['Members'].append({'@odata.id':"/redfish/v1/AccountService/Accounts/{id}".format(id=user.user_name)})
        return json_data
    
    @classmethod
    def fetch_role_by_id(cls, role_id):
        json_data = copy.deepcopy(cls.role_basic_data)
        role = RoleModel.get_by_id(role_id)
        if role is None:
            return None
        else:
            json_data['Id']=str(role.name)
            json_data['RoleId'] = str(role.name)
            json_data['Description'] = str(role.name) + " User Role"
            json_data['AssignedPrivileges'] = [] if not role.assigned_privileges else str(role.assigned_privileges).split(',')
            json_data["@odata.id"]="/redfish/v1/AccountService/Roles/{0}".format(role.name)
            return  json_data
        
    
    @classmethod
    def fetch_account_by_id(cls, account_id):
        json_data = copy.deepcopy(cls.account_basic_data)
        user = AccountModel.get_by_id(account_id)
        if user is None:
            return None
        else:
            
            json_data['Id']=str(user.user_name)
            json_data['UserName'] = user.user_name
            json_data['RoleId'] = user.role.name
            json_data['Enabled'] = user.enabled
            json_data['Locked'] = user.locked
            json_data['PasswordChangeRequired']=user.pass_change_required
            json_data['Links'] = {
                "Role": {
                    "@odata.id": "/redfish/v1/AccountService/Roles/{0}".format(user.role.name)
                }
            }
            json_data["@odata.id"]="/redfish/v1/AccountService/Accounts/{0}".format(user.user_name)
            return  json_data
        
    
    @classmethod
    def create_account(cls, json_input):
        """
        Create a new account.
        """
        try:
            validated = AccountCreateModel(**json_input)
            if not validated:
                return error_response('Invalid input data', 400, 'Base.PropertyValueFormatError')        
            
            existing_user = AccountModel.query.filter_by(user_name=json_input['UserName']).first()
            if existing_user:
                return error_response('User already exists', 400, 'Base.ResourceAlreadyExists')
            
            #new_account = AccountModel(user_name=json_input['UserName'], role=find_role, password=json_input['Password'])
            new_account = AccountModel(
                user_name=validated.user_name,
                role=RoleModel.query.filter_by(id=validated.role_id).first(),
                password=validated.password
            )

            max_allowed_setting = SettingModel.get_by_key('AccountService.MaxAllowedAccounts')
            
            # Check if the number of accounts exceeds the maximum allowed
            if AccountModel.query.count() >= int(max_allowed_setting.value):
                return error_response('Maximum number of accounts reached', 403, 'Base.OperationNotAllowed')

            db.session.add(new_account)
            db.session.commit()
        except ValueError as ve:
            # Check which field might have failed
            for error in ve.errors():
                err_msg= (f"{error['loc'][0]}: {error['msg']}")#
                return error_response(msg=err_msg,http_status=400,code='Base.PropertyValueFormatError')
                
            return ERROR_PROPERTY_FORMAT
 
        return cls.fetch_account_by_id(new_account.user_name)
    
    @classmethod
    def update_account(cls, account_id, json_input):
        """
        Update an existing account.
        """
        try:
            existing_user = AccountModel.query.filter_by(user_name=account_id).first()
            if not existing_user:
                return ERROR_RESOURCE_NOT_FOUND
            validated = AccountUpdateModel(**json_input)
            if not validated:
                return error_response('Invalid input data', 400, 'Base.PropertyValueFormatError')
            
            new_username_user = AccountModel.query.filter_by(user_name=validated.user_name).first()
            if new_username_user:
                return error_response('The user with this user name already exists', 400, 'Base.ResourceAlreadyExists')
            
            
            for key, value in validated.model_dump(exclude_none=True).items():
                existing_user.__setattr__(key, value)
                
            db.session.commit()
        except ValueError as ve:
            # Check which field might have failed
            for error in ve.errors():
                if not error['loc']:
                    return error_response(msg=error['msg'],http_status=400,code='Base.PropertyValueFormatError')
                err_msg= (f"{error['loc'][0]}: {error['msg']}")#
                return error_response(msg=err_msg,http_status=400,code='Base.PropertyValueFormatError')
            return ERROR_PROPERTY_FORMAT
        
        return cls.fetch_account_by_id(existing_user.user_name), 200
    
    @classmethod
    def delete(cls, account_id):
        """
        Delete an existing account.
        """
        try:
            existing_user = AccountModel.query.filter_by(user_name=account_id).first()
            if not existing_user:
                return ERROR_RESOURCE_NOT_FOUND
            if existing_user.redfish_sessions:
                return error_response(
                    "Cannot delete account because it has active sessions.",
                    400,
                    "Base.ResourceInUse"
                )
            db.session.delete(existing_user)
            db.session.commit()
        except Exception as e:
            return ERROR_RESOURCE_NOT_FOUND
        return ERROR_DELETE_SUCCESS
    
    account_service_data = {
        "@odata.type": "#AccountService.v1_18_0.AccountService",
        "@odata.id": "/redfish/v1/AccountService",
        "@odata.context":  "/redfish/v1/$metadata#AccountService.v1_18_0.AccountService",
        "Id": "AccountService",
        "Name": "Account Service",
        "Description": "Account Service",
        "Status": {
            "State": "Enabled",
            "Health": "OK"
        },
        "SupportedAccountTypes": [
            "Redfish"
        ],
        "ServiceEnabled": True,
        "AuthFailureLoggingThreshold": 0,
        "MinPasswordLength": 0,
        "MaxPasswordLength": 0,
        "AccountLockoutThreshold": 0,
        "AccountLockoutDuration": 0,
        "AccountLockoutCounterResetAfter": 0,
        "Accounts": {
            "@odata.id": "/redfish/v1/AccountService/Accounts"
        },
        "Roles": {
            "@odata.id": "/redfish/v1/AccountService/Roles"
        }
    }
    
    accounts_basic_data = {
        "@odata.type": "#ManagerAccountCollection.ManagerAccountCollection",
        "@odata.id": "/redfish/v1/AccountService/Accounts",
        "Name": "Accounts Collection",
        "Members@odata.count": 0,
        "Members": []
    }
    
    account_basic_data = {
        "@odata.id": "/redfish/v1/AccountService/Accounts/",
        "@odata.type": "#ManagerAccount.v1_12_1.ManagerAccount",
        "AccountTypes":[
            "Redfish"
        ],
        "Id": "1",
        "Name": "User Account",
        "Description": "User Account",
        "Password": None,
        "PasswordChangeRequired": False,
        "UserName": "Administrator",
        "RoleId": "Administrator",
        "Enabled": True,
        "Locked": False,
        "Links": {
            "Role": {
                "@odata.id": "/redfish/v1/AccountService/Roles/Admin"
            }
        }
    }
    
    roles_basic_data = {
        "@odata.type": "#RoleCollection.RoleCollection",
        "Name": "Roles Collection",
        "Members@odata.count": 0,
        "Members": [
            {
                "@odata.id": "/redfish/v1/AccountService/Roles/Administrator"
            },
            {
                "@odata.id": "/redfish/v1/AccountService/Roles/Operator"
            },
            {
                "@odata.id": "/redfish/v1/AccountService/Roles/ReadOnlyUser"
            }
        ],
        "@odata.id": "/redfish/v1/AccountService/Roles"
    }
    
    role_basic_data = {
        "@odata.type": "#Role.v1_3_2.Role",
        "Name": "User Role",
        "Id": "",
        "RoleId":"",
        "Description": "",
        "IsPredefined": True,
        "AssignedPrivileges": [],
        "OemPrivileges": [],
        "@odata.id": "/redfish/v1/AccountService/Roles/"
    }

