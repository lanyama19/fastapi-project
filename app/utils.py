import bcrypt

# Ensure passlib-bcrypt compatibility across versions
if not hasattr(bcrypt, '__about__'):
    class _BcryptAbout:
        __version__ = getattr(bcrypt, '__version__', 'unknown')

    bcrypt.__about__ = _BcryptAbout()

from passlib.context import CryptContext


BCRYPT_ROUNDS = 8

# Set default hashing algorithm for password encrypt
pwd_context = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto',
    bcrypt__rounds=BCRYPT_ROUNDS,
)


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
