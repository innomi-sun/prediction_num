import os
import json
import time
# import requests
import logging
import yaml

from easydict import EasyDict as edict
from flask import Flask, session, render_template, jsonify, request, current_app
from flask_cors import CORS
import redis
import jwt

import postgresDB as postgresDB
from LotteryData import LotteryData
from MyNumbers import MyNumbers
from access_token import check_access_token
import bp_auth_handler
from prediction.PredictNumbers import PredictNumbers

# $env:FLASK_APP = "./app.py";$env:FLASK_ENV="development";flask run --cert=adhoc --host=0.0.0.0 --port=5010
app = Flask(__name__, static_folder = "../static/spa")

# logging.getLogger('flask_cors').level = logging.DEBUG
# 2020-07-15 04:40:48,151 - /srv/main.py[line:42] - WARNING: main.py is running.
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger('main')

@app.route('/api/test_resource', methods=['GET', 'POST'])
# @check_access_token
def test_resource():
    # print(session['refreshToken'])
    return 'test resource page'

@app.route('/api/lottery_list/<lottery_type>/<times>', methods=['GET'])
def lottery_list(lottery_type, times):
    data_list = lottery.get_lottery_list(lottery_type, times)
    return jsonify(data_list)

# Get last lottery data
@app.route('/api/lottery_list/<lottery_type>', methods=['GET'])
@app.route('/api/lottery_list_last/<lottery_type>', methods=['GET'])
# @auth.login_required
def lottery_list_last(lottery_type):
    # set times 1e5 to get last data
    times = lottery.get_lottery_max_times(lottery_type)
    data_list = lottery.get_lottery_list(lottery_type, times)
    return jsonify(data_list)

@app.route('/api/lottery_detail/<lottery_type>/<data_id>', methods=['GET'])
# @auth.login_required
def lottery_detail(lottery_type, data_id):

    detail = lottery.get_lottery_detail(lottery_type, data_id)
    return jsonify(detail)

@app.route('/api/my_numbers', methods=['POST'])
@check_access_token
def new_numbers(user):
    data = request.get_json()
    user_id = user['user_id']
    if not data['my_numbers_id']:
        data_list = my_num.get_numbers_list(user_id)
        if len(data_list) >= current_app.config["MAX_MYLOTO_COUNT_PAID_LEVEL1"]:
            return 'Forbidden', 403
        
        my_num.new_numbers(data['lottery_type'], user_id, data['comment'], data['numbers'])
        
    else:
        my_num.edit_numbers(data['my_numbers_id'], data['lottery_type'], user_id, data['comment'], data['numbers'])

    return jsonify({})

@app.route('/api/my_numbers', methods=['DELETE'])
@check_access_token
def remove_numbers(user):
    data = request.get_json()
    my_num.remove_numbers(data['my_numbers_id'], user['user_id'])
    return jsonify({})

@app.route('/api/my_numbers_list', methods=['GET'])
@check_access_token
def my_numbers_list(user):
    data_list = my_num.get_numbers_list(user['user_id'])
    return jsonify(data_list)

@app.route('/api/ai_numbers', methods=['GET'])
@check_access_token
def ai_numbers(user):
    result = []
    for key in ['loto7', 'loto6', 'miniloto', 'numbers3', 'numbers4']:

        data = lottery.get_lottery_list(lottery_type=key, limit=64)
        next_info = lottery.get_next_times_info(key)
        predict_num = predictNumbers.predict(data, key)

        next_info['lottery_type'] = key
        next_info['predict_num'] = predict_num
        result.append(next_info)

    # [{lottery_type: '', next_times: '', next_date: '', predict_num: ''},
    # ...
    # ]
    return jsonify(result)

@app.route('/api/sta_numbers', methods=['GET'])
@check_access_token
def sta_numbers(user):

    result = []
    for key in ['loto7', 'loto6', 'miniloto', 'numbers3', 'numbers4']:

        data = lottery.get_lottery_list(lottery_type=key, limit=1000)
        next_info = {}
        predict_num = predictNumbers.statistics_predict(data, key)

        next_info['lottery_type'] = key
        next_info['predict_num'] = predict_num
        result.append(next_info)

    # [{lottery_type: '', next_times: '', next_date: '', predict_num: ''},
    # ...
    # ]
    return jsonify(result)

# @app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        # html = requests.get('http://localhost:8080/{}'.format(path)).text
        html = 'No Contents'
        return html
    return render_template("index.html")

@app.route('/robots.txt')
def static_from_root():
    return render_template("robots.txt")


def setup(app):
    # registe the auth handler blueprint
    app.register_blueprint(bp_auth_handler.bp)
    # dev environ
    if app.debug:
        with open('configs/app_dev.yaml', 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        config = edict(config)
        cors = CORS(app, resources={
            r"/api/*": {"origins": "https://mytest.loto:8080"}
        })
    else:
        with open('configs/app.yaml', 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        config = edict(config)

    os.environ['DB_HOST'] = config.DATABASE.DB_HOST
    os.environ['DB_USER'] = config.DATABASE.DB_USER
    os.environ['DB_PASS'] = config.DATABASE.DB_PASS
    os.environ['DB_NAME'] = config.DATABASE.DB_NAME

    app.config.from_mapping(config.FLASK_APP)
    app.config['AUTH'] = config.AUTH
    
    print(app.config)
setup(app)

db = postgresDB.init_connection_engine()
lottery = LotteryData(db)
my_num = MyNumbers(db)
predictNumbers = PredictNumbers()
    
if __name__ == '__main__':
    # print(app.config)
    # app.run()
    app.run(debug=True, port=app.config['PORT'], ssl_context='adhoc', host='0.0.0.0')


