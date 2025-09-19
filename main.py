from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from KIBox import KIBox, FakeNews
from db_service import DatabaseService
from auth_service import AuthService
from dotenv import load_dotenv
from pydantic import BaseModel
import os


load_dotenv()  

username = os.getenv("KIBOX_USER")
password = os.getenv("KIBOX_PASS")

class RegisterRequest(BaseModel):
    name: str
    klasse: str
    geburtstag: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

kibox = KIBox(kibox_instance=None)
news = FakeNews(kibox_instance=None)
db = DatabaseService(kibox_instance=None)
auth = AuthService(db)

async def wiederkehrende_aufgabe():
    try:
        while True:
            print("Event alle 5 Minuten ausgelöst!")
            news.ard_deletus()
            news.ard_api()
            await asyncio.sleep(300)
    except asyncio.CancelledError:
        print("Wiederkehrende Aufgabe beendet")

async def lifespan(app: FastAPI):
    # Startup
    kibox.login(username, password)
    news.login(username, password)
    db.login(username, password)
    # Hintergrundtask starten
    task = asyncio.create_task(wiederkehrende_aufgabe())
    db.project_check()
    
    yield 
    
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    print("App heruntergefahren")

app = FastAPI(lifespan=lifespan)

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

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/register")
def register(user: RegisterRequest):
    try:
        auth.register_user(
            user.name, user.klasse, user.geburtstag, user.email, user.password
        )
        return {"msg": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/login")
def login(data: LoginRequest):
    try:
        token = auth.login_user(data.username, data.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
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
