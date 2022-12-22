from functools import wraps
from flask import request, session, current_app

from authlib.jose import jwt
from datetime import datetime

def check_access_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].replace('Bearer ', '')
        
        if not token:
            return 'Unauthorized', 401
        
        key = open(current_app.config['AUTH'].ACCESS_TOKEN_PUBLIC_KEY, 'rb').read()
        try:
            payload = jwt.decode(token, key)
            print(payload)
        except Exception as e:
            return 'Unauthorized', 401
               
        remote_agent_ok, not_expired = False, False
        # check session info
        # if 'user_id' in session:
        #     if 'sub' in payload and payload['sub'] == session['user_id']:
        #         has_session = True
        
        # check user agent info
        if 'remote' in payload and len(payload['remote']) == 2:
            if payload['remote'][0] == request.remote_addr and payload['remote'][1] == request.user_agent.string:
                remote_agent_ok = True

        # check jwt is not expired
        if 'exp' in payload:
            exp = datetime.strptime(payload['exp'], '%Y-%m-%d %H:%M:%S')
            if exp > datetime.now():
                not_expired = True

        if remote_agent_ok and not_expired:
            current_user = {'user_id': str(payload['sub']), 'role': payload['role'], 'aud': payload['aud']}
        else:
            return 'Unauthorized', 401
        
        return f(current_user, *args, **kwargs)

    return decorated
