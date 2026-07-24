import redis
from fastapi import FastAPI , Request , Response
from fastapi.responses import JSONResponse
import uvicorn
import time
import uuid
from fixed_window_middleware import RateLimiter_FixedWindow_MiddleWare
app = FastAPI()
r = redis.Redis(host = 'localhost' , port = 6379 , decode_responses = True)


RateLimiter_FixedWindow_MiddleWare(app)
@app.get("/login")
def home(request : Request):       
    return {"message" : "hello in our main page" , "User" : r.hgetall(name = request.cookies.get("user_id"))}
