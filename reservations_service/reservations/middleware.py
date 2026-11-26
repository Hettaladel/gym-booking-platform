from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser

class SimpleUser:
    def __init__(self, id, role, username):
        self.id = id
        self.role = role
        self.username = username
        self.is_authenticated = True
        self.is_active = True
        self.is_staff = (role == 'ADMIN')
    
    def __str__(self):
        return self.username

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.COOKIES.get('access_token')
        if token:
            try:
                # Validates token using SECRET_KEY from settings
                access_token = AccessToken(token)
                
                # Extract claims
                user_id = access_token.get('user_id')
                role = access_token.get('role', 'MEMBER')
                username = access_token.get('username', 'User')
                
                request.user = SimpleUser(user_id, role, username)
            except Exception:
                # Token invalid or expired
                pass 
                
        # Fallback handled by Django default middleware if installed, 
        # but if we want to ensure request.user is set for our templates:
        if not hasattr(request, 'user') or request.user is None:
             request.user = AnonymousUser()

        response = self.get_response(request)
        return response
