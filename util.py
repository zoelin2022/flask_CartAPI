from datetime import datetime


def success(data=None): # 預設 data 為 None
    if data is None:
        return {'message': 'success'}, 200

    return {
        'message': 'success',
        'data': data,
        'datatime': datetime.utcnow().isoformat()
    }, 200

# 失敗的訊息設定
def failure(data):
    data["datatime"] = datetime.utcnow().isoformat()
    return data, 500