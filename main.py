from fastapi import FastAPI, Request
from KIBox import KIBox

app = FastAPI()
kibox = KIBox(kibox_instance=None)

@app.get("/")
def root():
    return {"message": "KIBox API ist bereit 🎉"}

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    return kibox.login(username, password)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message")
    if not kibox.token:
        return {"error": "Bitte zuerst einloggen (/login)"}
    response = kibox.chat(message)
    return {"response": response}