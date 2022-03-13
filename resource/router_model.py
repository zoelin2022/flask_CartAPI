# 引入 marshmallow 格式檢查的套件
from marshmallow import Schema, fields, validate

# Get 查詢商品
class ProductGetSchema(Schema):
    name = fields.Str(example="string")

# Post 新增商品
class ProductPostSchema(Schema):
    product_name = fields.Str(doc="product_name", example="string", required=True)
    price = fields.Int(doc="'price", example="string", required=True)
    amount = fields.Int(doc="amount", example="string", required=True)
    
# Patch 更新商品
class ProductPatchSchema(Schema):
    product_name = fields.Str(doc="product_name", example="string", required=True)
    price = fields.Int(doc="'price", example="string", required=True)
    amount = fields.Int(doc="amount", example="string", required=True)
    
# Delete 刪除商品    
class ProductDleteSchema(Schema):
    name = fields.Str(example="string")
    
###############################################################

# Get 查詢購物車內商品
class CartGetSchema(Schema):
    name = fields.Str(example="string", required=True) 
    
# Post 新增商品至購物車
class CartPostSchema(Schema):
    name = fields.Str(doc="name", example="string", required=True)
    product_name = fields.Str(doc="product_name", example="string", required=True)
    amount = fields.Int(doc="amount", example="string", required=True)

# Patch 修改購物車商品內容
class CartPatchSchema(Schema):
    name = fields.Str(doc="name", example="string", required=True)
    product_name = fields.Str(doc="product_name", example="string", required=True)
    amount = fields.Int(doc="amount", example="string", required=True)

# Delete 刪除購物車
class CartDleteSchema(Schema):
    name = fields.Str(example="string", required=True)
    
###############################################################
  
# Get 查詢訂單
class OrderNewGetSchema(Schema):
    order_no = fields.Str(example="string", required=True)
      
# Post 寫入訂單
class OrderNewPostOrderSchema(Schema):
    name = fields.Str(example="string") 
    
# Delete 刪除訂單
class OrderNewDleteSchema(Schema):
    order_no = fields.Str(example="string", required=True) 
    
###############################################################

# Post 註冊帳戶
class UserPostSchema(Schema):
    name = fields.Str(doc="name", example="string", required=True)
    gender = fields.Str(doc="gender", example="string", required=True)
    account = fields.Str(doc="account", example="string", required=True)
    password = fields.Str(doc="password", example="string", required=True, validate=[
                      validate.Length(min=6, max=20)])
    birth = fields.Str(doc="birth", example="string")
    note = fields.Str(doc="note", example="string")

# Login 登入帳戶
class LoginSchema(Schema):
    account = fields.Str(doc="account", example="string", required=True)
    password = fields.Str(doc="password", example="string", required=True)

###############################################################

# Response
class GetResponse(Schema):
    message = fields.Str(example="success")
    datatime = fields.Str(example="1970-01-01T00:00:00.000000")
    data = fields.List(fields.Dict())

class CommonResponse(Schema):
    message = fields.Str(example="success")
    


