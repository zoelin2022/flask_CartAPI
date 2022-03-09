import pymysql
from flask_apispec import MethodResource, marshal_with, doc, use_kwargs
import util as util
from . import router_model
from flask_jwt_extended import create_access_token, jwt_required # 產生token的套件
from datetime import timedelta


def db_init():
    db = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        port=8889,
        db='test'
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return db, cursor

def get():
    db, cursor = db_init()
    id = 12
    sql = f"SELECT * FROM test.orders WHERE id = '{id}';"
    result = cursor.execute(sql)
    old_orders = cursor.fetchall()
    print(result)
    print(old_orders)

get()
