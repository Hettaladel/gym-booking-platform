from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView, UserMeView, MyTokenObtainPairView, UserListView
from config.consul_registry import register_with_consul
import threading

# Register with Consul in background to not block startup
threading.Thread(target=register_with_consul, daemon=True).start()

urlpatterns = [
    # /api/auth/register/
    path("auth/register/", RegisterView.as_view(), name="auth-register"),

    # /api/auth/login/
    path("auth/login/", MyTokenObtainPairView.as_view(), name="auth-login"),

    # /api/auth/refresh/
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),

    # /api/users/me/
    path("users/me/", UserMeView.as_view(), name="users-me"),
    
    # /api/users/?ids=1,2,3
    path("users/", UserListView.as_view(), name="users-list"),
]
