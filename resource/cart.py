import pymysql
from flask_apispec import MethodResource, marshal_with, doc, use_kwargs
import util as util
from . import router_model
from flask_jwt_extended import create_access_token, jwt_required # 產生token的套件
from datetime import timedelta
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
    
class Cart(MethodResource):
    @doc(description='新增商品至購物車', tags=['購物車']) # 頁面的標題與分類
    @use_kwargs(router_model.CartPostSchema, location="form") # 頁面input欄位
    @marshal_with(router_model.CommonResponse, code=201) # Response
    @jwt_required() # 求client一定要提交token並驗證
################ POST 新增商品至購物車 ################ 
# 檢查商品存不存在
# 檢查庫存是否充足
# 如果商品已存在購物車，就更新購買數量即可
# 將商品庫存同步更新

    def post(self, **kwargs):
        product_name = kwargs["product_name"]
        name = kwargs["name"]
        db, cursor = db_init()      
        # 檢查db有無此商品
        sql = f"SELECT * FROM test.product WHERE product_name = '{product_name}';"
        result = cursor.execute(sql)
        products = cursor.fetchall()
        if result == 0:
            return util.failure({"message": "無此商品"})
        else:
            # 購買數量 > 商品數量 失敗的訊息設定
            if kwargs["amount"] > products[0]["amount"]:
                return util.failure({"message": f"庫存不足！商品剩餘數量: {products[0]['amount']}件"})
            else:
                
                # 檢查購物車是否已存在此商品
                sql = f"SELECT * FROM test.cart WHERE name = '{name}' AND product_name = '{product_name}';"
                result = cursor.execute(sql)
                old_products = cursor.fetchall()

                if result == 1:
                    # 如果已存在，只需更新此商品購買數量跟金額
                    cart_amount = old_products[0]["amount"] + kwargs["amount"]
                    total = cart_amount * products[0]["price"]
                    sql3 = """

                    UPDATE `test`.`cart` SET amount='{}', total='{}' WHERE product_name='{}';
                    """.format(cart_amount ,total, kwargs["product_name"])
                    result = cursor.execute(sql3)
                    
                    # 將商品庫存更新 (庫存數量-購物車加入數量)
                    new_amount = products[0]["amount"] - kwargs["amount"]
                    sql4 = """

                    UPDATE `test`.`product` SET amount='{}' WHERE product_name='{}';

                    """.format(new_amount , kwargs["product_name"])
                    result = cursor.execute(sql4)
                else:
                    # 庫存充足可購買，且商品不重複，就將新的購物車寫入db 
                    total = kwargs["amount"] * products[0]["price"]               
                    sql2 = """

                    INSERT INTO `test`.`cart` (`name`,`product_name`,`amount`,`total`)
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
                db.commit()
                db.close()
                total = kwargs["amount"] * products[0]["price"]
                msg = {
                    'name': kwargs['name'],
                    'product_name': kwargs['product_name'],
                    'price': products[0]["price"],
                    'amount': kwargs['amount'],
                    'total': total,
                }
                return util.success(msg)
    
    ################ Get 查詢購物車 ################ 
    # 檢查購物車存不存在
    # 查詢後自動合計總金額
    @doc(description='查詢購物車內容', tags=['購物車']) # 頁面的標題與分類
    @use_kwargs(router_model.CartGetSchema, location="query") # 頁面input欄位
    @marshal_with(router_model.GetResponse, code=200) # Response(檢查格式)
    @jwt_required() # 求client一定要提交token並驗證
    def get(self, name):
        db, cursor = db_init()
        sql = f"SELECT `product_name`,`amount`,`total` FROM test.cart WHERE name = '{name}';"         
        result = cursor.execute(sql)
        # 檢查購物車存不存在
        if result == 0:
            return util.failure({"message": "查無紀錄"})
        all_result = cursor.fetchall()
        db.close()
        total = 0
        for i in range(len(all_result)) : total += all_result[i]["total"]
        all_result.append({"購物車總金額":total})
        return util.success(all_result)
    
################ patch 更新購物車內容 ################
# 檢查要修改的商品存不存在於購物車
# 數量減少就更新購物車，加回庫存
# 數量增加的話，先檢查看庫存是否充足再更新購物車，扣掉庫存
# 輸入0代表刪除商品，數量加回庫存
    @doc(description='修改購物車商品內容\n想刪除商品，數量請輸入0', tags=['購物車']) # 頁面的標題與分類
    @use_kwargs(router_model.CartPatchSchema, location="form") # 頁面input欄位
    @marshal_with(router_model.CommonResponse, code=201) # Response(檢查格式)
    @jwt_required() # 求client一定要提交token並驗證
    def patch(self, **kwargs):
        db, cursor = db_init()
        # 撈出購物車的紀錄
        name = kwargs["name"]
        product_name = kwargs['product_name']
        sql = f"SELECT * FROM test.cart WHERE name = '{name}' AND product_name = '{product_name}';"
        result = cursor.execute(sql)
        old_cart = cursor.fetchall()
        if result == 0:
            return util.failure({"message": "查無紀錄"})
    
        # 撈出修改的商品資料
        sql2 = f"SELECT * FROM test.product WHERE product_name = '{product_name}';"
        result = cursor.execute(sql2)
        products = cursor.fetchall()
        new_amount = kwargs["amount"]
        old_amount = old_cart[0]["amount"]
        
        # 修改數量＝0 代表刪除此項商品
        if new_amount == 0:
            # 刪除購物車
            sql = f"DELETE FROM `test`.`cart` WHERE name = '{name}' AND product_name = '{product_name}';"
            cursor.execute(sql)
            
            # 將舊購物車的數量加回庫存
            re_amount = old_amount + products[0]["amount"]
            sql = "UPDATE `test`.`product` SET amount='{}' WHERE product_name='{}';".format(re_amount , old_cart[0]['product_name'])
            cursor.execute(sql)
        
        # 數量減少就更新購物車，加回庫存
        elif new_amount < old_amount:
            
            # 將購物車更新的數量更新進db
            update_total = kwargs["amount"] * products[0]["price"]
            update_sql = """
            UPDATE `test`.`cart` 
            SET amount='{}',total='{}'
            WHERE name='{}' AND product_name='{}';
            """.format(kwargs["amount"], update_total, name, kwargs["product_name"])
            cursor.execute(update_sql)
            
            # 將舊購物車的數量加回庫存
            re_amount = old_amount - new_amount + products[0]["amount"]
            sql = "UPDATE `test`.`product` SET amount='{}' WHERE product_name='{}';".format(re_amount , old_cart[0]['product_name'])
            cursor.execute(sql)
            
        # 增加就更新購物車，扣掉庫存
        else:
            # 檢查庫存是否充足
            new_amount = kwargs["amount"]
            old_amount = old_cart[0]["amount"]
            if (new_amount - old_amount) > products[0]["amount"]:
                return util.failure({"message": f"庫存不足！商品剩餘數量: {products[0]['amount']}件"})
            
            # 將購物車更新的數量更新進db
            update_total = kwargs["amount"] * products[0]["price"]
            update_sql = """
            UPDATE `test`.`cart` 
            SET amount='{}',total='{}'
            WHERE name='{}' AND product_name='{}';
            """.format(kwargs["amount"], update_total, name, kwargs["product_name"])
            cursor.execute(update_sql)
            
            # 扣掉庫存
            plus_amount = products[0]["amount"]-(new_amount - old_amount)
            sql = "UPDATE `test`.`product` SET amount='{}' WHERE product_name='{}';".format(plus_amount , old_cart[0]['product_name'])
            cursor.execute(sql)
        db.commit()
        db.close()
        return util.success()
        
################ Delete 刪除購物車 ################
# 檢查購物車紀錄存不存在
# 刪除購物車紀錄，同時把商品數量都更新加回庫存
    @doc(description='刪除購物車', tags=['購物車']) # 頁面的標題與分類
    @use_kwargs(router_model.CartDleteSchema, location="form") # 頁面input欄位
    @marshal_with(None, code=204) # Response(檢查格式)
    @jwt_required() # 求client一定要提交token並驗證
    def delete(self, name):
        db, cursor = db_init()
        
        sql = f"SELECT * FROM test.cart WHERE name = '{name}';"
        check = cursor.execute(sql)
        cart = cursor.fetchall()
        # 檢查購物車存不存在
        if check == 0:
            return util.failure({"message": "此購物車不存在"})
        else:
            # 1.撈出訂單每一項商品資料
            for item in cart:
                sql1 = f"SELECT * FROM test.product WHERE product_name = '{item['product_name']}';"
                cursor.execute(sql1)
                product = cursor.fetchall()
                # 2.逐一把商品數量加回庫存
                add_amount = product[0]["amount"] + item["amount"]
                sql2 = """

                UPDATE `test`.`product` 
                SET amount='{}' 
                WHERE product_name='{}';

                """.format(add_amount , item['product_name'])
                cursor.execute(sql2)
            # 3.刪除購物車
            sql3 = f"DELETE FROM `test`.`cart` WHERE name = '{name}';"
            cursor.execute(sql3)
        db.commit()
        db.close()
        return util.success()
        