from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from KIBox import KIBox, FakeNews
from db_service import DatabaseService
from dotenv import load_dotenv
import os

load_dotenv()  

username = os.getenv("KIBOX_USER")
password = os.getenv("KIBOX_PASS")

# --- Services ---
kibox = KIBox(kibox_instance=None)
news = FakeNews(kibox_instance=None)
data = DatabaseService(kibox_instance=None)

# --- FastAPI Setup ---
async def wiederkehrende_aufgabe():
    try:
        while True:
            print("Event alle 5 Minuten ausgelöst!")
            news.ard_api()
            await asyncio.sleep(300)
    except asyncio.CancelledError:
        print("Wiederkehrende Aufgabe beendet")

async def lifespan(app: FastAPI):
    # Startup
    kibox.login(username, password)
    news.login(username, password)
    data.login(username, password)
    # Hintergrundtask starten
    task = asyncio.create_task(wiederkehrende_aufgabe())
    data.project_check()
    
    yield  # <- hier läuft der Server
    
    # Shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    print("App heruntergefahren")

app = FastAPI(lifespan=lifespan)

# --- CORS Setup ---
origins = [
    "https://faktenchcker.netlify.app",
    "https://faktenchcker.netlify.app/",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
@app.get("/")
async def root():
    return {"status": "ok"}

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
    response = news.news_checker(message)
    return {"reply": response}

@app.post("/ard")
async def ard(request: Request):
    data = await request.json()
    message = data.get("message")
    if not kibox.token:
        return {"error": "Bitte zuerst einloggen (/login)"}
    response = news.run_monitor(message)
    print(response)
    return {"reply": response}

@app.post("/similar")
async def similar(request: Request):
    data = await request.json()
    message = data.get("message")
    if not kibox.token:
        return {"error": "Bitte zuerst einloggen (/login)"}
    response = news.similar(message)
    return {"reply": response}
