import uvicorn
from fastapi import FastAPI, Request, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse,HTMLResponse
from fastapi.exceptions import HTTPException

import firebase_admin
from firebase_admin import credentials, auth

import pyrebase
import json
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import qrcode

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

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("MainLogin.html", {"request": request})
@app.get("/join")
async def join(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# signup endpoint
@app.post("/signup", include_in_schema=False)
async def signup(request: Request, email: str = Form(...), password: str = Form(...), display_name: str = Form(...)):


   if email is None or password is None:
       return HTTPException(detail={'message': 'Error! Missing Email or Password'}, status_code=400)
   try:
       auth.create_user(email = email,password = password, display_name= display_name)

       return templates.TemplateResponse("signup.html", {"request": request})

   except:
       return HTTPException(detail={'message': 'Error Creating User'}, status_code=400)


@app.post("/login", include_in_schema=False)
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
   try:
       user = firebase.auth().sign_in_with_email_and_password(email, password)
       print(user['displayName'])
       context = {'request': request, 'data': user['displayName']}

       return templates.TemplateResponse("client.html", context)


   except:
       print("ERROR!")
       return templates.TemplateResponse("nidlogin.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host='0.0.0.0')
