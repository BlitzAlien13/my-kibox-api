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
    
    """ def start_conversation(self):
        while True:
            print("In welchem Bereich soll ich dir helfen?\n")
            AuswahlBerreich = input("1. Hauptfächer\n2. Gesellschaftswissenschaften\n3. Naturwissenschaften\n4. Sprachen\n5. Kunst und Musik\n6. Weitere Fächer\n7. quit\n")

            if AuswahlBerreich == "7" or AuswahlBerreich.lower() == "quit":
                print("Tschüss!")
                break

            elif AuswahlBerreich == "1" or AuswahlBerreich.lower() == "hauptfächer":
                print("Wähle ein Fach:\n")
                AuswahlHauptfach = input("1. Mathe\n2. Deutsch\n3. Englisch\n")

                if AuswahlHauptfach == "1" or AuswahlHauptfach.lower() == "mathe":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Mathe haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Mathe passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)
            
                elif AuswahlHauptfach == "2" or AuswahlHauptfach.lower() == "deutsch":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Deutsch haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Deutsch passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)

                elif AuswahlHauptfach == "3" or AuswahlHauptfach.lower() == "englisch":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Englisch haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Englisch passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)

            elif AuswahlBerreich == "2" or AuswahlBerreich.lower() == "gesellschaftwissenschaften":
                print("Wähle ein Fach:\n")
                AuswahlGesellschaftwissenschaften = input("1. Geschichte\n2. Erdkunde\n3. Politik-Wirtschaft\n4. Religion\n5. Werte und Normen\n6. Philosophie")

                if AuswahlGesellschaftwissenschaften == "1" or AuswahlGesellschaftwissenschaften.lower() == "geschichte":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Geschichte haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Geschichte passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)
            
                elif AuswahlGesellschaftwissenschaften == "2" or AuswahlGesellschaftwissenschaften.lower() == "erdkunde":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Erdkunde haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Erdkunde passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)

                elif AuswahlGesellschaftwissenschaften == "3" or AuswahlGesellschaftwissenschaften.lower() == "politik-wirtschaft":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Politik-Wirtschaft haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Politik-Wirtschaft passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)
                elif AuswahlGesellschaftwissenschaften == "4" or AuswahlGesellschaftwissenschaften.lower() == "religion":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Religion haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Religion passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)
            
                elif AuswahlGesellschaftwissenschaften == "5" or AuswahlGesellschaftwissenschaften.lower() == "werte und normen":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Werte und Normen haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Werte und Normen passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)

                elif AuswahlGesellschaftwissenschaften == "6" or AuswahlGesellschaftwissenschaften.lower() == "philosophie":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Philosophie haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Philosophie passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)

            elif AuswahlBerreich == "3" or AuswahlBerreich == "Naturwissenschaften":
                print("Wähle ein Fach:\n")
                AuswahlNaturwissenschaften = input("1. Mathe\n2. Biologie\n3. Chemie\n4. Physik\n")

                if AuswahlNaturwissenschaften == "1" or AuswahlNaturwissenschaften.lower() == "mathe":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Mathe haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Mathe passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)
            
                elif AuswahlNaturwissenschaften == "2" or AuswahlNaturwissenschaften.lower() == "biologie":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Bilogie haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Biologie passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)

                elif AuswahlNaturwissenschaften == "3" or AuswahlNaturwissenschaften.lower() == "chemie":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Chemie haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Chemie passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)
                elif AuswahlNaturwissenschaften == "4" or AuswahlNaturwissenschaften.lower() == "physik":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Physik haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Physik passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)
            
            elif AuswahlBerreich == "4" or AuswahlBerreich == "Sprachen":
                print("Wähle ein Fach:\n")
                AuswahlSprachen = input("1. Deutsch\n2. Englisch\n3. Spanisch\n4. Französich\n5. Russisch\n6. Latein\n")

                if AuswahlSprachen == "1" or AuswahlSprachen.lower() == "deutsch":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Deutsch haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Deutsch passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)
            
                elif AuswahlSprachen == "2" or AuswahlSprachen.lower() == "englisch":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Englisch haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Englisch passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)

                elif AuswahlSprachen == "3" or AuswahlSprachen.lower() == "spanisch":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Spanisch haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Spanisch passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)
                elif AuswahlSprachen == "4" or AuswahlSprachen.lower() == "französich":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Französich haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Französich passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)
            
                elif AuswahlSprachen == "5" or AuswahlSprachen.lower() == "russisch":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Russisch haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Russisch passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)

                elif AuswahlSprachen == "6" or AuswahlSprachen.lower() == "latein":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Latein haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Latein passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)

            elif AuswahlBerreich == "5" or AuswahlBerreich == "Kunst und Musik":
                print("Wähle ein Fach:\n")
                AuswahlKunstUndMusik = input("1. Kunst\n2. Musik\n")

                if AuswahlKunstUndMusik == "1" or AuswahlKunstUndMusik.lower() == "kunst":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Kunst haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Kunst passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)
            
                elif AuswahlKunstUndMusik == "2" or AuswahlKunstUndMusik.lower() == "musik":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Musik haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Musik passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)

            elif AuswahlBerreich == "6" or AuswahlBerreich == "Weitere Fächer":
                print("Wähle ein Fach:\n")
                AuswahlWeitereFächer = input("1. Informatik\n2. Sport\n")
                if AuswahlWeitereFächer == "1" or AuswahlWeitereFächer.lower() == "informatik":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Informatik haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Informatik passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)
            
                elif AuswahlWeitereFächer == "2" or AuswahlWeitereFächer.lower() == "sport":
                    kibox.add_system_message("Du bist ein hilfreicher Assistent für Schüler, die Fragen zum Fach Sport haben.")
                    while True:
                        frage = input("Stell bitte eine Frage, welche zum Fach Sport passt (oder 'back' zum Menü):\n")
                        if frage.lower() == "back":
                            break
                        antwort = kibox.chat(frage)
                        print(antwort)

            else:
                print("Keine gültige Eingabe!\n")"""

        


kibox = KIBox(kibox_instance=None)
if kibox.login("lorenc", "blitz-alien"):
   """kibox.start_conversation()"""

