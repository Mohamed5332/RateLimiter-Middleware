import redis
from fastapi import FastAPI , Request , Response
from fastapi.responses import JSONResponse
import uvicorn
import time
import uuid
app = FastAPI()
r = redis.Redis(host = 'localhost' , port = 6379 , decode_responses = True)


def user_registration(request : Request):
    is_new_user = False
    user_id = request.cookies.get("user_id")
    if user_id is None :
        user_id = str(uuid.uuid4())
        is_new_user = True    
    
    if not r.exists(user_id) :
        r.hset(name = user_id , mapping={
            "counter" : 0,
            "start_point" : time.time()
        })

    return user_id , is_new_user




@app.middleware("http")
async def RateLimiter(request : Request, call_back):
    user_id , is_new_user = user_registration(request)
    flag = Fixed_window(user_id , fixed_window = 10 , max_count = 10)
    if flag:
        response = await call_back(request)
        if is_new_user:
            response.set_cookie(
                key="user_id",
                value=user_id,
                httponly=True
            )
        return response 
    else :
        return JSONResponse(content="Rate limit exceeded, try again later...")



def Fixed_window(user_id , fixed_window = 10 ,  max_count = 10):
    counter = int(r.hget(name = user_id , key = "counter"))
    start_point = float(r.hget(name = user_id , key = "start_point"))
    now = time.time()
    if (now - start_point) < fixed_window :

        if counter < max_count :
            # accept the requst then do some thing
            counter +=1
            r.hset(name = user_id , key = "counter" , value = counter)
            return True

        else :
            # reject the request and send rejection message
            return False
    else:
        # accept the request
        r.hset(name = user_id , mapping = {
            "counter" : 1 , 
            "start_point" : time.time()
        })
        return True
                    


def RateLimiter_FixedWindow_MiddleWare(app):
    def user_registration(request : Request):
        is_new_user = False
        user_id = request.cookies.get("user_id")
        if user_id is None :
            user_id = str(uuid.uuid4())
            is_new_user = True    
        
        if not r.exists(user_id) :
            r.hset(name = user_id , mapping={
                "counter" : 0,
                "start_point" : time.time()
            })

        return user_id , is_new_user

    def Fixed_window(user_id , fixed_window = 10 ,  max_count = 10):
        counter = int(r.hget(name = user_id , key = "counter"))
        start_point = float(r.hget(name = user_id , key = "start_point"))
        now = time.time()
        if (now - start_point) < fixed_window :

            if counter < max_count :
                # accept the requst then do some thing
                counter +=1
                r.hset(name = user_id , key = "counter" , value = counter)
                return True

            else :
                # reject the request and send rejection message
                return False
        else:
            # accept the request
            r.hset(name = user_id , mapping = {
                "counter" : 1 , 
                "start_point" : time.time()
            })
            return True

    @app.middleware("http")
    async def RateLimiter(request : Request, call_back):
        user_id , is_new_user = user_registration(request)
        flag = Fixed_window(user_id , fixed_window = 10 , max_count = 10)
        if flag:
            response = await call_back(request)
            if is_new_user:
                response.set_cookie(
                    key="user_id",
                    value=user_id,
                    httponly=True
                )
            return response 
        else :
            return JSONResponse(content="Rate limit exceeded, try again later...")    