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
        self.token_login = self.at.token_login 
        
    def set_token(self, token: str):
        """Token von KIBox übernehmen"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {self.token}"
        
    def get_user_by_token(self): 
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
                "params": [self.token_login]
            }
        )

        if user_id.status_code == 200:
            data = user_id.json()
            print(f"User gefunden: {data}")
        else:
            print(f"✗ (get_user_by_token) Fehler: {user_id.status_code, user_id.text}")


