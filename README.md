# Rate Limiter Middleware

A small FastAPI + Redis middleware that stops any single client from hammering your API. It sits in front of your routes, checks how many requests that user has made recently, and returns `429` if they've gone over the limit. Three classic algorithms are implemented, each as a drop-in one-liner.

## Algorithms

| Algorithm | Redis structure | Good for |
|---|---|---|
| **Fixed Window** | Hash | Simple hourly/daily quotas |
| **Sliding Window Log** | Sorted Set | Strict limits — logins, OTPs |
| **Token Bucket** | Hash | General API traffic, allows bursts |

## Tech Stack

FastAPI · Redis · Python 3.9+

## Getting Started

```bash
pip install fastapi uvicorn redis
docker run -d -p 6379:6379 redis:7-alpine
uvicorn sliding_window_test:app --reload
```

## Usage

Attach the limiter to your app in one line:

```python
app = FastAPI()
SlidingWindow_MiddleWare(app)
```

## Try It

```bash
curl -i -c cookies.txt -b cookies.txt http://localhost:8000/
```

The first response sets a `user_id` cookie. Keep sending with the same cookie and the 6th request within 10 seconds comes back as `429` — wait for the window to pass and you're allowed through again.

> **Note:** each client is identified by a cookie, so the limits are per-browser. For production, key on an authenticated user ID or API key instead.

## Docs

Architecture, design diagrams, complexity analysis and the Redis data model are in [`Rate_Limiting_Middleware_Documentation.pdf`](./Rate_Limiting_Middleware_Documentation.pdf).
