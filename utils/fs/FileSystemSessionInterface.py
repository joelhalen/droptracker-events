from datetime import datetime, timedelta

from quart import Quart, session, request, redirect, url_for
from quart.sessions import SessionInterface, SecureCookieSession
from cachelib.file import FileSystemCache
import uuid
import json


class FileSystemSessionInterface(SessionInterface):
    def __init__(self, cache_dir, threshold=500, mode=0o600):
        self.cache = FileSystemCache(cache_dir, threshold=threshold, mode=mode)

    def generate_sid(self):
        return str(uuid.uuid4())

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return SecureCookieSession()
        data = self.cache.get(sid)
        if data is not None:
            return SecureCookieSession(json.loads(data))
        return SecureCookieSession()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        sid = request.cookies.get(app.session_cookie_name) or self.generate_sid()
        if not session:
            self.cache.delete(sid)
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        session_data = json.dumps(dict(session))
        timeout_seconds = int(app.permanent_session_lifetime.total_seconds())  # Convert timedelta to seconds
        expiration_time = datetime.utcnow() + timedelta(hours=24)
        self.cache.set(sid, session_data, timeout=timeout_seconds)
        response.set_cookie(app.session_cookie_name, sid, expires=expiration_time, httponly=True, domain=domain,
                            secure=True, samesite='None')
