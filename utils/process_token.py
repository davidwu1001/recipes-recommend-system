
from config import SECRET_KEY
import jwt
from datetime import datetime, timedelta
# 根据openid 生成有效期一周的token
def setToken(openid):
    payload = {'openid':openid,'exp':datetime.utcnow() + timedelta(weeks=1)}
    #生成Token
    token = jwt.encode(payload,SECRET_KEY,algorithm="HS256")
    return token

def decodeToken(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded_token
    except jwt.exceptions.InvalidSignatureError:
        return 'Invalid signature'
    except jwt.exceptions.ExpiredSignatureError:
        return 'Token has expired'
    except jwt.exceptions.DecodeError:
        return 'Invalid token'
