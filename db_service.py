import requests

class DatabaseService:
    def __init__(self, kibox_instance, api_url="https://api.phoenix.kibox.online"):
        self.api_url = api_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.kibox = kibox_instance

    def login(self, username, password):
        """Anmeldung bei der KI.Box"""
        response = requests.post(
            f"{self.api_url}/api/auth/token",
            json={"username": username, "password": password}
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data["token"]
            self.headers["Authorization"] = f"Bearer {self.token}"
            print(f"✓ db_Angemeldet als: {data['username']} ({data['role']})")
            return True
        else:
            print(f"✗ Login fehlgeschlagen: {response.json()}")
            return False
    
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
                search_table_response = requests.post(
                    f"{self.api_url}/api/db/execute",
                    headers=self.headers,
                    json={
                        "project": "db_user",
                        "sql": """
                            SELECT CASE WHEN EXISTS (
                                SELECT 1
                                FROM INFORMATION_SCHEMA.TABLES
                                WHERE TABLE_NAME = 'TUser'
                            ) THEN 1 ELSE 0 END AS TableExists;
                        """
                    }
                )
                if search_table_response.status_code == 200:
                    answer = search_table_response.json()
                    data = answer["data"][0]["TableExists"]
                    table_exists = bool(data)

                    if table_exists:
                        print("Table already exists")

                    else:
                        create_table_response = requests.post(
                            f"{self.api_url}/api/db/execute",
                            headers=self.headers,
                            json={
                                "project": "db_user",
                                "sql": """
                                    CREATE TABLE TUser(
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
                            print("TUser wurde erstellt")

                        else:
                            print(f"✗ (Table_Create) Fehler: {search_table_response.status_code}")

                else:
                    print(f"✗ (Table_Search) Fehler: {search_table_response.status_code}")


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
                print(data)
                print(f"✗ (add_user) Fehler: {AUser.status_code, AUser.text}")

    def get_user_by_username(self, username: str):
        user=requests.post(
            f"{self.api_url}/api/db/execute",
                headers=self.headers,
                json={
                    "project": "db_user",
                    "sql": f"""
                        SELECT CASE WHEN EXISTS (
                        SELECT 1
                        FROM TUser
                        WHERE name = '{username}'
                    ) THEN 1 ELSE 0 END AS UserExists;
                    """
                }
        )
        if user.status_code == 200:
            answer = user.json()
            data = answer["data"][0]["UserExists"]
            user_exists = bool(data)

            if user_exists:
                print("User schon verhanden")
            else:
                print("USer nicht Verhanden")
        else:
            print(f"✗ (get_user) Fehler: {user.status_code} - {user.text}")
            

