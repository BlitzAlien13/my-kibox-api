from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from KIBox import KIBox

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <- für Produktion bitte spezifizieren!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kibox = KIBox(kibox_instance=None)

@app.get("/")

@app.on_event("startup")
async def startup_event():
    kibox.login("lorenc", "blitz-alien")

def root():
    return {"message": "KIBox API ist bereit 🎉"}

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    username = "lorenc"
    password = "blitz-alien"
    return kibox.login(username, password)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message")
    if not kibox.token:
        return {"error": "Bitte zuerst einloggen (/login)"}
    response = kibox.chat(message)
    return {"reply": response}