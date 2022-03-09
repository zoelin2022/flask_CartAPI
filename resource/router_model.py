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
    
# Get 查詢訂單
class OrderGetSchema(Schema):
    name = fields.Str(example="string") 
    
# Post 新增訂單
class ProductPostOrderSchema(Schema):
    name = fields.Str(doc="name", example="string", required=True)
    product_name = fields.Str(doc="product_name", example="string", required=True)
    amount = fields.Int(doc="amount", example="string", required=True)

# Patch 修改訂單
class OrderPatchSchema(Schema):
    id = fields.Int(doc="id", example="string", required=True)
    name = fields.Str(doc="name", example="string", required=True)
    product_name = fields.Str(doc="product_name", example="string", required=True)
    amount = fields.Int(doc="amount", example="string", required=True)

# Delete 刪除訂單 
class OrderDleteSchema(Schema):
    id = fields.Int(example="string")
    
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
    


