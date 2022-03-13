import pymysql
from flask_apispec import MethodResource, marshal_with, doc, use_kwargs
import util as util
from . import router_model
from flask_jwt_extended import create_access_token, jwt_required # 產生token的套件
from datetime import timedelta
import datetime
# 使用 pymysql 連接 db
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

# 設定 token
def get_access_token(account):
    token = create_access_token(
        identity={"account": account}, # 一定要加，規定用dict形式
        expires_delta=timedelta(days=1) # 設定token時效
    )
    return token
    
################ POST 購物車結帳(新增訂單) ################ 
# 檢查購物車存不存在
# 結帳後，將購物車資料刪除
# 自動生成訂單編號提供查詢

class Order_new(MethodResource):
    @doc(description='購物車結帳(新增訂單)', tags=['訂單']) # 頁面的標題與分類
    @use_kwargs(router_model.OrderNewPostOrderSchema, location="form") # 頁面input欄位
    @marshal_with(router_model.CommonResponse, code=201) # Response
    @jwt_required() # 求client一定要提交token並驗證
    def post(self, name):
        db, cursor = db_init()
        #1.撈出購物車
        sql1 = f"SELECT * FROM test.cart WHERE name = '{name}';"
        cursor.execute(sql1)
        products = cursor.fetchall()
        order_no = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        total = 0
        #2.新增訂單
        for product in products:
            total += product["total"]
            sql2 = """
                INSERT INTO `test`.`orders` (`order_no`,`name`,`product_name`,`amount`,`total`)
                VALUES ('{}','{}','{}',{},{});
                """.format(
                    order_no, name, product["product_name"], product["amount"], product["total"])
            cursor.execute(sql2)
        sql3 = f"SELECT `product_name`,`amount`,`total` FROM test.orders WHERE order_no = '{order_no}';"
        cursor.execute(sql3)
        item = cursor.fetchall()
        msg = [{
                        '訂單編號': order_no,
                        '訂購人': products[0]['name'],
                        '商品明細': item,
                        '訂單金額': total,
                    }]

        # 3.刪除購物車
        sql4 = f"DELETE FROM `test`.`cart` WHERE name = '{name}';"
        cursor.execute(sql4)
        db.commit()
        db.close()
        return util.success(msg)
    
    ################ Get 查詢訂單 ################ 
# 檢查訂單存不存在
    @doc(description='查詢訂單', tags=['訂單']) # 頁面的標題與分類
    @use_kwargs(router_model.OrderNewGetSchema, location="query") # 頁面input欄位
    @marshal_with(router_model.GetResponse, code=200) # Response(檢查格式)
    @jwt_required() # 求client一定要提交token並驗證
    def get(self, **kwargs):
        db, cursor = db_init()
        order_no = kwargs["order_no"]
        # 撈出訂單明細
        sql = f"SELECT `product_name`,`amount`,`total` FROM test.orders WHERE order_no = '{order_no}';"      
        result = cursor.execute(sql)
        # 檢查訂單存不存在
        if result == 0:
            return util.failure({"message": "查無資料"})
        content = cursor.fetchall()
        query = [i for i in content]
        # 訂購人
        sql2 = f"SELECT `name` FROM test.orders WHERE order_no = '{order_no}';"      
        cursor.execute(sql2)
        name = cursor.fetchall()
        # 訂單金額
        total = 0
        for i in content:
            total += i["total"]
        msg = [{
                '訂單編號': order_no,
                '訂購人': name[0]["name"],
                '商品明細': query,
                '訂單金額': total,
            }]
        db.commit()
        db.close()
        return util.success(msg)

    ################ Delete 刪除訂單 ################
# 檢查訂單存不存在
# 刪除訂單，同時把商品數量都更新加回庫存
    @doc(description='刪除訂單', tags=['訂單']) # 頁面的標題與分類
    @use_kwargs(router_model.OrderNewDleteSchema, location="form") # 頁面input欄位
    @marshal_with(None, code=204) # Response(檢查格式)
    @jwt_required() # 求client一定要提交token並驗證
    def delete(self, order_no):
        db, cursor = db_init()
        # 撈出訂單資料
        sql = f"SELECT * FROM test.orders WHERE order_no = '{order_no}';"
        check = cursor.execute(sql)
        myorders = cursor.fetchall()
        #檢查訂單存不存在
        if check == 0:
            return util.failure({"message": "無此訂單"})
        else:
        # 1.撈出訂單每一項商品資料
            for orders in myorders:
                sql1 = f"SELECT * FROM test.product WHERE product_name = '{orders['product_name']}';"
                cursor.execute(sql1)
                product = cursor.fetchall()
                # 2.把商品加回庫存
                add_amount = product[0]["amount"] + orders["amount"]
                sql2 = """

                UPDATE `test`.`product` 
                SET amount='{}' 
                WHERE product_name='{}';

                """.format(add_amount , orders['product_name'])
                cursor.execute(sql2)
            # 3.刪除訂單
            sql3 = f"DELETE FROM `test`.`orders` WHERE order_no = '{order_no}';"
            cursor.execute(sql3)
            db.commit()
            db.close()
            return util.success()
        