#This file is responsible for signing, encoding
# and returning JWTs
import time, jwt
from decouple import config

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

# returns the generated tokens (JWTs)
def token_response(token: str):
    return {
        "access token" : token
    }

def signJWT(userID: str):
    payload = {
        "userID" : userID,
        "expiry" : time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm = JWT_ALGORITHM)
    return token_response(token)


def decodeJWT(token : str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decode_token
    except Exception as e:
        print(repr(e))
        return {}

    
#note: token itself is not encrypted. 
#it is encoded in Base64 representing binary data
# so this is binary text. But only server
#using secret can verify authenticity!!