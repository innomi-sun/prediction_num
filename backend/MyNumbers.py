import os
import json

import sqlalchemy

class MyNumbers(object):

    def __init__(self, db):

        self.db = db
        self.product_env = os.environ.get('PRODUCT_ENV')

        self.count_in_list = 100
        self.lottery_type_dict = {'loto7': 0, 'loto6': 1, 'miniloto': 2, 'numbers3': 3, 'numbers4': 4}
        
    def get_numbers_list(self, user_id):

        sql = 'SELECT id, user_id, lottery_type, my_numbers, comment FROM my_numbers \
            WHERE user_id = :user_id ORDER BY create_datetime DESC OFFSET 0 LIMIT :count'
        stmt = sqlalchemy.text(sql)
        
        with self.db.connect() as conn:
            his = conn.execute(stmt, user_id=user_id, count=self.count_in_list).fetchall()

        return [dict(r) for r in his]

    def new_numbers(self, lottery_type, user_id, comment, numbers):

        sql = 'INSERT INTO my_numbers(user_id, lottery_type, my_numbers, comment, create_datetime) VALUES (:user_id, :lottery_type, :my_numbers, :comment, current_timestamp)'
        stmt = sqlalchemy.text(sql)
        
        with self.db.connect() as conn:
            his = conn.execute(stmt, user_id=user_id, lottery_type=lottery_type, my_numbers=numbers, comment=comment)

    def edit_numbers(self, my_numbers_id, lottery_type, user_id, comment, numbers):

        sql = 'UPDATE my_numbers SET lottery_type = :lottery_type, my_numbers = :my_numbers, comment = :comment, \
            update_datetime = current_timestamp WHERE id = :my_numbers_id AND user_id = :user_id'
        stmt = sqlalchemy.text(sql)
        
        with self.db.connect() as conn:
            his = conn.execute(stmt, my_numbers_id=my_numbers_id, user_id=user_id, lottery_type=lottery_type, my_numbers=numbers, comment=comment)

    def remove_numbers(self, my_numbers_id, user_id):

        sql = 'DELETE FROM my_numbers WHERE user_id = :user_id AND id = :my_numbers_id'
        stmt = sqlalchemy.text(sql)
        
        with self.db.connect() as conn:
            his = conn.execute(stmt, user_id=user_id, my_numbers_id=my_numbers_id)