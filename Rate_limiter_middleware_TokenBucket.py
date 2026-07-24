import time
import redis
import uuid
from fastapi.responses import JSONResponse
from fastapi import Response , Request , FastAPI
r = redis.Redis(host = 'localhost' , port = 6379 , decode_responses = True)
class RateLimiter():
    def __init__(self, user_id , capacity = 10 , refill_rate = 1): 
        self.user_id = user_id
        self.capacity = capacity
        self.refill_rate = refill_rate

    def process_request(self):
        now = time.time()
        data = r.hgetall(name=self.user_id)

        last_time = float(data['last_time'])
        tokens = int(data['tokens'])
        difference = now - last_time
        amount = min(self.capacity , int(difference * self.refill_rate) + tokens)

        if amount >= 1 :
            amount = amount - 1
            r.hset(name=self.user_id , mapping={
                'tokens' : amount, 
                'last_time' : time.time() 
            })  
            return True
        else :
            return False



def rate_limiter_middle_ware(app , capacity , refill_rate):
    def handle_user_status(request : Request ):
            user_id = request.cookies.get("user_id")
            is_new = False
            if user_id is None :
                user_id = str(uuid.uuid4())
                r.hset(name = user_id , mapping = {
                    'tokens': capacity , 
                    'last_time' : time.time()
                })
                is_new = True
            if not r.exists(user_id):
                r.hset(name=user_id, mapping={
                    'tokens' : capacity, 
                    'last_time' : time.time()
                })
    
            rate_limiter = RateLimiter(user_id , capacity , refill_rate)
            flag = rate_limiter.process_request()
    
            return user_id , flag , is_new     
        
    @app.middleware("http")
    async def Rate_limiter_middleware(request : Request , call_next):

        user_id , flag , is_new = handle_user_status(request)
        if flag : 
            response = await call_next(request)
            if is_new:
                response.set_cookie(key = "user_id" , value = user_id , httponly = True)

            return response
        
        else :
            return JSONResponse(content = "Rate limit exceeded , try again later..." , status_code= 429)
