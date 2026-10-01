import json
import os
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from pydantic import ValidationError
from orchai.core.models import Task
from orchai.core.repository import TaskRepository
from orchai.service.task_service import TaskService, TaskServiceError
from orchai.auth.credentials import CredentialManager
from orchai.auth.rate_limit import RateLimiter
from orchai.auth.models import AuthContext, Role, Permission, User, ROLE_PERMISSIONS

class WebhookHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.task_service = TaskService()
        self.cred_manager = CredentialManager()
        self.rate_limiter = RateLimiter()
        # Mock user DB for MVP
        self._users = []
        super().__init__(*args, **kwargs)

    def _authenticate(self):
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        token = auth_header.split(" ")[1]
        
        # Admin override token
        if token == os.environ.get('ORCHAI_DEPLOYMENT_TOKEN'):
            return AuthContext(
                user_id="admin_override",
                tenant_id="global",
                roles=[Role.ADMIN],
                permissions=ROLE_PERMISSIONS[Role.ADMIN]
            )
            
        cred = self.cred_manager.verify(token)
        if not cred:
            return None
            
        # Try to find user to get roles (mock DB fallback to DEVELOPER)
        user = next((u for u in self._users if u.user_id == cred.user_id), None)
        roles = user.roles if user else [Role.DEVELOPER]
        perms = []
        for r in roles:
            perms.extend(ROLE_PERMISSIONS[r])
            
        return AuthContext(
            user_id=cred.user_id,
            tenant_id=cred.tenant_id,
            roles=roles,
            permissions=list(set(perms)),
            credential_id=cred.credential_id
        )

    def _send_response(self, code, payload):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def do_POST(self):
        if not self.path.startswith('/tasks') and not self.path.startswith('/auth'):
            return self._send_response(404, {"error": "Not found"})

        auth_context = self._authenticate()
        if not auth_context:
            return self._send_response(401, {"error": "Unauthorized"})

        if not self.rate_limiter.check_rate_limit(auth_context.user_id, "API_REQUEST"):
            return self._send_response(429, {"error": "Too Many Requests"})

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            if self.path == '/auth/users':
                if not auth_context.has_permission(Permission.USER_ADMIN):
                    return self._send_response(403, {"error": "Forbidden"})
                data = json.loads(body)
                user = User(
                    user_id=data.get("user_id"),
                    tenant_id=data.get("tenant_id", auth_context.tenant_id),
                    username=data.get("username"),
                    display_name=data.get("display_name"),
                    roles=[Role(r) for r in data.get("roles", ["DEVELOPER"])]
                )
                self._users.append(user)
                return self._send_response(201, json.loads(user.model_dump_json()))

            elif self.path == '/auth/credentials':
                if not auth_context.has_permission(Permission.USER_ADMIN):
                    return self._send_response(403, {"error": "Forbidden"})
                data = json.loads(body)
                cred, raw = self.cred_manager.generate(
                    user_id=data.get("user_id"),
                    tenant_id=data.get("tenant_id", auth_context.tenant_id)
                )
                res = json.loads(cred.model_dump_json())
                res["secret_token"] = raw # Only shown once
                return self._send_response(201, res)

            elif self.path == '/tasks':
                if not self.rate_limiter.check_rate_limit(auth_context.tenant_id, "TASK_CREATE"):
                    return self._send_response(429, {"error": "Too Many Requests"})
                    
                data = json.loads(body)
                idem_key = self.headers.get('Idempotency-Key')
                task = self.task_service.create_task(data.get('objective', 'Webhook Task'), idem_key, auth=auth_context)
                self.task_service.start_task(task.id, auth=auth_context)
                return self._send_response(202, {"status": "ACCEPTED", "task_id": task.id})
                
            elif self.path.startswith('/tasks/') and self.path.endswith('/cancel'):
                task_id = self.path.split('/')[2]
                self.task_service.cancel_task(task_id, auth=auth_context)
                return self._send_response(200, {"status": "CANCELLED"})
                
            elif self.path.startswith('/tasks/') and self.path.endswith('/changes'):
                task_id = self.path.split('/')[2]
                data = json.loads(body)
                self.task_service.request_changes(task_id, data.get('feedback', ''), auth=auth_context)
                return self._send_response(200, {"status": "CHANGES_REQUESTED"})

        except json.JSONDecodeError:
            return self._send_response(400, {"error": "Invalid JSON"})
        except TaskServiceError as e:
            if e.code == "FORBIDDEN":
                return self._send_response(403, {"error": e.code, "message": e.message})
            return self._send_response(400, {"error": e.code, "message": e.message})
        except Exception as e:
            return self._send_response(500, {"error": str(e)})

    def do_DELETE(self):
        auth_context = self._authenticate()
        if not auth_context:
            return self._send_response(401, {"error": "Unauthorized"})

        if self.path.startswith('/auth/credentials/'):
            if not auth_context.has_permission(Permission.USER_ADMIN):
                return self._send_response(403, {"error": "Forbidden"})
            cred_id = self.path.split('/')[-1]
            if self.cred_manager.revoke(cred_id):
                return self._send_response(200, {"status": "REVOKED"})
            return self._send_response(404, {"error": "Not Found"})
            
        return self._send_response(404, {"error": "Not found"})

    def do_GET(self):
        if self.path == '/health':
            return self._send_response(200, {"status": "ok"})
            
        if self.path == '/ready':
            # Check basic readiness (TaskRepository, AuditLedger)
            try:
                self.task_service.repository.list()
                self.task_service.ledger
                return self._send_response(200, {"status": "ready"})
            except Exception as e:
                return self._send_response(503, {"status": "not ready", "error": str(e)})
                
        if self.path == '/metrics':
            if 'text/plain' in self.headers.get('Accept', ''):
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; version=0.0.4')
                self.end_headers()
                self.wfile.write(self.task_service.metrics.format_prometheus().encode('utf-8'))
                return
            else:
                return self._send_response(200, self.task_service.metrics.get_metrics())

        auth_context = self._authenticate()
        if not auth_context:
            return self._send_response(401, {"error": "Unauthorized"})

        if self.path == '/auth/whoami':
            return self._send_response(200, json.loads(auth_context.model_dump_json()))
            
        if self.path == '/auth/users':
            if not auth_context.has_permission(Permission.USER_ADMIN):
                return self._send_response(403, {"error": "Forbidden"})
            return self._send_response(200, [json.loads(u.model_dump_json()) for u in self._users])

        if self.path.startswith('/tasks/') and self.path.endswith('/events'):
            task_id = self.path.split('/')[2]
            try:
                events = self.task_service.get_events(task_id, auth=auth_context)
                return self._send_response(200, {"events": events})
            except TaskServiceError as e:
                return self._send_response(403 if e.code == "FORBIDDEN" else 400, {"error": e.code})
            
        elif self.path.startswith('/tasks/') and self.path.endswith('/audit'):
            task_id = self.path.split('/')[2]
            try:
                events = self.task_service.get_events(task_id, auth=auth_context)
                return self._send_response(200, {"audit_events": events})
            except TaskServiceError as e:
                return self._send_response(403 if e.code == "FORBIDDEN" else 400, {"error": e.code})
            
        elif self.path.startswith('/tasks/'):
            task_id = self.path.split('/')[2]
            try:
                task = self.task_service.get_task(task_id, auth=auth_context)
                if not task:
                    return self._send_response(404, {"error": "Not Found"})
                return self._send_response(200, json.loads(task.model_dump_json()))
            except TaskServiceError as e:
                return self._send_response(403 if e.code == "FORBIDDEN" else 400, {"error": e.code})

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, WebhookHandler)
    httpd.serve_forever()
