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
@AccountService_ns.route("/AccountService/")
class AccountService(Resource):
    # # @requires_auth
    
    def get(self):
        resp = Response(json.dumps(RfAccountService.fetch_account_service()), status=200, content_type="application/json")
        resp.headers['Allow'] = 'GET'
        return resp

@AccountService_ns.route("/AccountService/Roles/")
class Roles(Resource):
    # # @requires_auth
    def get(self):
        roles = RfAccountService.fetch_roles()
        resp = Response(json.dumps(roles), status=200, content_type="application/json")
        resp.headers['Allow'] = 'GET'
        return resp

@AccountService_ns.route("/AccountService/Roles/<role_id>/")
class Role(Resource):
    # # @requires_auth
    def get(self, role_id):
        role = RfAccountService.fetch_role_by_id(role_id)
        if role is None:
            return ERROR_RESOURCE_NOT_FOUND
        resp = Response(json.dumps(role), status=200, content_type="application/json")
        resp.headers['Allow'] = 'GET,PATCH'
        return resp
    
    
    
@AccountService_ns.route("/AccountService/Accounts/")
class Accounts(Resource):
    # # @requires_auth
    def get(self):
        accounts = RfAccountService.fetch_accounts()
        resp = Response(json.dumps(accounts), status=200, content_type="application/json")
        resp.headers['Allow'] = 'GET, POST'
        return resp
    
    def post(self):
        body = request.get_json(force=True)
        try:
            result = RfAccountService.create(body)
            if isinstance(result, Response):
                return result
            resp = Response(json.dumps(result), status=201, content_type="application/json")
            resp.headers['Location'] = f"/redfish/v1/AccountService/Accounts/{result['Id']}"
            return resp
        except Exception:
            return ERROR_INTERNAL
    
@AccountService_ns.route("/AccountService/Accounts/<account_id>/")
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
    
    def patch(self, account_id):
        body = request.get_json(force=True)
        try:
            return RfAccountService.update(account_id, body)
        except Exception:
            return ERROR_INTERNAL
    
    def delete(self, account_id):
        try:
            return RfAccountService.delete(account_id)
        except Exception:
            return ERROR_INTERNAL
