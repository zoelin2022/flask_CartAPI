import flask
from flask_restful import Api
from resource.user import User, Login
from resource.product import Product
from resource.cart import Cart
from resource.order import Order_new
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin # 序列化處理框架(資料型別轉換校驗
from flask_apispec.extension import FlaskApiSpec # 產生api文件導入swagger
from flask_jwt_extended import JWTManager # 產生token的套件

# Flask setting
app = flask.Flask(__name__)

# Flask restful setting 建立元件物件
api = Api(app)

# Able to reload flask without exit the process 檔案有異動時會自動重啟
app.config["DEBUG"] = True 
#JWT token setting 設定環境變數
app.config["JWT_SECRET_KEY"] = "secret_key" 

# Swagger setting
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='購物車 Project',
        version='dv101',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
# 建立元件物件
docs = FlaskApiSpec(app)

# Product URL
api.add_resource(Product, "/product")
docs.register(Product)

# Cart URL
api.add_resource(Cart, "/Cart")
docs.register(Cart)

# Order_new URL
api.add_resource(Order_new, "/Order")
docs.register(Order_new)

# User URL
api.add_resource(User, "/user")
docs.register(User) 
# Login URL
api.add_resource(Login, "/login")
docs.register(Login)

if __name__ == '__main__':
    # JWT token 要透過__name__ == '__main__'方式執行，而且要放在app.run之前執行
    jwt = JWTManager().init_app(app) 
    app.run(host='127.0.0.1', port=10009)
