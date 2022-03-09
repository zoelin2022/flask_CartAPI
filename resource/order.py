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
    
class Order(MethodResource):
    @doc(description='Create Product.', tags=['新增訂單']) # 頁面的標題與分類
    @use_kwargs(router_model.ProductPostOrderSchema, location="form") # 頁面input欄位
    @marshal_with(router_model.CommonResponse, code=201) # Response
    
################ POST 新增訂單 ################ 
    def post(self, **kwargs):
        product_name = kwargs["product_name"]
        db, cursor = db_init()
        sql = f"SELECT * FROM test.product WHERE product_name = '{product_name}';"
        result = cursor.execute(sql)
        products = cursor.fetchall()
        
        # 檢查商品存不存在
        if result == 0:
            return util.failure({"message": "無此商品"})
        else:
            # 購買數量 > 商品數量 失敗的訊息設定
            if kwargs["amount"] > products[0]["amount"]:
                return util.failure({"message": f"庫存不足！商品剩餘數量: {products[0]['amount']}件"})
            else:
                # 庫存充足可購買的話，就將訂單寫入db
                total = kwargs["amount"] * products[0]["price"]
            
                sql2 = """

                INSERT INTO `test`.`orders` (`name`,`product_name`,`amount`,`total`)
                VALUES ('{}','{}','{}','{}');

                """.format(
                    kwargs["name"],kwargs["product_name"], kwargs["amount"], total)
                result = cursor.execute(sql2)
                
                # 將商品庫存更新 (庫存數量-購買數量)
                new_amount = products[0]["amount"] - kwargs["amount"]
                sql3 = """

                UPDATE `test`.`product` SET amount='{}' WHERE product_name='{}';

                """.format(new_amount , kwargs["product_name"])
                result = cursor.execute(sql3)
                db.commit()  # 測試,將執行成功的結果存進database裡
                db.close()
                msg = {
                    'name': kwargs['name'],
                    'product_name': kwargs['product_name'],
                    'price': products[0]["price"],
                    'amount': kwargs['amount'],
                    'total': total,
                }
                return util.success(msg)
    
    ################ Get 查詢訂單 ################ 
    @doc(description='Get Product info.', tags=['查詢訂單']) # 頁面的標題與分類
    @use_kwargs(router_model.OrderGetSchema, location="query") # 頁面input欄位
    @marshal_with(router_model.GetResponse, code=200) # Response(檢查格式)
    #@jwt_required() # 求client一定要提交token並驗證
    def get(self, **kwargs):
        db, cursor = db_init()
        name = kwargs.get("name") # 判斷是不是空值 None
        if name is not None:
            sql = f"SELECT * FROM test.orders WHERE name = '{name}';"         
        else:
            sql = f"SELECT * FROM test.orders ;" 
            
        result = cursor.execute(sql)
        # 檢查商品存不存在
        if result == 0:
            return util.failure({"message": "查無紀錄"})
        all_result = cursor.fetchall()
        db.close()
        total = 0
        for i in range(len(all_result)) : total += all_result[i]["total"]
        all_result.append({"累計消費金額":total})
        return util.success(all_result)
    
