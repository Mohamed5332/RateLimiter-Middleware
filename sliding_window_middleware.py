import redis 
import uuid
import time
from fastapi import FastAPI , Request
from fastapi.responses import JSONResponse
r = redis.Redis(host = 'localhost' , port = 6379)


def SlidingWindow_MiddleWare(app):
    def handle_user_request(request : Request):
        user_id = request.cookies.get("user_id")
        if user_id is None :
            user_id = str(uuid.uuid4())

        req_id = str(uuid.uuid4())    
        return user_id , req_id    

    def sliding_window(user_id , req_id , window = 10 , limit = 5):
        now = time.time()
        r.zremrangebyscore(user_id , 0 , now - window)
        number_of_requests = r.zcard(user_id)
        if number_of_requests < limit :
            r.zadd(user_id, {req_id : now})
            return True
        else :
            return False

    @app.middleware("http")
    async def SlidingWindow_MiddleWare(request : Request , call_next):
        user_id , req_id = handle_user_request(request)

        flag = sliding_window(user_id , req_id)
        if flag : 
            # go to the end point..
            response = await call_next(request)
            if request.cookies.get("user_id") is None:
                response.set_cookie("user_id" , user_id)

            return response
        else :
            return JSONResponse(status_code = 429 , content = "Rate limit execeeded , try again later...")  