import flask
from flask_restful import Api
from resource.user import User, Login
from resource.product import Product
from resource.order import Order
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_jwt_extended import JWTManager # 產生token的套件

# Flask setting
app = flask.Flask(__name__)

# Flask restful setting 建立元件物件
api = Api(app)


app.config["DEBUG"] = True # Able to reload flask without exit the process
app.config["JWT_SECRET_KEY"] = "secret_key" #JWT token setting # 設定環境變數

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

# URL(router) 
api.add_resource(Product, "/product")
docs.register(Product)

api.add_resource(Order, "/Order")
docs.register(Order)

api.add_resource(User, "/user")
docs.register(User) 

api.add_resource(Login, "/login")
docs.register(Login)

if __name__ == '__main__':
    # JWT token setting
    jwt = JWTManager().init_app(app) # 要透過__name__ == '__main__'方式執行，而且要放在app.run之前執行
    app.run(host='52.179.100.221', port=10009)
