import requests
import time

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
            print(f"✗ Fehler (chat): {response.status_code}")
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

    def clear_conversation(self):
        """Löscht den Gesprächsverlauf"""
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
            print(f"✗ (similar) Fehler: {similar_request.status_code}")

            return None
        
    def fetch_all_articles(search_text):
        page = 1
        articles = []

        while True:
            resp = requests.get(
                "https://www.tagesschau.de/api2u/search/",
                params={
                    "searchText": search_text,
                    "pageSize": 5,
                    "resultPage": page
                }
            )
            if resp.status_code != 200:
                print(f"Fehler: {resp.status_code}")
                return None

            data = resp.json()
            results = data.get("searchResults", [])
            if not results:
                return None  # keine weiteren Seiten

            for r in results:
                title = r.get("title") or r.get("headline")
                link = r.get("shareURL") or r.get("details")
                if link and link.startswith("/"):
                    link = "https://www.tagesschau.de" + link
                if title and link:
                    articles.append((title, link))

            page += 1
            return articles


    def run_monitor(self, search_text):
        seen_links = set()  # zum Duplikate vermeiden

        while True:
            print(f"\nSuche nach '{search_text}' ...")
            articles = self.fetch_all_articles(search_text)

            new_articles = []
            for title, link in articles:
                if link not in seen_links:
                    new_articles.append((title, link))
                    seen_links.add(link)

            if new_articles:
                print(f"Neue Artikel gefunden: {len(new_articles)}")
                for title, link in new_articles:
                    print(f"- {title}\n  {link}\n")
            else:
                print("Keine neuen Artikel gefunden.")


            time.sleep(300)

    def wiki_api(self, text):
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
            print(f"✗ (wiki) Fehler: {wiki.status_code}")

    def news_checker(self, message, temperature=0.7, max_tokens=500):
        self.clear_conversation()
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
            print(f"✗ (response) Fehler: {response.status_code}")




kibox = KIBox(kibox_instance=None)
checker = FakeNews(kibox_instance=None)

