# RateLimiter 

# import libraries
from Rate_limiter_middleware_TokenBucket import rate_limiter_middle_ware 
from fastapi import FastAPI , Request
import redis 



# define configrations 
r = redis.Redis(host = 'localhost' , port = 6379 , decode_responses = True)
app = FastAPI()
capacity = 10
refill_rate = 1


# Call middleware..
rate_limiter_middle_ware(app , capacity , refill_rate)



# add end point and test
@app.get("/")
def home_page(request : Request):
    return {"Message": "This is our main page" , "user" : r.hgetall(name = request.cookies.get("user_id"))}
