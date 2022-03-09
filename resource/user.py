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

def get_access_token(account):
    token = create_access_token(
        identity={"account": account}, # 一定要加，並且以dict形式
        expires_delta=timedelta(days=1) # 設定token時效
    )
    return token
    
####### API Action #########

    
############################## User 註冊帳戶 ##################################   
class User(MethodResource):
# User POST
    @doc(description='Create User.', tags=['註冊帳戶']) # 頁面的標題與分類
    @use_kwargs(router_model.UserPostSchema, location="form") # 頁面input欄位
    @marshal_with(router_model.CommonResponse, code=201) # Response(檢查格式)
    def post(self, **kwargs):
        db, cursor = db_init()
        
        # 檢查用戶是否已存在
        sql = f"SELECT * FROM test.member WHERE account = '{kwargs['account']}';"
        check = cursor.execute(sql)
        if check == 0:
            # 不存在就新增用戶資料
            user = {
            'name': kwargs['name'],
            'account': kwargs['account'],
            'password': kwargs['password'],
            'gender': kwargs['gender'],
            'birth': kwargs.get('birth') or '1900-01-01',
            'note': kwargs.get('note'),
            }

            sql = """

            INSERT INTO `test`.`member` (`name`,`gender`,`account`,`password`,`birth`,`note`)
            VALUES ('{}','{}','{}','{}','{}','{}');

            """.format(
                user['name'], user['gender'], user['account'], user['password'], user['birth'], user['note'])
        
            cursor.execute(sql)
            db.commit()  # 測試,將執行成功的結果存進database裡
            db.close()   
            return util.success() # 透過util.py檢查資料並把資料轉成dict再return      
        else:
            return util.failure({"message": "該帳號已註冊！"})
            

############################## Login 登入帳戶 ##################################  
class Login(MethodResource):
    @doc(description='User Login', tags=['登入帳戶']) # 頁面的標題與分類
    @use_kwargs(router_model.LoginSchema, location="form") # 頁面input欄位
    @marshal_with(router_model.GetResponse, code=200) # Response(格式檢查)
    def post(self, **kwargs):
        db, cursor = db_init()
        account, password = kwargs["account"], kwargs["password"]
        sql = f"SELECT * FROM test.member WHERE account = '{account}' AND password = '{password}';"
        cursor.execute(sql)
        user = cursor.fetchall()
        db.close()

        if user != (): # 如果用戶存在就建立token
            token = get_access_token(account)
            data = [{
                "message": f"Welcome back {user[0]['name']}",
                "token": token
                }]
            return util.success(data)
        
        return util.failure({"message":"Account or password is wrong"})


