# Python API專題製作️

## ⭐ 功能說明

### 1. 帳戶管理 user.py 
- User 註冊帳戶
    :::success
    - 檢查帳戶名稱有無重複，才能註冊帳戶
    :::
- Login 登入帳戶 
    :::success
    - 如果使用者登入成功，就建立token
    :::

### 2. 商品管理 product.py 
- Get 查詢商品 
    :::info
    - 不輸入的話，可以查詢全部資料
    - 檢查商品存不存在資料庫
- Post 新增商品
    :::info
    - 檢查商品是否已存在資料庫，避免重複建立
    :::
- Patch 更新商品
    :::info
    - 檢查要修改的商品有沒有存在於資料庫
    :::
- Dlete 刪除商品
    :::info
    - 檢查要刪除的商品有沒有存在於資料庫
    :::

### 3. 購物車管理 cart.py 
- POST 新增商品至購物車
    :::warning
    - 檢查商品是否已存在資料庫，避免重複建立
    - 檢查商品庫存是否充足
    - 如果商品已存在購物車，只要增加購買的數量即可
    - 加入購物車後，將商品庫存同步更新
    :::
- Get 查詢購物車
    :::warning
    - 檢查購物車存不存在
    - 查詢後自動合計總金額
    :::
- Patch 更新購物車內容
    :::warning 
    - 檢查要修改的商品存不存在於購物車
    - 數量減少就更新購物車，加回庫存
    - 數量增加的話，先檢查看庫存是否充足再更新購物車，扣掉庫存
    - 輸入0代表刪除商品，數量加回庫存
    :::
- Delete 刪除購物車
    :::warning
    - 檢查購物車紀錄存不存在
    - 刪除購物車紀錄，同時把商品數量更新加回庫存
    :::
### 4. 訂單管理 cart.py 
    
- POST 購物車結帳(新增訂單) 
    :::danger
    - 檢查購物車存不存在
    - 結帳後，將購物車資料刪除
    - 自動生成訂單編號提供查詢
    :::
- Get 查詢訂單
    :::danger
    - 檢查訂單存不存在
    :::
- Delete 刪除訂單
    :::danger
    - 檢查訂單存不存在
    - 刪除訂單，同時把商品數量都更新加回庫存
    :::

## ⭐ Swagger-UI API介面
![](https://i.imgur.com/PorqLiq.jpg)

## ⭐ DB架構

- member 資料表結構

|欄位|類型|
| --- |--- |
|//**id**//|int(11)|
|name|varchar(20)|
|account|varchar(40)|
|password|varchar(40)|
|gender|varchar(20)|
|birth|varchar(40)|
|note|varchar(100)|

- product 資料表結構

|欄位|類型|
| --- |--- |
|//**id**//|int(11)|
|product_name|varchar(50)|
|price|int(11)|
|amount|int(11)|

- cart 資料表結構

|欄位|類型|
| --- |--- |
|//**id**//|int(11)|
|name|varchar(20)|
|product_name|varchar(50)|
|amount|int(11)|
|total|int(20)|

- orders 資料表結構

|欄位|類型|
| --- |--- |
|//**id**//|int(11)|
|order_no|varchar(50)|
|name|varchar(50)|
|product_name|varchar(50)|
|amount|int(11)|
|total|int(11)|