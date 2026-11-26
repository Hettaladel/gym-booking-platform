from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user and request.user.is_staff:
            return True
        try:
            return request.user.token.get('role') == 'ADMIN'
        except:
            return False


class IsCoachOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions for Admin or Coach
        if request.user and request.user.is_staff:
            return True
            
        # Check if user has 'role' in token (we will need to parse this from token or request.user)
        # Since we use stateless JWT, the user object might not have 'role' attribute directly populated 
        # heavily dependent on how authentication backend is set up. 
        # However, SimpleJWT 'JWTStatelessUserAuthentication' populates user from token claims.
        # So we can check request.user.role if we mapped it, or check the token payload directly.
        
        # Let's assume the user object has a role attribute, or we check the token claim.
        # Actually standard Django User model doesn't have 'role', but the one in Auth service does.
        # Here in Courses service, request.user is likely a SimpleJWT TokenUser.
        
        # Let's check if 'role' is in request.user.token
        try:
            return request.user.token.get('role') in ['COACH', 'ADMIN']
        except:
            return False
