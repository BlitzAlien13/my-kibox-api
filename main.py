from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from KIBox import KIBox
from KIBox import FakeNews

app = FastAPI()
origins = [
    "https://faktenchcker.netlify.app",
    "https://faktenchcker.netlify.app/",
    "http://localhost:3000",         
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kibox = KIBox(kibox_instance=None)
news = FakeNews(kibox_instance=None)

@app.get("/")
async def root():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    kibox.login("lorenc", "blitz-alien")
    news.login("lorenc", "blitz-alien")
    asyncio.create_task(wiederkehrende_aufgabe())

async def wiederkehrende_aufgabe():
    while True:
        print("Event alle 5 Minuten ausgelöst!")
        news.ard_api()
        await asyncio.sleep(300)

    
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