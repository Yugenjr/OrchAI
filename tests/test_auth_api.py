import pytest
import os
import json
from orchai.api.gateway import WebhookHandler
import io

class MockReq:
    def makefile(self, *args, **kwargs):
        return io.BytesIO(b"")
    def sendall(self, data):
        pass

class MockServer:
    server_address = ('127.0.0.1', 8080)

def create_handler(method, path, auth_header=None, body=None):
    handler = WebhookHandler(MockReq(), ('127.0.0.1', 12345), MockServer)
    handler.command = method
    handler.path = path
    handler.headers = {}
    if auth_header:
        handler.headers['Authorization'] = auth_header
    
    if body:
        body_bytes = json.dumps(body).encode('utf-8')
        handler.headers['Content-Length'] = str(len(body_bytes))
        handler.rfile = io.BytesIO(body_bytes)
    else:
        handler.rfile = io.BytesIO(b"")
        
    handler.wfile = io.BytesIO()
    
    def send_response(code):
        handler.last_code = code
    def end_headers():
        pass
    def send_header(k, v):
        pass
        
    handler.send_response = send_response
    handler.end_headers = end_headers
    handler.send_header = send_header
    
    return handler

def test_missing_credential():
    handler = create_handler('GET', '/auth/whoami')
    handler.do_GET()
    assert handler.last_code == 401

def test_invalid_credential():
    handler = create_handler('GET', '/auth/whoami', auth_header="Bearer invalid_token")
    handler.do_GET()
    assert handler.last_code == 401

def test_valid_credential_admin_override():
    os.environ["ORCHAI_DEPLOYMENT_TOKEN"] = "test-token"
    handler = create_handler('GET', '/auth/whoami', auth_header="Bearer test-token")
    handler.do_GET()
    assert handler.last_code == 200
    
    response = json.loads(handler.wfile.getvalue().decode('utf-8'))
    assert response["user_id"] == "admin_override"
    assert "ADMIN" in response["roles"]

def test_health_public():
    handler = create_handler('GET', '/health')
    handler.do_GET()
    assert handler.last_code == 200