################ patch 更新訂單 ################

    @doc(description='Update User info.', tags=['更新訂單']) # 頁面的標題與分類
    @use_kwargs(router_model.OrderPatchSchema, location="form") # 頁面input欄位
    @marshal_with(router_model.CommonResponse, code=201) # Response(檢查格式)
    def patch(self, **kwargs):
        db, cursor = db_init()
        # 撈出原始訂單
        id = kwargs["id"]
        sql = f"SELECT * FROM test.orders WHERE id = '{id}';"
        result = cursor.execute(sql)
        old_orders = cursor.fetchall()
        if result == 0:
            return util.failure({"message": "無此訂單"})
        sql2 = f"SELECT * FROM test.product WHERE product_name = '{kwargs['product_name']}';"
        result = cursor.execute(sql2)
        products = cursor.fetchall()
        
        # 檢查商品存不存在
        if result == 0:
            return util.failure({"message": "無此商品"})
        
        if kwargs["product_name"] != old_orders[0]["product_name"]:
        # 如果改買另一項商品
            if kwargs["amount"] > products[0]["amount"]:
                return util.failure({"message": f"庫存不足！商品剩餘數量: {products[0]['amount']}件"})
            else:
                # 庫存充足可購買的話，就將訂單寫入db
                total = kwargs["amount"] * products[0]["price"]
                sql2 = """

                UPDATE `test`.`orders` 
                SET 
                name='{}',
                product_name='{}',
                amount='{}',
                total='{}'
                WHERE id='{}';

                 """.format(
                    kwargs["name"],kwargs["product_name"], kwargs["amount"],total,id)
                cursor.execute(sql2)
                
                # 將B商品庫存更新 (庫存數量-購買數量)
                new_amount = products[0]["amount"] - kwargs["amount"] 
                sql3 = """

                UPDATE `test`.`product` SET amount='{}' WHERE product_name='{}';

                """.format(new_amount , kwargs["product_name"])
                cursor.execute(sql3)
                
                # 將A商品庫存更新 (庫存數量+原購買數量)
                # 找出A商品原庫存數量
                sql4 = f"SELECT * FROM test.product WHERE product_name = '{old_orders[0]['product_name']}';"
                cursor.execute(sql4)
                old_products = cursor.fetchall()
                # 庫存數量＋原本購買的數量
                old_amount = old_products[0]["amount"] + old_orders[0]["amount"]
                sql5 = """

                UPDATE `test`.`product` 
                SET amount='{}' 
                WHERE product_name='{}';

                """.format(old_amount , old_orders[0]['product_name'])
                cursor.execute(sql5)
        else:
            # 商品一樣的情況，只有修改數量的話
            # 減少就更新訂單，加回庫存
            
            if kwargs["amount"] < old_orders[0]["amount"]:
            
                # 將訂單更新的數量更新進db
                total = kwargs["amount"] * products[0]["price"]
                sql2 = """

                UPDATE `test`.`orders` 
                SET 
                name='{}',
                product_name='{}',
                amount='{}',
                total='{}'
                WHERE id='{}';

                    """.format(
                    kwargs["name"],kwargs["product_name"], kwargs["amount"],total,id)
                cursor.execute(sql2)
                # 將舊訂單的數量加回庫存
                re_amount = old_orders[0]["amount"] - kwargs["amount"] + products[0]["amount"]
                sql = """

                UPDATE `test`.`product` 
                SET amount='{}' 
                WHERE product_name='{}';

                """.format(re_amount , old_orders[0]['product_name'])
                cursor.execute(sql)
                
            # 增加就更新訂單，扣庫存
            else:
                # 檢查庫存是否充足
                if kwargs["amount"] - old_orders[0]["amount"] > products[0]["amount"]:
                    return util.failure({"message": f"庫存不足！商品剩餘數量: {products[0]['amount']}件"})
                # 將訂單更新的數量更新進db
                total = kwargs["amount"] * products[0]["price"]
                sql2 = """

                UPDATE `test`.`orders` 
                SET 
                name='{}',
                product_name='{}',
                amount='{}',
                total='{}'
                WHERE id='{}';

                    """.format(
                    kwargs["name"],kwargs["product_name"], kwargs["amount"],total,id)
                cursor.execute(sql2)
                # 扣庫存
                plus_amount = products[0]["amount"]-(kwargs["amount"] - old_orders[0]["amount"])
                sql = """

                UPDATE `test`.`product` 
                SET amount='{}' 
                WHERE product_name='{}';

                """.format(plus_amount , old_orders[0]['product_name'])
                cursor.execute(sql)
        db.commit()
        db.close()
        return util.success()
        

    ################ Delete 刪除訂單 ################
    @doc(description='Delete Product info.', tags=['刪除訂單']) # 頁面的標題與分類
    @use_kwargs(router_model.OrderDleteSchema, location="form") # 頁面input欄位
    @marshal_with(None, code=204) # Response(檢查格式)
    def delete(self, id):
        db, cursor = db_init()
        
        sql = f"SELECT * FROM test.orders WHERE id = '{id}';"
        check = cursor.execute(sql)
        orders = cursor.fetchall()
        #檢查訂單存不存在
        if check == 0:
            return util.failure({"message": "無此訂單"})
        else:
            #1.撈出商品資料
            sql1 = f"SELECT * FROM test.product WHERE product_name = '{orders[0]['product_name']}';"
            cursor.execute(sql1)
            product = cursor.fetchall()
            #2.把商品加回庫存
            add_amount = product[0]["amount"] + orders[0]["amount"]
            sql2 = """

            UPDATE `test`.`product` 
            SET amount='{}' 
            WHERE product_name='{}';

            """.format(add_amount , orders[0]['product_name'])
            cursor.execute(sql2)
            #3.刪除訂單
            sql3 = f"DELETE FROM `test`.`orders` WHERE id = '{id}';"
            cursor.execute(sql3)
            
            db.commit()
            db.close()
            return util.success()
        
