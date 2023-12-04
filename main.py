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

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("MainLogin.html", {"request": request})

firebase = pyrebase.initialize_app(json.load(open('firebase_config.json')))

@app.get("/loggedin", response_class=HTMLResponse)
async def loggedIn(request: Request, email: str):

    context = {'request': request, 'data': email}

    return templates.TemplateResponse("client.html", context)


firebase = pyrebase.initialize_app(json.load(open('firebase_config.json')))
# signup endpoint
@app.post("/signup", include_in_schema=False)
async def signup(request: Request):
   req = await request.json()
   email = req['email']
   password = req['password']
   if email is None or password is None:
       return HTTPException(detail={'message': 'Error! Missing Email or Password'}, status_code=400)
   try:
       user = auth.create_user(
           email = email,
           password = password
       )
       return JSONResponse(content={'message': f'Successfully created user {user.uid}'}, status_code=200)
   except:
       return HTTPException(detail={'message': 'Error Creating User'}, status_code=400)


@app.post("/login", include_in_schema=False)
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
   try:
       firebase.auth().sign_in_with_email_and_password(email, password)
       print("sdafsfas")


       return RedirectResponse(url= f"/loggedin?email={email}", status_code=status.HTTP_303_SEE_OTHER)


   except:
       return HTTPException(detail={'message': 'There was an error logging in'}, status_code=400)


if __name__ == "__main__":
    uvicorn.run("main:app")