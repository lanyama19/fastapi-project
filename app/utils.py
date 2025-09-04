from passlib.context import CryptContext


# Set default hashing algorithm for password encrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)