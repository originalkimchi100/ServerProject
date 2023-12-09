import uvicorn
from fastapi import FastAPI, Request, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
import logging

import datetime
import firebase_admin
from firebase_admin import credentials, auth
from starlette.middleware.sessions import SessionMiddleware
import pyrebase
import json
from starlette.websockets import WebSocket
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import time
import asyncio
from sse_starlette.sse import EventSourceResponse
import sessionIDgen
import pyqrcode

from urllib.request import urlopen
import base64

sessionid = sessionIDgen #sessionIDgen

templates = Jinja2Templates(directory="templates")

if not firebase_admin._apps:
    cred = credentials.Certificate('firebase_auth.json')
    default_app = firebase_admin.initialize_app(cred)

app = FastAPI()

allow_all = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_all,
    allow_credentials=True,
    allow_methods=allow_all,
    allow_headers=allow_all
)

firebase = pyrebase.initialize_app(json.load(open('firebase_config.json')))


class SessionManager:
    def __init__(self):
        self.sessions = {}


    def create_session(self, session_id: str):
        self.sessions[session_id] = {"websocket": None}

    def set_websocket(self, session_id: str, websocket: WebSocket):
        if session_id in self.sessions:
            self.sessions[session_id]["websocket"] = websocket


    def get_session(self, session_id: str):
        return self.sessions.get(session_id)
    def remove_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

session_manager = SessionManager()


@app.get("/")
async def home(request: Request):
    print("redirected")
    id_token = request.cookies.get("session_cookie")
    print(id_token)

    if not id_token:
        return templates.TemplateResponse("MainLogin.html", {"request": request})

    try:
        decoded_token = auth.verify_id_token(id_token)

        # decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
        print(decoded_token)
        context = {'request': request, 'data': decoded_token['name']}

        return templates.TemplateResponse("client.html", context)


    except auth.ExpiredIdTokenError:
        return templates.TemplateResponse("MainLogin.html", {"request": request})


@app.get("/join")
async def join(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/qrlogin")
async def qrjoin(request: Request):
    base64 = sessionIDgen.generateID(10)
    session_manager.create_session(base64)
 # 여기서 필요한 작업 수행 (예: 템플릿 렌더링 등)
    return templates.TemplateResponse("qrlogin.html", {"request": request, "session_id": base64})

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):

   if not session_manager.get_session(session_id):
        raise HTTPException(status_code=400, detail="Invalid session_id")

   await websocket.accept()
   session_manager.set_websocket(session_id, websocket)

   try:
    while True:
       # WebSocket 연결 유지 중 웹소켓으로부터 데이터를 수신할 수 있습니다.
       await websocket.receive_text()
       print(session_manager)

   except Exception as e:
       print(e)


async def get_websocket(session_id: str):
    session = session_manager.get_session(session_id)
    if session:
        websocket = session.get("websocket")
        if websocket:
            return websocket

    raise HTTPException(status_code=400, detail="WebSocket connection not found for the given session ID")


@app.get("/qrclient")
async def qrclient(request: Request, session_id: str):
    id_token = request.cookies.get("session_cookie")
    websocket = await get_websocket(session_id)
    await websocket.send_text(id_token)

    return templates.TemplateResponse("qrlogin.html", {"request": request})




# signup endpoint
@app.post("/signup", include_in_schema=False)
async def signup(request: Request, email: str = Form(...), password: str = Form(...), display_name: str = Form(...)):
    if email is None or password is None:
        return HTTPException(detail={'message': 'Error! Missing Email or Password'}, status_code=400)
    try:
        auth.create_user(email=email, password=password, display_name=display_name)

        return templates.TemplateResponse("signup.html", {"request": request})

    except:
        return HTTPException(detail={'message': 'Error Creating User'}, status_code=400)


@app.post("/login", include_in_schema=False)
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    # expires_in = datetime.timedelta(minutes=6)
    try:

        user = firebase.auth().sign_in_with_email_and_password(email, password)
        # session_cookie = auth.create_session_cookie(user['idToken'], expires_in=expires_in)
        print(user)
        redirect_response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        print("a")
        redirect_response.set_cookie(key="session_cookie", value=user['idToken'], httponly='true')
        print("b")

        return redirect_response



    except Exception as e:
        print(e)


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="218.157.107.140")
