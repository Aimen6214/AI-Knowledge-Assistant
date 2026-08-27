from typing import Optional
from datetime import datetime, timedelta
from jose import jwt #jwt info=payload #jwt is a token
from utils.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None): #info input in the form of dictionary cuz of jwt input, expires_delta is optional
# data contains the JWT payload as a dictionary.
# expires_delta is optional; if not provided, the default expiry time is used.   
    to_encode = data.copy()
    #if expires_delta:
    #    expire = datetime.utcnow() + expires_delta
    # else:
    #     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) #token creation
    return encoded_jwt

