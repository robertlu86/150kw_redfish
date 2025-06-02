
from mylib.models.account_model import (
    AccountModel,AccountUpdateModel, RoleModel)
from mylib.db.extensions import db
from mylib.utils.rf_error import *
from werkzeug.security import generate_password_hash
from mylib.models.rf_account_service_model import RfAccountServiceModel
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
            acc_ser = RfAccountServiceModel(**json_input)
            if acc_ser.save_to_settings() == False:
                return error_response('Failed to save account service settings', 500, 'Base.GeneralError')
            return cls.fetch_service(), 200
        except ValueError as ve:
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
            json_data['AssignedPrivileges'] = str(role.assigned_privileges).split(',')
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
        if 'UserName' not in json_input:
            return error_response('No key of UserName', 400, 'Base.PropertyMissing')
        if not AccountModel.validate_name(json_input['UserName']):
            return ERROR_USERNAME_FORMAT
        if 'RoleId' not in json_input:
            return error_response('No key of RoleId', 400, 'Base.PropertyMissing')
        find_role = RoleModel.query.filter_by(name=json_input['RoleId']).first()
        if not find_role:
            return error_response('RoleId not found', 400, 'Base.PropertyValueNotInList')
        if 'Password' not in json_input:
            return error_response('No key of Password', 400, 'Base.PropertyMissing')
        if isinstance(json_input['Password'], str) == False:
            return ERROR_PASSWORD_FORMAT
        if not AccountModel.validate_password(json_input['Password']):
            return ERROR_PASSWORD_FORMAT
        existing_user = AccountModel.query.filter_by(user_name=json_input['UserName']).first()
        if existing_user:
            return error_response('User already exists', 400, 'Base.ResourceAlreadyExists')
        
        new_account = AccountModel(user_name=json_input['UserName'], role=find_role, password=json_input['Password'])
        db.session.add(new_account)
        db.session.commit()
 
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
            for key, value in validated.model_dump(exclude_none=True).items():
                existing_user.__setattr__(key, value)
            db.session.commit()
        except ValueError as ve:
            return ERROR_PROPERTY_FORMAT
        
        # move validation logic to pydantic model, so comment out the following code
        # if "RoleId" not in json_input and "Password" not in json_input:
        #     return error_response('No key of RoleId or Password', 400, 'Base.PropertyMissing')
        # if 'RoleId' in json_input:
        #     find_role = RoleModel.query.filter_by(name=json_input['RoleId']).first()
        #     if not find_role:
        #         return error_response('RoleId not found', 400, 'Base.PropertyValueNotInList')
        #     existing_user.role = find_role
        # if 'Password' in json_input:
        #     if isinstance(json_input['Password'], str) == False:
        #         return ERROR_PASSWORD_FORMAT
        #     if not AccountModel.validate_password(json_input['Password']):
        #         return ERROR_PASSWORD_FORMAT
        #     existing_user.password = generate_password_hash(json_input['Password'])
        
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
        "@odata.type": "#AccountService.v1_15_1.AccountService",
        "@odata.id": "/redfish/v1/AccountService",
        "@odata.context":  "/redfish/v1/$metadata#AccountService.v1_15_1.AccountService",
        "Id": "AccountService",
        "Name": "Account Service",
        "Description": "Account Service",
        "Status": {
            "State": "Enabled",
            "Health": "OK"
        },
        "ServiceEnabled": True,
        "AuthFailureLoggingThreshold": 0,
        "MinPasswordLength": 0,
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

