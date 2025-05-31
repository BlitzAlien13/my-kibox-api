from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from KIBox import KIBox  # importiere deine bestehende Klasse
import uvicorn

app = FastAPI()
kibox_instance = KIBox(kibox_instance=None)

class LoginData(BaseModel):
    username: str
    password: str

class ChatMessage(BaseModel):
    message: str
    temperature: float = 0.7
    max_tokens: int = 500

@app.post("/login")
def login(data: LoginData):
    success = kibox_instance.login(data.username, data.password)
    if not success:
        raise HTTPException(status_code=401, detail="Login fehlgeschlagen")
    return {"message": "Login erfolgreich"}

@app.post("/chat")
def chat(msg: ChatMessage):
    if not kibox_instance.token:
        raise HTTPException(status_code=401, detail="Nicht eingeloggt")
    antwort = kibox_instance.chat(
        message=msg.message,
        temperature=msg.temperature,
        max_tokens=msg.max_tokens
    )
    return {"antwort": antwort}

@app.post("/set-subject")
def set_subject(subject: str):
    kibox_instance.add_system_message(subject)
    return {"message": "Fachkontext gesetzt."}

@app.post("/clear")
def clear():
    kibox_instance.clear_conversation()
    return {"message": "Gesprächsverlauf gelöscht"}