from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
from services import kibox, news, db, auth
from dotenv import load_dotenv
from pydantic import BaseModel
from jose import jwt, JWTError, ExpiredSignatureError
import os


load_dotenv()  

username = os.getenv("KIBOX_USER")
password = os.getenv("KIBOX_PASS")
security = HTTPBearer()

def get_current_user_for(application: str):
    def dependency(credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        try:
            user_id = auth.get_user_by_token(token)
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token: no subject")
            print(f"User {user_id} führt Aktion {application} aus")
            return user_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    return dependency


class RegisterRequest(BaseModel):
    name: str
    klasse: str
    geburtstag: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

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
    # EIN Login bei KIBox
    kibox.login(username, password)
    
    # Den KIBox-Token an alle weitergeben
    token = kibox.token
    
    # Header gleich mit 
    news.set_token(token)
    db.set_token(token)
    auth.set_token(token)
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
    "https://faktenchecker.netlify.app",
    "https://faktenchecker.netlify.app/",
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
async def chat(request: Request, user_id: int = Depends(get_current_user_for("chat"))):
    data = await request.json()
    message = data.get("message")
    if not kibox.token:
        return {"error": "Bitte zuerst einloggen (/login)"}
    response = kibox.chat(message)
    return {"reply": response, "user_id": user_id}

@app.post("/wiki")
async def wiki(request: Request, user_id: int = Depends(get_current_user_for("wiki"))):
    data = await request.json()
    message = data.get("message")
    if not news.token:
        return {"error": "Bitte zuerst einloggen (/login)"}
    response = news.news_checker(message)
    return {"reply": response, "user_id": user_id}

@app.post("/ard")
async def ard(request: Request, user_id: int = Depends(get_current_user_for("ard"))):
    data = await request.json()
    message = data.get("message")
    if not news.token:
        return {"error": "Bitte zuerst einloggen (/login)"}
    response = news.run_monitor(message)
    print(response)
    return {"reply": response, "user_id": user_id}

@app.post("/similar")
async def similar(request: Request):
    data = await request.json()
    message = data.get("message")
    if not kibox.token:
        return {"error": "Bitte zuerst einloggen (/login)"}
    response = news.similar(message)
    return {"reply": response}
