import requests

class KIBox:
    def __init__(self, kibox_instance, api_url="https://api.phoenix.kibox.online"):
        self.api_url = api_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.kibox = kibox_instance
        self.conversation = []

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
            print(f"✓ Angemeldet als: {data['username']} ({data['role']})")
            return True
        else:
            print(f"✗ Login fehlgeschlagen: {response.json()}")
            return False
        
    def add_system_message(self, content):
        """Fügt eine System-Nachricht hinzu (z.B. Anweisungen)"""
        self.conversation.append({"role": "system", "content": content})

    def chat(self, message, temperature=0.7, max_tokens=500):
        """Führt ein Gespräch mit Verlauf"""
        # Benutzer-Nachricht hinzufügen
        self.conversation.append({"role": "user", "content": message})

        # An API senden
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

            # Antwort der KI zum Verlauf hinzufügen
            self.conversation.append({"role": "assistant", "content": assistant_message})

            return assistant_message
        else:
            print(f"✗ Fehler: {response.status_code}")
            return None

    def get_user_info(self):
        """Informationen über den aktuellen Benutzer"""
        response = requests.get(f"{self.api_url}/api/user/info", headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def clear_conversation(self):
        """Löscht den Gesprächsverlauf"""
        self.conversation = []
    
class FakeNews:
    def __init__(self, kibox_instance, api_url="https://api.phoenix.kibox.online"):
        self.api_url = api_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.kibox = kibox_instance
        self.conversation = []

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
            print(f"✓ Angemeldet als: {data['username']} ({data['role']})")
            return True
        else:
            print(f"✗ Login fehlgeschlagen: {response.json()}")
            return False

    def add_system_message(self, content):
        """Fügt eine System-Nachricht hinzu (z.B. Anweisungen)"""
        self.conversation.append({"role": "system", "content": content})

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
              
        else:
            print(f"✗ (extract) Fehler: {extract.status_code}")

    def news_checker(self, message, temperature=0.7, max_tokens=500):
        #Führt ein Gespräch mit Verlauf
        # Benutzer-Nachricht hinzufügen
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
            important_link_prompt = self.extract_important(important)
            wiki = requests.post(
                f"{self.api_url}/api/wikipedia-link/search",
                headers=self.headers,
                json={
                    "query": important_link_prompt,
                    "limit": 1
                }
            )
            if wiki.status_code == 200:
                answer = wiki.json()
                AnswerUrl = answer[0]["url"]
                self.conversation.append({"role": "assistant", "content": AnswerUrl })
                # Antwort der KI zum Verlauf hinzufügen
                return AnswerUrl
            else:
                print(f"✗ (wiki) Fehler: {response.status_code}")
        else:
            print(f"✗ (response) Fehler: {response.status_code}")




kibox = KIBox(kibox_instance=None)
checker = FakeNews(kibox_instance=None)

