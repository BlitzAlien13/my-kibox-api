from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from KIBox import KIBox
from KIBox import FakeNews

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <- für Produktion bitte spezifizieren!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kibox = KIBox(kibox_instance=None)
news = FakeNews(kibox_instance=None)

@app.get("/")

@app.on_event("startup")
async def startup_event():
    kibox.login("lorenc", "blitz-alien")

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

@app.post("/wiki")
async def wiki(request: Request):
    data = await request.json()
    message = data.get("message")
    if not kibox.token:
        return {"error": "Bitte zuerst einloggen (/login)"}
    response = kibox.chat(message)
    response = news.news_checker(message)
    return {"reply": response}