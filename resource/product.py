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

class Product(MethodResource):
    
    # Get 查詢商品
    @doc(description='Get Product info.', tags=['查詢商品']) # 頁面的標題與分類
    @use_kwargs(router_model.ProductGetSchema, location="query") # 頁面input欄位
    @marshal_with(router_model.GetResponse, code=200) # Response(檢查格式)
    #@jwt_required() # 求client一定要提交token並驗證
    def get(self, **kwargs):
        db, cursor = db_init()
        product_name = kwargs.get("name") # 判斷是不是空值 None
        if product_name is not None:
            sql = f"SELECT * FROM test.product WHERE product_name = '{product_name}';"         
        else:
            sql = f"SELECT * FROM test.product ;" 
        
        result = cursor.execute(sql)
        # 檢查商品存不存在
        if result == 0:
            return util.failure({"message": "無此商品"})
        msg = cursor.fetchall()
        db.close()
        return util.success(msg)
    
    # POST 新增商品
    @doc(description='Create Product.', tags=['新增商品']) # 頁面的標題與分類
    @use_kwargs(router_model.ProductPostSchema, location="form") # 頁面input欄位
    @marshal_with(router_model.CommonResponse, code=201) # Response(檢查格式)
    def post(self, **kwargs):
        db, cursor = db_init()
        # 檢查商品是否已存在
        name = kwargs["product_name"]
        sql = f"SELECT * FROM test.product WHERE product_name = '{name}';"
        check = cursor.execute(sql)
        if check == 0:

            sql = """

            INSERT INTO `test`.`product` (`product_name`,`price`,`amount`)
            VALUES ('{}','{}','{}');

            """.format(
                kwargs['product_name'], kwargs['price'], kwargs['amount'])
            result = cursor.execute(sql)
            db.commit()  # 測試,將執行成功的結果存進database裡
            db.close()
            return util.success()
        else:
            return util.failure({"message": "該商品資料已存在"})

    
    # patch 更新商品
    @doc(description='Update User info.', tags=['更新商品']) # 頁面的標題與分類
    @use_kwargs(router_model.ProductPatchSchema, location="form") # 頁面input欄位
    @marshal_with(router_model.CommonResponse, code=201) # Response(檢查格式)
    def patch(self, **kwargs):
        db, cursor = db_init()
        
        user = {
            'product_name': kwargs['product_name'],
            'price': kwargs['price'],
            'amount': kwargs['amount'],
        }

        query = []
        for key, value in user.items():
            if value is not None:
                query.append(f"{key} = '{value}'")
        query = ",".join(query)

        sql = """
            UPDATE `test`.`product`
            SET {}
            WHERE product_name= '{}';
        """.format(query, kwargs['product_name'])

        result = cursor.execute(sql)
        db.commit()
        db.close()
        # 檢查商品存不存在
        if result == 0:
            return util.failure({"message": "無此商品"})

        return util.success()

    # Delete 刪除商品
    @doc(description='Delete Product info.', tags=['刪除商品']) # 頁面的標題與分類
    @use_kwargs(router_model.ProductDleteSchema, location="form") # 頁面input欄位
    @marshal_with(None, code=204) # Response(檢查格式)
    def delete(self, name):
        db, cursor = db_init()
        sql = f"DELETE FROM `test`.`product` WHERE product_name = '{name}';"
        result = cursor.execute(sql)
        db.commit()
        db.close()
        # 檢查商品存不存在
        if result == 0:
            return util.failure({"message": "無此商品"})
        return util.success()
    