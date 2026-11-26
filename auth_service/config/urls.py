from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import frontend_login, frontend_register, frontend_logout, AdminDashboardView, AdminUserListView, AdminUserUpdateView, AdminUserDeleteView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Frontend Routes
    path("auth/login/", frontend_login, name="login"),
    path("auth/register/", frontend_register, name="register"),
    path("auth/logout/", frontend_logout, name="logout"),

    # Custom Admin Dashboard (gym-admin/ to avoid conflict with admin/)
    path("gym-admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("gym-admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("gym-admin/users/<int:pk>/edit/", AdminUserUpdateView.as_view(), name="admin-user-update"),
    path("gym-admin/users/<int:pk>/delete/", AdminUserDeleteView.as_view(), name="admin-user-delete"),

    # API Routes
    # ⚠️ Les endpoints token doivent être AVANT le include("accounts.urls")
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Toutes les routes de l'app accounts (login personnalisé, /users/me/, etc.)
    path("api/", include("accounts.urls")),
]
