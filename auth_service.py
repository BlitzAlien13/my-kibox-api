# auth_service.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from db_service import DatabaseService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "SUPERSECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class AuthService:
    def __init__(self, db: DatabaseService):
        self.db = db

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def register_user(self, name: str, klasse: str, geburtstag, email: str, password: str):
        if self.db.get_user_by_username(name):
            raise ValueError("Username already exists")
        password_hash = self.hash_password(password)
        print(password_hash)
        self.db.add_user(name, klasse, geburtstag, email, password_hash)

    def login_user(self, username: str, password: str) -> str:
        user = self.db.get_user_by_username(username)
        if not user or not self.verify_password(password, user["password_hash"]):
            raise ValueError("Invalid credentials")
        return self.create_access_token({"sub": user["username"]})
