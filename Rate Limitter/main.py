from collections import defaultdict
import time
from typing import Dict
from fastapi import FastAPI, HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="Rate Limit Demo")

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_records: Dict[str, float] = defaultdict(float)

    async def log_message(self, message: str):
        print(f"Message: {message}")

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        currTime = time.time()

        if currTime - self.rate_limit_records[client_ip] < 1: # allow 1 request per second
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")
        
        self.rate_limit_records[client_ip] = currTime
        path = request.url.path
        message = f"Request to {path}"
        await self.log_message(message)

        # Process the request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add custom header
        response.headers["X-Request-Time"] = str(process_time)

        return response
    
app.add_middleware(RateLimitMiddleware)

@app.get("/")
async def read_root():
    return {"message": "Hello - FastAPI is running."}

# request_count = {} # client_ip -> (count, window_start)
# RATE_LIMIT = 5
# WINDOW_SIZE = 10

# def is_rate_limited(client_ip: str) -> bool:
#     """Return True if client_ip is rate limited"""
#     now = time.time()
#     window_start = now - (now % WINDOW_SIZE)
#     count, start = request_count.get(client_ip, (0, window_start))

#     if start != window_start:
#         # Reset counter
#         count = 0
#         start = window_start
#     count += 1
#     request_count[client_ip] = (count, start)

#     return count > RATE_LIMIT

# @app.get("/protected")
# async def protected_endpoint(request: Request):
#     client = request.client.host if request.client else "unknown"
    
#     if is_rate_limited(client):
#         HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests!")
#     return {
#         "message": "This is a protected resource (fixed-window limited).",
#         "client": client,
#     }