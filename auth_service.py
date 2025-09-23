# auth_service.py
import requests
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
        self.token_login = None

    def login(self, username, password):
        response = requests.post(
            f"{self.api_url}/api/auth/token",
            json={"username": username, "password": password}
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data["token"]
            self.headers["Authorization"] = f"Bearer {self.token}"
            print(f"✓ KIB_Angemeldet als: {data['username']} ({data['role']})")
            return True
        else:
            print(f"✗ Login fehlgeschlagen: {response.json()}")
            return False

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)    # returnt aus dem Passwort ein hash

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)    #überprüft das eingegebene Passwort mit dem hash in der Datnebank

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

    def login_user(self, name: str, password: str) -> str:
        user = self.db.get_user_by_username(name)
        if not user or not self.verify_password(password, user["password_hash"]):
            raise ValueError("Invalid credentials")
        else:
            user_id = user["id"]
            self.token_login = self.create_access_token({"sub": user["name"]})   # <--- speichern
            self.db.update_user_login_db(user_id)
            self.db.add_user_login_db(name, self.token_login, user_id)
        return self.token_login
    



    
