import json
from flask import request,jsonify, Response
from flask import make_response
from flask_restx import Namespace, Resource, fields
from mylib.services.rf_session_service import RfSessionService
from mylib.utils.rf_error import error_response, ERROR_INTERNAL, ERROR_RESOURCE_NOT_FOUND, ERROR_UNAUTHORIZED

SessionService_ns = Namespace('', description='Session Service')

#================================================
# SessionService
#================================================

session_servive_patch_model = SessionService_ns.model('SessionServicePatch', {
    'SessionTimeout': fields.Integer(
        required=True,
        description='The timeout in seconds for a session before it is considered inactive.',
        example=3600,  # 1 hour
        minimum=30,
        maximum=86400  # 24 hours
    )
})


session_post_model = SessionService_ns.model('SessionPost', {
    'UserName': fields.String(
        required=True,
        description='The user name of the account.',
        example='MyUserName'
    ),
    'Password': fields.String(
        required=True,
        description='The password of the account.',
        example='P@ssw0rd'
    )
})


@SessionService_ns.route("/SessionService")
class SessionService(Resource):
    # # @requires_auth
    
    def get(self):
        resp = Response(json.dumps(RfSessionService.fetch_session_service()), status=200, content_type="application/json")
        resp.headers['Allow'] = 'GET, PATCH'
        return resp
    
    @SessionService_ns.expect(session_servive_patch_model, validate=True)
    def patch(self):
        body = request.get_json(force=True)
        try:
            return RfSessionService.update_session_service(body)
        except Exception:
            return ERROR_INTERNAL

@SessionService_ns.route("/SessionService/Sessions")
class Sessions(Resource):
    # # @requires_auth
    def get(self):
        sessions = RfSessionService.fetch_sessions()
        resp = Response(json.dumps(sessions), status=200, content_type="application/json")
        resp.headers['Allow'] = 'GET, POST'
        return resp
    
    @SessionService_ns.expect(session_post_model, validate=True)
    def post(self):
        body = request.get_json(force=True)
        try:
            result =  RfSessionService.create(body)
            if isinstance(result, Response):
                return result
            if result is None:
                return ERROR_UNAUTHORIZED
            else:
                if 'token' in result:
                    redfish_token = result.pop('token')
                
                resp = Response(json.dumps(result), status=201, content_type="application/json")
                resp.headers['Location'] = f"/redfish/v1/SessionService/Sessions/{result['Id']}"
                resp.headers['X-Auth-Token'] = redfish_token
                return resp
        except Exception:   
            return ERROR_INTERNAL

@SessionService_ns.route("/SessionService/Sessions/Members")
class SessionMembers(Resource):
    def post(self):
        body = request.get_json(force=True)
        try:
            result =  RfSessionService.create(body)
            if isinstance(result, Response):
                return result
            if result is None:
                return ERROR_UNAUTHORIZED
            else:
                if 'token' in result:
                    redfish_token = result.pop('token')
                
                resp = Response(json.dumps(result), status=201, content_type="application/json")
                resp.headers['Location'] = f"/redfish/v1/SessionService/Sessions/{result['Id']}"
                resp.headers['X-Auth-Token'] = redfish_token
                return resp
        except Exception:   
            return ERROR_INTERNAL
        
@SessionService_ns.route("/SessionService/Sessions/<session_id>")
class Session(Resource):
    # # @requires_auth
    def get(self, session_id):
        result = RfSessionService.fetch_session_by_id(session_id)
        
        if result is None:
            return ERROR_RESOURCE_NOT_FOUND
        
        result.pop('token')
        resp = Response(json.dumps(result), status=200, content_type="application/json")
        resp.headers['Allow'] = 'GET, DELETE'
        return resp
    
    def delete(self, session_id):
        try:
            return RfSessionService.delete(session_id)
        except Exception:
            return ERROR_INTERNAL

