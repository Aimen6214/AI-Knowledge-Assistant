from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #bcrypt: widely used hashing algorithm for password storage. It is designed to be slow and computationally expensive, making it resistant to brute-force attacks.
#deprecated="auto": automatically marks older, less secure hashing algorithms as deprecated, encouraging the use of more secure ones.
#cryptcontext: provides a convenient way to manage password hashing and verification, allowing you to easily switch between different hashing algorithms if needed.
def get_password_hash(password: str):
    return pwd_context.hash(password) #hashing the password using bcrypt algorithm
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password) #verifying the password by comparing the plain password with the hashed password