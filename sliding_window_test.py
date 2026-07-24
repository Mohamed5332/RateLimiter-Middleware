import redis 
import uuid
import time
from fastapi import FastAPI , Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI , Request
from fastapi.responses import JSONResponse
from sliding_window_middleware import SlidingWindow_MiddleWare
import uvicorn
r = redis.Redis(host = 'localhost' , port = 6379 , decode_responses = True)

app = FastAPI()
# middle ware calling...
SlidingWindow_MiddleWare(app)

@app.get("/")
def home_page(request : Request):
    return {"message" : "hello from home page.."}
