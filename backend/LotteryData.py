import os
import datetime
import time
import random
import requests
import sqlalchemy

class LotteryData(object):

    # start_day format: yyyymmdd
    def __init__(self, db, count=20, start_day=datetime.date.today().strftime('%Y%m%d')):

        self.db = db
        self.product_env = os.environ.get('PRODUCT_ENV')

        self.count_request_lottery_net = count
        self.start_day = start_day
        
        self.date_format = 'yyyy/mm/dd'
        self.nexttimes_deadline = [18, 30, 0]

        self.lottery_type_dict = {'loto7': 0, 'loto6': 1, 'miniloto': 2, 'numbers3': 3, 'numbers4': 4}

    def get_lottery_list(self, lottery_type, times=1e5, offset=0, limit=20):

        loto7 = 'SELECT id, to_char(lottery_date, \'' + self.date_format + '\') as lottery_date, times, \
            number1, number2, number3, number4, number5, number6, number7, bonus_1, bonus_2 FROM loto7 \
            WHERE times <= :times ORDER BY times DESC OFFSET :offset LIMIT :limit'

        loto6 = 'SELECT id, to_char(lottery_date, \'' + self.date_format + '\') as lottery_date, times, \
            number1, number2, number3, number4, number5, number6, bonus_1 FROM loto6 \
            WHERE times <= :times ORDER BY times DESC OFFSET :offset LIMIT :limit'

        miniloto = 'SELECT id, to_char(lottery_date, \'' + self.date_format + '\') as lottery_date, times, \
            number1, number2, number3, number4, number5, bonus_1 FROM miniloto \
            WHERE times <= :times ORDER BY times DESC OFFSET :offset LIMIT :limit'

        numbers3 = 'SELECT id, to_char(lottery_date, \'' + self.date_format + '\') as lottery_date, times, \
            number1, number2, number3 FROM numbers3 \
            WHERE times <= :times ORDER BY times DESC OFFSET :offset LIMIT :limit'

        numbers4 = 'SELECT id, to_char(lottery_date, \'' + self.date_format + '\') as lottery_date, times, \
            number1, number2, number3, number4 FROM numbers4 \
            WHERE times <= :times ORDER BY times DESC OFFSET :offset LIMIT :limit'

        sql = [loto7, loto6, miniloto, numbers3, numbers4]
        stmt = sqlalchemy.text(sql[self.lottery_type_dict[lottery_type]])
        
        with self.db.connect() as conn:
            his = conn.execute(stmt, times=times, offset=offset, limit=limit).fetchall()

        return [dict(r) for r in his]

    def get_lottery_max_times(self, lottery_type):

        loto7 = 'SELECT MAX(times) FROM loto7'

        loto6 = 'SELECT MAX(times) FROM loto6'

        miniloto = 'SELECT MAX(times) FROM miniloto'

        numbers3 = 'SELECT MAX(times) FROM numbers3'

        numbers4 = 'SELECT  MAX(times) FROM numbers4'

        sql = [loto7, loto6, miniloto, numbers3, numbers4]
        stmt = sqlalchemy.text(sql[self.lottery_type_dict[lottery_type]])
        with self.db.connect() as conn:
            his = conn.execute(stmt).fetchone()

        return his[0]

    def get_lottery_detail(self, lottery_type, data_id):

        loto7 = 'SELECT id, quantity_1, quantity_2, quantity_3, quantity_4, quantity_5, quantity_6, amount_1, amount_2, amount_3, amount_4, amount_5, amount_6, \
            carry_over FROM loto7 WHERE id = :id'

        loto6 = 'SELECT id, quantity_1, quantity_2, quantity_3, quantity_4, quantity_5, amount_1, amount_2, amount_3, amount_4, amount_5, \
            carry_over FROM loto6 WHERE id = :id'

        miniloto = 'SELECT id, quantity_1, quantity_2, quantity_3, quantity_4, amount_1, amount_2, amount_3, amount_4 \
            FROM miniloto WHERE id = :id'

        numbers3 = 'SELECT id, quantity_straight AS quantity_1, quantity_box AS quantity_2, quantity_set_straight AS quantity_3, \
            quantity_set_box AS quantity_4, quantity_mini AS quantity_5, \
            amount_straight AS amount_1, amount_box AS amount_2, amount_set_straight AS amount_3, amount_set_box AS amount_4, amount_mini AS amount_5 \
            FROM numbers3 WHERE id = :id'

        numbers4 = 'SELECT id, quantity_straight AS quantity_1, quantity_box AS quantity_2, \
            quantity_set_straight AS quantity_3, quantity_set_box AS quantity_4, \
            amount_straight AS amount_1, amount_box AS amount_2, amount_set_straight AS amount_3, amount_set_box AS amount_4 \
            FROM numbers4 WHERE id = :id'

        sql = [loto7, loto6, miniloto, numbers3, numbers4]
        stmt = sqlalchemy.text(sql[self.lottery_type_dict[lottery_type]])
        
        with self.db.connect() as conn:
            his = conn.execute(stmt, id=data_id).fetchone()

        return dict(his)
    
    # update today's data from 宝くじネット
    def new_data_by_lottery_net(self):
        
        target_url = 'https://www.takarakujinet.co.jp/api/search/past_result.php'
        today = self.start_day

        with self.db.connect() as conn:
            # loto7
            r = requests.post(target_url, json={"howmany": self.count_request_lottery_net, "ymd": today, "kuji_type": 4001})
            for item in r.json():
                stmt = sqlalchemy.text("SELECT COUNT(*) FROM loto7 WHERE times =:times")
                his = conn.execute(stmt, times=item['kaigo']).fetchone()

                if his[0] == 0:
                    sql = "INSERT INTO loto7(lottery_date, times, number1, number2, number3, number4, number5, number6, number7, bonus_1, bonus_2, \
                    quantity_1, quantity_2, quantity_3, quantity_4, quantity_5, quantity_6, \
                    amount_1, amount_2, amount_3, amount_4, amount_5, amount_6, carry_over, create_datetime) \
                    VALUES ('{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, current_timestamp)"
                    
                    sql = sql.format(item['chusen_ymd'], item['kaigo'], 
                    item['tousen']['1'], item['tousen']['2'], item['tousen']['3'], item['tousen']['4'], item['tousen']['5'], item['tousen']['6'], item['tousen']['7'], item['tousen']['bonus_1'], item['tousen']['bonus_2'], 
                    item['tousen']['kuchisu_1'], item['tousen']['kuchisu_2'], item['tousen']['kuchisu_3'], item['tousen']['kuchisu_4'], item['tousen']['kuchisu_5'], item['tousen']['kuchisu_6'], 
                    item['tousen']['tousen_kin1'], item['tousen']['tousen_kin2'], item['tousen']['tousen_kin3'], item['tousen']['tousen_kin4'], item['tousen']['tousen_kin5'], item['tousen']['tousen_kin6'], item['tousen']['carry_over'])
                    
                    conn.execute(sql)

            # sleep to avoid to be blocked
            time.sleep(random.randint(30, 100))
            
            # loto6
            r = requests.post(target_url, json={"howmany": self.count_request_lottery_net, "ymd": today, "kuji_type": 4000})
            for item in r.json():
                stmt = sqlalchemy.text("SELECT COUNT(*) FROM loto6 WHERE times =:times")
                his = conn.execute(stmt, times=item['kaigo']).fetchone()

                if his[0] == 0:
                    sql = "INSERT INTO loto6(lottery_date, times, number1, number2, number3, number4, number5, number6, bonus_1, \
                    quantity_1, quantity_2, quantity_3, quantity_4, quantity_5, \
                    amount_1, amount_2, amount_3, amount_4, amount_5, carry_over, create_datetime) \
                    VALUES ('{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, current_timestamp)"

                    sql = sql.format(item['chusen_ymd'], item['kaigo'], 
                    item['tousen']['1'], item['tousen']['2'], item['tousen']['3'], item['tousen']['4'], item['tousen']['5'], item['tousen']['6'], item['tousen']['bonus_1'],
                    item['tousen']['kuchisu_1'], item['tousen']['kuchisu_2'], item['tousen']['kuchisu_3'], item['tousen']['kuchisu_4'], item['tousen']['kuchisu_5'],
                    item['tousen']['tousen_kin1'], item['tousen']['tousen_kin2'], item['tousen']['tousen_kin3'], item['tousen']['tousen_kin4'], item['tousen']['tousen_kin5'], item['tousen']['carry_over'])
                   
                    conn.execute(sql)

            # sleep to avoid to be blocked
            time.sleep(random.randint(30, 100))
            
            # miniloto
            r = requests.post(target_url, json={"howmany": self.count_request_lottery_net, "ymd": today, "kuji_type": 4002})
            for item in r.json():
                stmt = sqlalchemy.text("SELECT COUNT(*) FROM miniloto WHERE times =:times")
                his = conn.execute(stmt, times=item['kaigo']).fetchone()

                if his[0] == 0:
                    sql = "INSERT INTO miniloto(lottery_date, times, number1, number2, number3, number4, number5, bonus_1, \
                    quantity_1, quantity_2, quantity_3, quantity_4, amount_1, amount_2, amount_3, amount_4, create_datetime) \
                    VALUES ('{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, current_timestamp)"
    
                    sql = sql.format(item['chusen_ymd'], item['kaigo'], 
                    item['tousen']['1'], item['tousen']['2'], item['tousen']['3'], item['tousen']['4'], item['tousen']['5'], item['tousen']['bonus_1'],
                    item['tousen']['kuchisu_1'], item['tousen']['kuchisu_2'], item['tousen']['kuchisu_3'], item['tousen']['kuchisu_4'],
                    item['tousen']['tousen_kin1'], item['tousen']['tousen_kin2'], item['tousen']['tousen_kin3'], item['tousen']['tousen_kin4'])
    
                    conn.execute(sql)

            # sleep to avoid to be blocked
            time.sleep(random.randint(30, 100))
            
            # numbers4
            r = requests.post(target_url, json={"howmany": self.count_request_lottery_net, "ymd": today, "kuji_type": 5001})
            for item in r.json():
                stmt = sqlalchemy.text("SELECT COUNT(*) FROM numbers4 WHERE times =:times")
                his = conn.execute(stmt, times=item['kaigo']).fetchone()

                if his[0] == 0:
                    sql = "INSERT INTO numbers4(lottery_date, times, number1, number2, number3, number4, \
                        quantity_straight, quantity_box, quantity_set_straight, quantity_set_box, amount_straight, amount_box, amount_set_straight, amount_set_box, create_datetime) \
                        VALUES ('{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, current_timestamp)"
                    
                    sql = sql.format(item['chusen_ymd'], item['kaigo'], item['tousen']['1'], item['tousen']['2'], item['tousen']['3'], item['tousen']['4'], 
                    item['tousen']['st_kuchisu'], item['tousen']['bx_kuchisu'], item['tousen']['set_st_kuchisu'], item['tousen']['set_bx_kuchisu'], 
                    item['tousen']['st_tousen_kin'], item['tousen']['bx_tousen_kin'], item['tousen']['set_st_tousen_kin'], item['tousen']['set_bx_tousen_kin'])
                    
                    conn.execute(sql)

            # sleep to avoid to be blocked
            time.sleep(random.randint(30, 100))
            
            # numbers3
            r = requests.post(target_url, json={"howmany": self.count_request_lottery_net, "ymd": today, "kuji_type": 5000})
            for item in r.json():
                stmt = sqlalchemy.text("SELECT COUNT(*) FROM numbers3 WHERE times =:times")
                his = conn.execute(stmt, times=item['kaigo']).fetchone()

                if his[0] == 0:
                    sql = "INSERT INTO numbers3(lottery_date, times, number1, number2, number3, \
                    quantity_straight, quantity_box, quantity_set_straight, quantity_set_box, quantity_mini, \
                    amount_straight, amount_box,amount_set_straight, amount_set_box, amount_mini, create_datetime) \
                    VALUES ('{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, current_timestamp)"
                    
                    sql = sql.format(item['chusen_ymd'], item['kaigo'], 
                    item['tousen']['1'], item['tousen']['2'], item['tousen']['3'], item['tousen']['st_kuchisu'], item['tousen']['bx_kuchisu'], item['tousen']['set_st_kuchisu'], 
                    item['tousen']['set_bx_kuchisu'], item['tousen']['mini_kuchisu'], item['tousen']['st_tousen_kin'], item['tousen']['bx_tousen_kin'], 
                    item['tousen']['set_st_tousen_kin'], item['tousen']['set_bx_tousen_kin'], item['tousen']['mini_tousen_kin'])

                    conn.execute(sql)

    def get_next_times_info(self, lottery_type):
        
        now = datetime.datetime.now()
        
        nd = self.nexttimes_deadline
        deadline_time = now.replace(hour=nd[0], minute=nd[1], second=nd[2], microsecond=0)
        
        if lottery_type in ('numbers3', 'numbers4'):
            offset = 8 - now.isoweekday() if now.isoweekday() in set((5, 6)) else 1
            if now > deadline_time:
                offset += 1 

        if lottery_type == 'loto7':
            offset = 5 - now.isoweekday() + now.isoweekday() // 6 * 7

        if lottery_type == 'loto6':
            offset_list = (0,2,1,0,3,2,1)
            offset = offset_list[now.isoweekday() - 1]

        if lottery_type == 'miniloto':
            offset_list = (1,0,6,5,4,3,2)
            offset = offset_list[now.isoweekday() - 1]

        next_times = self.get_lottery_max_times(lottery_type) + 1
        next_date = (now + datetime.timedelta(days=offset)).strftime('%Y/%m/%d')

        return {'next_times': next_times, 'next_date': next_date}