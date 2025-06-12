import json
from flask import request,jsonify, Response
from flask import make_response
from flask_restx import Namespace, Resource, fields
from mylib.services.rf_account_service import RfAccountService
from mylib.utils.rf_error import *

AccountService_ns = Namespace('', description='Account Service')

#================================================
# AccountService
#================================================
account_servive_patch_model = AccountService_ns.model('AccountServicePatch', {
    'AuthFailureLoggingThreshold': fields.Integer(
        required=False,
        description='The number of failed login attempts before the account is locked out.',
        example=5,
        minimum=0,  # Must be greater than 0
    ),
    'MinPasswordLength': fields.Integer(
        required=False,
        description='The minimum length of a password.',
        example=8,
        minimum=1  # Must be greater than 0
    ),
    'MaxPasswordLength': fields.Integer(
        required=False,
        description='The minimum length of a password.',
        example=15,
        maximum=50  # Must be less than or equal to 50
    ),
    'AccountLockoutThreshold': fields.Integer(
        required=False,
        description='The number of failed login attempts before the account is locked out.',
        example=3,
        minimum=0  # Must be greater than or equal to 0
    ),
    'AccountLockoutDuration': fields.Integer(
        required=False,
        description='The duration in seconds for which the account remains locked out.',
        example=100
    ),
    'AccountLockoutCounterResetAfter': fields.Integer(
        required=False,
        description='The time in seconds after which the lockout counter resets.',
        example=50
    )
})

account_post_model = AccountService_ns.model('AccountsPost', {
    'UserName': fields.String(
        required=True,
        description='The user name of the account.',
        example='MyUserName',
        pattern='^[A-Za-z0-9][A-Za-z0-9@_.-]{0,14}[A-Za-z0-9]$'
    ),
    'Password': fields.String(
        required=True,
        description='The password of the account.',
        example='P@ssw0rd'
    ),
    'RoleId': fields.String(
        required=True,
        description='The role ID associated with the account.',
        example='Administrator',
        enum=['Administrator', 'Operator', 'ReadOnly','NoAccess'] 
    ),
    # 'Enabled': fields.Boolean(
    #     required=False,
    #     description='Indicates whether the account is enabled or disabled.',
    #     example=True
    # ),
    # 'Locked': fields.Boolean(
    #     required=False,
    #     description='Indicates whether the account is locked.',
    #     example=False
    # )
})

account_patch_model = AccountService_ns.model('AccountsPatch', {
    'UserName': fields.String(
        required=False,
        description='The user name of the account.',
        example='MyUserName',
        pattern='^[A-Za-z0-9][A-Za-z0-9@_.-]{0,14}[A-Za-z0-9]$'
    ),
    'Password': fields.String(
        required=False,
        description='The password of the account.',
        example='P@ssw0rd'
    ),
    'RoleId': fields.String(
        required=False,
        description='The role ID associated with the account.',
        example='Administrator',
        enum=['Administrator', 'Operator', 'ReadOnly','NoAccess'] 
    ),
    'Enabled': fields.Boolean(
        required=False,
        description='Indicates whether the account is enabled or disabled.',
        example=True
    ),
    'Locked': fields.Boolean(
        required=False,
        description='Indicates whether the account is locked.',
        example=False
    )
})


@AccountService_ns.route("/AccountService")
class AccountService(Resource):
    # # @requires_auth
    
    def get(self):
        resp = Response(json.dumps(RfAccountService.fetch_service()), status=200, content_type="application/json")
        resp.headers['Allow'] = 'GET, PATCH'
        return resp
    @AccountService_ns.expect(account_servive_patch_model,validate=True)
    def patch(self):
        body = request.get_json(force=True)
        try:
            return RfAccountService.update_service(body)
        except Exception:
            return ERROR_INTERNAL

@AccountService_ns.route("/AccountService/Roles")
class Roles(Resource):
    # # @requires_auth
    def get(self):
        roles = RfAccountService.fetch_roles()
        resp = Response(json.dumps(roles), status=200, content_type="application/json")
        resp.headers['Allow'] = 'GET'
        return resp

@AccountService_ns.route("/AccountService/Roles/<role_id>")
class Role(Resource):
    # # @requires_auth
    def get(self, role_id):
        role = RfAccountService.fetch_role_by_id(role_id)
        if role is None:
            return ERROR_RESOURCE_NOT_FOUND
        resp = Response(json.dumps(role), status=200, content_type="application/json")
        resp.headers['Allow'] = 'GET,PATCH'
        return resp
    
    
    
@AccountService_ns.route("/AccountService/Accounts")
class Accounts(Resource):
    # # @requires_auth
    def get(self):
        accounts = RfAccountService.fetch_accounts()
        resp = Response(json.dumps(accounts), status=200, content_type="application/json")
        resp.headers['Allow'] = 'GET, POST'
        return resp
    
    @AccountService_ns.expect(account_post_model, validate=True)
    def post(self):
        body = request.get_json(force=True)
        try:
            result = RfAccountService.create_account(body)
            if isinstance(result, Response):
                return result
            resp = Response(json.dumps(result), status=201, content_type="application/json")
            resp.headers['Location'] = f"/redfish/v1/AccountService/Accounts/{result['Id']}"
            return resp
        except Exception:
            return ERROR_INTERNAL
    
@AccountService_ns.route("/AccountService/Accounts/<account_id>")
class Account(Resource):
    # # @requires_auth
    def get(self, account_id):
        account = RfAccountService.fetch_account_by_id(account_id)
        if account is None:
            return ERROR_RESOURCE_NOT_FOUND
        account_etag = f'"{hex(hash(json.dumps(account)))}"'  
        account['@odata.etag'] = account_etag
        resp = Response(json.dumps(account), status=200, content_type="application/json")
        resp.headers['Allow'] = 'GET, PATCH, DELETE'
        resp.headers['ETag'] = account_etag
        return resp
    
    @AccountService_ns.expect(account_patch_model, validate=True)
    def patch(self, account_id):
        body = request.get_json(force=True)
        try:
            return RfAccountService.update_account(account_id, body)
        except Exception:
            return ERROR_INTERNAL
    
    def delete(self, account_id):
        try:
            return RfAccountService.delete(account_id)
        except Exception:
            return ERROR_INTERNAL
