import logging
import traceback
import datetime
import pytz
import re
from urllib import response
from flask import (
    abort, Blueprint, make_response, render_template, request, session, current_app, Response, jsonify
)

bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='')

# Only forward requests from authenticating servers
@bp.before_request
def limit_remote_addr():
    if request.host != current_app.config['AUTH'].AUTH_HOST:
        abort(403)  # Forbidden

@bp.route('/verified', methods=['GET'])
def verified():
    # Get refresh token from auth server by uuid
    return jsonify({'code': 'test limit'})
    
# validate refresh token and return new access token and refresh token
@bp.route('/agent', methods=['GET'])
def get_token():
    
    # Get refresh token from auth server by uuid
    
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return 'Bad Request', 400
    try:
        token_item = dbs.query(TRN_REFRESH_TOKEN, MST_USER).join(MST_USER, MST_USER.role_cd!=0).\
                filter(TRN_REFRESH_TOKEN.refresh_token == refresh_token).all()
        
        if len(token_item) != 1:
            return 'Bad Request', 400
        else:
            one = token_item[0].MST_USER
            token = token_item[0].TRN_REFRESH_TOKEN
            remote_info = token.remote_info
            aud = current_app.config['RESOURCE'][token.resource_key]['AUDIENCE']
            now = datetime.datetime.now(tz=token.expiration_datetime.tzinfo)
            
            # Validate remote info is correct, user's resource url is in request, and refresh token is not expirat
            if remote_info[0] == request.remote_addr and\
                remote_info[1] == request.user_agent.string and\
                aud == request.origin and\
                token.expiration_datetime > now:
                    
                AUTH = current_app.config['AUTH']
                remote = [request.remote_addr, request.user_agent.string]
                payload = get_payload(AUTH, one.user_id, aud, remote, one.role_cd)
                
                access_token = secret.create_access_token(AUTH.ACCESS_TOKEN_PRIVATE_KEY, AUTH.ACCESS_TOKEN_ALG, payload)
                refresh_token = secret.create_refresh_token()
                expiration_datetime = now + datetime.timedelta(days=AUTH.REFRESH_TOKEN_EXPIRATION_TIME)
                
                token.remote_info = remote
                token.refresh_token = refresh_token
                token.expiration_datetime = expiration_datetime
                token.update_datetime = now
                
                result = jsonify({'code': 'I006', 'access_token': access_token, 'role_cd': one.role_cd})
                resp = make_response(result)
                resp.set_cookie('refresh_token', refresh_token,
                                httponly=AUTH.REFRESH_TOKEN_COOKIE_HTTPONLY, 
                                secure=AUTH.REFRESH_TOKEN_COOKIE_SECURE, 
                                samesite=AUTH.REFRESH_TOKEN_COOKIE_SAMESITE)
                
                resp.access_control_allow_credentials = True
                
                dbs.commit()
                return result
            else:
                return 'Bad Request', 400
        
    except Exception as e:
        # E002 = DB exception or email error
        logging.error(traceback.format_exc())
        dbs.rollback()
        return 'Internal Server Error', 500
            
