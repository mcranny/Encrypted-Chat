import bcrypt
import secrets
from functools import wraps
from flask import session
from datetime import datetime, timedelta

def generate_salt():
    return bcrypt.gensalt()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), generate_salt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def generate_session_id():
    return secrets.token_urlsafe(32)

class RateLimiter:
    def __init__(self):
        self.requests = {}
        self.WINDOW_SIZE = 60  # 1 minute
        self.MAX_REQUESTS = 100

    def is_allowed(self, ip):
        now = datetime.now()
        if ip not in self.requests:
            self.requests[ip] = []

        # Remove old requests
        self.requests[ip] = [time for time in self.requests[ip] 
                           if time > now - timedelta(seconds=self.WINDOW_SIZE)]

        # Check if limit exceeded
        if len(self.requests[ip]) >= self.MAX_REQUESTS:
            return False

        # Add new request
        self.requests[ip].append(now)
        return True

rate_limiter = RateLimiter()

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not rate_limiter.is_allowed(request.remote_addr):
            return {'error': 'Rate limit exceeded'}, 429
        return f(*args, **kwargs)
    return decorated_function
