import requests

class DatabaseService:
    def __init__(self, kibox_instance, api_url="https://api.phoenix.kibox.online"):
        self.api_url = api_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.kibox = kibox_instance

    def set_token(self, token: str):
        """Token von KIBox übernehmen"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {self.token}"
    
    def project_check(self):
        response_get = requests.get(
            f"{self.api_url}/api/db/projects",
            headers=self.headers,
            json={
                "success": True,
                "message": "string",
                "error": "string",
                "detail": "string",
                "data": "string",
                "count": 0,
                "affected_rows": 0,
                "last_insert_id": 0
            }
        )
        if response_get.status_code == 200:
            answer = response_get.json()
            data = answer.get("data", [])
            project_exists = any(project.get("name") == "db_user" for project in data)

            if project_exists:    
                create_table_response = requests.post(
                    f"{self.api_url}/api/db/execute",
                    headers=self.headers,
                    json={
                        "project": "db_user",
                        "sql": """
                            CREATE TABLE IF NOT EXISTS TUser(
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(100) NOT NULL,
                            klasse VARCHAR(10),
                            geburtstag DATE,
                            email VARCHAR(100),
                            eintrittsdatum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            password_hash VARCHAR(255)
                        )
                        """ 
                    }
                )
                if create_table_response.status_code == 200:
                    print("TUser")

                else:
                    print(f"✗ (Table_Create_User) Fehler: {create_table_response.status_code}")

                create_table_response_login = requests.post(
                    f"{self.api_url}/api/db/execute",
                    headers=self.headers,
                    json={
                        "project": "db_user",
                        "sql": """
                            CREATE TABLE IF NOT EXISTS TLogin(
                            name VARCHAR(100) NOT NULL,
                            token_login VARCHAR(255) NOT NULL,
                            id INT
                        )
                        """ 
                    }
                )
                if create_table_response_login.status_code == 200:
                    print("TLogin")

                else:
                    print(f"✗ (Table_Create_Login) Fehler: {create_table_response_login.status_code, create_table_response_login.text}")  

                create_table_response_chats = requests.post(
                    f"{self.api_url}/api/db/execute",
                    headers=self.headers,
                    json={
                        "project": "db_user",
                        "sql": """
                            CREATE TABLE IF NOT EXISTS TChats(
                            id SERIAL PRIMARY KEY,
                            user_id INT NOT NULL,
                            sender VARCHAR(50),        
                            message TEXT,
                            timestamp TIMESTAMP DEFAULT now(),
                            );
                            """
                    }
                )
                if create_table_response_chats.status_code == 200:
                    print("TChats")
                else:
                    print(f"✗ (Table_Create_Chats) Fehler: {create_table_response_chats.status_code, create_table_response_chats.text}")
            else:
                response_add = requests.post(
                    f"{self.api_url}/api/db/project",
                    headers=self.headers,
                    json={
                        "name": "db_user",
                        "description": "Hier sind User gespeichert",
                        "shared_with_role": "STUDENT"
                    }  
                )
                if response_add.status_code == 200:
                    print("Datenbank angelegt")

                else:
                    print(f"✗ (db_add) Fehler: {response_add.status_code} - {response_add.text}")
        else:
            print(f"✗ (project_list) Fehler: {response_get.status_code}")

    def add_user(self, name: str, klasse: str, geburtstag: str, email: str, password_hash: str):
            AUser=requests.post(
                f"{self.api_url}/api/db/execute",
                headers=self.headers,
                json={
                    "project": "db_user",
                    "sql": "INSERT INTO TUser (name, klasse, geburtstag, email, password_hash) VALUES (%s, %s, %s, %s, %s)",
                    "params": [name, klasse, geburtstag, email, password_hash]
                }
            )
            if AUser.status_code == 200:
                data = AUser.json()
                print(f"{name} hinzugefügt")
    
    def get_user_by_username(self, username: str):
        response = requests.post(
            f"{self.api_url}/api/db/execute",
            headers=self.headers,
            json={
                "project": "db_user",
                "sql": f"SELECT * FROM TUser WHERE name = '{username}';"
            }
        )
        
        if response.status_code != 200:
            print(f"✗ Fehler: {response.status_code} - {response.text}")
            return None

        answer = response.json()
        if not answer["data"]:
            return None  

        user_data = answer["data"][0]  
        return user_data
    
    def add_user_login_db(self, name: str, token_login: str, user_id: int):
            ACser=requests.post(
               f"{self.api_url}/api/db/execute",
                headers=self.headers,
                json={
                    "project": "db_user",
                    "sql": "INSERT INTO TLogin (name, token_login, id) VALUES (%s, %s, %s)",
                    "params": [name, token_login, user_id]
                }
            )
            if ACser.status_code == 200:
                print(f"User {name} hat sich mit id: {user_id} eingeloggt")
            else:
                print(f"✗ (ACer) Fehler: {ACser.status_code, ACser.text}")
                
    def update_user_login_db(self, user_id: int):
        DCser=requests.post(
               f"{self.api_url}/api/db/execute",
                headers=self.headers,
                json={
                    "project": "db_user",
                    "sql": """
                            DELETE FROM TLogin
                            WHERE id = (%s);
                    """,
                    "params": [user_id]
                }
            )
        
        if DCser.status_code == 200:
            print(f"User hat sich mit id: {user_id} ausgeloggt")
        else:
            print(f"✗ (ACer) Fehler: {DCser.status_code, DCser.text}")
