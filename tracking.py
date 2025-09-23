import requests
from db_service import DatabaseService
from auth_service import AuthService

class UserTracking:
    def __init__(self, db: DatabaseService, at: AuthService, kibox_instance, api_url="https://api.phoenix.kibox.online"):
        self.api_url = api_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.kibox = kibox_instance
        self.db = db
        self.at = at

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
        
    def get_user_by_token(self):
        token_login = self.at.token_login 
        user_id = requests.post(
               f"{self.api_url}/api/db/execute",
                headers=self.headers,
                json={
                    "project": "db_user",
                    "sql": """
                            SELECT *
                            FROM TLogin
                            WHERE token_login = (%s);
                    """,
                    "params": [token_login]
                }
            )
        name = (token_login["name"])
        if user_id.status_code == 200:
            print(f"User {name} mit token: {token_login}")
        else:
            print(f"✗ (get_user_by_token) Fehler: {user_id.status_code, user_id.text}")

