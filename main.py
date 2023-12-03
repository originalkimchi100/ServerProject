import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

import firebase_admin
from firebase_admin import credentials, auth

import pyrebase
import json


firebase = pyrebase.initialize_app(json.load(open('firebase_config.json')))


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
async def login(request: Request):
   req_json = await request.json()
   email = req_json['email']
   password = req_json['password']
   print(req_json,email,password)
   try:
       user = firebase.auth().sign_in_with_email_and_password(email, password)

       jwt = user['idToken']

       return JSONResponse(content={'token': jwt}, status_code=200)


   except:
       return HTTPException(detail={'message': 'There was an error logging in'}, status_code=400)


if __name__ == "__main__":
    uvicorn.run("main:app")