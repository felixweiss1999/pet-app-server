# The purpose of this file is to check whether
# the request is authorized or not 
# (Verification of the protected routes)
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_handler import decodeJWT
import time
# used to persist authentication on the routes
class jwtBearer(HTTPBearer):
    def extract_uid(self, jwtokenn : str):
        payload = decodeJWT(jwtokenn)
        try:
            if payload["expiry"] >= time.time():
                return payload["userID"]
        except Exception as e:
            print(repr(e))
            return False
        return False
    
    def __init__(self, auto_Error : bool = True):
        super(jwtBearer, self).__init__(auto_error=auto_Error) #inherit everything from HTTPBearer super class
    
    async def __call__(self, request : Request):
        credentials : HTTPAuthorizationCredentials = await super(jwtBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code = 403, detail="No token provided!")
            elif not self.extract_uid(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid Token!")
            else:
                return self.extract_uid(credentials.credentials) #actual token value
        else:
            raise HTTPException(status_code = 403, detail="No token provided!")
        
    
