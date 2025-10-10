import requests
import time
import uuid

class KIBox:
    def __init__(self, kibox_instance, api_url="https://api.phoenix.kibox.online"):
        self.api_url = api_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.kibox = kibox_instance
        self.conversation = []

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
        
    def add_system_message(self, content):
        self.conversation.append({"role": "system", "content": content})

    def chat(self, message, temperature=0.7, max_tokens=500):
        self.conversation.append({"role": "user", "content": message})

        response = requests.post(
            f"{self.api_url}/api/llm/chat/completions",
            headers=self.headers,
            json={
                "messages": self.conversation,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )

        if response.status_code == 200:
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]

            self.conversation.append({"role": "assistant", "content": assistant_message})

            return assistant_message
        else:
            print(f"✗ (chat) Fehler: {response.status_code, response.text}")
            return None

    def get_user_info(self):
        response = requests.get(f"{self.api_url}/api/user/info", headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def clear_conversation(self):
        self.conversation = []
    
class FakeNews:
    def __init__(self, kibox_instance, auth_service=None, api_url="https://api.phoenix.kibox.online"):
        self.api_url = api_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.kibox = kibox_instance
        self.auth_service = auth_service  
        self.conversation = []

    def set_token(self, token: str):
        """Token von KIBox übernehmen"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {self.token}"

    def add_system_message(self, content):
        self.conversation.append({"role": "system", "content": content})

    def clear_conversation(self):
        self.conversation = []

    def extract_important(self, text):
        extract = requests.post(
            f"{self.api_url}/api/keyterms/extract",
            headers=self.headers,
            json={
                "text": text
            }
        )
        if extract.status_code == 200:
                
                answer = extract.json()
                important = answer["research_terms"][0]
                return important
        
    def calc_vector(self, text):
        response = requests.post(
            f"{self.api_url}/api/embedding/embeddings",
            headers=self.headers,
            json={
                "input": [text]  # Liste von Texten        
                }
        )
        if response.status_code == 200:
            result = response.json()
            return result["data"][0]["embedding"]  # Erste (und einzige) Embedding 
        
        if response.status_code != 200:
            print(f"✗ calc_vector: {response.status_code, response.text}")
            print(response.text)
            return None
            
    def similar(self, text):
        similar_request = requests.post(
            f"{self.api_url}/api/vector/search/similar",
            headers=self.headers,
            json={
                    "project": text,
                    "collection_name": text,
                    "vector": [0],
                    "limit": 10,
                    "filter": {"additionalProp1": {}},
                    "score_threshold": 1
            }
        )
        if similar_request.status_code == 200:
                
                answer = similar_request.json()
                similar = answer["data"]
                return similar
        else:
            print(f"✗ (similar) Fehler: {similar_request.status_code, similar_request.text}")

            return None
        
    def ard_api(self):
        create_tagesschau=requests.post(
                f"{self.api_url}/api/vector/collection",
                headers=self.headers,
                json={
                    "project": "db_ard",
                    "collection_name": "tagesschau",
                    "vector_size": 768,
                    "distance": "COSINE",  
                    "description": "Tagesschau Homepage Vektoren",
                    "shared_with_role": "STUDENT"
                }
                )
        if create_tagesschau.status_code == 200:
            answer = create_tagesschau.json()
            print(answer)
            vektor_id = str(uuid.uuid4())

            resp = requests.get(
                "https://www.tagesschau.de/api2u/homepage/",
                headers=self.headers,
            )

            if resp.status_code != 200:
                    print(f"Fehler (ard_api): {resp.status_code, resp.text}")
                    return None
            else:
                data = resp.json()
                results = data.get("news", [])
                if not results:
                    return None 
                if results:
                    for r in results:
                        title = r.get("title") or r.get("headline")
                        link = r.get("shareURL") or r.get("details")
                        if link and link.startswith("/"):
                            link = "https://www.tagesschau.de" + link
                        if link and title:
                            vektor = self.calc_vector(title)
                        
                        if title and link and vektor:
                            vektor_id = str(uuid.uuid4())
                            atd=requests.post(
                                f"{self.api_url}/api/vector/points/upsert",
                                headers=self.headers,
                                json={
                                        "project": "db_ard",
                                        "collection_name": "tagesschau",
                                        "points": [
                                            {
                                            "id": vektor_id,
                                            "vector": vektor[:768],
                                            "payload": {
                                                "title": title,
                                                "link": link
                                            }
                                            }
                                        ]
                                        }
                            )
                            if atd.status_code == 200:
                                print(f"✓ (atd) Erfolg: {atd.status_code, atd.text}")
        else:
            print(f"✗ (collection tagesschau) Fehler: {create_tagesschau.status_code, create_tagesschau.text}")
        
    def run_monitor(self, message):
            text = self.extract_important(message)
            vektor = self.calc_vector(text)
            if vektor:
                similar_request = requests.post(
                f"{self.api_url}/api/vector/search/similar",
                headers=self.headers,
                json={
                        "project": "db_ard",
                        "collection_name": "tagesschau",
                        "vector": vektor[:768],
                        "limit": 1,
                        "filter": {},
                        "score_threshold": 0.2
                }
            )
                if similar_request.status_code == 200:
                        answer = similar_request.json()
                        link = answer["data"][0]["payload"]["link"]
                        self.conversation.append({"role": "assistant", "content": link })
                        return link
                        
                else:
                    print(f"✗ (monitor) Fehler: {similar_request.status_code, similar_request.text}")
            else:
                print(f"✗ (monitor) Fehler: Kein Vektor für Wiki")

    def ard_deletus(self):
        dfd=requests.delete(
            f"{self.api_url}/api/vector/collection/db_ard/tagesschau",
            headers=self.headers,
            params={
                "project": "db_ard",
                "collection_name": "tagesschau"
            }
        )
        if dfd.status_code == 200:
            deletus = dfd.json()
            print(deletus)
            print(f"✗ (deletus) Fehler: {dfd.status_code, dfd.text}")
        else:
            print(f"✗ (dfd) Fehler: {dfd.status_code, dfd.text}")
            
    def wiki_api(self, message):
        text = self.extract_important(message)
        wiki = requests.post(
            f"{self.api_url}/api/wikipedia-link/search",
            headers=self.headers,
            json={
                "query": text,
                "limit": 1
            }
        )

        if wiki.status_code == 200:
            answer_wiki = wiki.json()
            AnswerUrl_wiki = answer_wiki[0]["url"]
            self.conversation.append({"role": "assistant", "content": AnswerUrl_wiki })
            return AnswerUrl_wiki
        else:
            print(f"✗ (wiki) Fehler: {wiki.status_code, wiki.text}")

    def news_checker(self, message, temperature=0.7, max_tokens=500):
        self.clear_conversation()
        self.add_system_message("Du bist ein hochpräzises Faktenprüfungs-LLM. Antworte sofort auf Fragen, ohne Begrüßungen oder Füllworte. Gib präzise, sachliche Antworten in etwa 400 Zeichen. Prüfe Informationen kritisch, stütze dich auf zuverlässige Quellen und liefere nur gesicherte Fakten. Vermeide persönliche Meinungen oder Spekulationen.")
        self.conversation.append({"role": "user", "content": message})
        important= self.conversation[0]["content"]

        # An API senden
        response = requests.post(
            f"{self.api_url}/api/llm/chat/completions",
            headers=self.headers,
            json={
                "messages": self.conversation,
                "max_tokens": max_tokens
            }
        )

        if response.status_code == 200:
            important_prompt = self.extract_important(important)
            wiki = self.wiki_api(important_prompt)
            return wiki
        else:
            print(f"✗ (response) Fehler: {response.status_code, response.text}")


    def add_chat_TChats(self, user_id):
        chats = self.conversation
        converted = [{'sender': chat['role'], 'message': chat['content']} for chat in chats] 
        for chat in converted:
            sender = chat['sender']
            message = chat['message']
            real_user_id = user_id['id']
            print(sender, message)
            CTdb = requests.post(
                f"{self.api_url}/api/db/execute",
                headers=self.headers,
                json={
                    "project": "db_user",
                    "sql": """
                        INSERT INTO TChats(user_id, sender, message)
                        VALUES (%s, %s, %s)
                    """,
                    "params": [real_user_id, sender, message]
                }
            )
            if CTdb.status_code == 200:
                print(f"✓ User {user_id}: Chat gespeichert -> {chat}")
                self.conversation = []
            else:
                print(f"✗ Fehler beim Speichern: {CTdb.status_code} {CTdb.text}")

    def get_user_chats(self, user_id):
        real_user_id = user_id['id']
        response = requests.post(
            f"{self.api_url}/api/db/execute",
            headers=self.headers,
            json={
                "project": "db_user",
                "sql": """
                    SELECT sender, message
                    FROM TChats
                    WHERE user_id = %s
                    ORDER BY id DESC
                """,
                "params": [real_user_id]
            }
        )

        if response.status_code == 200:
            result = response.json()
            chats = result.get("data", [])
            for chat in chats:
                print(chat)
            return chats
        else:
            print(f"✗ Fehler beim Abrufen: {response.status_code} {response.text}")
            return []


